import urllib.request
import json
import gzip
import pickle

import resolver_utils


def getHeaders(cfg):
    # 从配置文件读取数据
    problemId=cfg['problemId']
    cookie=cfg['cookie']
    # 从浏览器复制的header
    headers={
        "Accept": "application/json;charset=UTF-8",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"zh-CN",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": cookie,
        "Eagleeye-Pappname": "eksabfi2cn@94d5b8dc408ab8d",
        "Eagleeye-Sessionid": "3wlLtwL4j0X5772F1ymv1jt2bv0O",
        "Eagleeye-Traceid": "3f793bf1171646202705810238ab8d",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Referer": "https://pintia.cn/problem-sets/"+problemId+"/rankings",
        "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        "X-Lollipop": "fd0f671d1f29b275fdfb4df1999ef66a",
        "X-Marshmallow": ""
    }
    return headers

# 计算出提交时间距离开始时间的时间戳，单位为毫秒
def transTimeToTimestamp(submitAt,startTimestamp):
    timestamp = resolver_utils.transTimeToTimestamp(submitAt)
    return (timestamp-startTimestamp)*1000


# 根据编译器信息得到语言
def transComplierToLanguage(compiler):
    if compiler=='GXX' or compiler=='CLANGXX':
        return "C++"
    elif compiler=='GCC' or compiler=='CLANG':
        return "C"
    elif compiler=='PYPY3' or compiler=='PYTHON3' or compiler=='PYTHON2':
        return "Python"
    elif compiler=='JAVAC':
        return "Java"
    else:
        return "Other Language"


# 将得到的提交记录转换为需要的格式
def transSubmit(submitList,problemList):
    # {
    #     "status": "WRONG_ANSWER",
    #     "team_id": "26",
    #     "problem_id": 12,
    #     "timestamp": 311820,
    #     "language": "C++",
    #     "submission_id": "787"
    # }
    # 读入config文件
    config="./config/config.json"
    with open(config, 'r', encoding='utf-8') as configFile:
        configData = json.load(configFile)
    startTimestamp=configData['start_time']*1000

    responseSubmitList=[]
    for i in range(0,len(submitList)):
        submitRecord={}
        submitRecord['team_id']=submitList[i]['userId']
        submitRecord['problem_id']=ord(problemList[submitList[i]['problemSetProblemId']]['label'])-ord('A')
        submitRecord['timestamp']=transTimeToTimestamp(submitList[i]['submitAt'],startTimestamp/1000)
        submitRecord['language']=transComplierToLanguage(submitList[i]['compiler'])
        submitRecord['submission_id']=submitList[i]['id']
        submitRecord['status']=submitList[i]['status']
        submitRecord['timestamp']=int(submitRecord['timestamp'])
        responseSubmitList.append(submitRecord)
    return responseSubmitList


# 获取下一页的提交数据
def getNextSubmitList(cfg,id,ans):
    # 从配置文件读取数据
    problemId=cfg['problemId']

    url="https://pintia.cn/api/problem-sets/"+problemId+"/submissions?before="+id+"&limit=100&filter=%7B%7D"
    # 直接从浏览器复制的header
    headers=getHeaders(cfg)
    # 发送请求
    req=urllib.request.Request(url,headers=headers)
    response=urllib.request.urlopen(req)

    # 解析请求
    content = gzip.decompress(response.read())
    data = content.decode('utf-8')
    json_data = json.loads(data)

    # 得到提交列表
    submitList=json_data['submissions']
    # 提交列表中涉及到的题目
    problemList=json_data['problemSetProblemById']
    # 提交列表中涉及到的用户的用户信息
    userList=json_data['examMemberByUserId']

    # 转换数据到board的格式
    ansNext=transSubmit(submitList,problemList)

    if len(ansNext)==0:
        return ""
    else:
        ans.extend(ansNext)
        return ansNext[len(ansNext)-1]['submission_id']
    



# 调用pta的接口得到提交列表
def getSubmitList(cfg):
    # 从配置文件读取数据
    problemId=cfg['problemId']

    # 请求提交列表的url
    url="https://pintia.cn/api/problem-sets/"+problemId+"/submissions?limit=100&filter=%7B%7D"

    # 直接从浏览器复制的header
    headers=getHeaders(cfg)

    # 发送请求
    req=urllib.request.Request(url,headers=headers)
    response=urllib.request.urlopen(req)

    # 解析请求
    content = gzip.decompress(response.read())
    data = content.decode('utf-8')
    json_data = json.loads(data)

    # 得到提交列表
    submitList=json_data['submissions']
    # 提交列表中涉及到的题目
    problemList=json_data['problemSetProblemById']
    # 提交列表中涉及到的用户的用户信息
    userList=json_data['examMemberByUserId']

    # 转换数据到board的格式
    ans=transSubmit(submitList,problemList)

    # 爬取后边页数
    id=""
    if len(ans)!=0:
        id=ans[len(ans)-1]['submission_id']
        id=getNextSubmitList(cfg,id,ans)
        while id!="":
            id=getNextSubmitList(cfg,id,ans)
    return ans

# 读取文件
def getJsonFiles():
    # 读入config文件
    config="./config/config.json"
    with open(config, 'r', encoding='utf-8') as configFile:
        configData = json.load(configFile)
    configString = json.dumps(configData, ensure_ascii=False, indent=4)
    # 读入team文件
    team="./config/team.json"
    with open(team, 'r', encoding='utf-8') as teamFile:
        teamData = json.load(teamFile)
    teamString = json.dumps(teamData, ensure_ascii=False, indent=4)
    # 读入run文件
    run="./data/run.json"
    with open(run, 'r', encoding='utf-8') as runFile:
        runData = json.load(runFile)
    runString = json.dumps(runData, ensure_ascii=False, indent=4)
    files={}
    files['run.json']=runString
    files['config.json']=configString
    files['team.json']=teamString
    return files
