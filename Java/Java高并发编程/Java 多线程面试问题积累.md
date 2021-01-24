###Java 多线程问题积累

参考博客 `https://blog.csdn.net/ll666634/article/details/78615505`

---

1. a, b, c 三个线程，如何保证b在a完成后执行，c在b完成后执行。

   使用join方法，thread.join()，把指定的线程加入到当前线程，可以讲俩个交替执行的线程合并为顺序执行的线程，例如在a的线程中调用了线程a得join方法，那么会在a线程执行结束之后才会执行线程b。

```java
private static void method01() {
        Thread t1 = new Thread(() -> {
            System.out.println("t1 is finished");
        });
        Thread t2 = new Thread(() -> {
            try {
                t1.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("t2 is finished");
        });
        Thread t3 = new Thread(() -> {
            try {
                t2.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("t3 is finished");
        });
        t3.start();
        t2.start();
        t1.start();
}
```

2. 在Java 中Lock 接口比sychronized 块的优势是什么？

* Lock 实现了比sychronizedLock提供了无条件的、可轮询的(tryLock方法)、定时的(tryLock带参方法)、可中断的(lockInterruptibly)、可多条件队列的(newCondition方法)锁操作,另外Lock的实现类基本都支持非公平锁(默认)和公平锁，synchronized只支持非公平锁,在大部分情况下，非公平锁是高效的选择.
* 看lock 的笔记

3. wait和sleep 有什么不同

* wait 会释放锁，sleep不会，wait 通常用于线程之间的交互，sleep 用于暂停执行，一直会持有锁

4. Java 实现队列阻塞 ： 可以用synchronized 和 wait()和notify()方法来实现阻塞队列 实现

```java
public class MyBlocingQueueSync<T> {

    private List list = new ArrayList<T>();
    private Integer MAX_NUM = 10;
    public T take(){
        while (true){
            synchronized (list){
                if (list.size() >0){
                    T e = (T) list.remove(0);
                    System.out.println("get first element " + e);
                    return e;
                }
            }
        }
    }
    // 效率会比较低，当 list 满了的时候，while 循环会一直轮询，等待元素被取走，才能新添加
    public void put(T value){
        while (true){
            synchronized (list){
                if (list.size() < MAX_NUM){
                    System.out.println("add value "+ value);
                    list.add(value);
                    return;
                }
            }
        }
    }

    //---------------------  wait 和 notify 方法 -------------------------
    public synchronized T take1(){
        while (list.size() == 0){
            try {
                wait();
                System.out.println("list none element");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        T o = (T) list.remove(0);
        System.out.println("get: " + o);
        notifyAll();
        return o;
    }
    public synchronized void put1(T e){
        while (list.size() == MAX_NUM){
            try {
                wait();
                System.out.println("list is full");
            } catch (InterruptedException e1) {
                e1.printStackTrace();
            }
        }
        list.add(e);
        System.out.println("add: "+e);
        notifyAll();
    }
    public static void main(String[] args) {
        MyBlocingQueueSync queueSync = new MyBlocingQueueSync();
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 20; i++) {
                queueSync.put1(i);
            }
        });
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                Integer o = (Integer) queueSync.take1();
            }
        });
        t1.start();
        t2.start();
    }
}
```























