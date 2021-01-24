import time
import random
from multiprocessing import Process, Queue, Condition

"""
    Condition 买足 Lock + Event 结合得场景， 再加锁得同事可以更具逻辑条件让其它进程等待或者重新
    唤醒
    这也是一个同步操作
"""
def producer(queue, condition):
    while 1:
        # 获取锁
        if condition.acquire():
            if not queue.empty():
                # 等待其他进程唤醒,锁住
                condition.wait()
            i = random.randint(1, 10)
            queue.put(i)
            print("producer -> %s" % i)
            # 唤醒其它进程
            condition.notify_all()

            # 释放锁
            condition.release()
            time.sleep(1)

def consumer(queue, condition):
    while 1:
        # 获取锁
        if condition.acquire():
            if not queue.empty():
                # 等待其他进程唤醒,锁住
                condition.wait()
            i = random.randint(1, 10)
            get = queue.get()
            print("consumer -> %s" % get)
            # 唤醒其它进程
            condition.notify_all()

            # 释放锁
            condition.release()
            time.sleep(1)

if __name__=="__main__":
    queue = Queue()
    condition = Condition()

    p1 = Process(target=producer, args=(queue, condition))
    p2 = Process(target=producer, args=(queue, condition))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

