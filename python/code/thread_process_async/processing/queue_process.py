import time
import random
from multiprocessing import Process, Queue

"""
    如果多个进程之间需要通信，可以使用队列，Pythono 中使用Queue 模块
    一边读，一边写
"""

class P1(Process):

    def __init__(self, queue):
        self.queue = queue
        # super(Process，self).__init__
        # 或者 super(__class__，self).__init__(参数)
        # 或者 Process.__init__(参数)

        super(__class__, self).__init__()

    def run(self):
        print("P put....")
        for i in range(5):
            time.sleep(random.randint(1,3))
            self.queue.put(i)
            print("put: P1 -> {}".format(i))

class P2(Process):
    def __init__(self, queue):
        self.queue = queue
        super(__class__, self).__init__()

    def run(self):
        print("P2 read....")
        while 1:
            i = self.queue.get()
            print("get: P2 <- {}".format(i))

if __name__ == "__main__":
    # 创建多进程队列 使之可通信
    queue = Queue()

    # 创建进程
    p1 = P1(queue)
    p2 = P2(queue)

    # 启动进程
    p1.start()
    p2.start()

    # 主进程等待P1 子进程结束
    p1.join()

    #p2 是死循环，只能强制结束
    p2.terminate()



