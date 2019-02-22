轻小说抓取器

目前仅支持：
* 抓取 www.23qb.net 的小说，使用小说编号
* 抓取后仅保存为txt

实际使用：
* 在上述小说网站找到需要的小说，比如 [《盾之勇者成名录》](https://www.23qb.net/book/1059/) 其链接为 https://www.23qb.net/book/1059/ 则使用如下命令下载改小说全文：
    >python novelcatch.py 1059
* 可以使用完整章节名指定开始下载的章节，比如：
    >python novelcatch.py 1059 "第十八卷 十三话 转生者"
    
    则只下载从该标题开始的内容及其后续内容
* 下载完成内容保存在download 目录下，该书名的目录中。使用前缀数字标记实际顺序。
* 建议借用carlibre 的功能导入txt 书籍后，批量转换成epub，再使用epub merge 插件合并成合计，导入kindle 观看

后续计划：
* 下载后直接保存为epub 书籍