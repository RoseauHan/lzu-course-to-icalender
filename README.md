# lzu2icalender
如果你和我一样，不喜欢使用第三方的课表软件（要么太丑，要么太臃肿，或者两者都有……）, 那么是时候使用一个简单的、原生的工具了！立马导出课程的icalender文件，添加到你的日程中吧！
登录兰州大学教务在线，自动将课程生成icalender文件，可以方便的添加到各类通用日历中。 Enjoy yourself！

![demo](./img/demo1.png) 
(更多图片展示)[]

## icalender 是什么？
[iCalendar](https://www.ibm.com/developerworks/cn/java/j-lo-ical4j/index.html)，简称“iCal”，是“日历数据交换”的标准（RFC 2445），该标准提供了一种公共的数据格式用于存储关于日历方面的信息，比如事件、约定、待办事项等。它不仅允许用户通过电子邮件发送会议或者待办事件等，也允许独立使用，而不局限于某种传输协议。

目前，所有流行日历工具比如：Lotus Notes、Outlook、GMail 和 Apple 的 iCal 都支持 iCalendar 标准，其文件扩展名为 .ical、.ics、.ifb 或者 .icalendar。C&S（Calendaring and Scheduling） 核心对象是一系列日历和行程安排信息。通常情况下，这些日历和行程信息仅仅包含一个 iCalendar 组件（iCalendar 组件分为 Events(VEVENT)、To-do(VTODO)、Journal(VJOURNAL)、Free/busy time (VFREEBUSY)、VTIMEZONE (time zones) 和 VALARM (alarms)），但是多个 iCalendar 组件可以被组织在一起。

## 本项目的功能？
自动将课表生成icalender文件，方便导入到各类日程中。
- 获取2016-2019年的所有课程icalender文件
- 自定义获取任意年的课程（需要自己输入开学时间）

## INSTALLATION

You need to install python 3 first.

```Shell
brew install python3
```

Second, you need install beautifulsoup4 and icalendar by pip (pip3).

```shell
pip install beautifulsoup4
pip install icalendar
```

## USAGE

```shell
python3 lzu2icalender.py
```
then, follow the terminal hint.


## 已知issue
- 如果使用windows的py解释器，生成的文件可能包含空行。而这可能会导致课表导入失败，建议使用Linux下的py解释器。
- google calender可能无法打开文件，解决方案：卸载重装…… 这个问题目前并不清楚原因……

## TODO list
- [ ] 兼容更多日历格式
- [ ] 一次性生成所有可用课表
- [ ] 提供一个美观的前端界面
- [ ] 使用 google 提供的接口，直接在线导入google calender
- [ ] 面向对象重构


## Others
欢迎PR、提issue！
项目部分灵感来源：[cqut-lesson-timetable-to-calendar](https://github.com/acbetter/cqut-lesson-timetable-to-calendar) Thanks！

# LICENSE 

GPL-3.0



