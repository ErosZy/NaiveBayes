# -*- coding:utf-8 -*-

from numpy import *
import operator

DEFAULT_STOPWORD_PATH = "/root/golang/src/SilverBulletPlan/pyscript/stopwords.txt"


class NavieBayes:
    def __init__(self):
        with open(DEFAULT_STOPWORD_PATH, "r") as f:
            self.stopwords = f.read().split(",")

    def clearStopWords(self, words):
        i = len(words) - 1

        while i >= 0:
            if words[i] in self.stopwords:
                del words[i]
            i -= 1
        return words

    def createVocabList(self, dataSet):
        vocabSet = set([])

        for document in dataSet:
            vocabSet = vocabSet | set(document)
        return list(vocabSet)

    def calcMostFreq(self, vocabList, fullText):
        freqDict = {}
        for token in vocabList:
            freqDict[token] = fullText.count(token)
        sortedFreq = sorted(freqDict.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sortedFreq[:30]

    def bagOfWords2Vec(self, vocabList, inputSet):
        results = [0] * len(vocabList)

        for word in inputSet:
            if word in vocabList:
                results[vocabList.index(word)] += 1

        return results

    def train(self, trainMatrix, trainCategory):
        numTrainDocs = len(trainMatrix)
        numWords = len(trainMatrix[0])
        pAbusive = sum(trainCategory) / float(numTrainDocs)
        p0Num = ones(numWords)
        p1Num = ones(numWords)
        p0Denom = 2.0
        p1Denom = 2.0

        for i in range(numTrainDocs):
            if trainCategory[i] == 1:
                p1Num += trainMatrix[i]
                p1Denom += sum(trainMatrix[i])
            else:
                p0Num += trainMatrix[i]
                p0Denom += sum(trainMatrix[i])

        p1Vect = log(p1Num / p1Denom)
        p0Vect = log(p0Num / p0Denom)

        return p0Vect, p1Vect, pAbusive

    def classify(self, vec2Classify, p0Vec, p1Vec, pClass1):
        p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)
        p1 = sum(vec2Classify * p1Vec) + log(pClass1)

        if p1 > p0:
            return 1
        else:
            return 0
