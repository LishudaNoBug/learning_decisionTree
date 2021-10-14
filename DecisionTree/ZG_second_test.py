# coding:utf-8
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pymysql
import uuid
from hdfs.client import Client
from decimal import *

def testAlgorithm(mmsi):
    # 1.查出该mmsi所有事件 eventListTuple
    # db = pymysql.connect(host="172.18.50.212", user="hangyun_ro", password="B@m4Mtli#y=", database="adims")
    db = pymysql.connect(host="172.18.50.212", user="adims", password="Yj69%M,6=4ub", database="adims")
    cursor = db.cursor()   # 使用cursor()方法获取操作游标

    sql="SELECT * FROM `t_kmeans_test` where mmsi='%s' limit 1" %(mmsi)
    cursor.execute(sql)
    haveMmsi=cursor.fetchall()
    if haveMmsi!=(): return     # 已有该mmsi数据，则跳过


    sql="SELECT event_name,arrive_time FROM `t_event_history` where arrive_time BETWEEN '2020-01-01 00:00:00' and '2021-01-01 00:00:00' and mmsi='%s'" %(mmsi)
    cursor.execute(sql)
    eventListTuple=cursor.fetchall()
    if eventListTuple==():
        print('t_ship无此mmsi数据 %s' %(mmsi))
        return                # t_ship没有静态信息，跳过此条船

    # 2. 加载历史数据到内存  ais_draught_storage ais_updatetime_storage
    ais_draught_storage=[]
    ais_updatetime_storage=[]
    txtPath='/user/hive/warehouse/ship_data.db/ais_history/mm=%s/month=202012/%s.txt' %(mmsi,mmsi)
    with client.read(txtPath, encoding='utf-8', delimiter='\n') as reader:
        for line in reader:
            if (line=='' or line=='\n'):                continue
            linearray=line.split(',')
            if len(linearray)!=14: continue
            try:
                ais_draught=float(linearray[13])
                ais_updatetime=linearray[1]
            except :
                continue
            ais_draught_storage.append(ais_draught)
            ais_updatetime_storage.append(ais_updatetime)

    # 3. 去查计算的质心，做好准备
    sql="SELECT cluster_0,cluster_1,min_number FROM `t_kmeans_cluster` where mmsi='%s'" %(mmsi)
    cursor.execute(sql)
    clusterdata=cursor.fetchall()
    cluster0=clusterdata[0][0]
    cluster1=clusterdata[0][1]
    minNumber=clusterdata[0][2]
    if (cluster0<cluster1):
        load_cluster=cluster0   # 质心小的吃水值小，应当是去装货的
        dischange_cluster=cluster1
    else:
        load_cluster=cluster1
        dischange_cluster=cluster0

    # 4.每个事件的arrival_time去找对应draught
    for event in eventListTuple:
        print(event)
        event_name=event[0]
        arrival_time=event[1]
        try:
            index=ais_updatetime_storage.index(arrival_time)
            ais_draught=ais_draught_storage[index]
        except :
            continue

        # 每个事件去预测
        # diff_load=abs(int(ais_draught)-int(load_cluster))
        # diff_dischange=abs(int(ais_draught)-int(dischange_cluster))
        # if (diff_load<diff_dischange):  # 如果ais信号的draught和装货质心近，那么应当是去装货的
        #     predict="装"
        # else:
        #     predict="卸"


        if (ais_draught>minNumber):
            predict="卸"
        else:
            predict="装"

        true_or_false=(predict in event_name)
        uuid_str=str(uuid.uuid3(uuid.NAMESPACE_URL,mmsi+arrival_time)).replace('-','')
        sql="insert into t_kmeans_test VALUES('%s','%s','%s','%s','%s','%s','%s')" %(uuid_str,mmsi,arrival_time,event_name,predict,true_or_false,ais_draught)
        print(sql)
        cursor.execute(sql)
        db.commit()

    db.close()






if __name__ == '__main__':
    client = Client("http://172.18.50.2:9870/",root="/",timeout=10000,session=False)
    with open('/opt/sample.txt', 'r') as f:
        list=f.readlines()
    for i in list:
        mmsi=i[0:i.index('\n')]
        print(mmsi)
        if (mmsi==''):continue
        testAlgorithm(mmsi)