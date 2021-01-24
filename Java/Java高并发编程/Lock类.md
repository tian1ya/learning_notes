### Lock

---

```
import java.util.concurrent.locks.Lock;
```

Lock是synchronized的扩展版，Lock提供了无条件的、可轮询的(tryLock方法)、定时的(tryLock带参方法)、可中断的(lockInterruptibly)、可多条件队列的(newCondition方法)锁操作。另外Lock的实现类基本都支持非公平锁(默认)和公平锁，synchronized只支持非公平锁，当然，在大部分情况下，非公平锁是高效的选择。多线程安全面前可以使用 sychronized关键字解决，对于线程得协作，可以使用 Object.wait()和 Object.notify()，Jdk1.5之后使用Lock来实现与上述相同的功能，并且优于他们，在1.6的jdk中对sychronized做优化，二者的性能差距不大。

#### 为什么出现Lock

---

sychronized修饰的代码块，当获得了锁，那么其它线程只能一直等下去，直到这个代码块执行结束或者运行过程中抛出异常，而不能手动释放锁，也就是在两种情况下，sychronized修饰的代码块会释放锁：

* 获取锁得线程执行完该代码
* 执行时候发生异常，JVM自动释放锁。

---

### Lock 类接口

```
public interface Lock {
    //用来获取锁。如果锁已被其他线程获取，则进行等待。
    void lock();
    
   // 当通过这个方法去获取锁时，如果线程正在等待获取锁，则这个线程能够响应中断，即中断线程的等待状态
    void lockInterruptibly() throws InterruptedException;
    
    //它表示用来尝试获取锁，如果获取成功，则返回true，如果获取失败（即锁已被其他线程获取），则返回false
    boolean tryLock();
    
    //与tryLock()方法是类似的，只不过区别在于这个方法在拿不到锁时会等待一定的时间，
    //在时间期限之内如果还拿不到锁，就返回false。如果如果一开始拿到锁或者在等待期间内拿到了锁，则返回true。
    boolean tryLock(long time, TimeUnit unit) throws InterruptedException;
    
    //释放锁
    void unlock();
    Condition newCondition();
}
```

lock方法不会主动释放锁，所以需要手动调用unlock释放锁，一般在try catch 中使用lock，也一般在finally中将锁释放。保证锁一定能被释放，防止死锁。

```
public class LockTest implements Runnable {
    // 定义一把重入锁
    public static ReentrantLock lock = new ReentrantLock();
    public static int c = 0;
    @Override
    public void run() {
        for (int i = 0; i < 10; i++) {
            try {
                lock.lock();
                System.out.println(Thread.currentThread().getName() + " 获得锁");
                System.out.println(Thread.currentThread().getName() + " ====> " + c);
                c++;
            }catch (Exception e){
                e.printStackTrace();
            }finally {
                System.out.println(Thread.currentThread().getName() + " 释放锁");
                lock.unlock();
            }
        }
    }
    public static void main(String[] args) {
        LockTest lockTest = new LockTest();
        Thread thread = new Thread(lockTest);
        Thread thread1 = new Thread(lockTest);
        thread.start();
        thread1.start();
        //让main线程等待th1、th2线程执行完毕后，再继续执行
        try {
            thread.join();
            thread1.join();
        }catch (InterruptedException e){
            e.printStackTrace();
        }
        System.out.println(c);
    }
}
```

也可以使用`Lock` 中的 `tryLock(long time, TimeUnit unit)` 方法，表示等待多少时间获取锁，如果过来这个时间仍然拿不到锁，那么就不在等待了，线程中断。

```java
public class TryLockTest {

    public static ReentrantLock lock = new ReentrantLock();
    private static int m = 0;
    private static boolean islocked;

    public static void main(String[] args) {

        Thread t1 = new Thread(() -> {
            try {
                islocked = lock.tryLock();
                if (islocked){
                    System.out.println(Thread.currentThread().getName() + " 未获得锁");
                }
            } catch (Exception e) {
                e.printStackTrace();
            }finally {
                if (islocked){
                    lock.unlock();
                }
            }
        });

        Thread t3 = new Thread(() -> {
            try {
                lock.lock();
                TimeUnit.SECONDS.sleep(2);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }finally {
                lock.unlock();
            }
        });

        t1.start();
        t3.start();

        //让main线程等待th1、th2线程执行完毕后，再继续执行
        try {
            t1.join();// 后执行，只等待一秒去获取锁，获取不到锁
            t3.join();// t3先执行，睡2秒，然后释放锁
        }catch (InterruptedException e){
            e.printStackTrace();
        }
        System.out.println(m);
    }
}
```

