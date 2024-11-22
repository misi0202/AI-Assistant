import time
from functools import wraps

def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)
        end_time = time.time()    # 记录结束时间
        elapsed_time = end_time - start_time  # 计算消耗时间
        print(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to execute.")
        return result
    return wrapper
