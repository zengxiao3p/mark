
介绍：
	本项目使用python3.5.2,使用scrapy作为爬取框架，主要爬取银行营销信息的爬虫项目，使用selenium模拟人工操作流程，包括保存登录信息cookies。
模拟人工操作规避ajax请求的动态渲染等问题。mysql作为持久化保存数据。


主要爬取的银行如下：
   中国银行
   工商银行
   农业银行
   建设银行
   交通银行
   民生银行
   广发银行
   广州银行
   招商银行
   平安银行
   浦发银行
   邮储银行
   农商行
   中信银行
   广大银行
   华夏银行


主要爬取的来源如下：
1、银行官网 
2、微信搜狗
3、微小宝。
4、银行标书（中标易，剑鱼）



	本项目采用scrapy作为爬取框架，详细的框架的使用请详细参考：https://github.com/scrapy/scrapy，
采用spiders->middlewares->pipelines->items 流程处理爬取流程。
1、spiders     发出请求
2、middlewares 我的中间件预处理请求
3、pipelines   处理爬取完的信息
4、item        将保存的信息实体作为对象。


文件结构：
biaoshu：        银行标书
weixinsougou：   微信搜狗
weixiaobao：     微小宝
其他：           按照银行拼音的各个银行官网信息


环境：
windows 7/10
python3.5.2
谷歌浏览器 70.0.3538.110（正式版本） （64 位）
mysql 5.5



运行使用：
1、首先保证含有python环境，本项目集成python3.5.2
2、安装编辑器，编辑本项目的时候使用pycharm。安装教程，自行谷歌
3、导入本项目，pip安装相应的依赖包，包括scrapy、selenium、pymysql，
4、本项目使用selenium，所以安装谷歌浏览器。以及相应的谷歌浏览器的驱动。
5、导入marking-spiders_back_4_26.sql
6、进入需要运行的文件夹（例如weixinsougou），修改相应的settings.py,包括mysql数据库账号和密码，或者其他参数。
7、运行相应模块的运行命令文件，例如：文件夹biaoshu/zby_start_biaoshu.py 



***********************************注意***********************************

   1、解决windows 命令行找不到pip命令的方法：
       1）找到安装python.exe的文件夹
       2）添加Script文件夹路径到环境变量当中。环境：C:\Users\user\AppData\Local\Programs\Python\Python35\Scripts

   2、解决安装scrapy会出现不能安装问题，报出Twisted 版本的错误时：
       1）手动安装Twisted-18.9.0-cp35-cp35m-win_amd64.whl文件即可解决
       2）运行 pip install 你的路径\Twisted-18.7.0-cp37-cp37m-win_amd64.whl
	   参考：https://www.jianshu.com/p/a294a4b2bcde
	   参考：https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted
	   
   3、本项目使用selenium，所以安装谷歌浏览器。以及相应的谷歌浏览器的驱动。
   参考：http://npm.taobao.org/mirrors/chromedriver/
   参考：https://blog.csdn.net/yoyocat915/article/details/80580066   

***********************************注意***********************************









