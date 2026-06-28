# -*- coding: utf-8 -*-
import os
import re
import time
import glob

from downloader import Downloader
from resolver import Resolver


class Rule(object):
    def __init__(self, name, url):
        self.Name = name
        self.FileName = self.Name.replace(' ', '_') + '.txt'
        self.URL = url
        self.Downloader = Downloader(os.getcwd() + '/rules/' + self.FileName, self.URL)

    def Update(self):
        if self.Downloader.Download():
            return True
        return False

def GetRuleList(fileName):
    ruleList = []
    with open(fileName, "r", encoding="utf-8") as f:
        for line in f:
            line = line.replace('\r', '').replace('\n', '')
            if line.find('|')==0 and line.rfind('|')==len(line)-1:
                rule = list(map(lambda x: x.strip(), line[1:].split('|')))
                if rule[1].find('(') > 0 and rule[1].find(')') > 0:
                    url = rule[1][rule[1].find('(')+1:rule[1].find(')')]
                    matchObj1 = re.match('(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', url)
                    if matchObj1:
                        ruleList.append([rule[0], url, rule[3]])
    return ruleList

def CreatReadme(ruleList, fileName):
    if os.path.exists(fileName):
        os.remove(fileName)
    
    f = open(fileName, 'a', encoding="utf-8")
    f.write("# Adlist\n")
    f.write("更适合国内互联网体质的超级过滤器\n\n")
    f.write("这是一个整合了easylist、chinalist、cjx list、adgk、adbyby、neo list、adguard dns filter等的超级过滤器，经过实际测试能过滤90%以上的广 告。代价是需要一定配置，低配机（安卓安兔兔20w以下或pc娱乐大师5w以下）慎用。\n\n")
    f.write("搭配DNS、隐身模式使用效果更佳，最好再添加一些补充过滤器，理论adguard和adblock应该都可以用\n\n")
    f.write("发现无法拦截欢迎issue，我看到就处理。\n\n")
    f.write("自动生成部分修改于217heidai/adblockfilters\n\n")
    f.write("## 订阅链接\n")
    f.write("主过滤器\n")
    f.write("* [原始链接](https://raw.githubusercontent.com/NaivG/adlist/main/mainlist.txt)\n")
    f.write("* [加速链接](https://mirror.ghproxy.com/https://raw.githubusercontent.com/NaivG/adlist/main/mainlist.txt)\n\n")
    f.write("附加过滤器\n")
    f.write("* [原始链接](https://raw.githubusercontent.com/NaivG/adlist/main/extralist.txt)\n")
    f.write("* [加速链接](https://mirror.ghproxy.com/https://raw.githubusercontent.com/NaivG/adlist/main/extralist.txt)\n\n")
    f.write("## 规则源\n")
    f.write("\n")
    f.write("| 规则 | 原始链接 | 加速链接 | 更新日期 |\n")
    f.write("|:-|:-|:-|:-|\n")
    for rule in ruleList:
        f.write("| %s | [原始链接](%s) | [加速链接](https://mirror.ghproxy.com/https://raw.githubusercontent.com/NaivG/adlist/main/rules/%s.txt) | %s |\n" % (rule[0],rule[1],rule[0].replace(' ', '_'),rule[2]))
    f.close()

def CreatFiters(blockList, unblockList, fileName):
    # 去重、排序
    def sort(L):
        L = list(set(L))
        L.sort()
        return L
    blockList = sort(blockList)
    unblockList = sort(unblockList)

    if os.path.exists(fileName):
        os.remove(fileName)
    
    f = open(fileName, 'a', encoding="utf-8")
    f.write("!\n")
    f.write("! Title: ADLIST BY Akina絵\n")
    f.write("! Homepage: https://naivg.uovou.cn\n")
    f.write("! Source: https://raw.githubusercontent.com/NaivG/adlist/main/mainlist.txt\n")
    f.write("! Version: %s\n"%(time.strftime("%Y%m%d%H%M%S", time.localtime())))
    f.write("! Last modified: %s\n"%(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())))
    f.write("! Blocked domains: %s\n"%(len(blockList)))
    f.write("! unBlocked domains: %s\n"%(len(unblockList)))
    f.write("!\n")
    for fiter in blockList:
        f.write("%s\n"%(fiter))
    for fiter in unblockList:
        f.write("%s\n"%(fiter))
    f.close()

def Entry():
    pwd = os.getcwd()
    ruleFile = pwd + '/README.md'

    ruleList = GetRuleList(ruleFile)
    isUpdate = False
    lastUpdate = time.strftime("%Y/%m/%d", time.localtime())
    print('开始更新规则')
    for i in range(0, len(ruleList)):
        relue = Rule(ruleList[i][0], ruleList[i][1])
        print('更新规则：%s'%(ruleList[i][0]))
        if relue.Update():
            isUpdate = True
            ruleList[i][2] = lastUpdate
    #isUpdate = True
    if isUpdate:
        print('存在更新，开始生成规则')
        blockList = []
        unblockList = []
        for i in range(0, len(ruleList)):
            resolver = Resolver(os.getcwd() + '/rules/' + ruleList[i][0].replace(' ', '_') + '.txt')
            L1, L2 = resolver.Resolve()
            blockList += L1
            unblockList += L2

        # 生成合并规则
        CreatFiters(blockList, unblockList, pwd + '/mainlist.txt')

        # 更新README.md
        CreatReadme(ruleList, pwd + '/README.md')
    print('规则生成完毕')
    print('开始删除临时下载文件')
    for f in glob.glob(pwd + '/rules/*.download'):
        os.remove(f)

if __name__ == '__main__':
    Entry()
