# -*- codeing = utf -8 -*-
# @Time : 2021/7/24 下午4:30
# @Author :yangyang
# @File : bubble_tea.py
# @Software: PyCharm

from weibo import Client
import urllib.request
import json
import ssl
import urllib.parse
import urllib.error
import random
import time

# 使用Python登录时就会抛出_ssl.c:645错误，不能读取页面, 所以直接忽略
# 使用ssl创建未验证的上下文，在url中传入上下文参数
context = ssl._create_unverified_context()
API_KEY = 'Your Key'
API_SECRET = 'Your Secret'
REDIRECT_URI = 'Your URI'
access = 'Your Access Token'
code = 'Your code'
taskLog = open('TaskLog.txt', 'a')

def logInWeibo():

    # 如果code过期需要重新启动以下三行，然后将code更新
    # userLogIn = Client(api_key=API_KEY, api_secret=API_SECRET, redirect_uri=REDIRECT_URI)
    # userLogIn.authorize_url
    # 'https://api.weibo.com/oauth2/authorize?redirect_uri=Your_URI&client_id=Your_Key'

    # 设置code，记录token
    # userLogIn.set_code(code)
    # token = userLogIn.token
    # print(token)
    # 记录完后在一段时间内可以直接登陆微博
    token = '你打印出来的token'
    client = Client(api_key=API_KEY, api_secret=API_SECRET, redirect_uri=REDIRECT_URI, token=token)
    client.get('users/show', uid=2703275934)
    print("登陆微博完成")


def getMessageId():
    global taskLog
    # 官方API，可以查看最新一个@自己账号的微博
    responseHandler = urllib.request.urlopen('https://api.weibo.com/2/statuses/mentions.json?count=1&access_token=' + access, context=context)
    jsonData = json.loads(responseHandler.read().decode('utf-8'))
    # 第一层字典
    statuses = jsonData['statuses'][0]
    # 第二层字典，idstr与id是一样的：当前微博的id
    currentMessageId = str(statuses['id'])
    # 发布微博的人
    currentMessageUser = statuses['user']
    UserName = str(currentMessageUser['screen_name'])
    taskLog.write("用户名是: " + UserName + '\n微博Id是: ' + currentMessageId + '\n')
    print("用户名是: " + UserName + '\n微博Id是: ' + currentMessageId)
    return currentMessageId


# 输入最新一条微博的ID
def writeIdIntoNotebook(messageId):
    global taskLog
    messageId = str(messageId)
    # 查看有无新微博ID
    messageIdWriter = open('current-message-id.txt', 'r')
    line = messageIdWriter.readlines()
    messageIdWriter.close()
    if not line:
        taskLog.write("空列表" + "\n")
        print("空列表")
        taskLog.write('写入Id： ' + messageId + "\n")
        print('写入Id： ' + messageId)
        messageIdWriter = open('current-message-id.txt', 'a')
        messageIdWriter.write(messageId + "\n")
        messageIdWriter.close()
        return 0
    else:
        for i in range(len(line)):
            line[i] = line[i].replace('\n', '')
        if messageId in line:
            taskLog.write("没有新消息" + "\n")
            print("没有新消息")
            return 1
        else:
            print('写入Id： ' + messageId)
            messageIdWriter = open('current-message-id.txt', 'a')
            messageIdWriter.write(messageId + "\n")
            messageIdWriter.close()
            taskLog.write("有新消息" + "\n")
            print("有新消息")
            return 2


def replyMessageToUser(messageId):
    global taskLog
    text = randomBubbleTea()
    postData = urllib.parse.urlencode({'comment': text, 'id': messageId, 'access_token': access}).encode('utf-8')
    try:
        urllib.request.urlopen('https://api.weibo.com/2/comments/create.json', postData, context=context)
        taskLog.write("已发送 '" + text + "' 至微博ID: " + messageId + "\n")
        print("已发送 '" + text + "' 至微博ID: " + messageId)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
            taskLog.write(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
            taskLog.write(e.reason)
# 查看json数据有哪些
# for i in jsonData.keys():
#     print(i)
# for i in currentMessageUser.keys():
#     print(i)


# 随机的奶茶推荐！
def randomBubbleTea():
    menu = []
    a_little = ['抹茶拿铁 去冰/三分/波霸', '阿华田 去冰/三分/奶霜', '四季奶青 去冰/五分/波霸', '可可芭蕾 去冰/三分/布丁', '乌龙奶茶 去冰/无糖/波霸', '葡萄柚绿 去冰/三分/椰果',
                '四季玛奇朵 去冰/三分/燕麦', '波霸奶茶 去冰/三分/冰激凌', '红茶玛奇朵/去冰/无糖/冰淇淋/珍波椰', '四季春玛奇朵/去冰/五分甜/布丁/冰淇淋', '冰淇淋红茶/去冰/三分甜/波霸/奶霜',
                '阿华田 /去冰/无糖/冰淇淋/两颗布丁', '四季春玛奇朵/常温/三分甜/波霸', '四季春奶青/去冰/半糖/波霸', '阿华田/去冰/三分甜/波霸/布丁', '焦糖奶茶/热/三分甜/仙草',
                '四季春奶青/去冰 /三分甜/燕麦', '乌龙玛奇朵/去冰/微糖/波霸',
                '四季春/去冰/三分糖/珍波椰', '可可芭蕾/去冰/三份甜/布丁' '乌龙奶茶/去冰/无糖/波霸', '柠檬养乐多/去冰/五分糖', '古早味奶茶/去冰/半糖']
    heyTea = ['多肉葡萄+芋圆波波+玫瑰青 少冰、少糖', '芝芝桃桃+红柚粒+脆波波+芝士换冰淇淋 少冰、正常糖',
              '芝芝芒芒+芝士换冰淇淋+芋圆波波 少冰、少糖', '芝芝莓莓+芦荟粒+芝士换酸奶 少冰、少少糖',
              '奶茶波波冰+黑糖波波 少冰、少少糖', '阿华田波波冰+黑波波换黑糖奶冻 少冰、不另外加糖',
              '纯绿妍+脆啵啵+红柚果粒 少冰、少少糖', '布甸波波冰+芋圆波波+黑糖奶冻 少冰', '金凤茶王+小丸子 五分糖']
    coco = ['双球冰淇淋红茶+芋头+珍珠 去冰、无糖', '鲜芋茶拿铁+布丁+珍珠 去冰、微糖', '双球冰淇淋草莓+珍珠+椰果 去冰、半糖',
            '双球冰淇淋抹茶+芋头+珍珠 去冰、三分糖', '茉香奶茶+芋鲜+青稞+珍珠 去冰、无糖', '杨枝甘露+椰果 少冰', '鲜百香果双响炮+椰果 少冰、半糖',
            '鲜芋雪冰+珍珠+冰淇淋 无糖', '青茶奶霜+芋头+冰淇淋+珍珠', '莓莓绵雪冰+冰淇淋+珍珠', '红果小姐姐+奶霜 半糖']
    chaBaiDao = ['桂花酒酿', '招牌芋圆奶茶', '黑糖牛乳波波茶', '杨枝甘露', '琥珀烤糖奶茶', '青心乌龙奶茶', '奥利奥芝士', '金桔柠檬', '杨枝甘露/少冰/三分糖',
                 '葡萄冻冻和葡萄芝士/芋圆/无糖', '豆乳玉麒麟', '酒酿芋圆奶茶', '粉荔多肉', '茉莉白桃']
    miXueIceCream = ['柠檬水！', '华夫冰淇淋', '黑糖珍珠圣代', '雪顶咖啡']
    menu.append(a_little)
    menu.append(heyTea)
    menu.append(coco)
    menu.append(chaBaiDao)
    menu.append(miXueIceCream)
    randomNoOne = random.randint(0, 7)
    if randomNoOne == 0 or randomNoOne == 1:
        randomNoTwo = random.randint(0, 21)
        text = '推荐一点点: ' + menu[0][randomNoTwo]
        return text
    elif randomNoOne == 2:
        randomNoTwo = random.randint(0, 8)
        text = '推荐喜茶: ' + menu[1][randomNoTwo]
        return text
    elif randomNoOne == 3 or randomNoOne == 4:
        randomNoTwo = random.randint(0, 9)
        text = '推荐COCO: ' + menu[2][randomNoTwo]
        return text
    elif randomNoOne == 5 or randomNoOne == 6:
        randomNoTwo = random.randint(0, 13)
        text = '推荐茶百道: ' + menu[3][randomNoTwo]
        return text
    elif randomNoOne == 7:
        randomNoTwo = random.randint(0, 3)
        text = '推荐蜜雪冰城： ' + menu[4][randomNoTwo]
        return text


def wait(seconds):
    global taskLog
    taskLog.write('wait for ' + str(seconds) + ' seconds' + '\n')
    print('wait for ' + str(seconds) + ' seconds')
    time.sleep(seconds)


# 程序循环
def tryToReplyNewMentions():
    while True:
        global taskLog
        messageId = getMessageId()
        feedback = writeIdIntoNotebook(messageId)
        # 如果有新的微博@，则发送微博
        if feedback == 0 or feedback == 2:
            replyMessageToUser(messageId)
        localtime = time.asctime(time.localtime(time.time()))
        taskLog.write("本地时间为 :" + localtime + '\n')
        print("本地时间为 :" + localtime)
        wait(60)


if __name__ == '__main__':
    logInWeibo()
    wait(10)
    tryToReplyNewMentions()
    taskLog.close()
