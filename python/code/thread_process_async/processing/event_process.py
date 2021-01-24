import time
import random
from multiprocessing import Process, Event, Queue

"""
    需要在多进程之间控制某些事件得开始和停止，也就是在多进程之间保持同步信号信息
    不同进程可以对通一个时间进程控制，并且这件事情的状态没个状态都是可知道得
"""

class P1(Process):

    def __init__(self, queue, event):
        self.queue = queue
        self.event = event
        super(__class__, self).__init__()

    def run(self):
        # 阻塞该进程，直到主进程发来信号，才继续执行
        self.event.wait()
        print("p1 put")
        for i in range(3):
            time.sleep(random.randint(1,4))
            self.queue.put(i)

class P2(Process):
    def __init__(self, queue, event):
        self.queue = queue
        self.event = event
        super(__class__, self).__init__()

    def run(self):
        self.event.wait()
        print("p2 read")

        while True:
            print("p2 get <- %s" % self.queue.get())


if __name__ == "__main__":
    queue = Queue()
    event = Event()

    p1 = P1(queue, event)
    p2 = P2(queue, event)

    # p1, p2 线程开始
    p1.start()
    p2.start()

    # 主线程将 p1, p2 线程阻塞3s
    print("sleep....")
    time.sleep(3)

    # 给 p1, p2 线程发送信息，p1, p2 线程开始继续执行被events 阻塞的程序
    event.set()

    # 主线程等待 p1 线程结束
    p1.join()
    p2.terminate()

#     程序先输出  sleep.... 因为p1， p2 再start 之后，被event 阻塞主了，无法执行
#     3秒后， 主线程给p2，p1 发送消息，让其开始执行
#  event 可以控制进程之间的同步问题

