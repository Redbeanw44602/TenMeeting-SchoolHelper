from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import json

TENCENT_MEETING_URL = "https://voovmeeting.com/r/"

CFG_VERSION         = 100
SCHEDULE_VERSION    = 100

CRON_LOOP_SLEEP = 30

cfg         = None
schedule    = None
driver      = None

def run_mainjob(meetingId,password):
    driver.get(TENCENT_MEETING_URL)

    time.sleep(3)

    inputs = driver.find_elements(By.CLASS_NAME, 'join-form__input')
    inputs[0].send_keys(meetingId)
    inputs[1].send_keys(cfg['join']['name']) # personName
    driver.find_element(By.CLASS_NAME, "join-form__button").click() #join the meeting.

    time.sleep(3)

    try:
        driver.switch_to.frame(0)
        driver.find_element(By.CLASS_NAME, 'fill-in-region-and-birth_button__GLPOf').click() #location verify
        driver.find_element(By.CLASS_NAME, 'met-checkbox').click() #license agreement.
        driver.find_element(By.CLASS_NAME, 'voov-agreement_button__OLc_O').click() #next
    except NoSuchElementException:
        pass

    time.sleep(3)

    try:
        pwd_input = driver.find_element(By.CLASS_NAME, "tea-input")
        pwd_input.click()
        pwd_input.send_keys(password)
        driver.find_elements(By.CLASS_NAME, "dialog-btn")[1].click()
    except NoSuchElementException:
        pass

def protected_run_job(id,pwd):
    global driver
    if not driver:
        driver = webdriver.Edge()
    try:
        run_mainjob(id,pwd)
    except:
        print('run_mainjob 发生异常！')
        time.sleep(1)
        protected_run_job(id,pwd)


if __name__ == '__main__':


    cfg = json.loads(open('config.json','r+',encoding='utf-8').read())
    schedule = json.loads(open('schedule.json','r+',encoding='utf-8').read())
    #driver = webdriver.Edge()

    assert schedule and schedule['version'] == SCHEDULE_VERSION, '课表文件版本号不匹配'
    assert cfg and cfg['version'] == CFG_VERSION, '配置文件版本号不匹配'

    wday_to_str = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    print('[[进入任务循环]]')
    cron_loops_count = 0
    while True:
        cron_loops_count += 1
        print('[第 %s 次常规任务循环]' % cron_loops_count)
        current = time.localtime(time.time())
        hr = current.tm_hour
        mi = current.tm_min
        da = wday_to_str[current.tm_wday]
        loops_count = -1
        print('当前时间: %s %s:%s' % (da,hr,mi))
        if schedule['courses'][da]:
            allNoClass = True
            for i in schedule['day_schedule']:
                loops_count += 1
                # element [[8,30],[9,10]]
                if not ((hr >= i[0][0] and mi + cfg['join']['early_min'] >= i[0][1]) and (hr <= i[1][0] and mi <= i[1][1])):
                    print('不在第 %s 节课时间段 %s:%s ~ %s:%s 内' % (loops_count + 1,i[0][0],i[0][1],i[1][0],i[1][1]))
                    continue
                allNoClass = False
                current_class = schedule['courses'][da][loops_count]
                if not current_class:
                    print('已配置当前时间段，但没有任何课程')
                    break
                if driver:
                    print('正在上课...')
                    break
                print('即将上课: 第 %s 节, %s 课程, 自动加入会议...' % (loops_count + 1, current_class))
                meet = schedule['classes'][current_class]
                protected_run_job(meet['meetingId'],meet['password'])
                break
            if allNoClass and driver:
                driver.quit()
                driver = None
        else:
            print('今天没有任何课程')
        print('进入休眠 %ss' % CRON_LOOP_SLEEP)
        time.sleep(CRON_LOOP_SLEEP)