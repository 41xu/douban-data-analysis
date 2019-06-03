# douban-data-analysis
Python Data Analysis 's project. 

> Based on Python 3.6

我用Django把这个简陋的推荐系统实现成了[Web项目](https://github.com/41xu/MovieRecommendWeb)啦！

## 函数介绍

Spide.py为爬取电影数据函数，运行时会有IP被封的风险

Spide.py运行时由于爬取数据量过大因此在运行时可以在主函数的相应注释位置修改每次爬取的数据量，休息一会多爬几次换换IP即可

DataPreprocess.py为保存每个进程爬取数据的函数可以不用运行

Movie.py保存并打印电影信息功能

Recommend.py进行协同过滤，算法输入需要data.csv,及用户id,针对该用户的观影习惯进行电影推荐，在main函数中设置的随机选取一个用户列表中用户进行输入预测，因此不需额外输入用户ID，如需进行其他测试可自行修改

### 相关数据介绍：
total_movies.csv为可获得的最大电影URL记录，存储近一万天电影URL，可在之后的电影信息爬取中进行输入

movies.csv为推荐系统需输入的1000部电影的URL，同时作为电影信息爬取的输入

data.csv为最终爬取的电影相关数据及用户评论相关数据

Data文件夹中为分批爬取的数据的记录存储


徐诗瑶
2018-11-02
