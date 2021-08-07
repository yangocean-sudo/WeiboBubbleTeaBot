# WeiboBubbleTeaBot
原文：https://yangocean-sudo.github.io/

想尝试该功能的请发送微博@今天喝点啥捏，脚本不定期开启

前几天看到有人在微博上@今天吃啥的bot，然后会秒收到一条随机的菜品推荐。这简直是选择困难症的福音，作为奶茶大户，我想着做一个奶茶推荐的bot。

在网上查找了许多资料但都没有类似的bot，最近一个类似的代码是2015年的，完全不能用。

# 原理
原理其实很简单，用python登陆微博 --> 使用微博官方的API：[statuses/mentions](https://open.weibo.com/wiki/2/statuses/mentions)，获取最新的提到登录用户的微博列表，即@我的微博 --> 获取微博id， 使用[comments/create](https://open.weibo.com/wiki/2/comments/create)回复那条微博。
## 登陆
不曾想到登陆是我花的时间最长的步骤，网上有很多登陆方式，但因为我们需要使用官方的API所以需要先在微博开放平台注册一个[网页应用](https://open.weibo.com/connect)。

然后在[API测试工具获得Access Token](https://open.weibo.com/tools/console):
![](/images/AccessToken.png)

在[我的应用](https://open.weibo.com/apps)中点击自己刚创建的应用，应用信息 --> 基本信息中获取App Key和App Secret。

PyPi里有个[微博登陆](https://pypi.org/project/weibo/)的包，竟然到现在也能使用。

介绍中说要在高级信息中设置授权回调页，但我只是一个脚本啊，没有URI可以用，最后找到了官方给手机端的默认回调页，竟然能用:
`https://api.weibo.com/oauth2/default.html`

其他的使用方法就和介绍写的差不多，我直接上代码：
``` python
API_KEY = 'Your Key'
API_SECRET = 'Your Secret'
REDIRECT_URI = 'Your URI'
access = 'Your Access Token'
code = 'Your code'


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
```
## 调用API
第一个API是获取最新一条@自己账号的微博，所以请求官方给的链接后会返回一个json值，层层揭开后微博的id就被找到了。

这里也提一嘴，官方文档中给的链接我是打不开的，借鉴了6年前的代码再修改之后才找到一个可以返回值的链接。
``` python
def getMessageId():
    # 官方API，可以查看最新一个@自己账号的微博
    responseHandler = urllib.request.urlopen('https://api.weibo.com/2/statuses/mentions.json?count=1&access_token=' + access)
    jsonData = json.loads(responseHandler.read().decode('utf-8'))
    # 第一层字典
    statuses = jsonData['statuses'][0]
    # 第二层字典，idstr与id是一样的：当前微博的id
    currentMessageId = str(statuses['id'])
    # 发布微博的人
    currentMessageUser = statuses['user']
    UserName = str(currentMessageUser['screen_name'])
    print("用户名是: ", UserName, '\n微博Id是: ', currentMessageId)
    return currentMessageId
```
---
第二个API就是发送评论啦，这部分没遇到啥挫折，直接上代码:
``` python
def replyMessageToUser(messageId):
    text = ‘想输入的话’
    postData = urllib.parse.urlencode({'comment': text, 'id': messageId, 'access_token': access}).encode('utf-8')
    try:
        urllib.request.urlopen('https://api.weibo.com/2/comments/create.json', postData, context=context)
        print("已发送 '", text, "' 至微博ID: ", messageId)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
```
# 回顾与展望
以上就是核心的代码了，因为没有通过应用审核，所以不能频繁地发送评论给用户(之前设置的间隔是20s，五分钟后就被403 forbidden了)。现在设置60s应该是没有问题的，~~只要不发生过一分钟就@我一次的情况~~。

如果以后还会优化的话优化的方向大致是：
* 每个月更新奶茶列表（这是最重要的！)
* 使用stack保存未处理的微博Id，防止漏掉每一个@(但因为获取最新@也需要调用API，即60s发生一次，所以当务之急还是通过应用审核)
* 换个思路的话就是使用爬虫直接获取所有@我但是我没有回复的用户，然后储存在stack里
* 将机器人上传至阿里云上运行 (~~今天尝试了从早上开到中午，觉得真正的bot总不会专门使用一台电脑联网开脚本吧~~)

---
# 7/31日更新
## 记录所有微博ID
在一个礼拜的脚本使用中，发现如果用户@完机器人后，删除了那条微博，那么脚本会自动将奶茶推荐发给上一个@机器人的用户，这就使部分用户收到了两次推荐的情况发生。当然，这不是用户的问题！于是我对脚本进行了优化，使他记录了运行后的每一条微博ID，如果新ID在记录之中，就不会发送新的推送。
``` python
# 输入最新一条微博的ID
def writeIdIntoNotebook(messageId):
    messageId = str(messageId)
    # 查看记录文件中有无新ID
    messageIdWriter = open('current-message-id.txt', 'r')
    line = messageIdWriter.readlines()
    messageIdWriter.close()
    # 如果记录文件为空，就记录新ID
    if not line:
        print("空列表")
        print('写入Id： ' + messageId)
        messageIdWriter = open('current-message-id.txt', 'a')
        messageIdWriter.write(messageId + "\n")
        messageIdWriter.close()
        return 0
    else:
        # 将txt文件中的ID转化为列表
        for i in range(len(line)):
            line[i] = line[i].replace('\n', '')
        # 如果新ID在列表里
        if messageId in line:
            print("没有新消息")
            return 1
        # 不在就写入新ID
        else:
            print('写入Id： ' + messageId)
            messageIdWriter = open('current-message-id.txt', 'a')
            messageIdWriter.write(messageId + "\n")
            messageIdWriter.close()
            print("有新消息")
            return 2
```
## 记录日志
我发现终端中打印的内容还是很有参考价值的，时间、用户、发送内容等等，每次停止脚本运行这些内容都会消失，于是决定写一个任务日志`TaskLog`来记录输出的内容。
## 奶茶列表更新与概率修改
这次更新了茶百道与蜜雪冰城的菜单，但因为蜜雪冰城只推荐了四款饮品，喜茶价格对我来说太贵，而他们的概率与其他饮品一样是20%，会显得不太合理。于是改成了

一点点 : 喜茶 : COCO : 茶百道 : 蜜雪冰城 = 25 : 12.5 : 25 : 25 : 12.5 
```python
# 随机的奶茶推荐！
def randomBubbleTea():
    menu = []
    # 具体菜单在下面
    a_little = []
    heyTea = []
    coco = []
    chaBaiDao = []
    miXueIceCream = []
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
```
# 8/6更新
## 获取最新评论
前几天有人在评论中@bot，但是bot显然不知道如何应对这样的情况，这当然不是用户的问题！于是我们开始更新bot，让他可以回复任意一篇微博中的@bot + 评论。

这次用到的也是官方api：[获取最新的提到当前登陆用户的评论](https://open.weibo.com/wiki/2/comments/mentions)，因为之后的回复需要评论id和微博id两个，所以提取起来更加复杂，我顺便将用户名，用户id，评论内容也获取到了，之后如果要定制用户的个性化推荐的话也提早做好了准备。
```python
# 回复评论@
def getReplyId():
    # 返回两个值，评论id和原文id
    reply_list = []
    # 官方API，可以查看最新一个@自己账号的评论
    responseHandler = urllib.request.urlopen('https://api.weibo.com/2/comments/mentions.json?count=1&access_token='
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
    print("@我的用户名是: " + comments_user_name + " 用户id是: " + comments_user_id + " 评论内容是: " + comments_text +
          " 评论ID是: " + comments_Id)
    taskLog.write("@我的用户名是: " + comments_user_name + " 用户id是: " + comments_user_id + " 评论内容是: " + comments_text
                  + " 评论ID是: " + comments_Id + "\n")
    print("原文用户名是: " + original_user_name + " 用户id是:" + original_user_id + " 微博内容是: " + original_text,
          " 微博ID是: " + original_text_id)
    taskLog.write("原文用户名是: " + original_user_name + " 用户id是:" + original_user_id + " 微博内容是: " + original_text
                  + " 微博ID是: " + original_text_id + "\n")
    return reply_list
```
## 回复一条评论
使用微博[回复评论](https://open.weibo.com/wiki/2/comments/reply)的API，需要cid(评论id)和id(微博id)，以及access token登陆。
``` python
# 回复评论
def replyMessageToComment(cid, id):
    global taskLog
    text = randomBubbleTea()
    postData = urllib.parse.urlencode({'comment': text, 'cid': cid, 'id': id, 'access_token': access}).encode('utf-8')
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
```
其他小细节的修改已上传至github。
# 8/7更新
今天收到一名用户@了bot，并直言道："我只想喝茶百道。" 于是修改了随机奶茶的方法，先获取用户发布的内容，然后与奶茶品牌比对，如果比对成功，就会只推荐那个品牌的商品。
``` python
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
```
# 奶茶列表
## 一点点
茉莉绿茶

阿萨姆红茶

四季春茶

清香乌龙茶

抹茶

黑糖红茶

翡翠柠檬

蜂蜜绿

养乐多绿

冰淇淋红茶

葡萄柚绿

百香绿

波霸奶茶

波霸奶绿

波霸红/烏

波霸绿/青

珍珠奶茶

珍珠奶绿

珍珠红/乌

珍珠绿/青

椰果奶茶

仙草奶冻

红豆ＱＱ奶茶

四季如意

布丁奶茶

燕麦奶茶

百香三重奏

咖啡奶冻

四季奶青

乌龙奶茶

红茶玛奇朵

乌龙玛奇朵

阿华田

抹茶奶茶

可可奶茶(黄金比例)

焦糖奶茶

黑糖奶茶

金桔柠檬

柠檬蜜

柠檬养乐多

季节限定：奶绿装芒

季节限定：柚心动了

季节限定：百香YOYO绿

季节限定：芒果YOYO绿

季节限定：花生豆花奶茶

## 喜茶
多肉葡萄+芋圆波波

芝芝芒芒+芋圆波波

芝芝莓莓桃

奶茶波波冰+黑糖波波

纯绿妍换牛乳茶底+桂花冻

金凤茶王+脆波波

雪山思乡龙眼季节限定：王榨油柑

季节限定：双榨杨桃油柑

冻暴柠

多肉芒芒甘露

原创生打椰椰奶冻

满杯红柚

烤黑糖波波牛乳
## COCO
上新：火焰蓝椰

雪顶蜜恋桃桃

白玉粉荔

白玉荔枝茶

白玉荔枝多多

牛油果布丁

鲜苹果百香

星空葡萄

荞麦轻奶茶

荞麦轻茶

芒芒绿茶

芒果多多

柠檬霸

沙棘百香双响炮

沙棘摇摇冻

鲜芋奶茶+青稞+无糖

铁观音珍珠茶拿铁 + 青稞 + 奶盖 + 芋头

双球冰激凌红茶 + 奶霜 + 珍珠 去冰半糖

鲜百香双响炮 + 椰果 少冰半糖

鲜柠檬茶

轻茶摇摇冻

法式奶霜茗茶鲜芋牛奶西米露 + 红豆 + 香芋无糖少冰

茉香奶茶 + 珍珠 + 仙草 去冰五分甜

双球冰淇淋红茶+芋头+珍珠 去冰、无糖

茉香奶茶+芋鲜+青稞+珍珠 去冰、无糖

杨枝甘露+椰果 少冰

红果小姐姐+奶霜 半糖

## 茶百道
季节水果茶：茉莉白桃子

季节水果茶: 白桃子酪酪

季节水果茶：鲜草莓酪酪

芒芒生打椰

生椰大满贯

杨枝甘露

西瓜啵啵

百香凤梨

手捣芒果绿

超级杯水果茶

奥利奥蛋糕

抹茶红豆蛋糕

招牌芋圆奶茶

豆乳玉麒麟

茉莉奶绿

黄金椰椰乌龙

血糯米奶茶

奥利奥奶茶

茉莉绿茶

冰乌龙

海盐芝士抹茶
## 蜜雪冰城
柠檬水！

华夫冰淇淋

黑糖珍珠圣代

雪顶咖啡
