import time
import random
from multiprocessing import Process, Pipe

"""
    Queue 只能是一端读取，一端写入数据
    如果是进程两端读取数据的同事，也想再写入数据
    
    Pipe 就是两端都可以进行读写
"""

class P1(Process):

    def __init__(self, pipe):
        self.pipe = pipe
        super(__class__, self).__init__()

    def run(self):
        print("p1 send")
        for i in range(3):
            time.sleep(random.randint(1,9))
            self.pipe.send("p1-%s" % i)
            print("send: p1 -> {}".format("p1-%s" % i))

        print("p1 received")
        for i in range(3):
            i = self.pipe.recv()
            print("recv: p1 <- {}".format(i))

class P2(Process):
    def __init__(self, pipe):
        self.pipe = pipe
        super(__class__, self).__init__()

    def run(self):
        print("p2 send: ")
        for i in range(3):
            self.pipe.send("p2-%s" % i)
            print("p2 -> send {}".format("p2-%s" % i))

        print("p2 recv")
        for i in range(3):
            recv = self.pipe.recv()
            print("p2 <- recv {}".format(recv))

if __name__ == "__main__":
    # Pipe 返回2 个管道，着两个管道分别交给2个进程，
    # 就实现了2 个管道之间的互相通信
    # 也就是说同一个管道Pipe()，产生两个口 pipe1, pipe2
    # 再这两个口中都可以实现读写，再P1进程类中send 得再P2 进程类中可以收到
    # 同样再P2进程类中send 得再P1 进程类中可以收到
    pipe1, pipe2 = Pipe()

    p1 = P1(pipe1)
    p2 = P2(pipe2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

