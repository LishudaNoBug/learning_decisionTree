import numpy as np
import matplotlib.pyplot as mp
import sklearn.metrics as sm
import sklearn.ensemble as se  # 集合算法模块
import sklearn.utils as su  # 打乱数据
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from matplotlib import pyplot as plt

"""
    我自己的随机森林集大成者
    使用到的：pandas读入，数据补全并str转化、切分数据和标签、切分训练集测试集、特征重要性
    缺：GridSearchCV自动调参、这个“加利福利亚”房价预测中有代码。
"""

# 读入数据集
titanic = pd.read_csv('titanic_train.csv')  # 使用pandas读取CSV文件

# 缺值补全、str转换
titanic['Age'] = titanic['Age'].fillna(titanic['Age'].median())
titanic.loc[titanic['Sex'] == 'male', 'Sex'] = 0
titanic.loc[titanic['Sex'] == 'female', 'Sex'] = 1
titanic['Embarked'] = titanic['Embarked'].fillna('S')
titanic.loc[titanic['Embarked'] == 'S', 'Embarked'] = 0
titanic.loc[titanic['Embarked'] == 'C', 'Embarked'] = 1
titanic.loc[titanic['Embarked'] == 'Q', 'Embarked'] = 2

# 拆分数据、标签
x=titanic[['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']]   # 数据
y=titanic['Survived']   # 标签

# 拆分训练集、测试集。
x=x.values  # dataFrame==>ndarray   注意一维array的+号可以直接加，但二维array的不能直接加因为它是一一对应加的会报错维度不同。要用np.append并且只能两两append。
y=y.values  # dataframe==>ndarray
x, y = su.shuffle(x, y, random_state=7)     # 首先打乱数据集，注意同时传入x、y这样保证打乱后x、y依然一一对应。
train_size = int(len(x) * 0.9)      # 取90%作为训练集
train_x, test_x, train_y, test_y = x[:train_size], x[train_size:], y[:train_size], y[train_size:]

# 构造模型
model = se.RandomForestRegressor(max_depth=10, n_estimators=1000, min_samples_split=2)  # 定义随机森林模型，参数自选
model.fit(train_x, train_y)     # 喂入训练集自动训练
pred_test_y = model.predict(test_x)     # 接着就可以调用并测试了
print('score得分：', sm.r2_score(test_y, pred_test_y))

# 打印特征重要性
predictors = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']   # 候选特征
selector = SelectKBest(f_classif, k=5)
selector.fit(titanic[predictors], titanic['Survived'])   # 将候选特征和label标签喂给selector
scores = -np.log10(selector.pvalues_)
plt.bar(range(len(predictors)), scores)
plt.xticks(range(len(predictors)), predictors, rotation='vertical')
plt.show()   # 柱状图越高则特征重要性越高，对于没用特征我们可以从随机森林中剔除。

# 换特征，重新预测：：：：：：：：：：：：：：：：：：：：：：：：：
# 拆分数据、标签
x=titanic[['Pclass', 'Sex', 'Fare', 'Embarked']]   # 数据
y=titanic['Survived']   # 标签

# 拆分训练集、测试集。
x=x.values  # dataFrame==>ndarray   注意一维array的+号可以直接加，但二维array的不能直接加因为它是一一对应加的会报错维度不同。要用np.append并且只能两两append。
y=y.values  # dataframe==>ndarray
x, y = su.shuffle(x, y, random_state=7)     # 首先打乱数据集，注意同时传入x、y这样保证打乱后x、y依然一一对应。
train_size = int(len(x) * 0.9)      # 取90%作为训练集
train_x, test_x, train_y, test_y = x[:train_size], x[train_size:], y[:train_size], y[train_size:]

# 构造模型
model = se.RandomForestRegressor(random_state=1, n_estimators=50, min_samples_split=4, min_samples_leaf=3)  # 定义随机森林模型，参数自选
model.fit(train_x, train_y)     # 喂入训练集自动训练
pred_test_y = model.predict(test_x)     # 接着就可以调用并测试了
print('特征重要性之后的score得分：', sm.r2_score(test_y, pred_test_y))
# print(model.score(train_x, train_y))   ?这又是什么东西啊！！