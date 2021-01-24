import threading

def run(name):
    for i in range(3):
        print("%s --> %s" % (name, i))

if __name__=="__main__":
    # 创建2 个线程
    t1 = threading.Thread(target=run, args=("t1", ))
    t2 = threading.Thread(target=run, args=("t2", ))

    # 开始执行
    t1.start()
    t2.start()

    # 主线程等待t1线程结束
    t1.join()

    # 主线程等待t1线程结束，之后主线程再等待t2 结束
    t2.join()