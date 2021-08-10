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
    global taskLog
    # 如果code过期需要重新启动以下三行，然后将code更新
    # userLogIn = Client(api_key=API_KEY, api_secret=API_SECRET, redirect_uri=REDIRECT_URI)
    # userLogIn.authorize_url
    # 'https://api.weibo.com/oauth2/authorize?redirect_uri=https://api.weibo.com/oauth2/default.html&client_id=1793365239'

    # 设置code，记录token
    # userLogIn.set_code(code)
    # token = userLogIn.token
    # print(token)
    # 记录完后在一段时间内可以直接登陆微博
    token = '你打印的token'
    client = Client(api_key=API_KEY, api_secret=API_SECRET, redirect_uri=REDIRECT_URI, token=token)
    client.get('users/show', uid=2703275934)
    taskLog.write("登陆微博完成"+"\n")
    print("登陆微博完成")


def getMessageId():
    global taskLog
    message_list = []
    # 官方API，可以查看最新一个@自己账号的微博
    responseHandler = urllib.request.urlopen(
        'https://api.weibo.com/2/statuses/mentions.json?count=1&access_token=' + access, context=context)
    jsonData = json.loads(responseHandler.read().decode('utf-8'))
    # 第一层字典
    statuses = jsonData['statuses'][0]
    # 第二层字典，idstr与id是一样的：当前微博的id
    currentMessageId = str(statuses['id'])
    message_list.append(currentMessageId)
    # 发布微博的人
    currentMessageUser = statuses['user']
    UserName = str(currentMessageUser['screen_name'])
    # 发布的微博
    text = statuses["text"]
    message_list.append(text)
    taskLog.write("用户名是: " + UserName + '\n微博Id是: ' + currentMessageId + '\n')
    print("用户名是: " + UserName + '\n微博Id是: ' + currentMessageId)
    return message_list


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


def replyMessageToUser(messageId, message_content):
    global taskLog
    text = randomBubbleTea(message_content)
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

menu = []
a_little = ["茉莉绿茶",
            "阿萨姆红茶",
            "四季春茶",
            "清香乌龙茶",
            "抹茶",
            "黑糖红茶",
            "翡翠柠檬",
            "蜂蜜绿",
            "养乐多绿",
            "冰淇淋红茶",
            "葡萄柚绿",
            "百香绿",
            "波霸奶茶",
            "波霸奶绿",
            "波霸红/烏",
            "波霸绿/青",
            "珍珠奶茶",
            "珍珠奶绿",
            "珍珠红/乌",
            "珍珠绿/青",
            "椰果奶茶",
            "仙草奶冻",
            "红豆ＱＱ奶茶",
            "四季如意",
            "布丁奶茶",
            "燕麦奶茶",
            "百香三重奏",
            "咖啡奶冻",
            "四季奶青",
            "乌龙奶茶",
            "红茶玛奇朵",
            "乌龙玛奇朵",
            "阿华田",
            "抹茶奶茶",
            "可可奶茶(黄金比例)",
            "焦糖奶茶",
            "黑糖奶茶",
            "金桔柠檬",
            "柠檬蜜",
            "柠檬养乐多",
            "季节限定：奶绿装芒",
            "季节限定：柚心动了",
            "季节限定：百香YOYO绿",
            "季节限定：芒果YOYO绿",
            "季节限定：花生豆花奶茶"
            ]
heyTea = ['多肉葡萄+芋圆波波',
          '芝芝芒芒+芋圆波波', '芝芝莓莓桃',
          '奶茶波波冰+黑糖波波',
          '纯绿妍换牛乳茶底+桂花冻', '金凤茶王+脆波波', "雪山思乡龙眼"
                                      '季节限定：王榨油柑', "季节限定：双榨杨桃油柑", "冻暴柠", "多肉芒芒甘露", "原创生打椰椰奶冻", "满杯红柚", "烤黑糖波波牛乳"]
coco = ['上新：火焰蓝椰', '雪顶蜜恋桃桃', '白玉粉荔', '白玉荔枝茶', '白玉荔枝多多', '牛油果布丁', '鲜苹果百香', '星空葡萄', '荞麦轻奶茶',
        '荞麦轻茶', '芒芒绿茶', '芒果多多', '柠檬霸', '沙棘百香双响炮', '沙棘摇摇冻',
        '鲜芋奶茶+青稞+无糖',
        '铁观音珍珠茶拿铁 + 青稞 + 奶盖 + 芋头',
        '双球冰激凌红茶 + 奶霜 + 珍珠 去冰半糖',
        '鲜百香双响炮 + 椰果 少冰半糖',
        '鲜柠檬茶',
        '轻茶摇摇冻',
        '法式奶霜茗茶'
        '鲜芋牛奶西米露 + 红豆 + 香芋无糖少冰',
        '茉香奶茶 + 珍珠 + 仙草 去冰五分甜',
        '双球冰淇淋红茶+芋头+珍珠 去冰、无糖',
        '茉香奶茶+芋鲜+青稞+珍珠 去冰、无糖', '杨枝甘露+椰果 少冰',
        '红果小姐姐+奶霜 半糖']
chaBaiDao = ['季节水果茶：茉莉白桃子', '季节水果茶: 白桃子酪酪', '季节水果茶：鲜草莓酪酪', '芒芒生打椰', '生椰大满贯', '杨枝甘露',
             '西瓜啵啵', '百香凤梨', '手捣芒果绿', '超级杯水果茶', '奥利奥蛋糕', '抹茶红豆蛋糕', '招牌芋圆奶茶', '豆乳玉麒麟',
             '茉莉奶绿', '黄金椰椰乌龙', '血糯米奶茶', '奥利奥奶茶', '茉莉绿茶', '冰乌龙', "海盐芝士抹茶"]
miXueIceCream = ['柠檬水！', '华夫冰淇淋', '黑糖珍珠圣代', '雪顶咖啡']
menu.append(a_little)
menu.append(heyTea)
menu.append(coco)
menu.append(chaBaiDao)
menu.append(miXueIceCream)


# 随机的奶茶推荐！
def randomBubbleTea(message):
    global menu
    if "一点点" in message:
        randomNoTwo = random.randint(0, len(menu[0]) - 1)
        text = '推荐一点点: ' + menu[0][randomNoTwo]
        return text
    elif "喜茶" in message:
        randomNoTwo = random.randint(0, len(menu[1]) - 1)
        text = '推荐喜茶: ' + menu[1][randomNoTwo]
        return text
    elif "COCO" in message or "coco" in message:
        randomNoTwo = random.randint(0, len(menu[2]) - 1)
        text = '推荐COCO: ' + menu[2][randomNoTwo]
        return text
    elif "茶百道" in message:
        randomNoTwo = random.randint(0, len(menu[3]) - 1)
        text = '推荐茶百道: ' + menu[3][randomNoTwo]
        return text
    elif "蜜雪" in message:
        randomNoTwo = random.randint(0, len(menu[4]) - 1)
        text = '推荐蜜雪冰城： ' + menu[4][randomNoTwo]
        return text
    else:
        randomNoOne = random.randint(0, 7)
        if randomNoOne == 0 or randomNoOne == 1:
            randomNoTwo = random.randint(0, len(menu[0]) - 1)
            text = '推荐一点点: ' + menu[0][randomNoTwo]
            return text
        elif randomNoOne == 2:
            randomNoTwo = random.randint(0, len(menu[1]) - 1)
            text = '推荐喜茶: ' + menu[1][randomNoTwo]
            return text
        elif randomNoOne == 3 or randomNoOne == 4:
            randomNoTwo = random.randint(0, len(menu[2]) - 1)
            text = '推荐COCO: ' + menu[2][randomNoTwo]
            return text
        elif randomNoOne == 5 or randomNoOne == 6:
            randomNoTwo = random.randint(0, len(menu[3]) - 1)
            text = '推荐茶百道: ' + menu[3][randomNoTwo]
            return text
        elif randomNoOne == 7:
            randomNoTwo = random.randint(0, len(menu[4]) - 1)
            text = '推荐蜜雪冰城： ' + menu[4][randomNoTwo]
            return text


# 获取评论@
def getReplyId():
    # 返回两个值，评论id和原文id
    reply_list = []
    # 官方API，可以查看最新一个@自己账号的评论
    responseHandler = urllib.request.urlopen('https://api.weibo.com/2/comments/mentions.json?count=0&access_token='
                                             + access, context=context)
    jsonData = json.loads(responseHandler.read().decode('utf-8'))
    comments = jsonData["comments"][0]
    # 评论id
    comments_Id = str(comments["id"])
    reply_list.append(comments_Id)
    # 评论人
    comments_user = comments["user"]
    # 评论人名称
    comments_user_name = comments_user["screen_name"]
    # 评论人id
    comments_user_id = str(comments_user["id"])
    # 评论内容
    comments_text = comments["text"]
    status = comments["status"]
    # 微博原文
    original_text = status["text"]
    # 微博id
    original_text_id = str(status["id"])
    reply_list.append(original_text_id)
    # 微博原文用户
    original_user = status["user"]
    # 微博原文用户id
    original_user_id = str(original_user["id"])
    # 微博原文用户名
    original_user_name = original_user["screen_name"]
    # 添加回复内容
    reply_list.append(comments_text)
    print("@我的用户名是: " + comments_user_name + " 用户id是: " + comments_user_id + " 评论内容是: " + comments_text +
          " 评论ID是: " + comments_Id)
    taskLog.write("@我的用户名是: " + comments_user_name + " 用户id是: " + comments_user_id + " 评论内容是: " + comments_text
                  + " 评论ID是: " + comments_Id + "\n")
    print("原文用户名是: " + original_user_name + " 用户id是:" + original_user_id + " 微博内容是: " + original_text,
          " 微博ID是: " + original_text_id)
    taskLog.write("原文用户名是: " + original_user_name + " 用户id是:" + original_user_id + " 微博内容是: " + original_text
                  + " 微博ID是: " + original_text_id + "\n")
    return reply_list


def replyMessageToComment(cid, id, comment_content):
    global taskLog
    text = str(randomBubbleTea(comment_content))
    postData = urllib.parse.urlencode({'comment': text, 'cid': cid, 'id': id, 'access_token': access}).encode('utf-8')
    # head = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    # }
    # request = urllib.request.Request('https://api.weibo.com/2/comments/reply.json', postData, headers=head)
    try:
        urllib.request.urlopen('https://api.weibo.com/2/comments/reply.json', postData, context=context)
        print("已发送 '" + text + "' 至微博ID: " + id + " 评论ID: " + cid)
        taskLog.write("已发送 '" + text + "' 至微博ID: " + id + " 评论ID: " + cid + "\n")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
            taskLog.write(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
            taskLog.write(e.reason)


def wait(seconds):
    global taskLog
    taskLog.write('wait for ' + str(seconds) + ' seconds' + '\n')
    print('wait for ' + str(seconds) + ' seconds')
    time.sleep(seconds)


# 程序循环
def tryToReplyNewMentions():
    while True:
        global taskLog
        message_list = getMessageId()
        messageId = message_list[0]
        message_content = message_list[1]
        feedback = writeIdIntoNotebook(messageId)
        # 如果有新的微博@，则发送微博
        if feedback == 0 or feedback == 2:
            replyMessageToUser(messageId, message_content)
        # 查看有没有新的评论@我
        commentId = getReplyId()
        cid = commentId[0]
        comment_content = commentId[2]
        id = commentId[1]
        feedback = writeIdIntoNotebook(cid)
        if feedback == 0 or feedback == 2:
            replyMessageToComment(cid, id, comment_content)
        localtime = time.asctime(time.localtime(time.time()))
        taskLog.write("本地时间为 :" + localtime + '\n')
        print("本地时间为 :" + localtime)
        wait(60)


if __name__ == '__main__':
    logInWeibo()
    wait(10)
    tryToReplyNewMentions()
    taskLog.close()
