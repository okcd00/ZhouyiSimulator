# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : 八字推算.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/08/19 00:33:26
#   desc     : 本方案采用当前经纬度进行计算真太阳时，是相对最为准确的推算方法之一
#              因此，与不包含地理位置的计算方式相比，在时柱部分可能会因偏移有所偏差
#   reference: https://www.zhihu.com/people/zhang-liang-de-12@张亮德
# ==========================================================================

import math
import ephem
from typing import Union
from datetime import datetime, timedelta

# 天干和地支的周期表
天干 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"] #十天干
地支 = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"] #十二地支


def 获取当前地点的时区偏移() -> float:
    current_time = datetime.now()

    # 获取UTC时间
    utc_time = datetime.utcnow()

    # 计算小时差
    time_zone_offset = round((current_time - utc_time).seconds / 3600.0,2)

    # 以0.5为基准进行舍入操作:
    if time_zone_offset >= 0 : 
        time_zone_offset = math.floor(time_zone_offset / 0.5 + 0.5) * 0.5
    else: 
        time_zone_offset = math.ceil(time_zone_offset / 0.5 - 0.5) * 0.5
    return time_zone_offset


def 计算本地经纬度的真太阳时(
        观测日期: datetime,
        观测纬度: Union[str, float]=39.90000,
        观测经度: Union[str, float]=116.40000) -> datetime:
    """
    根据观测者的经纬度和时间，计算真太阳时。

    返回:
    datetime: 调整后的真太阳时，已考虑观测者的经纬度和时区偏移量。
    """
    # 计算当前时区偏移 time_zone_offset
    time_zone_offset = 获取当前地点的时区偏移()    

    # 将观测者的纬度和经度转换为 ephem 格式
    lat, lon = ephem.degrees(str(观测纬度)), ephem.degrees(str(观测经度))

    # 创建一个新的观测者对象
    observer = ephem.Observer()
    observer.lat, observer.lon = lat, lon

    # 将输入的当地时间转换为ephem的Date格式
    date_0 = 观测日期 - timedelta(hours=time_zone_offset)# 将本地时间转换为UTC+0时间
    utc_date = ephem.Date(date_0)

    # 设置观测者的日期和时间
    observer.date = utc_date

    # 计算太阳的位置
    sun = ephem.Sun(observer)

    # 计算本地太阳正午时间 (在给定日期太阳通过当地子午线的时间) 
    next_noon = observer.next_transit(sun).datetime() + timedelta(hours=time_zone_offset)

    # 计算钟表正午时间
    clock_noon = next_noon.replace(hour=12, minute=0, second=0, microsecond=0)

    # 计算太阳正午和钟表正午之间的差值
    time_diff = (clock_noon - next_noon).total_seconds() / 3600.0

    # 调整本地时间以获得真太阳时(ephem通常已经考虑光行差)
    true_solar_time = 观测日期 + timedelta(hours=time_diff)
    return true_solar_time


def 计算年干支_年柱(
        观测日期: datetime,
        观测纬度: Union[str, float,int]=0,
        观测经度: Union[str, float,int]=0) -> str:
    """
    计算指定经纬度在特定时间的年干支。

    返回:
    str: 指定时间的年干支，范围从"甲子"到"癸亥"。
    """
    # 参考 2000 年立春时间: 2000年是庚辰年
    参考日期 = datetime(2000, 2, 4, 20, 40, 24)  

    # 如已指定经纬度，则计算真太阳时:
    if 观测纬度 != 0 or 观测经度 != 0 : 
        观测日期 = 计算本地经纬度的真太阳时(观测日期, 观测纬度, 观测经度)
    后推天数 = (观测日期 - 参考日期).days  # 计算指定日期与 2000 年 2 月 4 日之间的间隔天数

    # 回归年的长度: 365.24218968 - 0.0000000616*(t-2000)
    年均天数 = 365.24218968 - 0.0000000616 * (后推天数 / 365.24218968 / 2)  # 回归年的平均长度
    后推年数 = math.floor(后推天数 / 年均天数)  #算指定日期与2000年2月4日之间的年数

    # 2000年是庚辰年
    天干地支 = 天干[(后推年数 + 6) % 10] + 地支[(后推年数 + 4) % 12]
    return 天干地支


def 计算月干支_月柱(
        观测日期: datetime,
        观测纬度: Union[str, float]=39.90000, 
        观测经度: Union[str, float]=116.40000)-> str:
    """
    计算指定经纬度在特定时间的月干支。

    返回:
    str: 指定时间的月干支，范围从"甲子"到"癸亥"。
    """
    # 创建观察者的地球位置对象
    observer = ephem.Observer()
    observer.lat, observer.lon = ephem.degrees(str(观测纬度)), ephem.degrees(str(观测经度))  # 纬度，经度,需要转换为弧度

    # 计算当前时区偏移hour_difference
    时区偏移 = 获取当前地点的时区偏移() 

    # 解析日期字符串
    观测日期 = ephem.Date(观测日期 - timedelta(hours=时区偏移))  # 将本地观测日期转换为 UTC+0 时间
    观测日期 = datetime.strptime(str(观测日期), "%Y/%m/%d %H:%M:%S")
    
    # 创建观察者对象
    observer.date = 观测日期
    sun = ephem.Sun(observer)
    
    # 获取太阳的视黄经 (转换为度) :
    # 求太阳的视赤经&视赤纬 (epoch 设为所求时间就是视赤经&视赤纬) 
    equ = ephem.Equatorial(sun.ra, sun.dec, epoch=观测日期)  
    
    # 赤经赤纬转到黄经黄纬，对视黄经修正到 0 到 360 度的范围
    黄道经度 = (float(ephem.Ecliptic(equ).lon) * 180.0 / ephem.pi) % 360.0 
    
    # 己卯月始于3月5日 14:42:40惊蛰
    参考日期 = datetime(2000, 3, 5, 14, 42, 40)  
    后推天数 = (观测日期 - 参考日期).days
    
    # 从己卯月开始的第几个月
    月均天数 = (365.24218968 - 0.0000000616 * (后推天数 / 365.24218968 / 2)) / 12
    后推月数 = int(后推天数 / 月均天数)  
    
    # 推算月支与黄经的对应关系
    精确地支序号 = (int(((黄道经度 - 15) % 360) / 30.0) + 4) % 12  
    
    # 月支序数
    近似月支序数 = (后推月数 + 3) % 12  
    
    # 修正增量值(t12_diff) = 精确地支序号(solar_longitude_mi) - 近似地支序号(moon_num_id)
    地支修正偏移 = (精确地支序号 - 近似月支序数 + 12) % 12 
    
    # 月干支值域修正: 偏移只有 -6 ~ +6
    后推月数 += 地支修正偏移 if 地支修正偏移 < 6 else 地支修正偏移 - 12 # 月支序数修正
    天干地支 = 天干[(后推月数 + 5) % 10] + 地支[(后推月数 + 3) % 12]
    return 天干地支  # 返回月干支


def 计算日干支_日柱(
        观测日期: datetime,
        观测纬度: Union[str, float]=39.90000,
        观测经度: Union[str, float]=116.40000) -> str:
    """
    计算指定经纬度在特定时间的日干支。

    返回:
    str: 指定时间的日干支，范围从"甲子"到"癸亥"。
    """
    # 参考 1900 年 1 月 1 日是甲戌日: 日的分隔点是真太阳时 00:00:00
    参考时间 = datetime(1900, 1, 1, 0, 0, 0, 0)  

    # 根据观测者的经纬度和时间，计算真太阳时 (ephem通常已经考虑光行差):
    真太阳时 = 计算本地经纬度的真太阳时(观测日期, 观测纬度, 观测经度)
    后推天数 = (真太阳时 - 参考时间).days

	# 基于参考日期后推天干地支下标
    天干地支 = 天干[(后推天数 + 0) % 10] + 地支[(后推天数 + 10) % 12]
    return 天干地支


def 计算时干支_时柱(
        观测日期: datetime,
        观测纬度: Union[str, float]=39.90000,
        观测经度: Union[str, float]=116.40000) -> str:
    """
    计算指定经纬度在特定时间的时干支。

    返回:
    str: 指定时间的时干支，范围从"甲子"到"癸亥"。
    """
    # 根据观测者的经纬度和时间，计算真太阳时 (ephem通常已经考虑光行差):  
    真太阳时 = 计算本地经纬度的真太阳时(观测日期, 观测纬度, 观测经度)
    
    # 参考 1983-12-21 23:42:15 是甲子时: 甲子月 甲申日 甲子时 作为真太阳时起始点，子时的起点是真太阳时 23:00:00
    参考时辰 = datetime(1983, 12, 21, 23, 42, 15)  
     
    # 已经过去多少个时辰
    后推时辰数 = round((真太阳时 - 参考时辰).total_seconds() / 3600.0 / 2.0)
    
    # 时干支值域修正: 偏移只有 -6 ~ +6
    时干支修正偏移 = ((((真太阳时.hour + 1) // 2 - 后推时辰数) % 12) + 12) % 12 
    后推时辰数 += 时干支修正偏移 if 时干支修正偏移 < 6 else 时干支修正偏移 - 12

	# 基于参考日期后推天干地支下标
    天干地支 = 天干[(后推时辰数 + 0) % 10] + 地支[(后推时辰数 + 0) % 12]
    return 天干地支


if __name__ == "__main__":
    观测时间 = '2020-01-01 01:01:01'  # 示例时间
    经纬度 = '116.40000,39.90000'  # 北京市东城区

    观测经度, 观测纬度 = 经纬度.split(',')
    观测日期 = datetime.strptime(观测时间, '%Y-%m-%d %H:%M:%S')
    年干支 = 计算年干支_年柱(观测日期, 观测纬度, 观测经度)
    月干支 = 计算月干支_月柱(观测日期, 观测纬度, 观测经度)
    日干支 = 计算日干支_日柱(观测日期, 观测纬度, 观测经度)
    时干支 = 计算时干支_时柱(观测日期, 观测纬度, 观测经度)
    
    print("经纬度: ", 经纬度)
    print(观测时间 + " 对应的年柱: " + 年干支)
    print(观测时间 + " 对应的月柱: " + 月干支)
    print(观测时间 + " 对应的日柱: " + 日干支)
    print(观测时间 + " 对应的时柱: " + 时干支)
    print("因此，该时间地点对应的八字为: " + 年干支 + 月干支 + 日干支 + 时干支)
