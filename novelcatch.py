import os
import sys
import asyncio
import re
import requests
from pyquery import PyQuery as pq

base_download_dir = "download"
base_url = "https://www.23qb.com"
regex_newline = re.compile("\n+")

def normal(value: str) -> str:
    chars = '\\/:*?"<>|'
    replacechars = '＼／：＊？“〈〉｜'
    for c in chars:
        value = value.replace(c,replacechars[chars.index(c)])
    return value

def download_content(chapter_url: str) -> (pq, bool, str):
    resp = requests.get(chapter_url)
    if resp.status_code != 200:
        print(resp.status_code)
    chapter = pq(resp.content)
    chapter_content = chapter("div#mlfy_main_text div#TextContent").remove("dt")
    continue_flag = len(chapter("div#mlfy_main_text div#TextContent center"))==1
    next_chapter_url = ''
    if continue_flag:
        next_chapter_url = base_url + chapter("body#readbg p.mlfy_page a:nth-child(5)")[0].get("href")
    return (regex_newline.sub("\n",chapter_content.remove("center").text()), continue_flag, next_chapter_url)

async def savefile(workername, filename, num, chapter_name, chapter_url):
    loop = asyncio.get_event_loop()
    chapter_content, continue_flag, next_chapter_url = await loop.run_in_executor(None, download_content, chapter_url)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(chapter_name)
        f.write("\n\n")
        while True:
            f.write(chapter_content)
            f.flush()
            if continue_flag:
                print(f"{workername} downloading {num:05d}\t{next_chapter_url}")
                chapter_content, continue_flag, next_chapter_url = await loop.run_in_executor(None, download_content, next_chapter_url)
            else:
                break

async def worker(name, queue):
    while not queue.empty():
        filename, num, chapter_name, chapter_url = await queue.get()
        print(f"{name} start job {num:05d} {chapter_name}\n{name} downloading {num:05d}\t{chapter_url}")
        await savefile(name, filename, num, chapter_name, chapter_url)
        print(f'{name} finish job {num:05d} {chapter_name}')
        queue.task_done()

async def main():
    book_no = sys.argv[1]    
    book_url = base_url+"/book/"+book_no+"/"
    start_download_chapter_name = ""
    if len(sys.argv)>2:
        start_download_chapter_name = sys.argv[2]
    resp = requests.get(book_url)
    if resp.status_code != 200:
        print(resp.status_code)
    doc = pq(resp.content)
    bookname = doc("div#maininfo div#bookinfo div.d_title h1:nth-child(1)")[0].text_content()
    download_dir = os.path.join(base_download_dir, normal(bookname))
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    num=1
    queue = asyncio.Queue()
    for it in doc("ul#chapterList li a"):
        chapter_name = it.text_content()
        if len(start_download_chapter_name)>0 and start_download_chapter_name != chapter_name:
            num += 1
            continue
        else:
            start_download_chapter_name = ""
        chapter_url = base_url+it.get("href")
        filename = os.path.join(download_dir, "{:05d}_{!s}.txt".format(num, normal(chapter_name)))
        queue.put_nowait((filename, num, chapter_name, chapter_url))
        num += 1

    tasks = []
    for i in range(5):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    await queue.join()

if __name__ == "__main__":
    asyncio.run(main())