# -*- coding: utf-8 -*-
import gdal
from osgeo import ogr, osr


def read_img(filename):
    '''读取栅格数据的范围、坐标系及数据'''
    dataset = gdal.Open(filename)

    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize

    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)

    # del dataset
    return im_width, im_height, im_proj, im_geotrans, im_data, dataset


def create_poly(img_path, strVectorFile, bboxes):
    """
    这个函数是用来创建矩形框面矢量
    :param img_path: 参考遥感影像路径
    :param strVectorFile: 输出shp路径
    :param bboxes: 矩形框坐标列表，例如， [[xmin, ymin, xmax, ymax],[xmin, ymin, xmax, ymax], .......]
    :return:
    """
    im_width, im_height, im_proj, im_geotrans, im_data, dataset = read_img(img_path)
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")  # 为了使属性表字段支持中文
    ogr.RegisterAll()
    strDriverName = "ESRI Shapefile"  # 创建数据，这里创建ESRI的shp文件
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s 驱动不可用！\n", strDriverName)

    oDS = oDriver.CreateDataSource(strVectorFile)  # 创建数据源
    if oDS == None:
        print("创建文件【%s】失败！", strVectorFile)

    # srs = osr.SpatialReference()  # 创建空间参考
    # srs.ImportFromEPSG(4326)  # 定义地理坐标系WGS1984
    srs = osr.SpatialReference(
        wkt=dataset.GetProjection())  # 我在读栅格图的时候增加了输出dataset，这里就可以不用指定投影，实现全自动了，上面两行可以注释了，并且那个proj参数也可以去掉了，你们自己去掉吧
    papszLCO = []
    # 创建图层，创建一个多边形图层,"TestPolygon"->属性表名
    oLayer = oDS.CreateLayer("TestPolygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("图层创建失败！\n")

    '''下面添加矢量数据，属性表数据、矢量数据坐标'''
    # oFieldName = ogr.FieldDefn("FieldName", ogr.OFTString)  # 创建一个叫FieldName的字符型属性
    # oFieldName.SetWidth(100)  # 定义字符长度为100
    # oLayer.CreateField(oFieldName, 1)

    oDefn = oLayer.GetLayerDefn()  # 定义要素
    # 创建单个面
    for bbox in bboxes:
        # if cls > len(cls_dict) - 1:
        #     continue
        oFeatureTriangle = ogr.Feature(oDefn)
        # oFeatureTriangle.SetField(1, "单个面")
        ring = ogr.Geometry(ogr.wkbLinearRing)  # 构建几何类型:线
        ring.AddPoint(bbox[0], bbox[1])  # 添加点01
        ring.AddPoint(bbox[2], bbox[1])  # 添加点02
        ring.AddPoint(bbox[2], bbox[3])  # 添加点03
        ring.AddPoint(bbox[0], bbox[3])  # 添加点04
        yard = ogr.Geometry(ogr.wkbPolygon)  # 构建几何类型:多边形
        yard.AddGeometry(ring)
        yard.CloseRings()

        geomTriangle = ogr.CreateGeometryFromWkt(str(yard))  # 将封闭后的多边形集添加到属性表
        oFeatureTriangle.SetGeometry(geomTriangle)
        oLayer.CreateFeature(oFeatureTriangle)

    oDS.Destroy()
    print("面矢量数据集创建完成！\n")


def create_point(img_path, OutShpFile, Points):
    """
    :param img_path: 参考遥感影像路径
    :param OutShpFile: 输出shp路径
    :param Points: 点矢量的经纬度坐标列表， 例如： [[x1, y1], [x2, y2], ......]
    :return:
    """
    im_width, im_height, im_proj, im_geotrans, im_data, dataset = read_img(img_path)
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")  # 为了使属性表字段支持中文
    ogr.RegisterAll()
    ## 生成点矢量文件 ##
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(OutShpFile)  ## shp文件名称
    srs = osr.SpatialReference()
    srs = osr.SpatialReference(
        wkt=dataset.GetProjection())  # 我在读栅格图的时候增加了输出dataset，这里就可以不用指定投影，实现全自动了，上面两行可以注释了，并且那个proj参数也可以去掉了，你们自己去掉吧
    layer = data_source.CreateLayer("Point", srs, ogr.wkbPoint)  ## 图层名称要与shp名称一致
    field_name = ogr.FieldDefn("Name", ogr.OFTString)  ## 设置属性
    field_name.SetWidth(20)  ## 设置长度
    layer.CreateField(field_name)  ## 创建字段
    field_Longitude = ogr.FieldDefn("Longitude", ogr.OFTReal)  ## 设置属性
    layer.CreateField(field_Longitude)  ## 创建字段
    field_Latitude = ogr.FieldDefn("Latitude", ogr.OFTReal)  ## 设置属性
    layer.CreateField(field_Latitude)  ## 创建字段
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField("Name", "point")  ## 设置字段值
    for Longitude, Latitude in Points:
        feature.SetField("Longitude", str(Longitude))  ## 设置字段值
        feature.SetField("Latitude", str(Latitude))  ## 设置字段值
        wkt = "POINT(%f %f)" % (float(Longitude), float(Latitude))  ## 创建点
        point = ogr.CreateGeometryFromWkt(wkt)  ## 生成点
        feature.SetGeometry(point)  ## 设置点
        layer.CreateFeature(feature)  ## 添加点
    data_source.Destroy()
    print("点矢量数据集创建完成！\n")
