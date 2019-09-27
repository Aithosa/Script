import requests
import json
import time
import os
import configparser
import sys
import datetime
import hashlib


# V2.0_测试

# 获取房间Id
def getRoomId(room_source):
    # objid = "100455441_100455316" objname = "532"
    # objid = "100455324_100455316" objname = "403-2"
    if room_source == "532":
        return "100455441_100455316"
    elif room_source == "403-2":
        return "100455324_100455316"
    else:
        return None


# 从config读数据
def readRoom(conf, room):
    # 零点开始预约第二天的房间
    date = str(datetime.date.today() + datetime.timedelta(days=1))

    start_time = conf.get(room, 'reserve_start_time')
    end_time = conf.get(room, 'reserve_end_time')
    room_source = conf.get(room, 'room')

    # room = getSeatId(room_source)
    room = getRoomId(room_source)

    return [room, date, start_time, end_time]


# 从conf里读取数据
def confDeal():
    conf = configparser.ConfigParser()
    conf.read('./user_data.cfg')

    # 读取用户数据
    uid = conf.get('user_set', 'user_id')
    pwd = conf.get('user_set', 'user_password')
    if pwd == '000000':
        pwd = input('输入密码:')
        os.system('cls')
    user = [uid, pwd]

    # 读取座位是否启用
    flag1 = conf.get('room_set_1', 'flag')
    flag2 = conf.get('room_set_2', 'flag')

    # 读取座位1
    arr1 = readRoom(conf, 'room_set')
    if flag1 == 'true':
        arr2 = readRoom(conf, 'room_set_1')
    else:
        arr2 = False
    if flag2 == 'true':
        arr3 = readRoom(conf, 'room_set_2')
    else:
        arr3 = False
    return [user, arr1, arr2, arr3]
    # return [user, False, False, False]


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
            print('\n login success')
            print('Welcome '+reply['data']['name']+'\n')
            return True

        # 失败重试
        else:
            print('login failed')
            ide = input('id:')
            pwde = input('pwd')
            return login([ide, pwde], cookies)


# 预约座位
def reserve(arr, cookies):
    url = 'http://10.20.232.19/ClientWeb//pro/ajax/reserve.aspx'

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
    print(rep, '\n', rep.text)
    rept = ''
    rept = rept + rep.text + '\n'
    repj = json.loads(rep.text)
    if repj['msg'] == '操作成功！':
        now = time.strftime('%H:%M:%S', time.localtime(time.time()))
        rept = rept + now
        room_file = open('logfile.log', 'w')
        room_file.write(rept)
        room_file.close()
    else:
        time.sleep(10)
        reserve(arr, cookies)


# 这个函数暂未修改，只预约532可以使用getRoomId(seat)
# 转换座位id
def getSeatId(seat):
    print('\n 寻找你的房间...')
    date = str(datetime.date.today())
    url = 'http://10.20.232.19/ClientWeb/pro/ajax/device.aspx'
    params = {
        'date': date,
        'act': 'get_rsv_sta'
    }
    rep = requests.get(url, params=params)
    content = json.loads(rep.text)
    seatObj = content['data']
    for obj in seatObj:
        if obj['title'] == seat:
            print('\n 校对你的房间信息:')
            retxt = '\n className: ' + str(obj['className'])+'   labName: ' + str(obj['labName'])+'   kindName: ' + str(
                obj['kindName'])+' devName: ' + str(obj['devName'])+'\n open_time: ' + '-'.join(obj['open'])+'   devId: ' + str(obj['devId'])
            print(retxt)
            time.sleep(3)
            return obj['devId']
    print('cannot find the room.\n please try again\n')
    s = input('输入房间：')
    getSeatId(s)


# 预约主体：获取sid、登陆、预约
def reserve_main():
    main_url = 'http://10.20.232.19/ClientWeb/xcus/ic2/Default.aspx'
    # 得到cookies----asp.net session id
    rep = requests.get(main_url)
    Cookies = rep.cookies

    # 获得验证过的预约信息(不登陆无法读取房间, 所以不验证直接返回房间固定id)
    reserveArr = confDeal()
    user = reserveArr[0]
    seat = reserveArr[1]
    seat1 = reserveArr[2]
    seat2 = reserveArr[3]

    if login(user, Cookies):
        print('\n 登陆成功...')
        time.sleep(2)
        os.system('cls')
        if SetTime():
            if login(user, Cookies):
                reserve(seat, Cookies)
                if seat1 != False:
                    reserve(seat1, Cookies)
                if seat2 != False:
                    reserve(seat2, Cookies)


# 定时判断器只能提前一天——还未开放
def SetTime():
    print('定时器启动...')
    while True:
        now = time.strftime('%H:%M:%S', time.localtime(time.time()))    # 时:分:秒
        nowm = time.strftime('%H:%M', time.localtime(time.time()))    # 时:分
        H = 24 - int(now.split(':')[0])    # 时
        M = int(now.split(':')[1])    # 分
        S = int(now.split(':')[2])    # 秒
        
        sleepTime = H*3600 - M*60 - S
        if nowm == '00:00':
            print('零点，待机三十秒')
            time.sleep(30)
            return True
        elif H > 23:
            print('零点，待机十秒')
            time.sleep(10)
            return True
        elif H > 1:
            sys.stdout.write('\r{0}'.format(
                '现在时间:'+now+'  待机时间：'+str(round(H-M/60, 1))))
            time.sleep(360)
            sys.stdout.flush()
        elif sleepTime > 120:
            sys.stdout.write('\r{0}'.format(
                '现在时间:'+now+'  待机时间：'+str(round(H*60-M-S/60, 1))))
            time.sleep(6)
            sys.stdout.flush()
        else:
            sys.stdout.write('\r{0}'.format(
                '现在时间:'+now+'  待机时间：'+str(sleepTime)))
            time.sleep(1)
            sys.stdout.flush()

# 验证
def encipher():
    ipt = input('验证码：')
    hl = hashlib.md5()
    hl.update(ipt.encode(encoding='utf-8'))
    if hl.hexdigest() == 'bcedc450f8481e89b1445069acdc3dd9':
        return True


# 主函数
def main():
    input('\n***************************************\n* 欢迎使用图书馆自动预约-这是自动模式 *\n***************************************\n* -在完成必要步骤后                   *\n* -软件将在00:15进行预约              *\n* -预约完成自动关机                   *\n* ---请确保：                         *\n*   1、各部分功能能够顺利运行         *\n*   2、电脑电源模式不会自动关机或待机 *\n*   3、完成配置文件                   *\n***************************************\n*         Powered by wenz_xv          *\n***************************************\n    Enter启动... ')

    # 主进程
    reserve_main()
    # print('30s 后关机 \n 你可以关闭程序来阻止\n')
    # time.sleep(20)
    # print('10s后关机，可能不太能阻止了...')
    # os.system('shutdown -s -f -t 10')


main()

# if encipher():
#     os.system('cls')
#     main()
