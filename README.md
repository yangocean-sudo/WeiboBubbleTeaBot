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
## 奶茶列表
### 一点点
抹茶拿铁 去冰/三分/波霸

阿华田 去冰/三分/奶霜

四季奶青 去冰/五分/波霸

可可芭蕾 去冰/三分/布丁

乌龙奶茶 去冰/无糖/波霸

葡萄柚绿 去冰/三分/椰果

四季玛奇朵 去冰/三分/燕麦

波霸奶茶 去冰/三分/冰激凌

红茶玛奇朵/去冰/无糖/冰淇淋/珍波椰

四季春玛奇朵/去冰/五分甜/布丁/冰淇淋

冰淇淋红茶/去冰/三分甜/波霸/奶霜

阿华田 /去冰/无糖/冰淇淋/两颗布丁

四季春玛奇朵/常温/三分甜/波霸

四季春奶青/去冰/半糖/波霸

阿华田/去冰/三分甜/波霸/布丁

焦糖奶茶/热/三分甜/仙草

四季春奶青/去冰 /三分甜/燕麦

乌龙玛奇朵/去冰/微糖/波霸

四季春/去冰/三分糖/珍波椰

可可芭蕾/去冰/三份甜/布丁乌龙奶茶/去冰/无糖/波霸

柠檬养乐多/去冰/五分糖

古早味奶茶/去冰/半糖

### 喜茶
多肉葡萄+芋圆波波+玫瑰青 少冰、少糖

芝芝桃桃+红柚粒+脆波波+芝士换冰淇淋 少冰、正常糖

芝芝芒芒+芝士换冰淇淋+芋圆波波 少冰、少糖

芝芝莓莓+芦荟粒+芝士换酸奶 少冰、少少糖

奶茶波波冰+黑糖波波 少冰、少少糖

阿华田波波冰+黑波波换黑糖奶冻 少冰、不另外加糖

纯绿妍+脆啵啵+红柚果粒 少冰、少少糖

布甸波波冰+芋圆波波+黑糖奶冻 少冰

金凤茶王+小丸子 五分糖

### COCO
双球冰淇淋红茶+芋头+珍珠 去冰、无糖

鲜芋茶拿铁+布丁+珍珠 去冰、微糖

双球冰淇淋草莓+珍珠+椰果 去冰、半糖

双球冰淇淋抹茶+芋头+珍珠 去冰、三分糖

茉香奶茶+芋鲜+青稞+珍珠 去冰、无糖

杨枝甘露+椰果 少冰

鲜百香果双响炮+椰果 少冰、半糖

鲜芋雪冰+珍珠+冰淇淋 无糖

青茶奶霜+芋头+冰淇淋+珍珠

莓莓绵雪冰+冰淇淋+珍珠

红果小姐姐+奶霜 半糖

### 茶百道
桂花酒酿

招牌芋圆奶茶

黑糖牛乳波波茶

杨枝甘露

琥珀烤糖奶茶

青心乌龙奶茶

奥利奥芝士

金桔柠檬

杨枝甘露/少冰/三分糖

葡萄冻冻和葡萄芝士/芋圆/无糖

豆乳玉麒麟

酒酿芋圆奶茶

粉荔多肉

茉莉白桃
### 蜜雪冰城
柠檬水！

华夫冰淇淋

黑糖珍珠圣代

雪顶咖啡
