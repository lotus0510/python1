import time
def timer(func):
    def wrapper():
        start = time.time()
        res=func()
        end = time.time()
        return res,end - start
    return wrapper

@timer
def run_loop():
    for i in range(10000):
        print(i)

times=run_loop()
print(f"執行時間: {times} 秒")