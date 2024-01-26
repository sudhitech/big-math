import time
from decimal import Decimal

def time_task(func):
    start = time.perf_counter()
    res = func()
    end = time.perf_counter()
    time_taken = Decimal(end)-Decimal(start)
    return res, time_taken

def time_task_wrapper(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        time_taken = Decimal(end)-Decimal(start)
        return res, time_taken
    return wrapper