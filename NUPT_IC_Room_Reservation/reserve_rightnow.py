# -*- coding: utf-8 -*-

import requests
import json
import time
import os
import configparser
# import sys
import datetime


# V2.0_测试

# 获取房间Id
def getRoomId(room_source):
    # objid = "100455324_100455316" objname = "403-2"
    # objid = "100455441_100455316" objname = "532"
    # objid="100455445_100455316" objname="533"
    roomIdDict = {"403-2": "100455324",
                  "532": "100455441",
                  "533": "100455445"
                  }

    if room_source in roomIdDict:
        return roomIdDict[room_source]
    else:
        return None


# 从config读数据
def readRoom(conf, room):

    # 考虑到程序执行的时间会影响预先获取的预约时间
    # 零点开始预约第二天的房间,否则获取第三天的时间
    now = time.strftime('%H:%M:%S', time.localtime(time.time()))    # 时:分:秒
    H = int(now.split(':')[0])    # 小时
    # M = int(now.split(':')[1])    # 分
    H = 0

    if H >= 1:
        # 可以获取需要预约的时间，但一定不会预约成功，除非等待至零点以后
        date = str(datetime.date.today() + datetime.timedelta(days=2))
    else:
        date = str(datetime.date.today() + datetime.timedelta(days=1))

    start_time = conf.get(room, 'reserve_start_time')
    end_time = conf.get(room, 'reserve_end_time')
    room_source = conf.get(room, 'room')

    # room = getSeatId(room_source)
    room = getRoomId(room_source)

    print([room, date, start_time, end_time])

    return [room, date, start_time, end_time]


# 从conf里读取数据
def confDeal():
    # 预约队列，利用python特性创建可变长度的队列
    reserve_queue = []
    conf = configparser.ConfigParser()
    conf.read('./user_data.cfg')

    # 读取用户数据
    uid = conf.get('user_set', 'user_id')
    pwd = conf.get('user_set', 'user_password')

    if pwd == '000000':
        pwd = input('输入密码:')
        os.system('cls')
    user = [uid, pwd]

    # 添加用户信息
    reserve_queue.append(user)

    flags = []

    # 读取座位是否启用
    flag0 = conf.get('room_set_0', 'flag')
    flag1 = conf.get('room_set_1', 'flag')
    flag2 = conf.get('room_set_2', 'flag')
    flag3 = conf.get('room_set_3', 'flag')

    flags = [flag0, flag1, flag2, flag3]

    print("预约请求队列: ")

    # 读取座位1
    if flag0 == 'true':
        arr0 = readRoom(conf, 'room_set_0')
    else:
        arr0 = False

    if flag1 == 'true':
        arr1 = readRoom(conf, 'room_set_1')
    else:
        arr1 = False

    if flag2 == 'true':
        arr2 = readRoom(conf, 'room_set_2')
    else:
        arr2 = False

    if flag3 == 'true':
        arr3 = readRoom(conf, 'room_set_3')
    else:
        arr3 = False

    return [user, arr0, arr1, arr2, arr3]


# 登陆
def login(arr, cookies):
    # 先判断是否已经登陆
    judurl = 'http://10.20.232.19/ClientWeb/pro/ajax/login.aspx?act=is_login'
    repj = json.loads(requests.get(judurl, cookies=cookies).text)
    if repj['ret'] == 1:
        return True

    # 进行登陆
    else:
        url = 'http://10.20.232.19/ClientWeb/pro/ajax/login.aspx'
        uid = arr[0]
        pwd = arr[1]
        body = {
            'id': uid,
            'pwd': pwd,
            'act': 'login',
        }
        reply = json.loads(requests.post(url, cookies=cookies, data=body).text)

        # 如果登陆成功
        if reply['msg'] == 'ok':
            print('\n login success!')
            print('\n Welcome, ' + reply['data']['name'] + '!' + '\n')
            return True

        # 失败重试
        else:
            print('login failed')
            ide = input('id:')
            pwde = input('pwd')
            return login([ide, pwde], cookies)


# 预约座位
def reserve(arr, cookies):
    url = 'http://10.20.232.19/ClientWeb/pro/ajax/reserve.aspx'

    room = arr[0]
    date = arr[1]    # date由上面readRoom函数自动提供
    st = arr[2]
    et = arr[3]
    # url传入开始时间格式:2019-4-20 09:10
    s_t = date+' '+st[0:2]+':'+st[2:]
    e_t = date+' '+et[0:2]+':'+et[2:]

    params = {
        'dev_id': room,
        'type': 'dev',
        'test_name': '个人',
        'start': s_t,
        'end': e_t,
        'start_time': st,
        'end_time': et,
        'act': 'set_resv'
    }
    rep = requests.get(url, params=params, cookies=cookies)
    print(room, st, '-', et, rep, '\n', rep.text, '\n')
    rept = ''
    rept = rept + rep.text + '\n'
    repj = json.loads(rep.text)
    if repj['msg'] == '操作成功！':
        now = time.strftime('%H:%M:%S', time.localtime(time.time()))
        rept = rept + now
        room_file = open('logfile.log', 'w')
        room_file.write(rept)
        room_file.close()

        return True

    else:
        return False

        # time.sleep(0.5)
        # reserve(arr, cookies)


# 预约主体：获取sid、登陆、预约
def reserve_main():
    main_url = 'http://10.20.232.19/ClientWeb/xcus/ic2/Default.aspx'
    # 得到cookies----asp.net session id
    rep = requests.get(main_url)
    Cookies = rep.cookies

    # 获得验证过的预约信息(不登陆无法读取房间, 所以不验证直接返回房间固定id)
    reserveArr = confDeal()

    user = reserveArr[0]
    seat0 = reserveArr[1]
    seat1 = reserveArr[2]
    seat2 = reserveArr[3]
    seat3 = reserveArr[4]

    if login(user, Cookies):
        print('\n 登陆成功...')
        # time.sleep(2)
        os.system('cls')

        # if SetTime():
        if True:
            flags = [False, False, False, False]

            while (True):
                if login(user, Cookies):

                    if not flags[0]:
                        flags[0] = reserve(seat0, Cookies)
                    else:
                        flags[0] = True

                    if seat1 is not False and not flags[1]:
                        flags[1] = reserve(seat1, Cookies)
                    else:
                        flags[1] = True

                    if seat2 is not False and not flags[2]:
                        flags[2] = reserve(seat2, Cookies)
                    else:
                        flags[2] = True

                    if seat3 is not False and not flags[3]:
                        flags[3] = reserve(seat3, Cookies)
                    else:
                        flags[3] = True

                    time.sleep(0.5)

                    # 再次预约失败的房间
                    if login(user, Cookies):

                        if not flags[0]:
                            flags[0] = reserve(seat0, Cookies)
                        if not flags[1]:
                            flags[1] = reserve(seat1, Cookies)
                        if not flags[2]:
                            flags[2] = reserve(seat2, Cookies)
                        if not flags[3]:
                            flags[3] = reserve(seat3, Cookies)

                    # 退出循环条件
                    if flags[0] and flags[1] and flags[2] and flags[3]:
                        break
                    # 如果时间到达00:05且还有没有预约成功的时间段，则停止预约
                    elif stopcond(flags):
                        break


# 停止函数: 如果时间到达00:05且还有没有预约成功的时间段，则停止预约
def stopcond(flags):
    now = time.strftime('%H:%M:%S', time.localtime(time.time()))    # 时:分:秒
    H = int(now.split(':')[0])    # 距离零点还剩的小时
    M = int(now.split(':')[1])    # 分
    S = int(now.split(':')[2])    # 秒

    successful = True
    for flg in flags:
        if not flg:
            successful = False

    if H == 0 and M == 5 and not successful:
        return True


# 定时判断器只能提前一天——还未开放
def SetTime():
    print('定时器启动...\n')
    pass


# 主函数
def main():
    print('\t  *****************************************\n\
          *  欢迎使用图书馆自动预约-这是自动模式  *\n\
          *           系统延迟00:03:30            *\n\
          *****************************************\n\
          * -在完成必要步骤后                     *\n\
          * -软件将在02:00进行预约                *\n\
          * -预约完成自动退出                     *\n\
          * ---请确保：                           *\n\
          *   1、各部分功能能够顺利运行           *\n\
          *   2、电脑电源模式不会自动关机或待机   *\n\
          *   3、完成配置文件                     *\n\
          *****************************************\n\
          *          Powered by wenz_xv           *\n\
          *****************************************\n\
          Enter启动... ')

    # 主进程
    time.sleep(40)   # 00:03启动，等待40秒开始预约，注意程序本身启动需要若干秒
    reserve_main()
    print('程序即将退出...\n')
    time.sleep(5)
    # os.system('shutdown -s -f -t 10')


if __name__ == "__main__":
    main()
