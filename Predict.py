import rasterio
import joblib
import gdal
import pandas as pd
from osgeo import osr
import numpy as np
import time
import Projection as PJ

# estimator1 = ensemble.RandomForestRegressor(n_estimators=200,oob_score=True,max_depth=60,max_leaf_nodes=1500)
estimator1 = joblib.load(r"LR_joblib_221901.pkl")


def predict_LAI(imgpath, outpath='LAIRes_0922.tif'):
    # imgpath   =  r"S2B_MSIL1C_20220819T024529_N0400_R132_T50SNA_20220819T043846_resampled.tif"        # 路径
    # 打开文件 rasterio.io.DatasetReader,包含了栅格的所有信息
    # from sklearn.preprocessing import MinMaxScaler
    # mm = MinMaxScaler()
    # train_label = mm.fit_transform(LAI.reshape(-1, 1))

    # src1 = gdal.Open(imgpath)
    # # 获取TIFF的范围信息
    # adfGeoTransform = src1.GetGeoTransform()
    #
    # # 读取波段信息
    # x_train_2 = src1.GetRasterBand(2).ReadAsArray()
    # x_train_3 = src1.GetRasterBand(3).ReadAsArray()
    # x_train_4 = src1.GetRasterBand(4).ReadAsArray()
    # x_train_8 = src1.GetRasterBand(8).ReadAsArray()
    #
    # # 转为一维数组1,-1
    #
    # x_2 = list(chain.from_iterable(x_train_2))
    # x_3 = list(chain.from_iterable(x_train_3))
    # x_4 = list(chain.from_iterable(x_train_4))
    # x_8 = list(chain.from_iterable(x_train_8))
    # data = pd.DataFrame({'bound2': x_2, 'bound3': x_3, 'bound4': x_4, 'bound8': x_8})
    # X = data.loc[:, ('bound2', 'bound3', 'bound4', 'bound8')]
    src1 = rasterio.open(imgpath)
    rat = src1.read()
    train = np.transpose(rat[1:9], (1, 2, 0))
    train = train.reshape(-1, 8)
    X = pd.DataFrame(train, columns=['B' + str(i) for i in range(1, 8)] + ['B8'])
    y_predict1 = estimator1.predict(X)
    driver = gdal.GetDriverByName('GTiff')

    src0 = gdal.Open(imgpath)
    # 获取TIFF的范围信息
    adfGeoTransform = src0.GetGeoTransform()
    # adfGeoTransform1 = (1076350.853198954, 10.0, 0.0, 3567604.9181152456, 0.0, -10.0)
    # 创建结果
    dst_ds = driver.Create(outpath, src0.RasterXSize, src0.RasterYSize, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(adfGeoTransform)
    # 设置坐标系
    # 创建坐标系
    srs = osr.SpatialReference()
    # 设置椭球体即地理坐标系
    srs.SetWellKnownGeogCS('WGS84')
    # 设置投影坐标
    # 输入50带和是否在北半球
    srs.SetUTM(50, 1)
    dst_ds.SetProjection(srs.ExportToWkt())

    result = y_predict1.reshape((src0.RasterYSize, src0.RasterXSize))

    dst_ds.GetRasterBand(1).WriteArray(result)
# profile = src1.profile
# profile.update(
#     dtype=y_predict1.dtype,
#     count=1
# )
# with rasterio.open(outpath, mode='w', **profile) as dst:
#     dst.write(y_predict1.reshape(src1.width, src1.height), 1)
# res = mm.inverse_transform(y_predict1.reshape(-1, 1))


file_name = '2022-05-06_QJS2DL.tif'
name = file_name.split('.')
GEE_file = r'E:\Desktop\20220913-20220916-0919-0923\20220916-0921\Sklearn回归模型规整\投影\{}'.format(file_name)

raster_path = r'E:\Desktop\20220913-20220916-0919-0923\20220916-0921\01GEE影像\{}'.format(file_name)
# 保存投影栅格数据路径
UTM_raster_path = r'E:\Desktop\20220913-20220916-0919-0923\20220916-0921\Sklearn回归模型规整\投影\{}'.format(file_name)
longitude = 117
is_north = True
PJ.raster_WGS2UTM(raster_path, UTM_raster_path, longitude, is_north)

mdhms = time.strftime('%d%H%M', time.localtime(time.time()))
Predict_LAI = r"LAI" + '_' + name[0] + '_' + mdhms + ".tif"
predict_LAI(GEE_file, Predict_LAI)
