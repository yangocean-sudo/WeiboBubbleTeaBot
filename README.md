# WeiboBubbleTeaBot
原文：https://yangocean-sudo.github.io/

前几天看到有人在微博上@今天吃啥的bot，然后会秒收到一条随机的菜品推荐。这简直是选择困难症的福音，作为奶茶大户，我想着做一个奶茶推荐的bot。

在网上查找了许多资料但都没有类似的bot，最近一个类似的代码是2015年的，完全不能用。
<!--more-->
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

