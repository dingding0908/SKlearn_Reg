import pandas as pd
import time
import joblib
import gdal
from itertools import chain
from sklearn.model_selection import train_test_split
from sklearn import ensemble
import numpy as np
import rasterio

# 读取LAI_0814和LAI_0615
imgpath = r"./训练数据/LAI_img_0814_clip_982_V4.tif"
src0 = gdal.Open(imgpath)
# 获取TIFF的范围信息
extend = src0.GetGeoTransform()
# 读取波段信息
y_train = src0.GetRasterBand(1).ReadAsArray()
y_0 = list(chain.from_iterable(y_train))
datay = pd.DataFrame({'result': y_0})
Y = datay.loc[:, ('result')]

imgpath1 = r"./重采样LAI数据/LAI_img_0615_clip_982.tif"
src0 = gdal.Open(imgpath1)
# 获取TIFF的范围信息
extend = src0.GetGeoTransform()
# 读取波段信息
y_train01 = src0.GetRasterBand(1).ReadAsArray()
y_1 = list(chain.from_iterable(y_train))
datay1 = pd.DataFrame(y_1)
Y = pd.concat([Y, datay1])
Y = Y.values.ravel()

imgpath = r"./训练数据/GEE_0814_clip_982.tif"  # 路径
# 打开文件 rasterio.io.DatasetReader,包含了栅格的所有信息
src1 = rasterio.open(imgpath)
rat = src1.read()
train = np.transpose(rat[1:9], (1, 2, 0))
train = train.reshape(-1, 8)
data = pd.DataFrame(train, columns=['B' + str(i) for i in range(1, 8)] + ['B8'])

imgpath2 = r"./训练数据/GEE_0615_clip_982.tif"  # 路径
# 打开文件 rasterio.io.DatasetReader,包含了栅格的所有信息
src2 = rasterio.open(imgpath2)
rat2 = src2.read()
train2 = np.transpose(rat2[1:9], (1, 2, 0))
train2 = train.reshape(-1, 8)
df = pd.DataFrame(train2, columns=['B' + str(i) for i in range(1, 8)] + ['B8'])
X = pd.concat([data, df])

# X.to_csv('train_x.csv', index=None)
# Y.to_csv('train_y.csv', index=None)

# imgpath = r"./训练数据/GEE_0814_clip_982.tif"
# src1 = gdal.Open(imgpath)
# # 获取TIFF的范围信息
# extend_x = src1.GetGeoTransform()
# # 读取波段信息
# x_train_2 = src1.GetRasterBand(2).ReadAsArray()
# x_train_3 = src1.GetRasterBand(3).ReadAsArray()
# x_train_4 = src1.GetRasterBand(4).ReadAsArray()
# x_train_8 = src1.GetRasterBand(8).ReadAsArray()
# # 转为一维数组1,-1
# x_2 = list(chain.from_iterable(x_train_2))
# x_3 = list(chain.from_iterable(x_train_3))
# x_4 = list(chain.from_iterable(x_train_4))
# x_8 = list(chain.from_iterable(x_train_8))
# data = pd.DataFrame({'bound2': x_2, 'bound3': x_3, 'bound4': x_4, 'bound8': x_8})
# X = data.loc[:, ('bound2', 'bound3', 'bound4', 'bound8')]

# data.to_csv('train_x.csv', index=None)
# datay.to_csv('train_y.csv', index=None)

# 训练模型


# # 定义多项式回归,degree的值可以调节多项式的特征
# poly_reg = PolynomialFeatures(degree=4)
# # 特征处理
# x_poly = poly_reg.fit_transform(data)
# # 定义回归模型
# lin_reg = LinearRegression()
# # 训练模型
# lin_reg.fit(x_poly, y)


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=1, random_state=1)

estimator1 = ensemble.RandomForestRegressor(n_estimators=200, oob_score=True, max_depth=60, max_leaf_nodes=1500)
# model.fit(data, y_0)
estimator1.fit(X_train, y_train)

# 给保存的模型的名字加上时间标签，以区分训练过程中产生的不同的模型
mdhms = time.strftime('%d%H%M', time.localtime(time.time()))
# 保存的模型的文件名
FILE = r'./LR_joblib' + '_' + mdhms + '.pkl'

joblib.dump(estimator1, FILE)
