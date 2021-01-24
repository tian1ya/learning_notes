import time
import random
from multiprocessing import Process, Pool
import os

"""
    进程虽然可以提高运行效率，单同事不建议无限制得创建进程,过多的进程会给操作系统的调用
    和上下文得切换带来更大的负担，进程越来越多也有可能导致效率低下
    
    理论来讲,同时执行的进程数与CPU 核心相等，才会保证最高效率得运行效率
"""

def task(name):
    s = random.randint(1,5)
    print("pid: {}, name: {}, sleep: {}s ...".format(os.getpid(), name, s))
    time.sleep(s)

if __name__=="__main__":
    # 大小为5 得进程池，同一时刻最多只有5个在执行
    pool = Pool(5)

    # 运行10个任务,按照上面的定义，同一时刻只能跑10 个进程
    for i in range(10):
        pool.apply_async(task, ("p-%s" % i, ))

    # close() 关闭进程池，标识不在添加新的进程，之后才能run
    pool.close()
    pool.join()

    # 一般在多进程执行多个任务的时候，是会使用进程池，避免资源的浪费