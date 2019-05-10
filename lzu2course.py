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
import msvcrt
import os

loginurl = 'http://my.lzu.edu.cn/userPasswordValidate.portal'
homeurl = 'http://my.lzu.edu.cn/index.portal'
courseurl = 'http://jwk.lzu.edu.cn/academic/calogin.jsp'
mainurl = "http://jwk.lzu.edu.cn/academic/student/currcourse/currcourse.jsdo"

# 密码输入自动转为***
def passwdInput():
    print('请输入邮箱密码: ', end='', flush=True)
    li = []
    while 1:
        ch = msvcrt.getch()
        # 回车
        if ch == b'\r':
            msvcrt.putch(b'\n')
            return b''.join(li).decode()
        # 退格
        elif ch == b'\x08':
            if li:
                li.pop()
                msvcrt.putch(b'\b')
                msvcrt.putch(b' ')
                msvcrt.putch(b'\b')
        # Esc
        elif ch == b'\x1b':
            break
        else:
            li.append(ch)
            msvcrt.putch(b'*')
    os.system('pause')

# 选择学期，获取payload及开学日期
def getCoursePayload():
    timeDict = {
        "91": {"y": 2019, "m": 2, "d": 25, "term": 1, "year": 39, "info": "2019春季学期"},
        "92": {"y": 2019, "m": 9, "d": 1, "term": 2, "year": 39, "info": "2019秋季学期"},
        "81": {"y": 2018, "m": 3, "d": 5, "term": 1, "year": 38, "info": "2018春季学期"},
        "82": {"y": 2018, "m": 9, "d": 2, "term": 2, "year": 38, "info": "2018秋季学期"},
        "71": {"y": 2017, "m": 2, "d": 27, "term": 1, "year": 37, "info": "2017春季学期"},
        "71": {"y": 2017, "m": 9, "d": 4, "term": 2, "year": 37, "info": "2017秋季学期"},
        "62": {"y": 2016, "m": 8, "d": 29, "term": 2, "year": 36, "info": "2016秋季学期"},
    }
    print("当前可选的学期信息如下：")
    for key in timeDict:
        print(key + "：" + timeDict[key]['info'])
    print("00: 自定义学期信息")

    while 1:
        termSelect = int(input("请输入对应学期前的数字: "))
        if termSelect in timeDict.keys() or "00":
            break
        else:
            print("参数错误，请检查")
    if termSelect == 00:
        timeInput = input("请按照'年 月 日 学期'的格式输入开学日期及学期信息\n"
                         "春季学期: 1 , 秋季学期：2\n"
                          "可通过http://jwk.lzu.edu.cn/academic/calendar/calendarViewList.do查询\n")
        # TODO 自动将所有往年学期信息获取
        timeDict["00"]['y'] = timeInput[0]
        timeDict["00"]['m'] = timeInput[1]
        timeDict["00"]['d'] = timeInput[2]
        timeDict["00"]['term'] = timeInput[3]
        timeDict["00"]['year'] = int(timeInput[0]) - 1980
        timeDict["00"]['info'] = timeDict[0] + ("春季学期" if timeInput[3] == 1 else "秋季学期")
        print("TESTTEST")
        print(timeDict["00"]['y'] + timeDict["00"]['m'] + timeDict["00"]['d'] + timeDict["00"]['term'] + timeDict["00"]['info'])

    coursePayload = {
        'year': timeDict[termSelect]['year'],
        'term': timeDict[termSelect]['term']
    }
    date_start = date(timeDict[termSelect]['y'], timeDict[termSelect]['m'], timeDict[termSelect]['d'])
    return coursePayload, date_start

# 自动获取每节课的时间
def getCourseTimeDict(rawCourseData):
    print("正在获取课程时间字典……")
    soup = bs(rawCourseData, features="html.parser")
    courseTimeTable = soup(class_="infolist_tab")[1]
    courseTimeTable = courseTimeTable.find_all(class_='infolist_common')
    time_dict = dict()
    for i in courseTimeTable:
        try:
            courseName = str(i.find_all("td")[1].get_text().replace(" ", "").replace("\n", ''))
            timeHelp = i.find_all("td")[3].get_text().split()
            courseStartHour = int(timeHelp[0][:2])
            courseStartMin = int(timeHelp[0][-2:])
            courseEndHour = int(timeHelp[2][:2])
            courseEndMin = int(timeHelp[2][-2:])
            time_dict[courseName] = {"sTime": time(courseStartHour, courseStartMin),
                                     "eTime": time(courseEndHour, courseEndMin)}
        except Exception as e:
            traceback.print_exc()
            print("获取课程时间失败！！！")
    print("获取课程时间字典成功！")
    return time_dict

# 获取课程详情
def getCourseInfo(rawCourseData):
    print("正在获取课程详情……")
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
    day_dic = getCourseTimeDict(rawCourseData)
    week_danshaung_dic = {"全": 1, "单": 2, "双": 2}
    courseData = []
    soup = bs(rawCourseData, features="html.parser")
    course_table = soup(class_="infolist_tab")[0]
    course_table = course_table.find_all(class_='infolist_common')
    if course_table != False:
        i_course_data = {}
        for i in course_table:
            try:
                i_course_data.clear()
                name = i.find(href=re.compile("course_detail")).string.strip()
                teacher = [item.string for item in i.find_all(href=re.compile("showTeacherInfoItem"))]
                all_time = i.table.find_all("tr")
                testime = [item.get_text().split() for item in all_time]
                numofCourseKind = len(testime)  # 有几种类型的课
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
                    courseData.append(i_course_data.copy())
            except:
                i_course_data['name'] = 0
                continue
                print("获取课程详情失败！！！")
        print("获取课程详情成功！")
        return courseData
    else:
        print("暂无当前时间课表信息！")
        return False

# 将课程转化为ics格式
def toICS(courseInfo,date_start_Argu):
    print("正在生成日历……")
    date_start = date_start_Argu
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//LZU//roseauhan//CN'
    for item in courseInfo:
        event = Event()
        ev_start_date = date_start + relativedelta(weeks=(item['sWeek'] - 1), weekday=(item['xinqiji'] - 1))
        ev_start_datetime = datetime.combine(ev_start_date, item['sTime'])  # 上课时间
        ev_end_datetime = datetime.combine(ev_start_date, item['eTime'])
        ev_interval = item['EvenOddWeek']
        ev_count = item['eWeek'] - item['sWeek'] + 1 \
            if not item['EvenOddWeek'] == 2 else item['eWeek'] - item['sWeek'] // 2 + 1
        # 添加事件
        event.add('uid', str(uuid1()) + '@LZU')
        event.add('summary', item['name'])
        event.add('dtstamp', datetime.now())
        event.add('dtstart', ev_start_datetime)
        event.add('dtend', ev_end_datetime)
        event.add('location', item['location'])
        event.add('rrule', {'freq': 'weekly', 'interval': ev_interval, 'count': ev_count})
        # TODO 添加自定义时间提醒
        cal.add_component(event)

    with open('output.ics', 'w+', encoding='utf-8') as file:
        file.write(cal.to_ical().decode('utf-8'.replace('\r\n', '\n').strip()))
    print("已将所有课程生成日历!")

# 登录
def lzuLogin():
    print("欢迎使用Lzu2Ics！ created by roseauhan")
    User = input("请输入兰大邮箱，不包括后缀: ")
    passwd = passwdInput()
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
        print("开始登录兰大信息门户网站……")
        response_login = session.post(loginurl, data=payload, timeout=(3, 5))
        if "handleLoginSuccessed" in response_login.text:
            print("登录成功!")
            try:
                coursePayload = getCoursePayload()[0]
                date_start = getCoursePayload()[1]
                response_home = session.get(homeurl, timeout=(3, 5))
                response_jwkloginklogin = session.get(courseurl, headers=jwk_headers, timeout=(3, 5))
                response_course = session.get(mainurl, headers=jwk_headers, params=coursePayload, timeout=(3, 5))
                try:
                    courseInfo = getCourseInfo(response_course.text)
                    if courseInfo == False:
                        return
                    else:
                        toICS(courseInfo,date_start)
                        print("Congratulation!\n请使用谷歌日历打开文件：output.ics 进行导入")
                except Exception as e:
                    print("解析课表错误！！！")
                    traceback.print_exc()
            except Exception as e:
                print("获取课表错误！！！")
                traceback.print_exc()
                print(e)
        elif "用户不存在或密码错误" in response_login.text:
            print("账号或密码错误！！！\n即将重新登录")
            lzuLogin()
    except Exception as e:
        print("请检查网络错误或其它错误！！!")
    finally:
        print("感谢使用！Bye！")

if __name__ == '__main__':
    lzuLogin()
