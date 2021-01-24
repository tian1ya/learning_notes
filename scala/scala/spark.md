#### spark

**跑第一个例子**

启动 start 集群 sbin/start-all.sh

> bin/spark-submit --master spark://node-1:7077 --class org.apache.spark.examples.SparkPi examples/jars/spark-examples_2.11-2.2.0.jar 100
>
> 可以给spark 参数 
>
> --executor-memory 2048mb： 每个executor 使用内存
>
>  --total-executor-cores 12  所有 executor 使用core 个数
>
> spark-submit(Driver) 提交任务
>
> 如果集群配置了高可用,可以指定多个mater
>
> bin/spark-submit --master spark://node-1:7077, node-2:7077 --class org.apache.spark.examples.SparkPi examples/jars/spark-examples_2.11-2.2.0.jar 100
>
> 

当集群跑起来之后worker 会有 CoarseGrainedExecutorBackend 的一个进程

> 称为执行器，真正的任务是在这个进程中执行的，执行结束之后这个进程就会退出，资源需要释放掉。

spark 提交一个任务，会产生哪些进程

> 1. sparkSubmit(Driver) 提交任务
> 2. Executor 执行真正的计算任务

spark shell 在任意一台机器上启动都是可以的

> 直接在 bin 目录下启动 spark-shell 是没有启动spark 集群，而是在 local 模式下的。
>
> /spark-shell --master spark://node-1:7077 启动方式才能时在集群上运行，在启动之后，再UI 界面可以看见一个正在运行的application，名称为 spark-shell，这个shell 是一直在运行的，在worker 中可以看见 CoarseGrainedExecutorBackend 进程，及在master 节点上可以看见 SparkSubmit

格式化nameNode： ./hdfs namenode -format

启动hdfs ./start-dfs.sh (./start-all.sh 还会将yarn 也启动)

---

在node-1上创建wordcount.txt文件，然后将其上传到hdfs，spark 集群运行下，数据集都是从hdfs 上读取

```scala
sc.textFile("hdfs://node-1:9000/wordcount.txt").flatMap(_.split(" ")).map((_,1)).reduceByKey(_+_).collect()
```

注意这里文件路径的写法。

---

Driver 提交任务，向master 申请资源，在执行spark-submit 的时候，需要执行executor参数，当然也是有默认的，也会有 --total-executor-cores, --executor-memory 等参数，都是有默认的。

master 负责资源调度，就是分配资源，如有10个核，那么是由任务调度的策略的，尽量让任务运行在更多的机器上，

worker 会给master 提交自己的状态，心跳，告诉worker 还在的。

master 和 worker 进行二次通信，让worker 启动executor，并与此同时，将分配的参数传递到executor

然后给worker 的executor(2 core 1G/executor)发送指令，executor 和 driver 在进行通信，，driver 将计算的任务，交给executor执行(真正的计算任务是在Driver 生成的)，一个 executor 中可以执行多个任务，

---

### Yarn VS spark standalone 调度

ResourceManager   Master  管理子节点，资源调度，接受任务请求，

NodeManager         Worker  管理当前节点，并管理子进程

YarnChild                 executor  运行真正的运算逻辑

Client                        spark-submit   yarn 的client + applicationMaster 提交任务，提交app，管理该任务		

ApplicationMaster							 executor 并将task 提交到集群上(executor)，



---

RDD： 它是分散在各个数据集上的数据的抽象，本身并不是数据集或者存储这数据集，当对RDD进行操作的时候，RDD将这些操作下发到真正的分散在各个机器上的数据集上，也就是说，RDD可以理解为数据集的一个代理，

RDD是一个抽象的数据集，理解为这是一个代理，对代理进行操作，然后这个操作由RDD下发到真正的数据集。

有这个代理的好处是，并不需要关心操作细节，而是结果

操作这个RDD，**那么好像就是操作本地的一块数据集一样**，至于调度，容错等都是不需要关注的

RDD 会将操作分为很多的 task，这些task 会分到 node 的executor 上，去操作。这些task 就是真正的业务逻辑，

---

#### RDD transformation

```scala
val rdd2 = sc.parallelize(List(1,2,3,4,5,6,6,4,3,2)).map(_*2).sortBy(x=>x, true)
rdd2.collect
collect 会将集群上的所有数据拉到Driver 的节点上。
每次transformation 产生新的RDD，并不会产生结果

val rdd4 = sc.parallelize(Array("a b c", "d e f", "h i j"))
rdd4.flatMap(_.split(" ")).collect

val rdd5 = sc.parallelize(List(List("a b c", "a b c"), List("e f d", "e f d"), List("h i j", "a b c")))
rdd5.flatMap(_.flatMap(_.split(" "))).collect
这里第一个flatMap 是 rdd 的方法，第二个 flatMap 是scala 中 String 的方法

val rdd5 = sc.parallelize(List(1,2,3))
val rdd6 = sc.parallelize(List(1,2,3,4,5,6,7))
rdd5.union(rdd6).collect 
求集合的并集 Array(1, 2, 3, 1, 2, 3, 4, 5, 6, 7)

rdd5.intersection(rdd6).collect
Array[Int] = Array(1, 2, 3)
求交集

val rdd1 = sc.parallelize(List(("tom",1), ("jerry",2), ("kitty",3)))
val rdd2 = sc.parallelize(List(("tom",1), ("jerry",2), ("kitty",3), ("hello",4)))
rdd1.join(rdd2)
Array[(String, (Int, Int))] = Array((tom,(1,1)), (kitty,(3,3)), (jerry,(2,2)))
join 取得二者共有的
可以写到hdfs rdd3.saveAsTextFile("hdfs://node-1:9000/testJoin")
写到 hdfs 之会写 n 个part 文件，这个n是由参数和集群总共核数决定的，当给定这个参数的时候，就有
这个参数指定的核数，当没有指定的时候，就是按照机器的核数

val rdd3 = rdd1 union rdd2
rdd3.groupByKey().collect
Array[(String, Iterable[Int])] = Array((tom,CompactBuffer(1, 1)), (kitty,CompactBuffer(3, 3)), (hello,CompactBuffer(4)), (jerry,CompactBuffer(2, 2)))
key 相同的值会被分到一个 CompactBuffer 中

使用groupByKey 作 wordcount
sc.textFile("hdfs://node-1:9000/wordcount.txt").flatMap(_.split(" ")).map((_,1)).groupByKey().mapValues(_.sum).collect()
res6: Array[(String, Int)] = Array((d,8), (f,4), (tt,1), (fr,2), (r,6), (e,2), (ttq,1), (q,1))

groupByKey 会将集群中的相同key 的value 拉倒同一个机器上，shuffle 过程会耗很多的通信资源
但是 reduceByKey 会现在本地将相同的key 进行reduce 操作，然后再将集群间相同的key 进行拉倒一个机器上，这样通信的耗费就会减少

val rdd1 = sc.parallelize(List(("tom",1), ("jerry",2), ("kitt",3)))
val rdd2 = sc.parallelize(List(("tom",1), ("jerry",2), ("kitty",3), ("hello",4)))
rdd1.leftOuterJoin(rdd2).collect
选择左边存在的键，为主键，左边没有，右边有的键是会被忽略的，如果左边又右边也有会产生some，反之，左边又
右边没有，那么就会产生None 值
res2: Array[(String, (Int, Option[Int]))] = Array((tom,(1,Some(1))), (kitt,(3,None)), (jerry,(2,Some(2))))

协分组
rdd1.cogroup(rdd2).collect
Array[(String, (Iterable[Int], Iterable[Int]))] = Array((tom,(CompactBuffer(1),CompactBuffer(1))), (kitt,(CompactBuffer(3),CompactBuffer())), (kitty,(CompactBuffer(),CompactBuffer(3))), (hello,(CompactBuffer(),CompactBuffer(4))), (jerry,(CompactBuffer(2),CompactBuffer(2))))
将所有的键都组合，没有的那么显示空CompactBuffer()
```

> **transformation 特点**
>
> * lazy
> * 生成新的RDD
> * RDD不存储任何要计算的数据，而是记录RDD 的转换关系及操作

#### 查看Partition

> ```scala
> val rdd = sc.textFile("hdfs://node-1:9000/wordcount.txt")
> rdd.partitions.length
> res4: Int = 2
> ```
>
> 查看/目录下的文件wordcount.txt
>
> ```
> ./hdfs dfs -ls /
> ```
>
> 只有一个文件
>
> > -rw-r--r--   3 root supergroup         55 2019-08-17 01:19 /wordcount.txt
>
> 原因是文件太小，当文件大于128M的时候就会切片了

#### Action

> collect
>
> count
>
> take
>
> takeOrdered(n) 按照次序那值

---

#### 其它action

> RDD 的 map 方法，真正在Executor 中执行时，是一条一条的将数据拿出来处理
>
> **mapPartitionWithIndex**
>
> > RDD 中有分区的概念，分区中记录中以后要去读的数据(数据的偏移量)，然后每一个分区会形成一个task，分区中的数据所在机器也就是这个分区对应的task所在机器，mapPartitionWithIndex 执行的时候，既会拿到分区也会拿到分区的index
> >
> > 所以这个算子的功能室，一次拿出一个分区，这个分区中有多条数据(数据的记录)，真正生成的Task会去读取这些数据，并且这个Task有这个分区的index，
> >
> > 功能：取分区中对应的数据时候，还可以将分区的编号取出来，这样就可以知道数据是哪个分区的（哪个分区对应的Task，一个task对应一个分区），
> >
> > 一个分区对应一个Task，Task是真正处理数据，Task 读取的数据，就可以认为是这个分期中记录的数据
> >
> > ```
> > Return a new RDD by applying a function to each partition of this RDD
> > ```
>
> ```scala
> val rdd = sc.parallelize(List(1,2,3,4,5,6,6,7,8,9),2)
> 
> val func = (index:Int, it:Iterator[Int]) => {it.map(e => s"$index, ele: $e")}
> val rdd2 = rdd.mapPartitionsWithIndex(func)
> rdd2.collect
> Array[String] = Array(0, ele: 1, 0, ele: 2, 0, ele: 3, 0, ele: 4, 0, ele: 5, 1, ele: 6, 1, ele: 6, 1, ele: 7, 1, ele: 8, 1, ele: 9)
> 
> 这样理解这个算子，主要的就是那个 func 函数，这个函数将rdd 中的每一个分区中的值进行定义好的函数的操作
> 然后生成新的rdd，index 就是那个分区号，通过上面的func函数的转换，就可以知道哪些数据是属于哪些分区的
> 
> 如果有多余的分区中没有数据：
> val rdd = sc.parallelize(List("1","2", "3","4","5","6","7"),9)
> def func2(index:Int, iter:Iterator[String]):Iterator[String] = {iter.map(x => "[partID:" + index + "val: " + x + "]")}
> rdd.mapPartitionsWithIndex(func2).collect
> res8: Array[String] = Array([partID:1val: 1], [partID:2val: 2], [partID:3val: 3], [partID:5val: 4], [partID:6val: 5], [partID:7val: 6], [partID:8val: 7])
> 从结果上来看，只输出7个，剩余的第index 8， 和 index 9，都是没有数据的分区，所以都是没有的
> 
> 然后存储
> rdd.saveAsTextFile("hdfs://node-1:9000/wad")
> 然后查看文件
> ./hdfs dfs -ls /wad
> 结果
> -rw-r--r--   3 root supergroup          0 2019-08-24 11:03 /wad/_SUCCESS
> -rw-r--r--   3 root supergroup          0 2019-08-24 11:03 /wad/part-00000
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00001
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00002
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00003
> -rw-r--r--   3 root supergroup          0 2019-08-24 11:03 /wad/part-00004
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00005
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00006
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00007
> -rw-r--r--   3 root supergroup          2 2019-08-24 11:03 /wad/part-00008
> 会有9个分区，但是有2个是没有数据的，如上面所说到的，只有7个元素，但是有9个分区
> 这剩余2个空分区也会产生task
> ```
>
> **arregate**
>
> > 聚合操作
>
> ```scala
> val arr1 = sc.parallelize(List(1,2,3,4,5,6,7,8,9),2)
> rdd1.aggregate(0)(_+_, _+_).collect
> aggregate(0)(_+_, _+_)
> // aggregate[U: ClassTag](zeroValue: U)(seqOp: (U, T) => U, combOp: (U, U) => U): U
> 接受第一个参数代表示从arr1的第0个分区开始的执行计算的初始值，包括全局计算的时候也会使用初始值，第一个函数参数 seqOp 是分别在从起始的分区中分别计算每一个分区，然后得到结果，得到的每一个分区的结果都又交给combOp函数，然后得到最后的结构
> 也就是说 aggregate 函数现在每一个分区中计算结构，然后将计算结构放到全局中去计算
> 
> 那么上面的结果
> res15: Int = 45
> 
> 如果计算
> arr1.aggregate(0)(math.max(_,_), _+_)
> res17: Int = 13
> 首先在第一个分区中得到最大值4，然后再第二个分区中得到最大值 9， 二者相加的结构 13
> 
> 另外一种情况
> val arr1 = sc.parallelize(List("1","2","3","4","5","6","7","8","9"),2)
> arr1.aggregate("")(_+_, _+_)
> 那么几次返回的结果可能是不一样的
> res19: String = 123456789
> res20: String = 567891234
> 之所以会这样是因为，在计算每一个分区的时候是并行的，并不能确定哪一个先计算结束，然后返回
> 所以会出钱前后不一致的情况，但是分区里面的结果是确定一致的
> ```
>
> 







































