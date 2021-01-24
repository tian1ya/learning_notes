import time
from multiprocessing import Process, Lock

"""
    执行多进程执行任务过程中，如果需要对同一个资源进程访问，为了防止一个进程操作的资源
    不被另外一个进程篡改，可以使用Lock 对齐进程加锁互斥，也就是一个进程再写的时候
    不允许另一个进程读，或者一个进程读的时候，不允许另一个写，必须是读完写，
    或者写完读
"""

class P1(Process):
    def __init__(self, lock, fp):
        self.lock = lock
        self.fp = fp
        super(__class__, self).__init__()

    def run(self):
        print("p1 lock status", self.lock)
        while self.lock:
            for i in range(5):
                f = open(self.fp, "a+")
                f.write("p1 - %s\n" % i)
                f.close()


class P2(Process):
    def __init__(self, lock, fp):
        self.lock = lock
        self.fp = fp
        super(__class__, self).__init__()

    def run(self):
        # 只有一个进程可以进入
        print("p2 lock status", self.lock)
        while self.lock:
            for i in range(5):
                f = open(self.fp, "a+")
                f.write("p2 - %s\n" % i)
                f.close()

if __name__=="__main__":
    # 进程锁
    lock = Lock()
    fp = "Users/xuxliu/Desktop/test.txt"
    p1 = P1(lock, fp)
    p2 = P2(lock, fp)

    p1.start()
    p2.start()

    p1.join()
    p2.join()


