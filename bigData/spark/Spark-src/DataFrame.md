#### DataFrame

> `rdd` 之上的抽象，使用更加的简单，直接谢谢`SQL` 就可以了。
>
> 用于和**结构化的**数据进行操作。

#### Spark Streaming

> * 微批次
> * 准实时，微批的产生会有一些延时
> * Application(Driver) 一直运行

> `Driver` 和 `Executor` 是不停止的，且之间的通信不间断的，且`Driver` 是不停的向集群提交任务的。如我们启动的`spark-shell`, 那么这个线程是不停的，那么在这个`shell` 中不停的执行`action` 操作，给集群提交`job`, 当这个提交的频率快一些，那么就可以认为是流式的执行方式。
>
> sparkStreaming 提交的任务是一直运行的，不停的提交`job`的，每次提交的`job`使用的数据变少(微批，每个微批是一个 job)，数据是一直往这个程序中流入的。
>
> 每隔一个时间段，从外面读数据，读进来的数据就成为一个微批，然后提交这个微批，准实时，产生一个 job。
>
> spark 基本是可以满足一般的需求，延时个几秒钟，几分钟也是可以的。

* 可容错
* 高吞吐
* 可扩展
* 编程API 丰富
* 可以保证 `exectly once` 语义

缺点：

* 有一定的延迟

最重要的2个东西

* streamingContext

> 是 `sparkContext` 的封装，里面持有 sparkContext 的引用，并且要指定生成批次的时间间隔，用来创建原始的DStream

* DStream

> Discretized Stream: 是对连续stream 的抽象。也理解为一系列的RDD
>
> 是对`SparkSream` 的最基本的封装，也是抽象的分布式集合，也是封装这描述信息，是对RDD 的进一步封装，DStream 可以定期的生成RDD
>
> DStream 可以从很多的数据源创建
>
> 你对DStream进行操作，本质但是是对DStream中的RDD 进行操作，你的RDD 的每一个分区进行操作
>
> DStream上的方法也分为 transformation 和 action，还有一些方法既不是Transformation 也不是 action，比如foreachRDD，调用Transformation 后可以生成一个新的DStream

* **Receiver**

> 分为2类
>
> **Basic Souce**:  在 `StreamingContext`中可以使用的API，如systems, and socket connections.
>
> **Advanced source**: Kafka, Kinesis 等，他们需要和外部依赖才能够使用
>
> 需要注意的是如果使用了`Receiver` 那么就不能够设置 `master("local[1]")/master("local")`
>
> 是可以从多个 source 中接受数据的，会有多个 `DStream`，如我们可以从`kafka` 的多个分区中使用多个`Receiver`同时读数据，但这个时候注意`core` 的设置。

```scala
val spark = SparkSession
.builder()
.master("local[2]")
// 这里的 core 至少需要有2个，因为一个被 receiver 占了，剩下的被计算逻辑占用
//
.getOrCreate()

val sc = spark.sparkContext
// sc 用来创建 RDD
sc.setLogLevel("ERROR")

val ssc = new StreamingContext(sc, Seconds(2)) // 一个小批次产生的时间间隔
ssc.sparkContext.setLogLevel("WARN")
// ssc 创建实时计算抽象的数据集 DStream

val lines: ReceiverInputDStream[String] = ssc.socketTextStream("localhost", 9999)

// 实时的 wordcount
val value: DStream[String] = lines.flatMap(_.split(" "))
val value1: DStream[(String, Int)] = value.map(a => (a, 1))

val value2: DStream[(String, Int)] = value1.reduceByKey((a, b) => a + b)

value2.print()

// 开启
ssc.start()

// 让程序一直运行, 将Driver 挂起
ssc.awaitTermination()
```

计算不是有状态的，如上面的列子，`s` 在2秒前输如，然后在2s后再输出统计器count，不将之前的计入，也就是没有状态的。

---

和 kafka 整合，可以自动提交数据消费的偏移量。也就是spark2.0提供的`Advanced Source` 消费者直连到 `source`，目前支持`kafka` 和 `kinesis`



