import re
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo


# 1717245853
# 10位的是秒时间戳

# 1717245853000
# 13位的是毫秒时间戳



# 将时间戳转换为iso国际标准的时间（时区为东八区）
# 格式为 2023-05-26T09:00:00Z
def transTimestampToTime(timestamp):# 传入秒时间戳
    # 直接将时间戳转换为上海时区的datetime对象
    # 注意这里直接在转换时指定了时区为Asia/Shanghai
    dt_shanghai = datetime.fromtimestamp(timestamp, ZoneInfo("Asia/Shanghai"))
    # 获取时区偏移量，并格式化为带有冒号的形式
    offset = dt_shanghai.strftime('%z')
    offset_with_colon = f'{offset[:-2]}:{offset[-2:]}'
    # 格式化时间，并手动添加格式化的时区偏移量
    formatted_time = dt_shanghai.strftime('%Y-%m-%dT%H:%M:%S') + offset_with_colon
    return formatted_time



# 将iso标准时间改为时间戳，单位为秒
def transTimeToTimestamp(time_str):
    # 使用正则表达式匹配ISO 8601时间字符串中的时区偏移部分
    match = re.search(r'([+-]\d{2}):?(\d{2})$', time_str)
    
    if match:
        # 提取时区偏移的小时和分钟
        hours, minutes = map(int, match.groups())
        # 应用正确的时区偏移
        dt = datetime.fromisoformat(time_str.replace(match.group(), ""))
        dt = dt.replace(tzinfo=timezone(timedelta(hours=hours, minutes=minutes)))
    else:
        # 如果没有找到时区偏移，则假设为UTC
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
    
    # 转换为UTC时间
    dt_utc = dt.astimezone(timezone.utc)
    
    # 转换为时间戳
    timestamp = dt_utc.timestamp()

    return int(timestamp)


# 将时间戳转换为iso国际标准的时间（时区为东八区）
# 格式为 2023-05-26T09:00:00Z
def calculateTimeDiff(timestamp1,timestamp2):# 传入秒时间戳
    # 将时间戳转换为datetime对象
    dt1 = datetime.fromtimestamp(timestamp1)
    dt2 = datetime.fromtimestamp(timestamp2)
    
    # 计算时间差
    time_diff = dt2 - dt1
    
    # 计算小时、分钟和秒
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # 格式化时间差为"HH:MM:SS"的形式
    formatted_diff = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return formatted_diff