#### `cogroup`

> 该算子使用的很少，但是他却功能强大，因为它作为底层算子，很多其他我们使用的比较多的算子都是该算子实现的。

```scala
val rdd1: RDD[(String, Int)] = sc.parallelize(List(("hbase", 1), ("hadoop", 1), ("flink", 1), ("spark", 1)))
val rdd2: RDD[(String, Int)] = sc.parallelize(List(("spark", 2), ("hadoop", 2), ("hbase", 2), ("hive", 2)))
print(rdd1.cogroup(rdd2).collect().mkString(","))

(hive,(CompactBuffer(),CompactBuffer(2))),
(flink,(CompactBuffer(1),CompactBuffer())),
(hbase,(CompactBuffer(1),CompactBuffer(2))),
(spark,(CompactBuffer(1),CompactBuffer(2))),
(hadoop,(CompactBuffer(1),CompactBuffer(2)))
```

和 `groupBy` 类算子不同的是，这里它会将多个 `RDD` 的多个分区中的数据进行收集。每一个 `key` 会分别对应着不同`RDD`中的值。

看看气源码

```scala
  def cogroup[W](other: RDD[(K, W)]): RDD[(K, (Iterable[V], Iterable[W]))] = self.withScope {
    cogroup(other, defaultPartitioner(self, other))
  }

// 最多可以有4个 rdd 之间的 cogroup
def cogroup[W](other: RDD[(K, W)], partitioner: Partitioner)
: RDD[(K, (Iterable[V], Iterable[W]))] = self.withScope {
  if (partitioner.isInstanceOf[HashPartitioner] && keyClass.isArray) {
    throw new SparkException("HashPartitioner cannot partition array keys.")
  }
  val cg = new CoGroupedRDD[K](Seq(self, other), partitioner)
  cg.mapValues { case Array(vs, w1s) =>
    // 元祖元祖中放着2个迭代器，分别是每个RDD 中的数据
    // 这里面都有 shuffle 操作，至于里面如何shuffle 的，后续再学习shuffle 的时候，弄明白
    (vs.asInstanceOf[Iterable[V]], w1s.asInstanceOf[Iterable[W]])
  }
}
```

#### `distinct` 

> `distinct` 源码

```scala
def distinct(): RDD[T] = withScope {
  distinct(partitions.length)
}

def distinct(numPartitions: Int)(implicit ord: Ordering[T] = null): RDD[T] = withScope {
    def removeDuplicatesInPartition(partition: Iterator[T]): Iterator[T] = {
      // Create an instance of external append only map which ignores values.
      val map = new ExternalAppendOnlyMap[T, Null, Null](
        createCombiner = _ => null,
        mergeValue = (a, b) => a,
        mergeCombiners = (a, b) => a)
      map.insertAll(partition.map(_ -> null))
      map.iterator.map(_._1)
    }
  
    partitioner match {
      case Some(_) if numPartitions == partitions.length =>
        mapPartitions(removeDuplicatesInPartition, preservesPartitioning = true)
      // map 方法本身就持有该 rdd， 所以这里只传入一个函数，然后就可以将该函数 map 到当前rdd
      // 将当前rdd 中的每个数都转为元素，然后使用 reduceByKey 再map 端和 reduce 端分别聚合
      // 可以获取唯一值
      case _ => map(x => (x, null)).reduceByKey((x, _) => x, numPartitions).map(_._1)
    }
}
```

学习其中最重要的代码片段就是

```scala
value.map(x => (x, null)).reduceByKey((x,_) => x)
```

#### `intersaction` 算子

> 使用 `cogroup` 实现 交集功能

```scala
val rdd1: RDD[(String, Int)] = sc.parallelize(List(("hbase", 1), ("hadoop", 1), ("flink", 1), ("spark", 1)))
val rdd2: RDD[(String, Int)] = sc.parallelize(List(("spark", 2), ("hadoop", 2), ("hbase", 2), ("hive", 2)))
val value: RDD[(String, Int)] = rdd1.intersection(rdd2)

def intersection(other: RDD[T]): RDD[T] = withScope {
  this.map(v => (v, null)).cogroup(other.map(v => (v, null)))
   // 就是使用 cogroup 实现的 interaction 功能
  .filter { case (_, (leftGroup, rightGroup)) => leftGroup.nonEmpty && rightGroup.nonEmpty }
  .keys
}
```

#### `Join` 算子

> 均是以 `cogroup` 算子为基础实现的

```scala
val rdd1: RDD[(String, Int)] = sc.parallelize(List(("hbase", 1), ("hadoop", 1), ("flink", 1), ("spark", 1)))
val rdd2: RDD[(String, Int)] = sc.parallelize(List(("spark", 2), ("hadoop", 2), ("hbase", 2), ("hive", 2)))

val value: RDD[(String, (Int, Int))] = rdd1.join(rdd2)
// 输出结果 (hbase,(1,2)), (hbase,(1,22)), (spark,(1,2)), (hadoop,(1,2))
def join[W](other: RDD[(K, W)], partitioner: Partitioner): RDD[(K, (V, W))] = self.withScope {
  this.cogroup(other, partitioner).flatMapValues( pair =>
     // 但凡这里有一个 key 对应的 iterator 是空 buffer 那么这里就不会 yield 数据
     // 注意这里的 join 的结果和平时如 mysql 中的join 是不一样的。这里相当于是双层循环                                              
     for (v <- pair._1.iterator; w <- pair._2.iterator) yield (v, w)
  )
}
```

还有一起看看算子

* `leftOutterJoin`

```scala
val value: RDD[(String, (Int, Option[Int]))] = rdd1.leftOuterJoin(rdd2)

def leftOuterJoin[W](
  other: RDD[(K, W)],
  partitioner: Partitioner): RDD[(K, (V, Option[W]))] = self.withScope {
  this.cogroup(other, partitioner).flatMapValues { pair =>
    if (pair._2.isEmpty) {
      // 注意上面提到的，如果pair._2(iterator) 是空，那么 yield 是不会产生数据的
      // 所以这里特殊处理
      pair._1.iterator.map(v => (v, None))
    } else {
      for (v <- pair._1.iterator; w <- pair._2.iterator) yield (v, Some(w))
    }
  }
}
```

* `rightOuterJoin`

```scala
val value: RDD[(String, (Option[Int], Int))] = rdd1.rightOuterJoin(rdd2)

def rightOuterJoin[W](other: RDD[(K, W)], partitioner: Partitioner)
: RDD[(K, (Option[V], W))] = self.withScope {
  this.cogroup(other, partitioner).flatMapValues { pair =>
    if (pair._1.isEmpty) {
      pair._2.iterator.map(w => (None, w))
    } else {
      for (v <- pair._1.iterator; w <- pair._2.iterator) yield (Some(v), w)
    }
  }
}
```

* `fullOuterJoin`

```scala
val value: RDD[(String, (Option[Int], Option[Int]))] = rdd1.fullOuterJoin(rdd2)

def fullOuterJoin[W](other: RDD[(K, W)], partitioner: Partitioner)
: RDD[(K, (Option[V], Option[W]))] = self.withScope {
  this.cogroup(other, partitioner).flatMapValues {
    // 处理出现空的情况
    case (vs, Seq()) => vs.iterator.map(v => (Some(v), None))
    case (Seq(), ws) => ws.iterator.map(w => (None, Some(w)))
    case (vs, ws) => for (v <- vs.iterator; w <- ws.iterator) yield (Some(v), Some(w))
  }
}
```

