```scala
val spark: SparkSession = Commons.sparkSession
val sc: SparkContext = spark.sparkContext

val rdd1: RDD[Int] = sc.parallelize(List(1,2,3,4), 2)

val intToBoolean: Int => Boolean = x => x % 2 == 0

val rdd2: RDD[Int] = rdd1.filter(intToBoolean)

val intToInt: Int => Int = a => a * 2
val rdd3: RDD[Int] = rdd2.map(intToInt)

rdd3.collect()

spark.close()
```

#### filter

点进去查看 `filter` 的代码

```scala
def filter(f: T => Boolean): RDD[T] = withScope {
  val cleanF = sc.clean(f)
  new MapPartitionsRDD[T, T](
    this,
    (_, _, iter) => iter.filter(cleanF),
    preservesPartitioning = true)
}
```

`sc.clean` 方法是做闭包序列化检查的，可能会有一些闭包函数使用到外部的变量，这些变量能够被序列化，就是检查这个事情的。

然后`new MapPartitionsRDD` 产线一个新的 `RDD` 也就是代码 `rdd1.filter(intToBoolean)` 返回的 `RDD` 从代码中可以看出，新创建的·`RDD` 是持有父`RDD`  的引用的。

这里主要看下函数 `(_, _, iter) => iter.filter(cleanF)`

函数类是这样的

```scala
private[spark] class MapPartitionsRDD[U: ClassTag, T: ClassTag](
    var prev: RDD[T],
    f: (TaskContext, Int, Iterator[T]) => Iterator[U],  
   // (TaskContext, partition index(分区索引), iterator(父分区的迭代器))
    preservesPartitioning: Boolean = false,
    isFromBarrier: Boolean = false,
    isOrderSensitive: Boolean = false)
  extends RDD[U](prev) {

  override val partitioner = if (preservesPartitioning) firstParent[T].partitioner else None

  override def getPartitions: Array[Partition] = firstParent[T].partitions

  override def compute(split: Partition, context: TaskContext): Iterator[U] =
    f(context, split.index, firstParent[T].iterator(split, context))
    // 这里是在调读起来的时候回执行的地方
    // firstParent[T].iterator(split, context) 获取父rdd 的迭代器
    // 然后 根据 f 函数的签名，以及 new MapPartitionsRDD 传入的函数
    // 连在一起实际上调的是 firstParent[T].iterator(split, context).filter(cleanF)
    // 所以这里看出一个分区其实就是一个数据的迭代器
    // firstParent[T].iterator(split, context) 这里返回的数据累加就是 scala 的Iterator

  override def clearDependencies(): Unit = {
    super.clearDependencies()
    prev = null
  }
```

#### map

在看看 `map` 的源码

```scala
def map[U: ClassTag](f: T => U): RDD[U] = withScope {
  val cleanF = sc.clean(f)
  new MapPartitionsRDD[U, T](this, (_, _, iter) => iter.map(cleanF))
}
```

这里和上面的代码是一样的，只不过执行的是父 `partition(iterator)`  的 `map` 方法。

---

在进一步看看是如何到父 `RDD` 中获取迭代器的，也就是代码 `firstParent[T].iterator(split, context)`

是如何执行的。

```scala
final def iterator(split: Partition, context: TaskContext): Iterator[T] = {
  if (storageLevel != StorageLevel.NONE) {
    // 如果有缓存，那么从缓存中获取
    getOrCompute(split, context)
  } else {
    // 没有缓存，那么从 Checkpoint 中获取
    computeOrReadCheckpoint(split, context)
  }
}
```

---

上面也看出 `RDD` 的抽象，是一个描述信息。

`filter` 和 `map` 都是在没一个分区中(数据迭代器)执行`filter` 和 `map` 方法。

---

代码

```scala
val spark: SparkSession = Commons.sparkSession
val sc: SparkContext = spark.sparkContext

val rdd1: RDD[Int] = sc.parallelize(List(1, 2, 3, 4, 5, 6, 7, 8), 2)

println(rdd1.map {
  x => {
    println("******")
    val index = TaskContext.getPartitionId()
    (index, x * 100)
  }
}.collect())

spark.close()
```

执行这里的方法，第8行的代码会打印出 8次，也就是 `map` 中的方法被执行了8次。使用`map`  每调用一条数据，那么就调用 `map` 方法一次。

如果仅仅是处理一条数据那似乎也没啥问题，加入说 `map` 方法会调用外部的数据，如去`es` 读数据，那么频繁的创建和销毁连接。且这个创建连接不能定义到`map` 方法的外部，因为连接是不能序列化的(回想上面提到的 `sc.clean` 方法)。

#### mapPartitions

于是出现了 `mapPartitions`

```scala
println(rdd1.mapPartitions {
  x => {
    println("******")
    x.map(x => x * 2)
  }
```

这次只会有 2 次打印输出※。

这是因为这里的 x 就是一个迭代器，也就是一个分区了，也就是在调用函数的时候，给函数在压栈的时候直接将一个分区数据压进去了。

而上面的`map` 在函数调用压栈的时候，每次只压每个分区中的一条数据进函数。

看看源码

```scala
def mapPartitions[U: ClassTag](
  f: Iterator[T] => Iterator[U],
  preservesPartitioning: Boolean = false): RDD[U] = withScope {
  val cleanedF = sc.clean(f)
  new MapPartitionsRDD(
    this,
    (_: TaskContext, _: Int, iter: Iterator[T]) => cleanedF(iter),
    preservesPartitioning)
}
```

这里主要是查看

 `(_: TaskContext, _: Int, iter: Iterator[T]) => cleanedF(iter),`

来看看和上面 `map` 中的区别

`(_, _, iter) => iter.map(cleanF)`

一个是调用分区(迭代器中的 `map` 方法)， 另外一个是直接将一个分区(迭代器) 作为函数的输出参数。

---

#### mapPartitionsWithIndex

看看 `mapPartitionsWithIndex`

```scala
val value: RDD[(Int, Int)] = rdd1.mapPartitionsWithIndex((index, iter) => iter.map(ele => (index, ele)))
```

除iter，传入另外一个参数 index

看下其源码

```scala
  def mapPartitionsWithIndex[U: ClassTag](
      f: (Int, Iterator[T]) => Iterator[U],
      preservesPartitioning: Boolean = false): RDD[U] = withScope {
    val cleanedF = sc.clean(f)
    new MapPartitionsRDD(
      this,
      (_: TaskContext, index: Int, iter: Iterator[T]) => cleanedF(index, iter),
      // 给函数传的是分区的 index
      preservesPartitioning)
  }
```

---

#### flatMap

`flatMap`

```scala
val spark: SparkSession = Commons.sparkSession
val sc: SparkContext = spark.sparkContext

val rdd1: RDD[String] = sc.parallelize(Array("a as da ", "dsa da da f g a h dd"), 2)

val value: RDD[String] = rdd1.flatMap(a => a.split(" "))

spark.close()
```

源码

```scala
def flatMap[U: ClassTag](f: T => TraversableOnce[U]): RDD[U] = withScope {
  val cleanF = sc.clean(f)
  new MapPartitionsRDD[U, T](this, (_, _, iter) => iter.flatMap(cleanF))
  // 迭代器的 flatMap 调用我们传入的函数
}
```

这里和 `map filter` 基本是一致的。

注意这里传入的函数 f的签名 `f: T => TraversableOnce[U]`

需要传入一个可以被压平的数据类型。

---

#### groupByKey

`groupbyKey`

```scala
val spark: SparkSession = Commons.sparkSession
val sc: SparkContext = spark.sparkContext

val rdd1: RDD[String] = sc.parallelize(List("spark", "hadoop", "spark","hive", "flink", "hbase", "hadoop", "flink", "hbase"),
                                       2)
val value: RDD[(String, Int)] = rdd1.map((_, 1))
val value1: RDD[(String, Iterable[Int])] = value.groupByKey()
spark.close()
```

`groupByKey` 的源码

```scala
def groupByKey(): RDD[(K, Iterable[V])] = self.withScope {
  groupByKey(defaultPartitioner(self)) // self 是父RDD
}


def defaultPartitioner(rdd: RDD[_], others: RDD[_]*): Partitioner = {
  // 这边的 rdd 可能会是多个，如发生 join 操作等的时候就是多个
  val rdds = (Seq(rdd) ++ others)
	
  // 找到 rdd 中分区数 > 0 的那些 rdd
  val hasPartitioner = rdds.filter(_.partitioner.exists(_.numPartitions > 0))
 
  // 分区数最大的那个 rdd
  val hasMaxPartitioner: Option[RDD[_]] = if (hasPartitioner.nonEmpty) {
    Some(hasPartitioner.maxBy(_.partitions.length))
  } else {
    None
  }

// 并行度，如果给了 spark.default.parallelism 参数，那么并行度就是父 rdd 上下文中的 defaultParallelism
// 否则并行度就是父 rdd 中最大的那个分区数量
  // defaultNumPartitions 从这里来看这个值要么是从父 rdd 中来的，要么是sc上下文中来的
  // sc 中的defaultParallelism 猜测是用户通过 spark.default.parallelism 设置的。
  val defaultNumPartitions = if (rdd.context.conf.contains("spark.default.parallelism")) {
    rdd.context.defaultParallelism
  } else {
    rdds.map(_.partitions.length).max
  }

  // If the existing max partitioner is an eligible one, or its partitions number is larger
  // than or equal to the default number of partitions, use the existing partitioner.
  // 看这里的翻译，如果存在一个最大分区的 partitioner，且它是合格的，且分区数大于默认分区数，那么使用
  // 最大数的分区器
  // 否则新创建一个分区器
  // 且分区器的个数就是 defaultNumPartitions(要么是父 rdd 中最大的分区数，要么是用户设置的)
  if (hasMaxPartitioner.nonEmpty && (isEligiblePartitioner(hasMaxPartitioner.get, rdds) ||
                                     defaultNumPartitions <= hasMaxPartitioner.get.getNumPartitions)) {
    hasMaxPartitioner.get.partitioner.get
  } else {
    new HashPartitioner(defaultNumPartitions)
  }
}
```

产生分区index

```scala
class HashPartitioner(partitions: Int) extends Partitioner {
  require(partitions >= 0, s"Number of partitions ($partitions) cannot be negative.")

  def numPartitions: Int = partitions

  // 产生分区index
  // 在 shuffle write 的时候调用，将数据写到那个 分区中
  def getPartition(key: Any): Int = key match {
    case null => 0
    case _ => Utils.nonNegativeMod(key.hashCode, numPartitions)
    // 哈希计算分区 index
  }

  override def equals(other: Any): Boolean = other match {
    case h: HashPartitioner =>
      h.numPartitions == numPartitions
    case _ =>
      false
  }

  override def hashCode: Int = numPartitions
}


 /* Calculates 'x' modulo 'mod', takes to consideration sign of x,
  * i.e. if 'x' is negative, than 'x' % 'mod' is negative too
  * so function return (x % mod) + mod in that case.
  */
  // 小于的时候回再和 mod 进行相加，确保取模之后的值是在 [0, mod] 内
  def nonNegativeMod(x: Int, mod: Int): Int = {
    val rawMod = x % mod
    rawMod + (if (rawMod < 0) mod else 0)
  }

// 测试这个方法
println(nonNegativeMod(1, 10))
println(nonNegativeMod(6, 10))
println(nonNegativeMod(16, 10))
println(nonNegativeMod(-13, 10))

rawMod: 1,  1
rawMod: 6,  6
rawMod: 6,  6
rawMod: -3, 7
```

接下来看看 `groupByKey` 的源码

```scala
def groupByKey(partitioner: Partitioner): RDD[(K, Iterable[V])] = self.withScope {
  // groupByKey shouldn't use map side combine because map side combine does not
  // 注释中说明 groupByKey 不会再 map side 进行聚合的
  // reduce the amount of data shuffled and requires all map side data be inserted
  // into a hash table, leading to more objects in the old gen.
  val createCombiner = (v: V) => CompactBuffer(v) 
  // 分区中的第一个元素，包为一个CompactBuffer，初始化操作
  val mergeValue = (buf: CompactBuffer[V], v: V) => buf += v
  // 分区中后来的元素追加到初始化创建的 CompactBuffer
  val mergeCombiners = (c1: CompactBuffer[V], c2: CompactBuffer[V]) => c1 ++= c2
  // 分区之间的 CompactBuffer 的组合方式
  // mapSideCombine = false 不允许 mapSide 有聚合操作，仅仅是收集数据
  val bufs = combineByKeyWithClassTag[CompactBuffer[V]](
    createCombiner, mergeValue, mergeCombiners, partitioner, mapSideCombine = false)
  bufs.asInstanceOf[RDD[(K, Iterable[V])]]
}
```

继续

```scala
  def combineByKeyWithClassTag[C](
      createCombiner: V => C,
      mergeValue: (C, V) => C,
      mergeCombiners: (C, C) => C,
      partitioner: Partitioner,
      mapSideCombine: Boolean = true,
      serializer: Serializer = null)(implicit ct: ClassTag[C]): RDD[(K, C)] = self.withScope {
    require(mergeCombiners != null, "mergeCombiners must be defined") // required as of Spark 0.9.0
    // 做一些检查
    if (keyClass.isArray) {
      if (mapSideCombine) {
        throw new SparkException("Cannot use map-side combining with array keys.")
      }
      if (partitioner.isInstanceOf[HashPartitioner]) {
        throw new SparkException("HashPartitioner cannot partition array keys.")
      }
    }
    // aggregator
    val aggregator = new Aggregator[K, V, C](
      self.context.clean(createCombiner),
      self.context.clean(mergeValue),
      self.context.clean(mergeCombiners))
    if (self.partitioner == Some(partitioner)) {
      self.mapPartitions(iter => {
        val context = TaskContext.get()
        new InterruptibleIterator(context, aggregator.combineValuesByKey(iter, context))
      }, preservesPartitioning = true)
    } else {
      // 创建 ShuffledRDD，并将对应的操作都进行赋值
      new ShuffledRDD[K, V, C](self, partitioner)
        .setSerializer(serializer)
        .setAggregator(aggregator)
        .setMapSideCombine(mapSideCombine)
    }
  }
```

使用 `spark` 底层的 `shuffledRDD` 写一个 `groupByKey`

```scala
val spark: SparkSession = Commons.sparkSession
    val sc: SparkContext = spark.sparkContext

    val rdd1: RDD[String] = sc.parallelize(List("spark", "hadoop", "spark","hive", "flink", "hbase", "hadoop", "flink", "hbase"),
      2)
    val value: RDD[(String, Int)] = rdd1.map((_, 1))

    val shuffledRdd: ShuffledRDD[String, Int, ArrayBuffer[Int]] = new ShuffledRDD[String, Int, ArrayBuffer[Int]](
      value,
      new HashPartitioner(value.partitions.length)
    )

    // 禁止 map side 的聚合
    shuffledRdd.setMapSideCombine(false)
    // map 端执行
    val createCombiner:Int => ArrayBuffer[Int] = a => ArrayBuffer[Int](a)
    val mergeValue: (ArrayBuffer[Int], Int) => ArrayBuffer[Int] = (buf, a) => buf += (a)

    // shuffle read 之后执行
    val mergeCombiners: (ArrayBuffer[Int], ArrayBuffer[Int]) => ArrayBuffer[Int] = (a, b) => a ++ b

    shuffledRdd.setAggregator(new Aggregator[String, Int, ArrayBuffer[Int]](
      createCombiner,
      mergeValue,
      mergeCombiners))

    println(shuffledRdd.collect().mkString(","))
```

#### groupBy

`groupBy`

```scala
// 分组的结果 Iterable 中还持有 key
// 而 groupByKey 分组之后的 Iterable 不在有持有 key
// groupBy 更加的灵活，但是shuffle 的时候会传输更多的数据
// groupBy 可以更具元组中的任何一个位置的元素进行 分组
val unit: RDD[(String, Iterable[(String, Int)])] = value.groupBy(a => a._1)

//    val value1: RDD[(String, Iterable[Int])] = value.groupByKey()
```

看看 `groupBy` 的源码

```scala
def groupBy[K](f: T => K)(implicit kt: ClassTag[K]): RDD[(K, Iterable[T])] = withScope {
  groupBy[K](f, defaultPartitioner(this))
}

def groupBy[K](f: T => K, p: Partitioner)(implicit kt: ClassTag[K], ord: Ordering[K] = null)
: RDD[(K, Iterable[T])] = withScope {
  val cleanF = sc.clean(f)
  this.map(t => (cleanF(t), t)).groupByKey(p)
  // 底层还是掉了 groupByKey， 在spark 内部有新包了个元组，元组的第一个元素就是函数选出的那个位置的元
  // 素, 也就是groupBy = map.groupByKey
  // value.map(a => (a._1, a)).groupByKey()
}
```

---

#### reduceByKey

`reduceByKey`:  底层使用了 `combineByKeyWithClassTag`

```scala
val unit: RDD[(String, Int)] = value.reduceByKey((a, b) => a + b)

def reduceByKey(func: (V, V) => V): RDD[(K, V)] = self.withScope {
  reduceByKey(defaultPartitioner(self), func)
}

def reduceByKey(partitioner: Partitioner, func: (V, V) => V): RDD[(K, V)] = self.withScope {
  combineByKeyWithClassTag[V]((v: V) => v, func, func, partitioner)
  // 这里也可以看出来，分区内的计算和分区间的计算都是使用同一个函数 func，
  // 就是我们传进来的那个
}


def combineByKeyWithClassTag[C](
      createCombiner: V => C,
      mergeValue: (C, V) => C, // 这里的函数类型相同
      mergeCombiners: (C, C) => C, // 这里的函数类型相同
      partitioner: Partitioner,
      mapSideCombine: Boolean = true, 
  	  // 这个值设置的是 true，表示可以进行 mapSide的聚合
      serializer: Serializer = null)(implicit ct: ClassTag[C]): RDD[(K, C)] = self.withScope {
    require(mergeCombiners != null, "mergeCombiners must be defined") // required as of Spark 0.9.0
    if (keyClass.isArray) {
      if (mapSideCombine) {
        throw new SparkException("Cannot use map-side combining with array keys.")
      }
      if (partitioner.isInstanceOf[HashPartitioner]) {
        throw new SparkException("HashPartitioner cannot partition array keys.")
      }
    }
  // 这里后面的函数和 groupByKey 是一样的。
    val aggregator = new Aggregator[K, V, C](
      self.context.clean(createCombiner),
      self.context.clean(mergeValue),
      self.context.clean(mergeCombiners))
    if (self.partitioner == Some(partitioner)) {
      self.mapPartitions(iter => {
        val context = TaskContext.get()
        new InterruptibleIterator(context, aggregator.combineValuesByKey(iter, context))
      }, preservesPartitioning = true)
    } else {
      new ShuffledRDD[K, V, C](self, partitioner)
        .setSerializer(serializer)
        .setAggregator(aggregator)
        .setMapSideCombine(mapSideCombine)
    }
  }
```

#### combineByKey

看看`combineByKey` 的代码

```scala
// 分区中的第一个元素的操作
val intToInt: Int => String = a => a.toString
// 分区中后续元素和之前操作的结果的之间的操作

val function: (String, Int) => String = (a: String, b: Int) => a + b

// 分区结果之间的操作
val function2: (String, String) => String = (a: String, b: String) => a + b
value.combineByKey(intToInt, function, function2)

// 甚至可以直接调用
value.combineByKeyWithClassTag(intToInt, function, function2, new HashPartitioner(5))
```

从上面来看，`combineByKey` 在分区间和分区内之间的操作，和`reduceByKey` 更加的灵活，可以在分区内和分区间使用不同的函数，以及函数的类型也是可以变化的。

也是可以直接使用 `ShuffledRDD` 实现`combineByKey` 的。

```scala
val shuffledRDD: ShuffledRDD[String, Int, Int] = new ShuffledRDD[String, Int, Int](
  value,
  new HashPartitioner(value.partitions.length)
)

val aggregator: Aggregator[String, Int, Int] = new Aggregator[String, Int, Int](
  (e:Int) => e,
  (e:Int, acc: Int) => acc + e,
  (accP1: Int, accP2: Int) => accP1 + accP2
)

shuffledRDD.setAggregator(aggregator)
```

#### foldByKey

`foldByKey`

```scala
def foldByKey(zeroValue: V)(func: (V, V) => V): RDD[(K, V)] = self.withScope {
  foldByKey(zeroValue, defaultPartitioner(self))(func)
}

def foldByKey(
  zeroValue: V,
  partitioner: Partitioner)(func: (V, V) => V): RDD[(K, V)] = self.withScope {
  // Serialize the zero value to a byte array so that we can get a new clone of it on each key
  val zeroBuffer = SparkEnv.get.serializer.newInstance().serialize(zeroValue)
  val zeroArray = new Array[Byte](zeroBuffer.limit)
  zeroBuffer.get(zeroArray)

  // When deserializing, use a lazy val to create just one instance of the serializer per task
  lazy val cachedSerializer = SparkEnv.get.serializer.newInstance()
  val createZero = () => cachedSerializer.deserialize[V](ByteBuffer.wrap(zeroArray))

  val cleanedFunc = self.context.clean(func)
  combineByKeyWithClassTag[V]((v: V) => cleanedFunc(createZero(), v),
                              cleanedFunc, cleanedFunc, partitioner)
}
```

---

#### aggregateByKey

`aggregateByKey`

```scala
val aaa = value.aggregateByKey("0")(
  (zero: String, ele: Int) => zero + ele,
  (elep1: String, elep2: String) => elep1 + elep2
)
```

既有`foldByKey` 的设置初始值的功能，也有`combineByKey` 的2个函数传递的功能。

```scala
def aggregateByKey[U: ClassTag](zeroValue: U)(seqOp: (U, V) => U,
                                              combOp: (U, U) => U): RDD[(K, U)] = self.withScope {
  aggregateByKey(zeroValue, defaultPartitioner(self))(seqOp, combOp)
}

def aggregateByKey[U: ClassTag](zeroValue: U, partitioner: Partitioner)(seqOp: (U, V) => U,
                                                                        combOp: (U, U) => U): RDD[(K, U)] = self.withScope {
  // Serialize the zero value to a byte array so that we can get a new clone of it on each key
  val zeroBuffer = SparkEnv.get.serializer.newInstance().serialize(zeroValue)
  val zeroArray = new Array[Byte](zeroBuffer.limit)
  zeroBuffer.get(zeroArray)

  lazy val cachedSerializer = SparkEnv.get.serializer.newInstance()
  val createZero = () => cachedSerializer.deserialize[U](ByteBuffer.wrap(zeroArray))

  // We will clean the combiner closure later in `combineByKey`
  val cleanedSeqOp = self.context.clean(seqOp)
  combineByKeyWithClassTag[U]((v: V) => cleanedSeqOp(createZero(), v),
                              cleanedSeqOp, combOp, partitioner)
}

```

#### 总结

* #### **map 基础算子**

  * `map/filter/flatMap/mapPartitions/mapPartitionsWithIndex` 的底层都是 `MapPartitionsRDD`
  * `map/filter/flatMap` 三个算子都是调用了每个分区数据(`scala iterator`) 的相对应的方法，计算的时候每个分区域的每条数据依次压入
  * `mapPartitions/mapPartitionsWithIndex` 是将整个分区数据(`scala iterator`)全部都压进去计算

* #### shuffle 聚合算子

  * 默认的分区器以及分区数

    * 使用父亲的分区器 + 分区数的条件

      1. 有父亲分区器，
      2. 父亲分区器的分区数大于默认分区个数。分区个数来源于用户配置的 `spark.default.parallelism` 或者父`rdd` 的最大分区数

    * `new partitioner`

      当第一个条件不能满足的时候，则新建一个分区器，新建的分区个数就是默认的分区个数。分区个数来源于用户配置的 `spark.default.parallelism` 或者父`rdd` 的最大分区数

  * **groupByKey** 底层是一个 `shuffledRdd`，它具有的属性有

    * `Aggregator`： 决定了`mapside` 如何操作数据、`reduceSide` 如何操作数据
    * `serializer`: 序列化器
    * 是否有 `mapSide` 的聚合操作 `mapSideCombine:Boolean`
    * 真正的计算在底层的`Aggregator` ，`groupByKey` 不能给`Aggregator` 传任何参数，在底层直接收集分组分区中的数据

  * **groupBy**

    * 相对比较灵活，可以传入一个`key` 的选择函数`groupBy` = `map` + `groupByKey`

  * **reduceByKey**

    * 底层和`groupByKey` 基本一致，不一样的地方在如传入的 `Aggregator` 
    * 和 `grouped`类的算子比较，用户可以传入一个函数，，也就是给了`Aggregator` 的`mapSide` 和 `reduceSide`端2个相同的函数

  * **combineByKey**

    * 底层和`groupByKey` 基本一致，不一样的地方在如传入的 `Aggregator` 
    * 和 `grouped`类的算子比较，用户可以传入两个函数，，也就是给了`Aggregator` 的`mapSide` 和 `reduceSide`端2个不同的函数，且2个函数类型也是可以不同的。

  * **foldByKey**

    * 和 `reduceByKey`一样，只不过多了一个初始值的功能。

  * **aggregateByKey**

    * 和 `combineByKey` 一样，可以传入2个函数，只不过多了多了一个可出传入的初值。