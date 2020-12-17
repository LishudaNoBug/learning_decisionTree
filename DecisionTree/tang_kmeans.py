#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    K-Means算法实例
"""

import matplotlib.pyplot as plt
import sklearn.datasets as ds
import matplotlib.colors
#造数据
N=800
centers=4
# 生成2000个（默认）2维样本点集合，中心点5个
data,y=ds.make_blobs(N,centers=centers,random_state=0)
#原始数据分布
#在使用matplotliblib画图的时候经常会遇见中文或者是负号无法显示的情况，我们会添加下面两句话：
#pylot使用rc配置文件来自定义图形的各种默认属性，称之为rc配置或rc参数。通过rc参数可以修改默认的属性，包括窗体大小、每英寸的点数、线条宽度、颜色、样式、坐标轴、坐标和网络属性、文本、字体等。
matplotlib.rcParams['font.sans-serif'] = [u'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
cm = matplotlib.colors.ListedColormap(list('rgbm'))
plt.scatter(data[:,0],data[:,1],c=y,cmap=cm)
plt.title(u'原始数据分布')
plt.grid()
plt.show()

'''
sklearn.cluster.KMeans(
	n_clusters=8, 
	init='k-means++', 
	n_init=10, 
	max_iter=300, 
	tol=0.0001, 
	precompute_distances='auto', 
	verbose=0, 
	random_state=None, 
	copy_x=True, 
	n_jobs=1, 
	algorithm='auto' )
参数说明：
(1)n_clusters:簇的个数，即你想聚成几类
(2)init: 初始簇中心的获取方法
(3)n_init: 获取初始簇中心的更迭次数，为了弥补初始质心的影响，算法默认会初始10次质心，实现算法，然后返回最好的结果。
(4)max_iter: 最大迭代次数（因为kmeans算法的实现需要迭代）
(5)tol: 容忍度，即kmeans运行准则收敛的条件
(6)precompute_distances：是否需要提前计算距离，这个参数会在空间和时间之间做权衡，如果是True 会把整个距离矩阵都放到内存中，auto 会默认在数据样本大于featurs*samples 的数量大于12e6 的时候False,False 时核心实现的方法是利用Cpython 来实现的
(7)verbose: 冗长模式（不太懂是啥意思，反正一般不去改默认值）
(8)random_state: 随机生成簇中心的状态条件。
(9)copy_x: 对是否修改数据的一个标记，如果True，即复制了就不会修改数据。bool 在scikit-learn 很多接口中都会有这个参数的，就是是否对输入数据继续copy 操作，以便不修改用户的输入数据。这个要理解Python 的内存机制才会比较清楚。
(10)n_jobs: 并行设置
(11)algorithm: kmeans的实现算法，有：‘auto’, ‘full’, ‘elkan’, 其中 'full’表示用EM方式实现
'''
#K-Means
from sklearn.cluster import KMeans
# n_clusters=k
model=KMeans(n_clusters=3,init='k-means++')
#model.fit_predict相当于两个动作的合并：model.fit（data）+model.predict（data），
#可以一次性得到聚类预测之后的标签，免去了中间过程。
y_pre=model.fit_predict(data)
plt.scatter(data[:,0],data[:,1],c=y_pre,cmap=cm)
plt.title(u'K-Means聚类')
plt.grid()
plt.show()
