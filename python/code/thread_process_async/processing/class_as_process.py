import os
import random
import time
from multiprocessing import Process
"""
    复杂逻辑写类
"""
class P(Process):
    """
        这里需要重写 run 方法，当执行，start 的时候，就会在这里执行它
    """
    def run(self):
        s = random.randint(1,10)
        print("pid: {}, name: {}, sleep: {}s".format(os.getpid(), self.name, s))
        time.sleep(s)


if __name__ == '__main__':
    ps = []
    for i in range(5):
        p = P()
        ps.append(p)
        p.start()
    for p in ps:
        p.join()