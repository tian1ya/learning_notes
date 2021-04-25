#### `reduce` 算子

```scala
val value: RDD[Int] = sc.parallelize(List(1, 2, 3, 4))
val i: Int = value.reduce((a, b) => a + b)

// 源码
def reduce(f: (T, T) => T): T = withScope {
  val cleanF = sc.clean(f)
  // map 端的计算
  val reducePartition: Iterator[T] => Option[T] = iter => {
    if (iter.hasNext) {
      // 这里调的是 scala 的迭代器的方法 reduceLeft
      Some(iter.reduceLeft(cleanF))
    } else {
      None
    }
  }
  
  // reduce 端的计算，注意这里是没有初始值的，从每个分区的计算结果中在去聚合结果
  var jobResult: Option[T] = None
  val mergeResult = (_: Int, taskResult: Option[T]) => {
    if (taskResult.isDefined) {
      jobResult = jobResult match {
        case Some(value) => Some(f(value, taskResult.get))
        case None => taskResult
      }
    }
  }
  sc.runJob(this, reducePartition, mergeResult)
  // 获取结果
  jobResult.getOrElse(throw new UnsupportedOperationException("empty collection"))
}
```

#### `sc.runJob` 

```scala
def runJob[T, U: ClassTag](
      rdd: RDD[T],
      processPartition: Iterator[T] => U,
      resultHandler: (Int, U) => Unit): Unit

// processPartition: a function to run on each partition of the RD
// map side 的函数, 在每个分区中得到分区结果
// resultHandler: callback to pass each result to
// 将分区结果传给这里，最终汇总计算
```

#### `collect`

```scala
def collect(): Array[T] = withScope {
  // (iter: Iterator[T]) => iter.toArray 一次收集每个迭代器(分区) 中的数据转换为 array
  val results = sc.runJob(this, (iter: Iterator[T]) => iter.toArray)
  // 将每个分区中得到的 array 都 concat 起来
  Array.concat(results: _*)
}

def runJob[T, U: ClassTag](rdd: RDD[T], func: Iterator[T] => U): Array[U] = {
  // 0 until rdd.partitions.length 遍历每一个分区
  runJob(rdd, func, 0 until rdd.partitions.length)
}
```

#### `sum`

```scala
val value: RDD[Int] = sc.parallelize(List(1, 2, 3, 4))
value.sum()

def sum(): Double = self.withScope {
  self.fold(0.0)(_ + _)
}

// 有了初始值的功能
def fold(zeroValue: T)(op: (T, T) => T): T = withScope {
  // Clone the zero value since we will also be serializing it as part of tasks
  var jobResult = Utils.clone(zeroValue, sc.env.closureSerializer.newInstance())
  val cleanOp = sc.clean(op)
  // 最主要的还是下面2个函数，
  // 用于在分区中进行计算，使用scala iter 的 fold 方法
  val foldPartition = (iter: Iterator[T]) => iter.fold(zeroValue)(cleanOp)
  // 然后收集分区中的结果到 jobResult
  val mergeResult = (_: Int, taskResult: T) => jobResult = op(jobResult, taskResult)
  sc.runJob(this, foldPartition, mergeResult)
  jobResult
}
```

#### `aggregate`

```scala
val value: RDD[Int] = sc.parallelize(List(1, 2, 3, 4))
val function: (String, Int) => String = (a, b) => a + b.toString
val function1: (String, String) => String = (a, b) => a + " : " + b
val str: String = value.aggregate("0")(function, function1)

def aggregate[U: ClassTag](zeroValue: U)(seqOp: (U, T) => U, combOp: (U, U) => U): U = withScope {
  // Clone the zero value since we will also be serializing it as part of tasks
  var jobResult = Utils.clone(zeroValue, sc.env.serializer.newInstance())
  val cleanSeqOp = sc.clean(seqOp)
  val cleanCombOp = sc.clean(combOp)
  
  // it.aggregate 也是调用的 scala iterator 上的方法
  // 这里和 aggregateByKey 也是差不多的，
  val aggregatePartition = (it: Iterator[T]) => it.aggregate(zeroValue)(cleanSeqOp, cleanCombOp)
  val mergeResult = (_: Int, taskResult: U) => jobResult = combOp(jobResult, taskResult)
  sc.runJob(this, aggregatePartition, mergeResult)
  jobResult
}
```

功能从 `reduce`  到 `aggregate` 是越来越灵活切功能越强大的。

#### `foreach`  类似于 `map`, 只不过 是一个 `action` 的算子

```scala
value.foreach(a => {
  // 注意这里的打印是在 executor 上打印的，二不是在 driver 中的
  print(a)
})

def foreach(f: T => Unit): Unit = withScope {
  val cleanF = sc.clean(f)
  // 直接执行了，没有返回值，也就是数据并不会拿到 Driver 端。只会在 Executor 中
  sc.runJob(this, (iter: Iterator[T]) => iter.foreach(cleanF))
}
```

#### `foreachPartitions`  类似于 `mapPartition`, 只不过 是一个 `action` 的算子

```scala
value.foreachPartition((a: Iterator[Int]) => {
  // 注意这里的打印是在 executor 上打印的，二不是在 driver 中的
  print("*****")
  for (elem <- a) {
    print(elem)
  }
})

def foreachPartition(f: Iterator[T] => Unit): Unit = withScope {
  val cleanF = sc.clean(f)
  // 直接执行了，没有返回值，也就是数据并不会拿到 Driver 端。
  sc.runJob(this, (iter: Iterator[T]) => cleanF(iter))
}
```

比较实用的，将数据以一个分区的形式拿出来，

而 `foreachPartitions`  使用的比较多，主要还是使用在和外界资源进行交互的的时候，如写外部数据库，在和外界的交互的时候，该算子每一个分区才会创建一个连接，而`foreach` 每条数据都会创建一条数据。

使用 `foreachPartitions` 会有的一些问题

```scala
val rdd;

val res = rdd.foreachPartitions { a => {
  	val http = 打开一个 http 连接
    a.map(aa => {
      进行了一系列操作
    })
  }
  http.cloes() 关闭 http 连接 
}

res.collect
```

上面的代码是由问题的，是因为在没有执行 `collect` 的操作的时候，这个时候`foreachPartitions` 还没有真正执行，所以你打开了一个 http 连接，但是后面又给关闭了。导致后面真正出发 collect 的时候，没有连接可用了。

但是如果不关闭 连接那么有影响效率(虽然后续 JVM GC 会回收连接对象)

改进就是增加一个是否断开连接的判断

```scala
val rdd;

val res = rdd.foreachPartitions { a => {
  	val http = 打开一个 http 连接
    a.map(aa => {
      进行了一系列操作
    })
  }
  if (!a.hasNext)
     http.cloes() 关闭 http 连接 
}

res.collect
```

---

#### `count`

```scala
// 这里总共分为了2部分，第一部分穿进去一个获取每个迭代器(分区数据)的 size，
// 返回 每个迭代器的 size 之后，将其 sum 起来，返回
def count(): Long = sc.runJob(this, Utils.getIteratorSize _).sum

def getIteratorSize(iterator: Iterator[_]): Long = {
  var count = 0L
  while (iterator.hasNext) {
    count += 1L
    iterator.next()
  }
  count
}
```

#### `top`

```scala
def top(num: Int)(implicit ord: Ordering[T]): Array[T] = withScope {
  takeOrdered(num)(ord.reverse)
}

def takeOrdered(num: Int)(implicit ord: Ordering[T]): Array[T] = withScope {
  if (num == 0) {
    Array.empty
  } else {
    val mapRDDs = mapPartitions { items =>
      // Priority keeps the largest elements, so let's reverse the ordering.
      val queue = new BoundedPriorityQueue[T](num)(ord.reverse)
      queue ++= collectionUtils.takeOrdered(items, num)(ord)
      Iterator.single(queue)
    }
    if (mapRDDs.partitions.length == 0) {
      Array.empty
    } else {
      mapRDDs.reduce { (queue1, queue2) =>
				// 这里有个好玩的点，从上面 map 计算出来的每个分区的最大的前 num 个值
        // 然后在这里对每个分区的结果进行汇总，因为这个 queue 始终是只保存了2个元素的
        // 所以queue1 ++= queue2 的结果并不是保留全部的2个queue 中的所有元素
        // 而是保留2个queue 中最大的前 num 个元素
        queue1 ++= queue2
        queue1
      }.toArray.sorted(ord)
    }
  }
}
```

#### `take`

```scala
val ints: Array[Int] = value.take(2)

def take(num: Int): Array[T] = withScope {
    val scaleUpFactor = Math.max(conf.get(RDD_LIMIT_SCALE_UP_FACTOR), 2)
    if (num == 0) {
      new Array[T](0)
    } else {
      val buf = new ArrayBuffer[T]
      val totalParts = this.partitions.length
      var partsScanned = 0
      // 做这个循环主要是，如我需要拿到10个数据，可是目前扫过的分区中我只拿到了5条数据
      // 所以还需要继续从后续的分区中继续获取数据
      while (buf.size < num && partsScanned < totalParts) {
        // The number of partitions to try in this iteration. It is ok for this number to be
        // greater than totalParts because we actually cap it at totalParts in runJob.
        var numPartsToTry = 1L
        val left = num - buf.size
        if (partsScanned > 0) {
          // If we didn't find any rows after the previous iteration, quadruple and retry.
          // Otherwise, interpolate the number of partitions we need to try, but overestimate
          // it by 50%. We also cap the estimation in the end.
          if (buf.isEmpty) {
            numPartsToTry = partsScanned * scaleUpFactor
          } else {
            // As left > 0, numPartsToTry is always >= 1
            // 计算后续还去到几个分区中尝试获取数据
            numPartsToTry = Math.ceil(1.5 * left * partsScanned / buf.size).toInt
            numPartsToTry = Math.min(numPartsToTry, partsScanned * scaleUpFactor)
          }
        }

        // p = a until b 是一个迭代器
        val p = partsScanned.until(math.min(partsScanned + numPartsToTry, totalParts).toInt)
        // 提交 job
        val res = sc.runJob(this, (it: Iterator[T]) => it.take(left).toArray, p)

        res.foreach(buf ++= _.take(num - buf.size))
        partsScanned += p.size
      }

      buf.toArray
    }
  }
```

#### `first`

```scala
def first(): T = withScope {
  take(1) match {
    case Array(t) => t
    case _ => throw new UnsupportedOperationException("empty collection")
  }
}
```

#### `min/max`

```scala
def min()(implicit ord: Ordering[T]): T = withScope {
  // 两两比较，每次获取最小值
  this.reduce(ord.min)
}

def max()(implicit ord: Ordering[T]): T = withScope {
  this.reduce(ord.max)
}
```

---

#### `cache/persist`

> ```scala
> def cache(): this.type = persist()
> 
> def persist(): this.type = persist(StorageLevel.MEMORY_ONLY)
> 
> def persist(newLevel: StorageLevel): this.type = {
>   if (isLocallyCheckpointed) {
>     // 如果已经persist，那么覆盖在 persisit
>     // This means the user previously called localCheckpoint(), which should have already
>     // marked this RDD for persisting. Here we should override the old storage level with
>     // one that is explicitly requested by the user (after adapting it to use disk).
>     persist(LocalRDDCheckpointData.transformStorageLevel(newLevel), allowOverride = true)
>   } else {
>     persist(newLevel, allowOverride = false)
>   }
> }
> ```
>
> `cache()`： 序列化到内存，调用了`persist(memory_only)`
>
> `persist(storage_level): `序列化

> 还有
>
> ```scala
> // 删除已经 persist 的数据
> def unpersist(blocking: Boolean = false): this.type = {
>   logInfo(s"Removing RDD $id from persistence list")
>   sc.unpersistRDD(id, blocking)
>   storageLevel = StorageLevel.NONE
>   this
> }
> ```

#### `实现排序`

```scala
/*
    extends Comparable[Boy]: 实现比较排序功能
    Serializable: 可以序列化类

    而使用 case class 默认是可以序列化接口的
 */
class Boy(val name: String, val id: Int, val score: Double) extends Comparable[Boy] with Serializable {
  override def compareTo(o: Boy): Int = if (this.score >= o.score) 1 else -1

  override def toString = s"Boy($name, $id, $score)"
}

/*
  属性默认就是 val 的
  本身就是可以 Serializable 的,以及 toString
 */
case class Man(name: String, id: Int, score: Double) extends Ordered[Man]{
  override def compare(that: Man): Int = if (this.score >= that.score) 1 else -1
}


val lines: RDD[String] = sc.parallelize(List("laoda,90,90", "nihao,4,2", "wode,9,8"))

val value: RDD[Man] = lines.map(line => {
  val strings = line.split(",")
  val name = strings(0)
  val int = strings(1).toInt
  val double = strings(2).toDouble
  new Man(name, int, double)
})

/*
      Boy 中没有具备 排序，所以在 sortBy 中隐士变换并没有实现该隐士方法
      需要一个 Order/Comparable 中的方法
     */
print(value.sortBy(x => x).collect().mkString(","))

```

使用隐士转换解决排序

```scala
case class Man(name: String, id: Int, score: Double)

// 另外定义 object
object ManOrder {
  implicit object manOrder extends Ordering[Man] {
    override def compare(x: Man, y: Man): Int = if (x.score >= y.score) 1 else -1
  }
}

// 或者直接在当前上下文中定义
implicit val manOrder = new Ordering[Man] {
  override def compare(x: Man, y: Man): Int = if (x.score > y.score) 1 else 0
}
```

使用 `tuple`

```scala
val value: RDD[(String, Int, Double)] = lines.map(line => {
  val strings = line.split(",")
  val name = strings(0)
  val int = strings(1).toInt
  val double = strings(2).toDouble
  (name, int, double)
})

/*
   Tuple 中是有 Order 的排序规则的
   类型 Int 或者 String 也都是可以直接排序的，* (-1) 就可以逆序了
*/
val value1: RDD[(String, Int, Double)] = value.sortBy(x => -1 * x._3)
print(value1.collect().mkString(","))
```

#### `sortBy`

> 算子返回的是一个 `RDD`，但是从`spark-UI` 中能看到该算子是返回了一个`RDD`

```scala
val value1: RDD[(String, Int, Double)] = value.sortBy(x => -1 * x._3)
```

> 这里就需要了解下分布式下的排序
>
> 1. 通过在每个分区中进行采样，获取现在数据大概的最大最小值，加入说min=1, max=1000.
> 2. 根据获取的最小最大值，进行范围分区，如partition1的范围1-> 500, partition2的方位 500-800， partition3的范围800-1000
> 3. 然后将原始数据进行范围分区`rangePartition` 将合适的值分到合适的分区中
> 4. 在分区内进行排序，保持分区内的顺序
> 5. 第四步保证了分区内的排序，而前3步保证了分区键的排序
> 6. 保证了全局的排序。

看看源码

```scala
def sortBy[K](
  f: (T) => K,
  ascending: Boolean = true,
  numPartitions: Int = this.partitions.length)
(implicit ord: Ordering[K], ctag: ClassTag[K]): RDD[T] = withScope {
  this.keyBy[K](f) // 这里会有一个 MapPartitionsRDD
  .sortByKey(ascending, numPartitions) // 这里会有 RangePartitioner -> ShuffledRDD 以及一次 collect 操作
  .values // 这里会有 MapPartitionsRDD
}

def sortByKey(ascending: Boolean = true, numPartitions: Int = self.partitions.length)
: RDD[(K, V)] = self.withScope
{
  val part = new RangePartitioner(numPartitions, self, ascending)
  new ShuffledRDD[K, V, V](self, part)
  .setKeyOrdering(if (ascending) ordering else ordering.reverse)
}
```

看看`RangePartitioner`源码

```scala
def this(partitions: Int, rdd: RDD[_ <: Product2[K, V]], ascending: Boolean) = {
  // 
  this(partitions, rdd, ascending, samplePointsPerPartitionHint = 20)
}
```

构造函数中最关键的代码

```scala
private var rangeBounds: Array[K] = {
  if (partitions <= 1) {
    // 如果分区数小于1，直接返回，后续直接排序就好
    Array.empty
  } else {
    val sampleSize = math.min(samplePointsPerPartitionHint.toDouble * partitions, 1e6)
    // 计算得到分区内的采样比例
    val sampleSizePerPartition = math.ceil(3.0 * sampleSize / rdd.partitions.length).toInt
    // 采样得到结果
    // (total number of items, an array of (partitionId, number of items, sample))
    val (numItems, sketched) = RangePartitioner.sketch(rdd.map(_._1), sampleSizePerPartition)
    if (numItems == 0L) {
      Array.empty
    } else {
      // If a partition contains much more than the average number of items, we re-sample from it
      // to ensure that enough items are collected from that partition.
      val fraction = math.min(sampleSize / math.max(numItems, 1L), 1.0)
      val candidates = ArrayBuffer.empty[(K, Float)]
      val imbalancedPartitions = mutable.Set.empty[Int]
      sketched.foreach { case (idx, n, sample) =>
        if (fraction * n > sampleSizePerPartition) {
          imbalancedPartitions += idx
        } else {
          // The weight is 1 over the sampling probability.
          val weight = (n.toDouble / sample.length).toFloat
          for (key <- sample) {
            candidates += ((key, weight))
          }
        }
      }
      if (imbalancedPartitions.nonEmpty) {
        // Re-sample imbalanced partitions with the desired sampling probability.
        val imbalanced = new PartitionPruningRDD(rdd.map(_._1), imbalancedPartitions.contains)
        val seed = byteswap32(-rdd.id - 1)
        val reSampled = imbalanced.sample(withReplacement = false, fraction, seed).collect()
        val weight = (1.0 / fraction).toFloat
        candidates ++= reSampled.map(x => (x, weight))
      }
      // 中间细节太多，直接看这里吧
      // 它会返回一个 Array[Int] 里面就是每个 partition 的范围
      RangePartitioner.determineBounds(candidates, math.min(partitions, candidates.size))
    }
  }
}
```

看看 `sketch` 的代码

```scala
def sketch[K : ClassTag](
  rdd: RDD[K],
  sampleSizePerPartition: Int): (Long, Array[(Int, Long, Array[K])]) = {
  val shift = rdd.id
  // val classTagK = classTag[K] // to avoid serializing the entire partitioner object
  val sketched = rdd.mapPartitionsWithIndex { (idx, iter) =>
    val seed = byteswap32(idx ^ (shift << 16))
    val (sample, n) = SamplingUtils.reservoirSampleAndCount(
      iter, sampleSizePerPartition, seed)
    Iterator((idx, n, sample))
    // 这里有一个 collect操作，所以 sortBy 会提交一个 job
  }.collect()
  val numItems = sketched.map(_._2).sum
  // 返回的数据
  // (total number of items, an array of (partitionId, number of items, sample))
  (numItems, sketched)
}
```

总结上面的源码，从开始执行 `sortBy`  总共会有如下的`RDD`

`MapPartitionsRDD-> ShuffledRDD(RangePartitioner)->MapPartitionsRDD `



