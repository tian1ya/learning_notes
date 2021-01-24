from concurrent.futures import ProcessPoolExecutor
import time

def task(t):
    nu = 0
    for i in range(t):
        nu += i

    return nu

if __name__=="__main__":

    now = time.time()
    pool = ProcessPoolExecutor(max_workers = 5)
    # equivalent to map(fn, iter)
    # # 批量任务 放入进程池执行
    result = pool.map(task, [1000000000, 2000000000, 3000000000,1000000000, 2000000000, 3000000000])

    # for it in result:
    #     print(it)

    print(time.time() - now)

    now = time.time()
    i = map(task, [1000000000, 2000000000, 3000000000,1000000000, 2000000000, 3000000000])
    # for it in i:
    #     print(it)

    print(time.time() - now)
