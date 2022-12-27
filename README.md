# TenMeeting-SchoolHelper
🔥 基于网课环境设计的腾讯会议定时自动入会工具

### Features
 - 支持设定课程表 `schedule.json`
 - 支持要求密码的会议
 - 根据时间段在上课时加入，下课时退出
 - 提前N分钟进入课堂
 - 并非完全后台“挂”，想听的时候调出窗口就能听

### Usage
 - 准备 EdgeDriver （msedgedriver.exe） 放在 `tsh.py` 同级目录
 - 配置 `sample_config.json` 和 `sample_schedule.json`
 - 修改名称，去除 `sample_` 前缀
 - 执行
```
python tsh.py
```
 - 一直挂着就行了