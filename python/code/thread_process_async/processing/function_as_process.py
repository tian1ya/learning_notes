import time
import random
from multiprocessing import Process
import os

"""
    简单逻辑写方法就够来
"""
def task(name):
    s = random.randint(1,10)

    print("pid: {}, name: {}, sleep: {}s".format(os.getpid(), name, s))
    time.sleep(s)


if __name__ == "__main__":
    ps = []
    # 创建5个子进程
    for i in range(5):
        """
            p = Process(target=func, args=(arg1, arg2...))  即可创建一个进程
        """
        p = Process(target=task, args=("p%s" % i, ))
        ps.append(p)
        """
            p.start() 启动一个进程
        """
        p.start()

    # 主进程等待子进程结束
    for p in ps:
        """
        p.join()使得主进程等待子进程执行结束后才退出。主进程不会再子进程结束之前退出
        保证所有的子进程都执行结束
        """
        p.join()