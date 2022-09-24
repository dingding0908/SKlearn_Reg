import rasterio
from osgeo import gdal
import numpy as np
from osgeo import osr


def xy_to_rowcol(extend, x, y):
    '''根据GDAL的六参数模型将给定的投影坐标转为影像图上坐标(行列号)
    根据GDAL的六参数模型将给定的投影或地理坐标转为影像图上坐标(行列号)
    :param extend: 图像的空间范围
    :param x:投影坐标x
    :param y:投影坐标y
    :return:投影坐标(x, y)对应的影像图上行列号(row, col)
'''
    a = np.array([[extend[1], extend[2]], [extend[4], extend[5]]])
    b = np.array([x - extend[0], y - extend[3]])
    row_col = np.linalg.solve(a, b)  # 使用numpy的linalg. solve进行二 元一次 方程的求解
    row = int(np.floor(row_col[1]))
    col = int(np.floor(row_col[0]))
    #
    return row, col


def Resampl(GEE_path, LAI_path, Out_LAI_path):
    '''

    :param GEE_path: 输入GEE栅格数据，投影过的
    :param LAI_path: 输入LAI栅格数据
    :param Out_LAI_path: 输出重采样后的数据
    :return:
    '''
    # 路径LAI
    src0 = gdal.Open(LAI_path)
    extend = src0.GetGeoTransform()  # 获取TIFF的范围信息
    img = src0.GetRasterBand(1).ReadAsArray()  # 读取波段信息

    # 路径GEE
    src1 = rasterio.open(GEE_path)
    rat = src1.read(1)

    gdal.AllRegister()
    dataset = gdal.Open(GEE_path)
    # extend1 = dataset.GetGeoTransform()
    adfGeoTransform = dataset.GetGeoTransform()

    # 左上角地理坐标
    print(adfGeoTransform[0])
    print(adfGeoTransform[3])

    nXSize = dataset.RasterXSize  # 列数
    nYSize = dataset.RasterYSize  # 行数

    arrSlope = []  # 用于存储每个像素的（X，Y）坐标
    raster = np.zeros((rat.shape[0], rat.shape[1]))
    for i in range(nYSize):
        for j in range(nXSize):
            px = adfGeoTransform[0] + i * adfGeoTransform[1] + j * adfGeoTransform[2]
            py = adfGeoTransform[3] + i * adfGeoTransform[4] + j * adfGeoTransform[5]
            row, col = xy_to_rowcol(extend, px, py)
            raster[j, i] = img[row, col]

    # 重采样LAI数据，命名LAI_img_0814_clip_982.tif
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(Out_LAI_path, rat.shape[0], rat.shape[1], 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(adfGeoTransform)
    srs = osr.SpatialReference()
    srs.SetProjection(dataset.GetProjection())
    dst_ds.GetRasterBand(1).WriteArray(raster)


GEE_path = r'E:\Desktop\20220913-20220916-0919-0923\20220916-0921\Sklearn回归模型规整\训练数据\GEE_0615_clip_982.tif'
LAI_path = r'E:\Desktop\20220913-20220916-0919-0923\20220916-0921\Sklearn回归模型规整\训练数据\LAI_img_0615_clip_1002.tif'
Out_LAI_path = r'E:\Desktop\20220913-20220916-0919-0923\20220916-0921\Sklearn回归模型规整\重采样LAI数据\LAI_img_0615_clip_982.tif'
Resampl(GEE_path, LAI_path, Out_LAI_path)
