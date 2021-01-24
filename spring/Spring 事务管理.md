### Spring 事务管理

---

**什么是事务**

> 事务是逻辑上的一组操作，这组逻辑操作要么都执行，要么都不执行。
>
> ```
> 事务：做事有始有终，要么做完，要么 什么也没做（ACID）
>     原子性(Atomic)：
>     一致性(Consistency)：数据一致性
>     隔离性(Isolation)：操作的隔离性，如不能同时对同一个数据进行删除
>     持久性(Dueablity)：
> 根据此设置的事务4个基本
>     READ_UNCOMMITTED
>     READ_COMMITTED
>     REPEATABLE_READ
>     SERIALIZABLE
> 
>     从上往下： 级别越来越高，并发越来越差，安全性越来越高
> 
> 事务面临的问题：
>     脏读(Dirty Read):读到了有问题数据 ，事务A读到了事务B未提交的数据，并在这个基础上做了其他的操作
>     不可重复读(Unrepeatable Read)：两次读的数据不一致(其他线程改变了这个值)，事务A读到了事务B已经提交的更改数据
>     Phantom Read: 幻读，事务A读取了事务B已经提交的新增数据
> 
>     第一个是坚决抵制的，其他2个是可以多数情况下不考虑
> ```

**事务的特性**

> * 原子性： 事务是最小的执行单位，不允许分割，要么全部完成，要不全部不完成
> * 一致性：执行事务前后，数据保持一致
> * 隔离性：多个事务之间不会互相干扰，如多个事务访问数据库
> *  持久性：一个事务被提交之后，他对数据库中的数据的改变是持久化的。

**Spring 事务管理接口**

> * PlatformTransactionManager:  事务管理器
> * TransactionDefinition: 事务定义信息(隔离级别，传播行为，只读，回滚规则)
> * TransactionStatus: 事务运行状态

事务管理可以理解为：

> 按照给定的事务规则，执行提交或者回滚等操作

#### 分别对管理接口进行解读

**PlatformTransactionManager**

> Spring 并不会直接管理事务，而是提供多种事务管理器，它们将事务管理的职责委托给Hibernate 或者JTA 等持久化机制所提供的相关平台框架的事务实现，Spring事务管理器PlatformTransactionManager 通过这个接口，Spring 为各个平台如 JDBC Hibernate 等都提供对应得事务管理器，但是具体的实现就是各个平台自己的事情。
>
> PlatformTransactionManager 提供单个方法：
>
> ```java
> Public interface PlatformTransactionManager()...{  
>     // 根据指定的传播行为，返回当前活动的事务或创建一个新事务
>     TransactionStatus getTransaction(TransactionDefinition definition) throws 	TransactionException; 
>     // 使用事务目前的状态提交事务
>     Void commit(TransactionStatus status) throws TransactionException;  
>     // 对执行的事务进行回滚
>     Void rollback(TransactionStatus status) throws TransactionException;  
> } 
> ```

PlatformTransactionManager 也根据不同的持久层框架实现不同的接口类

![1637b21877cf626d](\1637b21877cf626d.png)



**TransactionDefinition**

> 可以理解事务属性是事务的基本配置，描述了事务策略如何应用到方法上。主要包括5个方面
>
> * 隔离级别
> * 传播行为
> * 回滚规则
> * 是否只读
> * 事务超时

```java
public interface TransactionDefinition {
    // 返回事务的传播行为
    int getPropagationBehavior(); 
    
    // 返回事务的隔离级别，事务管理器根据它来控制另外一个事务可以看到本事务内的哪些数据
    int getIsolationLevel(); 
    
    //返回事务的名字
    String getName()；
        
    // 返回事务必须在多少秒内完成
    int getTimeout();  
    
    // 返回是否优化为只读事务。
    boolean isReadOnly();
} 
```

**事务隔离级别**： 定义了一个事务是否受其它并发事务的影响即影响程度

> **ISOLATION_DEFAULT**：  使用后端数据库默认的隔离级别，也就是说app 中的事务不是由Spring 决定的，而是Spring 使用的后端数据库决定的。Mysql 默认采用的 REPEATABLE_READ隔离级别 Oracle 默认采用的 READ_COMMITTED隔离级别.
>
> **ISOLATION_READ_UNCOMMITTED**：最低的隔离级别，允许读取尚未提交的数据变更，**可能会导致脏读、幻读或不可重复读**
>
> **ISOLATION_READ_COMMITTED** ： 允许读取并发事务已经提交的数据，**可以阻止脏读，但是幻读或不可重复读仍有可能发生**
>
> **ISOLATION_REPEATABLE_READ** 对同一字段的多次读取结果都是一致的，除非数据是被本身事务自己所修改，**可以阻止脏读和不可重复读，但幻读仍有可能发生。**
>
> **ISOLATION_SERIALIZABLE**： 最高的隔离级别，完全服从ACID的隔离级别。所有的事务依次逐个执行，这样事务之间就完全不可能产生干扰，也就是说，**该级别可以防止脏读、不可重复读以及幻读**。但是这将严重影响程序的性能。通常情况下也不会用到该级别。

**并发事务带来的问题**：

> 并发操作相同的数据来完成个子的任务，可能会导致一下的一些问题
>
> * 脏读(dirty read): 一个事务在对数据进行修改，但是还没有提交，而此时另外一个事务来了读取数据，那么读到的数据是 『脏数据』
> * 丢失修改(lost to modify): 两个事务同时对数据进行修改，但是第一个事务的提交早于第二个事务的提交，这样第一个事务的修改就会丢失。
> * 不可重复读(unrepeatable read): 在一个事务内多次读取同一个数据，在这个事务还没有结束时候，另一个事务也访问该数据，那么在第一个书屋中的两次读取之间，第二个事务**修改**了第一个事务读取的数据，导致第一个事务两次读取不一致。
> * 幻读(phantom read): 和不可重复度类似，第一次事务连续读取多个数据的的时候，第二个事务，在这些数据直接**插入(新增)**新的数据，导致第一个事务读取到多余的数据。

**事务传播行为** 业务层方法之间互相调用的事务问题

> 当事务方法被另外一个事务方法调用时候，必须指定事务应该如何传播，例如：方法可能继续在现有事务中运行，也可能在新事务，也可能在自己的事务中运行。
>
> **支持当前事务的情况：**
>
> > **PROPAGATION_REQUIRED**： 必须有事务存在，当前有事务则加入，如果没有则新建一个事务
> >
> > **PROPAGATION_SUPPORTS**：支持事务，有事务那么以事务的方式执行，如果没有那么按照没有事务方式运行
> >
> > **PROPAGATION_MANDATORY**：当前存在事务，那么加入到当前事务，如果当前没有 事务，那么就退出。
>
> **不支持当前事务**
>
> > **PROPAGATION_REQUIRES_NEW**: 当前会新建一个事务，如果当前有事务，那么会先把这个事务挂起
> >
> > 始终会启动一个新事务
> >
> > **PROPAGATION_NOT_SUPPORTED**： 非事务方式运行，如果当前有事务，那么会先把这个事务挂起
> >
> > **PROPAGATION_NEVER**：以非事务方式运行，如果当前存在事务，则抛出异常
>
> **其他情况：**
>
> > **PROPAGATION_NESTED**: 如果当前存在事务，则创建一个事务作为当前事务的嵌套事务来运行；如果当前没有事务，则该取值等价于TransactionDefinition.PROPAGATION_REQUIRED。两个事务有关联的，外部事物回滚，那么内部事务也回滚。

#### 事务超时

> 就是一个事务允许执行的最长时间，如果超过这个时间，但是事务还没有完成，则会自动回滚事务，spring 中 以 **秒**记事务超时。

#### 事务只读属性

> 事务性资源就是指那些被事务管理的资源，对这些资源是只读的。

#### 回滚规则

> 这些规则定义了哪些异常会导致事务回滚而哪些不会，默认情况下，事务只有遇到运行期异常时才会回滚，而在遇到检查型异常时不会回滚，

### TransactionStatus

> 用来记录事务的状态，该接口定义了一组方法，用来获取判断事务的相应的状态信息。
>
> ```java
> public interface TransactionStatus{
>     boolean isNewTransaction(); // 是否是新的事物
>     boolean hasSavepoint(); // 是否有恢复点
>     void setRollbackOnly();  // 设置为只回滚
>     boolean isRollbackOnly(); // 是否为只回滚
>     boolean isCompleted; // 是否已完成
> } 
> ```

上面提到的大多数是编程式的事务回滚，在项目中使用到的基本都会是声明式的回滚

[Spring 事务例子](https://blog.csdn.net/u010963948/article/details/82761383)

<https://blog.csdn.net/u010963948/article/details/82761383>

----

事务各个属性的实验的

主要代码如下：

```java
@Component
public class FooServiceImpl implements FooService{

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private FooService fooService;

    @Override
    @Transactional()
    public void insertRecord() {
        jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('AAA')");
    }

    // 这里会发送回滚
    @Override
    @Transactional(rollbackFor = RollbackException.class)
    public void insertThenRollback() throws RollbackException {
        jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
        throw new RollbackException();
    }
    @Override
    @Transactional(rollbackFor = RollbackException.class)
    public void invokeInsertThenRollback() throws RollbackException {
        insertThenRollback();
    }
}
```

执行代码：

```java
@SpringBootApplication
@EnableTransactionManagement(mode = AdviceMode.PROXY)
@Slf4j
public class DemoApplication implements CommandLineRunner {
    @Autowired
    private FooService fooService;
    @Autowired
    private JdbcTemplate jdbcTemplate;

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

    @Override
    public void run(String... args) throws Exception {
        fooService.insertRecord();
        log.info("AAA {}",jdbcTemplate
            .queryForObject("SELECT COUNT(*) FROM FOO WHERE BAR='AAA'", Long.class));
        try {
            fooService.insertThenRollback();
        } catch (Exception e) {
            log.info("BBB {}",jdbcTemplate
                .queryForObject("SELECT COUNT(*) FROM FOO WHERE BAR='BBB'", Long.class));}

        try {
            fooService.invokeInsertThenRollback();
        } catch (Exception e) {
            log.info("BBB {}",jdbcTemplate
                .queryForObject("SELECT COUNT(*) FROM FOO WHERE BAR='BBB'", Long.class));}
    }
}
```

上面输出：

> AAA 1
>
> BBB 0
>
> BBB 1

也就是 执行 `fooService.invokeInsertThenRollback();` 的时候执行成功了，并没有抛出异常而回滚，也就是说事务没有在这里起作用，导致这个问题的关键是：

```java
@Override
    @Transactional(rollbackFor = RollbackException.class)
    public void insertThenRollback() throws RollbackException {
        jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
        throw new RollbackException();
    }
    @Override
    @Transactional(rollbackFor = RollbackException.class)
    public void invokeInsertThenRollback() throws RollbackException {
        insertThenRollback();
    }
```

> invokeInsertThenRollback 在类里面直接调用 insertThenRollback方法，在这里事务没有产生作用，主要是因为Spring 的事务是使用动态代理实现的，而执行动态代理的时候需要使用 **类.方法**  的方式调用，但是如果直接在类里面调用方法那么动态代理不生效的。如果将上面的代码改为：就会发送回滚了

```java
    @Override
    @Transactional(rollbackFor = RollbackException.class)
    public void insertThenRollback() throws RollbackException {
        jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
        throw new RollbackException();
    }

    @Override
    @Transactional(propagation=Propagation.REQUIRED, rollbackFor = RollbackException.class)
    public void invokeInsertThenRollback() throws RollbackException {
        fooService.insertThenRollback();
    }
```

> AAA 1
>
> BBB 0
>
> BBB 1

---

Spring 中的Transactional 注解主要值

```java
public @interface Transactional {
    // 默认使用 Propagation.REQUIRED 的事务传播 必须有事务存在
    Propagation propagation() default Propagation.REQUIRED;
    
    // 隔离默认值是-1，也就是隔离机制完全取决于后端数据库
    Isolation isolation() default Isolation.DEFAULT;
    
    // 隔离默认值是-1，也就是timeout机制完全取决于后端数据库
    int timeout() default TransactionDefinition.TIMEOUT_DEFAULT;
    
    boolean readOnly() default false;
    
    // 定义出现回滚的异常，也就是出现这个异常之后会发生回滚
    Class<? extends Throwable>[] rollbackFor() default {};
}
```

如果改代码为：

```java
@Override
@Transactional(propagation=Propagation.REQUIRES_NEW, rollbackFor = RollbackException.class)
public void insertThenRollback() throws RollbackException {
    jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
    throw new RollbackException();
}

@Override
public void invokeInsertThenRollback() throws RollbackException {
    jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
    fooService.insertThenRollback();
}
```

> REQUIRES_NEW 会在 当前事务新建一个事务，如果当前有事务那先将当前事务挂起来
>
> 执行invokeInsertThenRollback方法，会插入一个BBB，就是 invokeInsertThenRollback 方法里面会插入，虽然这里有异常，但是没有回滚，而是插入进入。而在 invokeInsertThenRollback 方法中执行 insertThenRollback 抛出异常，产生事务，然后回滚

如果将代码改为：

```java
@Override
@Transactional(propagation=Propagation.REQUIRES_NEW, rollbackFor = RollbackException.class)
public void insertThenRollback() throws RollbackException {
    jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
    throw new RollbackException();
}

@Override
@Transactional(rollbackFor = RollbackException.class)
public void invokeInsertThenRollback() throws RollbackException {
    jdbcTemplate.execute("INSERT INTO FOO (BAR) VALUES ('BBB')");
    fooService.insertThenRollback();
}
```







