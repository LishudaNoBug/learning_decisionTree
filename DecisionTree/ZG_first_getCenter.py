# coding:utf-8
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from hdfs import HdfsError
from sklearn.cluster import KMeans
import pymysql
import uuid
from hdfs.client import Client

"""
    计算各个mmsi历史数据的质心，并插入mysql
    放在172.18.50.204上
"""


def getCentroid(mmsi):

    # 打开数据库连接，缺少关键数据的直接return
    db = pymysql.connect(host="172.18.50.212", user="adims", password="Yj69%M,6=4ub", database="adims")
    cursor = db.cursor()   # 使用cursor()方法获取操作游标
    sql="select deadweight,breadth,length_overall_loa,shiptype_level5_sub_group,draught from t_ship where mmsi='%s'" %(mmsi)
    cursor.execute(sql)
    data=cursor.fetchall()
    if data==():
        print('t_ship船舶档案无此mmsi %s' %(mmsi))
        return                # t_ship没有静态信息，跳过此条船
    deadweight=data[0][0]
    if deadweight==None: deadweight=0
    breadth=data[0][1]
    if breadth==None: breadth=0
    length_overall_loa=data[0][2]
    if length_overall_loa==None: length_overall_loa=0
    shiptype_level5_sub_group=data[0][3]
    if shiptype_level5_sub_group==None: shiptype_level5_sub_group=''
    draught=data[0][4]
    if draught==None or draught==0 or draught=='0': return      # 设计吃水值空，就跳过此条船

    # 从hdfs拉取数据==========================================
    try:
        hdfsList=client.list("/user/hive/warehouse/ship_data.db/ais_history/mm="+mmsi, status=False)
    except HdfsError:
        print("hdfs无三年历史数据")
        return
    lines = []
    for monthday in hdfsList:   # 每个月份的文件夹
        monthdayPath='/user/hive/warehouse/ship_data.db/ais_history/mm='+mmsi+'/'+monthday

        txtList=client.list(monthdayPath, status=False)
        try:
            txtName=txtList[0]
        except IndexError:
            return
        txtPath=monthdayPath+'/'+txtName    # 每个月份内的txt文件
        print(txtPath)

        with client.read(txtPath, encoding='utf-8', delimiter='\n') as reader:
            for line in reader:
                if (line=='' or line=='\n'):
                    continue
                linearray=line.split(',')
                if len(linearray)!=14: continue # 过滤掉问题行数据
                try:
                    linearray[13]=float(linearray[13])
                except :
                    continue
                lines.append(linearray)  # 将各个文件加到lines里
    print('list大小：'+str(len(lines)))

    # 数据开始输入给算法==============================================
    beer=pd.DataFrame(lines)    # 将所有数据先转成dataframe
    beer.columns=['mmsi', 'updatetime', 'lon', 'lat', 'course', 'speed', 'heading', 'rot', 'status','static_info_updatetime', 'eta', 'dest', 'destination_tidied', 'draught']
    if beer.shape[0]==1:return    # txt只有1行则跳过

    min=(draught*0.5)
    max=(draught*1.2)
    print('静态draught为%s'%(draught))

    X = beer[(min<beer['draught']) & (beer['draught']<max)]   # 过滤掉超过设计吃水值的行数据
    X=X[['draught']]
    if X.shape[0]==0:
        print('X.shape[0]==0')
        return
    km = KMeans(n_clusters=2).fit(X)
    X['cluster'] = km.labels_  # 将训练结果新增到beer的cluster列（0-1-2-1-2-0-2-2-1......）
    centers = X.groupby('cluster').mean().reset_index()  # 每个簇的原始数据计算各个属性平均值
    print(centers)
    """
           cluster   draught
    0        0  3.628551
    1        1  5.545809
    """

    # 异常画图时用
    # plt.rcParams['font.size'] = 14     # 设置绘图样式plt字体大小
    # colors = np.array(['red', 'green', 'blue', 'yellow'])     # 簇为0位red，簇为1位green
    # plt.scatter(X['draught'], X['draught'], c=colors[X['cluster']])         # 画data
    # plt.scatter(centers['draught'], centers['draught'], marker='+', s=150, c='black')
    # plt.xlabel('draught')
    # plt.ylabel('draught')
    # plt.show()


    uuid_str=str(uuid.uuid4())
    cluster_0= centers.loc[0,'draught']
    if centers.shape[0]==1:
        cluster_1= 0
    else:       # 原始数据有问题，只聚出一类
        cluster_1= centers.loc[1,'draught']

    if(cluster_0>cluster_1):
        min=cluster_1
    else:
        min=cluster_0

    cluster_0=format(cluster_0,'.1f')
    cluster_1=format(cluster_1,'.1f')
    min=format(min,'.1f')   # min就是二分类中的小质心，并且保留一位小数

    # 插入mysql
    sql="insert into t_kmeans_cluster(id,mmsi,cluster_0,cluster_1,deadweight,breadth,length_overall_loa,shiptype_level5_sub_group,min_number) values('%s','%s',%s,%s,%s,%s,%s,'%s',%s)" %(uuid_str,mmsi,cluster_0,cluster_1,deadweight,breadth,length_overall_loa,shiptype_level5_sub_group,min)
    cursor.execute(sql)
    db.commit()
    db.close()



if __name__ == '__main__':
    client = Client("http://172.18.50.3:9870/",root="/",timeout=10000,session=False)
    # 读取sample.txt
    with open('/opt/mmsi_all.txt', 'r') as f:
        list=f.readlines()
    for i in list:
        mmsi=i[0:i.index('\n')]
        print(mmsi)
        if (mmsi=='' or mmsi==None or mmsi=="\n" ): continue
        try:
            getCentroid(mmsi)
            print()
        except:
            continue


