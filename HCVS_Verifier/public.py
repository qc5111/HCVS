import datetime
import functools
import threading


def mtsToDateTime(mts):
    timestamp = mts // 1000  # 转换为秒级时间戳
    dt = datetime.datetime.fromtimestamp(timestamp)
    uk_dt = dt.strftime("%d-%m-%Y %H:%M:%S")  # 英国日期时间格式
    return uk_dt


def thread_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # print("Executing function:", func.__name__)
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper
