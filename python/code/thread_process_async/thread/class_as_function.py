import threading

class A(threading.Thread):
    def run(self):
        for i in range(5):
            print("%s --> %s" % (self.name, i))

if __name__=="__main__":
    a1 = A()
    a2 = A()

    a1.start()
    a2.start()

    a1.join()
    a2.join()
