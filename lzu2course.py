#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
__title__ = 'Course2ics for LZU'
__description__ = 'Spider Class Schedule of LZU and Save to iCalendar file for Calendar App.'
__url__ = 'https://roseauhan.github.io'
__version__ = '1.0'
__author__ = 'roseauhan'
__author_email__ = 'roseauhan@gmail.com'
__copyright__ = 'Copyright 2019 roseauhan'

"""
import os
import re
import msvcrt
import requests
import traceback
from uuid import uuid1
from bs4 import BeautifulSoup as bs
from icalendar import Calendar, Event
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

login_url = 'http://my.lzu.edu.cn/userPasswordValidate.portal'
home_url = 'http://my.lzu.edu.cn/index.portal'
course_url = 'http://jwk.lzu.edu.cn/academic/calogin.jsp'
main_url = "http://jwk.lzu.edu.cn/academic/student/currcourse/currcourse.jsdo"

filename = "课表信息" # 
User: str = "lzuer"


# 密码输入自动转为***
def passwd_input():
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
def get_course_payload():
    time_dict = {
        "91": {"y": 2019, "m": 2, "d": 25, "term": 1, "year": 39, "info": "2019春季学期"},
        "92": {"y": 2019, "m": 9, "d": 1, "term": 2, "year": 39, "info": "2019秋季学期"},
        "81": {"y": 2018, "m": 3, "d": 5, "term": 1, "year": 38, "info": "2018春季学期"},
        "82": {"y": 2018, "m": 9, "d": 2, "term": 2, "year": 38, "info": "2018秋季学期"},
        "71": {"y": 2017, "m": 2, "d": 27, "term": 1, "year": 37, "info": "2017春季学期"},
        "72": {"y": 2017, "m": 9, "d": 4, "term": 2, "year": 37, "info": "2017秋季学期"},
        "62": {"y": 2016, "m": 8, "d": 29, "term": 2, "year": 36, "info": "2016秋季学期"},
    }
    print("当前可选的学期信息如下：")
    for key in time_dict:
        print(key + "：" + time_dict[key]['info'])
    print("0: 自定义学期信息")

    while 1:
        term_select = str(input("请输入对应学期前的数字: "))
        if (term_select in time_dict.keys()) or (term_select == "0"):
            break
        else:
            print("参数错误，请检查")
    if term_select == '0':
        time_input = input("请按照'年 月 日 学期号'的格式输入开学日期及学期信息\n"
                           "春季学期: 1 , 秋季学期：2\n"
                           "可通过http://jwk.lzu.edu.cn/academic/calendar/calendarViewList.do查询\n")
        time_dict[term_select] = {}
        time_dict[term_select]['y'] = int(time_input.split()[0])
        time_dict[term_select]['m'] = int(time_input.split()[1])
        time_dict[term_select]['d'] = int(time_input.split()[2])
        time_dict[term_select]['term'] = int(time_input.split()[3])
        time_dict[term_select]['year'] = int(time_input.split()[0]) - 1980
        time_dict[term_select]['info'] = str(time_dict[term_select]) + (
            "春季学期" if time_input.split()[3] == 1 else "秋季学期")
    course_payload = {
        'year': time_dict[term_select]['year'],
        'term': time_dict[term_select]['term']
    }
    date_start = date(time_dict[term_select]['y'], time_dict[term_select]['m'], time_dict[term_select]['d'])
    global filename
    filename = time_dict[term_select]['info'] + "_" + User + ".ics"
    return course_payload, date_start


# 自动获取每节课的时间
def get_course_time_dict(raw_course_data):
    print("正在获取课程时间字典……")
    soup = bs(raw_course_data, features="html.parser")
    course_time_table = soup(class_="infolist_tab")[1]
    course_time_table = course_time_table.find_all(class_='infolist_common')
    time_dict = dict()
    for i in course_time_table:
        try:
            course_name = str(i.find_all("td")[1].get_text().replace(" ", "").replace("\n", ''))
            time_help = i.find_all("td")[3].get_text().split()
            course_start_hour = int(time_help[0][:2])
            course_start_min = int(time_help[0][-2:])
            course_end_hour = int(time_help[2][:2])
            course_end_min = int(time_help[2][-2:])
            time_dict[course_name] = {"sTime": time(course_start_hour, course_start_min),
                                      "eTime": time(course_end_hour, course_end_min)}
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("获取课程时间失败！！！")
    print("获取课程时间字典成功！")
    return time_dict


# 获取课程详情
def get_course_info(raw_course_data):
    print("正在获取课程详情……")
    week_dic = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "日": 7, "天": 7}
    day_dic = get_course_time_dict(raw_course_data)
    week_evenodd_dic = {"全": 1, "单": 2, "双": 2}
    course_data = []
    soup = bs(raw_course_data, features="html.parser")
    course_table = soup(class_="infolist_tab")[0]
    course_table = course_table.find_all(class_='infolist_common')
    has_course_info = bool(len(course_table))  # 是否有课程信息
    if has_course_info:
        i_course_data = {}
        for i in course_table:
            try:
                i_course_data.clear()
                name = i.find(href=re.compile("course_detail")).string.strip()
                teacher = [item.string for item in i.find_all(href=re.compile("showTeacherInfoItem"))]
                all_time = i.table.find_all("tr")
                time_help = [item.get_text().split() for item in all_time]
                course_kind_num = len(time_help)  # 有几种类型的课
                for i_time in time_help:
                    if "全周" or "单周" or "双周" in i_time[0]:
                        tmp_week = i_time[0]
                        i_time[0] = [int(x) for x in re.findall(r"\d+\.?\d*", i_time[0])]
                        i_time[0].append(week_evenodd_dic[tmp_week[-2]])
                    else:
                        i_time[0] = -1
                    i_time[1] = week_dic[i_time[1][2]]
                    i_time.append(day_dic[i_time[2]])
                for j in range(course_kind_num):
                    i_course_data["name"] = name
                    i_course_data["teacher"] = teacher
                    i_course_data["day_of_week"] = int(time_help[j][1])
                    i_course_data["location"] = time_help[j][3]
                    i_course_data["sTime"] = time_help[j][4]["sTime"]
                    i_course_data["eTime"] = time_help[j][4]["eTime"]
                    i_course_data["sWeek"] = int(time_help[j][0][0])
                    i_course_data["eWeek"] = int(time_help[j][0][1])
                    i_course_data["EvenOddWeek"] = int(time_help[j][0][2])
                    course_data.append(i_course_data.copy())
            except Exception:
                i_course_data['name'] = 0
                continue
        print("获取课程详情成功！")
        return course_data
    else:
        print("暂无当前时间课表信息！")
        return False


# 将课程转化为ics格式
def to_ics(course_info, date_start_argu):
    print("正在生成日历……")
    date_start = date_start_argu
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//LZU//roseauhan//CN'
    for item in course_info:
        event = Event()
        ev_start_date = date_start + relativedelta(weeks=(item['sWeek'] - 1), weekday=(item['day_of_week'] - 1))
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
        event.add('categories', "S")
        event.add('comment', item['teacher'])
        cal.add_component(event)

    with open(filename, 'w+', encoding='utf-8') as file:
        file.write(cal.to_ical().decode('utf-8'.replace('\r\n', '\n').strip()))
    print("已将所有课程生成日历!")


# 登录
def lzu_login():
    print("欢迎使用Lzu2Ics！ created by roseauhan")
    global User
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
        response_login = session.post(login_url, data=payload, timeout=(3, 5))
        if "handleLoginSuccessed" in response_login.text:
            print("登录成功!")
            try:
                course_payload = get_course_payload()[0]
                date_start = get_course_payload()[1]
                session.get(home_url, timeout=(3, 5))
                session.get(course_url, headers=jwk_headers, timeout=(3, 5))
                response_course = session.get(main_url, headers=jwk_headers, params=course_payload, timeout=(3, 5))
                try:
                    course_info = get_course_info(response_course.text)
                    if course_info:
                        to_ics(course_info, date_start)
                        print("Congratulation!\n"
                              "文件名：" + filename + "\n"
                                                  "请使用谷歌日历(或其它支持ics格式的软件) 打开本文件进行导入")
                    else:
                        return

                except Exception:
                    print("解析课表错误！！！")
                    traceback.print_exc()
            except Exception as e:
                print("获取课表错误！！！")
                traceback.print_exc()
                print(e)
        elif "用户不存在或密码错误" in response_login.text:
            print("账号或密码错误！！！\n即将重新登录")
            lzu_login()
    except Exception as e:
        print("my.lzu.edu.cn连接超时\n请检查网络错误或其它错误！！!")
        print(e)
    finally:
        print("感谢使用！Bye！")


if __name__ == '__main__':
    lzu_login()
