# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from bayes import NavieBayes
from sampleLoader import SampleLoader
from numpy import *
import jieba
import re
import sys
import random

reload(sys)
sys.setdefaultencoding('utf8')

sl = SampleLoader()
results = {"target": {}, "notTarget": {}}
gCount = 3

while(gCount > 0):

    # 从数据库加载词典
    badPostingsCount = sl.getCount(state=0)
    goodPostingsCount = sl.getCount(state=1)
    startIndex = -1
    badPostings = goodPostings = []

    if badPostingsCount > goodPostingsCount:
        startIndex = badPostingsCount - goodPostingsCount - 1
        goodPostings = sl.getClassSamples(startIndex=0, state=1, maxLimit=goodPostingsCount)
        badPostings = sl.getClassSamples(startIndex=random.randint(0,startIndex), state=0, maxLimit=goodPostingsCount)
        badPostings = badPostings[:len(goodPostings)]
    elif badPostingsCount < goodPostingsCount:
        startIndex = goodPostingsCount - badPostingsCount - 1
        badPostings = sl.getClassSamples(startIndex=0, state=0, maxLimit=badPostingsCount)
        goodPostings = sl.getClassSamples(startIndex=random.randint(0,startIndex), state=1, maxLimit=badPostingsCount)
        goodPostings = goodPostings[:len(badPostings)]

    print len(goodPostings),len(badPostings)

    # 合并向量词典
    postingList = []
    classVec = []
    minLength = len(badPostings)

    for index in range(minLength):
        postingList.append(badPostings[index])
        classVec.append(0)
        postingList.append(goodPostings[index])
        classVec.append(1)

    # 分词，去除干扰符号及停词
    filterReg = re.compile(r'[*+-/，。？！,.?!\[\]{}()（）&^%$#@!~`:;\"\'”“‘’【】<>《》：；|、\\…—_=]|\s+|\d+')
    bayes = NavieBayes()

    for index in range(0, len(postingList)):
        tmp = filterReg.sub("", postingList[index])
        tmp = list(jieba.cut(tmp, cut_all=False,HMM=False))
        postingList[index] = bayes.clearStopWords(tmp)

    # 创建词向量并进行样本训练
    trainMatrix = []
    myVocabList = bayes.createVocabList(postingList)

    # 去除频次最高的前30个词
    top30Words = bayes.calcMostFreq(myVocabList, postingList)

    for pairW in top30Words:
        if pairW[0] in myVocabList:
            myVocabList.remove(pairW[0])

    for postinDoc in postingList:
        trainMatrix.append(bayes.bagOfWords2Vec(myVocabList, postinDoc))
    p0V, p1V, pAb = bayes.train(array(trainMatrix), array(classVec))

    # 模型进行判断
    startIndex = 0
    offset = 50

    while (True):
        data = sl.getData(startIndex, offset)

        for item in data:
            entry = bayes.clearStopWords(list(jieba.cut(filterReg.sub("", item["text"]), cut_all=False,HMM=False)))
            doc = array(bayes.bagOfWords2Vec(myVocabList, entry))	
	    key = item["mainKey"]

            if bayes.classify(doc, p0V, p1V, pAb) == 0:
                if key not in results["target"]:
                    results["target"][key] = 1
                else:
                    results["target"][key] += 1
            else:
                if key not in results["notTarget"]:
                    results["notTarget"][key] = 1
                else:
                    results["notTarget"][key] += 1
	
	if len(data) < offset:
            break
        else:
            startIndex += offset

    gCount -= 1


def getLargeThan2Data(results):
    tmp = []
    for key in results:
        if results[key] >= 2:
            tmp.append(key)
    return tmp

targets = getLargeThan2Data(results["target"])
notTargets = getLargeThan2Data(results["notTarget"])

print len(targets),len(notTargets)

if len(targets) != 0:
    sl.updateState(targets,0)

if len(notTargets) != 0:
    sl.updateState(notTargets,1)

sl.close()
