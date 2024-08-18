# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : 八字推算.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/08/19 00:33:26
#   desc     : 本方案采用当前经纬度进行计算真太阳时，是相对最为准确的推算方法之一
#              因此，与不包含地理位置的计算方式相比，在时柱部分可能会因偏移有所偏差
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
        date_local: datetime,
        observer_latitude: Union[str, float]=39.90000,
        observer_longitude: Union[str, float]=116.40000) -> datetime:
    """
    根据观测者的经纬度和时间，计算真太阳时。

    参数：
    date_local (datetime): 观察时间
    observer_latitude (str): 观测者的纬度，以度为单位。
    observer_longitude (str): 观测者的经度，以度为单位。

    返回：
    datetime: 调整后的真太阳时，已考虑观测者的经纬度和时区偏移量。
    """
    # 根据观测者的经纬度和时间，计算真太阳时:
    # 计算当前时区偏移time_zone_offset
    time_zone_offset = 获取当前地点的时区偏移()    

    # 将观测者的纬度和经度转换为 ephem 格式
    lat, lon = ephem.degrees(str(observer_latitude)), ephem.degrees(str(observer_longitude))

    # 创建一个新的观测者对象
    observer = ephem.Observer()
    observer.lat, observer.lon = lat, lon

    # 将输入的当地时间转换为ephem的Date格式
    date_0 = date_local - timedelta(hours=time_zone_offset)# 将本地时间转换为UTC+0时间
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
    true_solar_time = date_local + timedelta(hours=time_diff)
    return true_solar_time


def 计算年干支_年柱(
        date: datetime,
        observer_latitude: Union[str, float,int]=0,
        observer_longitude: Union[str, float,int]=0) -> str:
    # 2000年立春时间
    startDate = datetime(2000, 2, 4, 20, 40, 24)  

    #如果指定了站点则计算真太阳时间:
    if observer_latitude != 0 or observer_longitude != 0 : 
        date = 计算本地经纬度的真太阳时(date,observer_latitude,observer_longitude)
    diff_days = (date - startDate).days  # 计算指定日期与2000年2月4日之间的间隔天数

    # 回归年的长度：365.24218968 - 0.0000000616*(t-2000)
    day_per_year = 365.24218968 - 0.0000000616 * (diff_days / 365.24218968 / 2)  # 回归年的平均长度
    years = math.floor(diff_days / day_per_year)  #算指定日期与2000年2月4日之间的年数

    # 2000年是庚辰年
    gan_index = (years + 6) % 10  # 加6位
    zhi_index = (years + 4) % 12  # 加4位
    gan_zhi = 天干[gan_index] + 地支[zhi_index]
    return gan_zhi


def 计算月干支_月柱(
        date: datetime,
        latitude: Union[str, float]=39.90000, 
        longitude: Union[str, float]=116.40000)-> str:
    """
    计算指定站点在特定时间的月干支。

    参数:
    date (datetime): 观察时间
    latitude (str): 观测者的纬度，以度为单位。
    longitude (str): 观测者的经度，以度为单位。

    返回:
    str
        指定时间的月干支，范围从"甲子"到"癸亥"。
    """
    # 创建观察者的地球位置对象
    observer = ephem.Observer()
    observer.lat, observer.lon = ephem.degrees(str(latitude)), ephem.degrees(str(longitude))  # 纬度，经度,需要转换为弧度

    # 计算当前时区偏移hour_difference
    hour_difference = 获取当前地点的时区偏移() 

    # 解析日期字符串
    date_local = date
    date_0 = date_local - timedelta(hours=hour_difference)# 将本地时间转换为UTC+0时间
    date = ephem.Date(date_0)
    
    # 创建观察者对象
    observer.date = date
    sun = ephem.Sun(observer)
    
    # 获取太阳的视黄经 (转换为度) :
    # 求太阳的视赤经视赤纬 (epoch 设为所求时间就是视赤经视赤纬) 
    equ = ephem.Equatorial(sun.ra, sun.dec, epoch=date)  
    
    # 赤经赤纬转到黄经黄纬
    ecl_v = ephem.Ecliptic(equ) 
    
    # 对视黄经进行修正为 0 到 360 度的范围
    solar_longitude = (float(ecl_v.lon) * 180.0 / ephem.pi) % 360.0 
    
    # 己卯月始于3月5日 14:42:40惊蛰
    start_date = datetime(2000, 3, 5, 14, 42, 40)  
    diff_days = (date_local - start_date).days
    day_per_moon = (365.24218968 - 0.0000000616 * (diff_days / 365.24218968 / 2)) / 12
    
    # 从己卯月开始的第几个月
    moon_num = int(diff_days / day_per_moon)  
    
    # 推算月支与黄经的对应关系
    solar_longitude_mi = (int(((solar_longitude - 15) % 360) / 30.0) + 4) % 12  
    
    # 月支序数
    moon_num_id =  (moon_num + 3) % 12  
    
    # 修正增量值(t12_diff)=精确地支序号(solar_longitude_mi)-近似地支序号(moon_num_id)
    t12_diff = (solar_longitude_mi - moon_num_id + 12) % 12 
    
    # 修正：当 solar_longitude_mi 和 moon_num_id 分别居于头尾的偏差
    # 如果 t12_diff 大于等于 6，表示实际差值应为负数，因此再减去 12
    if t12_diff >= 6:
        t12_diff -= 12
    moon_num += t12_diff # 月支序数修正
    gan_index = (moon_num + 5) % 10  # 加5位
    zhi_index = (moon_num + 3) % 12  # 加3位
    gan = 天干[gan_index]  # 天干序列获取
    zhi = 地支[zhi_index]   # 地支序列获取
    return gan + zhi  # 返回月干支


def 计算日干支_日柱(
        date_local: datetime,
        observer_latitude: Union[str, float]=39.90000,
        observer_longitude: Union[str, float]=116.40000) -> str:
    """
    参数:
    date (datetime): 观察时间
    latitude (str): 观测者的纬度，以度为单位。
    longitude (str): 观测者的经度，以度为单位。
    """
    # 日的分隔点是真太阳时 00:00:00
    start_date = datetime(1900, 1, 1, 0, 0, 0, 0)  

    # 根据观测者的经纬度和时间，计算真太阳时(ephem通常已经考虑光行差):
    true_solar_time = 计算本地经纬度的真太阳时(date_local,observer_latitude,observer_longitude)
    difference_in_days = (true_solar_time - start_date).days

	# 1900年1月1日是甲戌日:
    gan_index = (difference_in_days + 0) % 10  # 加0位
    zhi_index = (difference_in_days + 10) % 12  # 加10位
    gan_zhi = 天干[gan_index] + 地支[zhi_index]
    return gan_zhi


def 计算时干支_时柱(
        date_local: datetime,
        observer_latitude: Union[str, float]=39.90000,
        observer_longitude: Union[str, float]=116.40000) -> str:
    """
    根据观测者的经纬度和时间，计算真太阳时。

    参数:
    date (datetime): 观察时间
    latitude (str): 观测者的纬度，以度为单位。
    longitude (str): 观测者的经度，以度为单位。

    返回：
    datetime: 调整后的真太阳时，已考虑观测者的经纬度和时区偏移量。
    """
    # 根据观测者的经纬度和时间，计算真太阳时 (ephem通常已经考虑光行差):  
    true_solar_time = 计算本地经纬度的真太阳时(date_local,observer_latitude,observer_longitude)
    
    # 甲子月 甲申日 甲子时 作为真太阳时起始点
    start_time_period = datetime(1983, 12, 21, 23, 42, 15)  
     
    # 已经过去多少个时辰
    total_time_periods = round((true_solar_time - start_time_period).total_seconds() / 3600.0/ 2.0)
    
    # 子时的起点是真太阳时23:00:00
    total_time_correction = ((((true_solar_time.hour + 1) // 2 - total_time_periods) % 12) + 12) % 12 
    if total_time_correction >= 6:
        total_time_correction -= 12
    total_time_periods += total_time_correction

	# 1983-12-21 23:42:15 是甲子时:
    gan_index = (total_time_periods + 0) % 10  # 加0位
    zhi_index = (total_time_periods + 0) % 12  # 加0位
    gan_zhi = 天干[gan_index] + 地支[zhi_index]
    return gan_zhi


if __name__ == "__main__":
    观测时间 = '1994-05-04 11:30:00'  # 示例时间

    经纬度 = '116.40000,39.90000'  # 北京市东城区
    # 经纬度 = '114.328710,29.827230'  # 	湖北省咸宁市咸安区

    观测经度, 观测纬度 = 经纬度.split(',')
    时间 = datetime.strptime(观测时间, '%Y-%m-%d %H:%M:%S')
    年干支 = 计算年干支_年柱(时间, 观测纬度, 观测经度)
    月干支 = 计算月干支_月柱(时间, 观测纬度, 观测经度)
    日干支 = 计算日干支_日柱(时间, 观测纬度, 观测经度)
    时干支 = 计算时干支_时柱(时间, 观测纬度, 观测经度)
    
    print("经纬度: ", 经纬度)
    print(观测时间 + " 对应的年柱: " + 年干支)
    print(观测时间 + " 对应的月柱: " + 月干支)
    print(观测时间 + " 对应的日柱: " + 日干支)
    print(观测时间 + " 对应的时柱: " + 时干支)
    print("因此，该时间地点对应的八字为: " + 年干支 + 月干支 + 日干支 + 时干支)
