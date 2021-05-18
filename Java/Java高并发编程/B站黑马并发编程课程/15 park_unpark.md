```java
public class ParkUnpark {

    /*
        LockSupport.park() 暂停当前线程
        LockSupport.unpark() 恢复某个线程的运行

     */
    public static void main(String[] args) {
        Thread t = new Thread(() -> {
            System.out.println("start,,,");
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            System.out.println("park...");

            LockSupport.park();
            // 子线程在这里暂停了，知道这个线程启动之后才会继续往下执行，对应的状态还是 WAIT 状态

            System.out.println("subThread resume");
        });

        t.start();
        System.out.println("主线程中将子线程重新启动");
        LockSupport.unpark(t);
        /*
            既可以在 park 之前调用，也可以在 park 之后调用
            在 park 之前调用了 unpark，那么在线程未来 unpark 线程

            unpark 可以很精确的唤醒某个线程，而 notify/notifyall 并不能

            wait notify/notifyall 必须配合 object monitor 一起使用，
            而 park unpark 不需要

            park/unpark 则不需要，是以线程为单位来 [阻塞]和【唤醒】 线程，
            而notify 只能随机唤醒一个等待线程，notifyAll 是唤醒所有的等待线程，就不那么精确

            park/unpark 可以先 unpark， 而 wait notify 不能先 notify
            
            wait和notify都是Object中的方法,在调用这两个方法前必须先获得锁对象，这限制了其使用场合:只能在同步代码块中。
            使用LockSupport的话，我们可以在任何场合使线程阻塞，同时也可以指定要唤醒的线程，相当的方便
         */
    }
}
```

