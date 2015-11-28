# -*- coding:utf-8 -*-

import ConfigParser
import pymysql.cursors
import time

DEFAULT_INI_PATH = "/root/golang/src/SilverBulletPlan/config.ini"


class SampleLoader:
    def __init__(self):
        configParser = ConfigParser.ConfigParser()
        configParser.read(DEFAULT_INI_PATH)
        self.connection = pymysql.connect(host=configParser.get("database", "host"),
                                          port=int(configParser.get("database", "port")),
                                          user=configParser.get("database", "user"),
                                          password=configParser.get("database", "passwd"),
                                          db=configParser.get("database", "dbName"),
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
    def getCount(self,state):
        query = "SELECT COUNT(*) AS count FROM FocusItem WHERE State=%s AND IsOperate=1"
        cursor = self.connection.cursor()

        cursor.execute(query,(state))
        result = cursor.fetchone()
        cursor.close()

        return result["count"]


    def getClassSamples(self, startIndex,state,maxLimit):
        tmp = []
        offset = 50
        querySQL = "SELECT * FROM FocusItem WHERE State=%s LIMIT %s,%s"
        cursor = self.connection.cursor()

        while (True):
            count = 0
            cursor.execute(querySQL, (state, startIndex, offset))

            for row in cursor:
                tmp.append(row["Title"] + row["Content"])
                count += 1

            if len(tmp) > maxLimit or count < offset:
                break
            else:
                startIndex += offset

        cursor.close()
        return tmp

    def getData(self, startIndex, offset):
        tmp = []
        state = -1
        querySQL = "SELECT * FROM FocusItem WHERE State=%s LIMIT %s,%s"
        cursor = self.connection.cursor()

        cursor.execute(querySQL, (state,startIndex,offset))
        for row in cursor:
            tmp.append({"mainKey": row["MainKey"], "text": row["Title"] + row["Content"]})

        cursor.close()
        return tmp

    def updateState(self, mainKeys, state):
        createAt = int(time.time())

        updateSQL = "UPDATE FocusItem set State=%s,CreateAt=%s WHERE MainKey IN (" + ",".join(mainKeys) + ")"
        cursor = self.connection.cursor()
        cursor.execute(updateSQL, (state, createAt))

        cursor.close()
        self.connection.commit()

    def close(self):
        self.connection.close()
