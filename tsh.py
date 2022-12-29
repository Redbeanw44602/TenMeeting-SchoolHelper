from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import json

TENCENT_MEETING_URL = "https://voovmeeting.com/r/"

CFG_VERSION         = 100
SCHEDULE_VERSION    = 100

CRON_LOOP_SLEEP = 30
WAIT_FOR_LOAD   = 10

cfg         = None
schedule    = None
driver      = None

today           = None
today_schedule  = None

def generate_schedule():
    global today_schedule
    current = time.localtime(time.time())
    s = current[:]
    e = current[:]
    today_schedule = []
    for i in schedule['day_schedule']:
        # element [[8,30],[9,10]]
        # time tuple:
        # 0 tm_year     5 tm_sec
        # 1 tm_mon      6 tm_wday
        # 2 tm_mday     7 tm_yday
        # 3 tm_hour     8 tm_isdst
        # 4 tm_min
        s = s[:3] + (i[0][0], i[0][1], 0,) + s[6:]
        e = e[:3] + (i[1][0], i[1][1], 0,) + e[6:]
        today_schedule.append([time.mktime(s),time.mktime(e)])


def run_mainjob(meetingId,password):
    driver.get(TENCENT_MEETING_URL)

    time.sleep(WAIT_FOR_LOAD)

    inputs = driver.find_elements(By.CLASS_NAME, 'join-form__input')
    inputs[0].send_keys(meetingId)
    inputs[1].send_keys(cfg['join']['name']) # personName
    driver.find_element(By.CLASS_NAME, "join-form__button").click() #join the meeting.

    time.sleep(WAIT_FOR_LOAD)

    try:
        driver.switch_to.frame(0)
        driver.find_element(By.CLASS_NAME, 'fill-in-region-and-birth_button__GLPOf').click() #location verify
        driver.find_element(By.CLASS_NAME, 'met-checkbox').click() #license agreement.
        driver.find_element(By.CLASS_NAME, 'voov-agreement_button__OLc_O').click() #next
    except NoSuchElementException:
        pass

    time.sleep(WAIT_FOR_LOAD)

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
        current = time.time()
        tmp_today = wday_to_str[time.localtime(current).tm_wday]
        if today != tmp_today:
            print("正在更新时间表...")
            generate_schedule()
        today = tmp_today
        loops_count = -1
        if schedule['courses'][today]:
            allNoClass = True
            for i in today_schedule:
                loops_count += 1
                # element timestamp: [start,end]
                if not (current + cfg['join']['early_min'] * 60 >= i[0] and current <= i[1]):
                    # print('不在第 %s 节课时间段内' % (loops_count + 1))
                    continue
                allNoClass = False
                current_class = schedule['courses'][today][loops_count]
                if not current_class:
                    print('已配置当前时间段，但没有任何课程')
                    break
                if driver:
                    print('正在上第 %s 节课...' % (loops_count + 1))
                    break
                print('即将上课: 第 %s 节, %s 课程, 自动加入会议...' % (loops_count + 1, current_class))
                meet = schedule['classes'][current_class]
                protected_run_job(meet['meetingId'],meet['password'])
                break
            if allNoClass:
                print("当前时间没有课程")
                if driver:
                    driver.quit()
                    driver = None
        else:
            print('今天没有任何课程')
        print('进入休眠 %ss' % CRON_LOOP_SLEEP)
        time.sleep(CRON_LOOP_SLEEP)