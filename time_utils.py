import datetime
import re

def parse_duration(duration_str):
    """
    文字列 (例: 10m, 1h, 1d) を timedelta に変換します。
    単位がない場合は分として扱います。
    """
    if duration_str.lower() == "無期限":
        return None
    
    match = re.match(r"(\d+)([smhd]?)", duration_str.lower())
    if not match:
        try:
            return datetime.timedelta(minutes=int(duration_str))
        except ValueError:
            return None
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == "s":
        return datetime.timedelta(seconds=value)
    elif unit == "m":
        return datetime.timedelta(minutes=value)
    elif unit == "h":
        return datetime.timedelta(hours=value)
    elif unit == "d":
        return datetime.timedelta(days=value)
    else:
        return datetime.timedelta(minutes=value)

def format_dt(dt):
    return discord.utils.format_dt(dt, style="F")
