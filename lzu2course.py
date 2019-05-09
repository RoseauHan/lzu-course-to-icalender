#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup as bs
import re
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta, timezone
from icalendar import Calendar, Event
from uuid import uuid1
import traceback
import os

loginurl = 'http://my.lzu.edu.cn/userPasswordValidate.portal'
homeurl = 'http://my.lzu.edu.cn/index.portal'
courseurl = 'http://jwk.lzu.edu.cn/academic/calogin.jsp'
mainurl = "http://jwk.lzu.edu.cn/academic/student/currcourse/currcourse.jsdo"


def parRawData(str):
    weak_dic = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "日": 7,
        "天": 7
    }
    day_dic = {
        "第1节": {"sTime": time(8, 30), "eTime": time(10, 10)},
        "上午12节": {"sTime": time(8, 30), "eTime": time(9, 15)},
        "上午123节": {"sTime": time(8, 30), "eTime": time(11, 15)},
        "上午1-4节": {"sTime": time(8, 30), "eTime": time(12, 10)},
        "1-6节": {"sTime": time(8, 30), "eTime": time(16, 10)},
        "1-8节": {"sTime": time(8, 30), "eTime": time(18, 10)},
        "1-9节": {"sTime": time(8, 30), "eTime": time(19, 45)},
        "第2节": {"sTime": time(9, 25), "eTime": time(12, 10)},
        "上午234节": {"sTime": time(9, 25), "eTime": time(12, 10)},
        "第3节": {"sTime": time(10, 30), "eTime": time(11, 15)},
        "上午34节": {"sTime": time(10, 30), "eTime": time(12, 10)},
        "3-6节": {"sTime": time(10, 30), "eTime": time(16, 10)},
        "3-8节": {"sTime": time(10, 30), "eTime": time(18, 10)},
        "3-10节": {"sTime": time(10, 30), "eTime": time(20, 40)},
        "第4节": {"sTime": time(11, 25), "eTime": time(12, 10)},
        "中午1节": {"sTime": time(12, 20), "eTime": time(13, 15)},
        "中午2节": {"sTime": time(13, 25), "eTime": time(14, 20)},
        "第5节": {"sTime": time(14, 30), "eTime": time(15, 15)},
        "下午56节": {"sTime": time(14, 30), "eTime": time(16, 10)},
        "下午5-7节": {"sTime": time(14, 30), "eTime": time(17, 15)},
        "下午5-8节": {"sTime": time(14, 30), "eTime": time(18, 10)},
        "5-10节": {"sTime": time(14, 30), "eTime": time(20, 40)},
        "5-11节": {"sTime": time(14, 30), "eTime": time(21, 35)},
        "5-12节": {"sTime": time(14, 30), "eTime": time(22, 30)},
        "第6节": {"sTime": time(15, 25), "eTime": time(16, 10)},
        "下午6-8节": {"sTime": time(15, 25), "eTime": time(18, 10)},
        "第7节": {"sTime": time(16, 30), "eTime": time(17, 15)},
        "下午78节": {"sTime": time(16, 30), "eTime": time(18, 10)},
        "7-9节": {"sTime": time(16, 30), "eTime": time(19, 45)},
        "7-10节": {"sTime": time(16, 30), "eTime": time(20, 40)},
        "7-12节": {"sTime": time(16, 30), "eTime": time(22, 30)},
        "第8节": {"sTime": time(17, 25), "eTime": time(18, 10)},
        "8-10节": {"sTime": time(17, 25), "eTime": time(20, 40)},
        "第9节": {"sTime": time(19, 0), "eTime": time(19, 45)},
        "晚9-10节": {"sTime": time(19, 0), "eTime": time(20, 40)},
        "晚9-11节": {"sTime": time(19, 0), "eTime": time(21, 35)},
        "晚9-12节": {"sTime": time(19, 0), "eTime": time(22, 30)},
        "第10节": {"sTime": time(19, 55), "eTime": time(20, 40)},
        "第11节": {"sTime": time(20, 50), "eTime": time(21, 35)},
        "晚11-12节": {"sTime": time(20, 50), "eTime": time(22, 30)},
        "第12节": {"sTime": time(21, 45), "eTime": time(22, 30)},
    }
    week_danshaung_dic = {"全": 1, "单": 2, "双": 2}
    all_rawdata = []
    soup = bs(str, features="html.parser")
    course_table = soup(class_="infolist_tab")[0]
    course_table = course_table.find_all(class_='infolist_common')
    i_course_data = {}
    for i in course_table:
        try:
            i_course_data.clear()
            name = i.find(href=re.compile("course_detail")).string.strip()
            teacher = [item.string for item in i.find_all(href=re.compile("showTeacherInfoItem"))]
            all_time = i.table.find_all("tr")
            testime = [item.get_text().split() for item in all_time]
            numofCourseKind = len(testime)   #有几种类型的课
            for i_time in testime:
                if "全周" or "单周" or "双周" in i_time[0]:
                    tmp_zhou = i_time[0]
                    i_time[0] = [int(x) for x in re.findall(r"\d+\.?\d*", i_time[0])]
                    i_time[0].append(week_danshaung_dic[tmp_zhou[-2]])
                else:
                    i_time[0] = -1
                i_time[1] = weak_dic[i_time[1][2]]
                i_time.append(day_dic[i_time[2]])
            for j in range(numofCourseKind):
                i_course_data["name"] = name
                i_course_data["teacher"] = teacher
                i_course_data["xinqiji"] = int(testime[j][1])
                i_course_data["location"] = testime[j][3]
                i_course_data["sTime"] = testime[j][4]["sTime"]
                i_course_data["eTime"] = testime[j][4]["eTime"]
                i_course_data["sWeek"] = int(testime[j][0][0])
                i_course_data["eWeek"] = int(testime[j][0][1])
                i_course_data["EvenOddWeek"] = int(testime[j][0][2])
                all_rawdata.append(i_course_data.copy())
        except:
            i_course_data['name'] = 0
            continue
    return all_rawdata
def lzuLogin():

    print("欢迎使用Lzu2Ics！")
    User = input("请输入兰大邮箱，不包括后缀: ")
    passwd = input("请输入邮箱密码: ")
    payload = {
        'Login.Token1': User,
        'Login.Token2': passwd,
        'goto': "http://my.lzu.edu.cn/loginSuccess.portal",
        'gotoOnFail': "http://my.lzu.edu.cn/loginFailure.portal",
    }
    jwk_headers = {

        "Host": "jwk.lzu.edu.cn",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15",
        "Referer": "http://my.lzu.edu.cn/index.portal",
        "Accept-Language": "zh-cn",
        "Accept-Encoding": "gzip, deflate"
    }
    try:
        session = requests.Session()
        print("开始登录兰大信息门户网站")
        response_login = session.post(loginurl, data=payload, timeout=(3, 5))
        if "handleLoginSuccessed" in response_login.text:
            print("登录成功!")
            print("开始获取课程信息……")
            try:
                all_rawdata = []
                canl = []
                response_home = session.get(homeurl, timeout=(3, 5))
                response_jwkloginklogin = session.get(courseurl, headers=jwk_headers, timeout=(3, 5))
                response_course = session.get(mainurl, headers=jwk_headers, timeout=(3, 5))
                try:
                    all_rawdata = parRawData(response_course.text)
                    cal = Calendar()
                    cal['version'] = '2.0'
                    cal['prodid'] = '-//LZU//roseauhan//CN'
                    date_start = date(2019, 2, 25) # 当前学期开学时间
                    print("请确认当前学期的开学时间是否为 2019/2/25")
                    for item in all_rawdata:
                        event = Event()
                        ev_start_date =date_start + relativedelta(weeks=(item['sWeek']-1),weekday=(item['xinqiji']-1))
                        ev_start_datetime = datetime.combine(ev_start_date, item['sTime'])  # 上课时间
                        ev_end_datetime = datetime.combine(ev_start_date,item['eTime'])
                        ev_interval = item['EvenOddWeek']
                        ev_count = item['eWeek'] - item['sWeek'] + 1 \
                            if not item['EvenOddWeek']==2 else item['eWeek'] - item['sWeek'] // 2 + 1
                        # 添加事件
                        event.add('uid', str(uuid1()) + '@LZU')
                        event.add('summary', item['name'])
                        event.add('dtstamp', datetime.now())
                        event.add('dtstart', ev_start_datetime)
                        event.add('dtend', ev_end_datetime)
                        event.add('location', item['location'])
                        event.add('rrule', {'freq': 'weekly', 'interval': ev_interval, 'count': ev_count})
                        cal.add_component(event)
                    with open('output.ics', 'w+', encoding='utf-8') as file:
                        file.write(cal.to_ical().decode('utf-8'.replace('\r\n', '\n').strip()))
                    print("获取成功！output.ics 请使用谷歌日历打开")
                except Exception as e:
                    print("解析课表错误！")
                    traceback.print_exc()
            except Exception as e:
                print("获取课表错误：")
                print(e)
        else:
            print("账号或密码错误！")
    except Exception as e:
        print("请检查网络错误或其它错误！")
    finally:
        print("Bye！")

if __name__ == '__main__':
    lzuLogin()