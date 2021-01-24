from concurrent.futures import ProcessPoolExecutor

def task(t):
    nu = 0
    for i in range(t):
        nu += i

    return nu

if __name__=="__main__":
    pool = ProcessPoolExecutor(max_workers=5)

    result = []
    result.append(pool.submit(task, 1))
    result.append(pool.submit(task, 10))
    result.append(pool.submit(task, 100))
    result.append(pool.submit(task, 1000))

    for i in result:
        # 获取没个进程得结果
        print(i.result())
