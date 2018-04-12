# 自如租房找房邮件自动通知爬虫

### 简介
    本项目初衷是为满足自己找房需求，通过爬虫程序定期爬取某些房源列表并按照给
    定规则筛选出满足自己需求的房源，筛选条件包括价格、面积、朝向、步行时间、距离等几个维度。

### 使用方式
 1. 将configurations.py.bak 重命名为 configurations.py
 2. 配置好configurations.py 邮件相关参数
 3. config中key是高德地图key，可以从开发者平台中获得 地址为[http://lbs.amap.com](http://lbs.amap.com)
    服务平台选择web服务即可，按每半小时调用一次的话，一天大约几百次路径规划调用，完全到不了收费的次数限制。
 4. 设置好相关配置项，代码中注释已经足够详细。自如房源url可以从浏览器打开我给的实例url，自行变更参数，后续会增加多个url适配
 5. pip3 install -r requirements.txt
 6. 执行 ziroom_spider.py

### 注意
    即便有这个程序，我依然绝望的发现，倒计时结束后手速不够快还是抢不到。
    另外，自如有个分期付款，每月都会有手续费，所以资金不太紧张的最好还是选择季付以上的方式租房。
    最后，希望大家都能找到适合自己的房源

### extra crontab 配置
```
export LANG="en_US.UTF-8";
cd /path/to/ziroom_crawler
/usr/local/bin/python3 ./ziroom_spider.py
```
脚本路径和python环境路径可以自行设置，
修改完成后保存到项目根目录，命名为 start.sh，
crontab 配置如下：
```
*/30 * * * *  /path/to/ziroom_crawler/start.sh > /path/to/ziroom_crawler/logs.txt 2>&1
```
时间间隔可自行调整

### 效果如下
![ddd](art/pic01.png)

![ddd](art/pic02.png)

