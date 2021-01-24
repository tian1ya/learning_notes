Despite their utility, **key/value operations can lead to a number of performance issues**. In fact, most expensive operations in Spark fit into the key/value pair paradigm because most wide transformations are key/value transformations, and most require some fine tuning and care to be performant.



operations on key/value pairs can cause:

* Out-of-memory errors in the driver
* Out-of-memory errors on the executor nodes
* Shuffle failures
* “Straggler tasks” or partitions, which are especially slow to compute

The last three performance issues—out of memory on the executors, shuffles, and straggler tasks—are all most often caused by **shuffles associated with the wide transformations in the PairRDDFunctions and OrderedRDDFunctions classes**

---

### shuffle less  and shuffle better

**shuffle less**

* make sure to preserve partitioning across narrow transformations to avoid reshuffling data
* use the same partitioner on a sequence of wide transforma‐ tions

**shuffle better**

* using wide transformations such as reduceByKey and aggregateByKey that can preform map-side reductions and that do not require loading all the records for one key into memory

---

### Task: return the nth best element in each column

```scala
  val df: DataFrame = Seq[(String, Double, Double, Double,Double)](
    ("mama",     15.0, 0.25, 2467.0, 0.0),
    ("papa",     2.0,  1000, 35.4,   0.0),
    ("baby",     10.0, 2.0,  50.0,   0.0),
    ("baby toy", 3.0,  8.5,  0.2,    98.0)
  ).toDF("name", "happiness", "niceness", "softness", "sweetness")
```



```scala
def findRankStatistics(dataFrame: DataFrame, ranks: List[Long]): Map[Int, Iterable[Double]] = {
    require(ranks.forall(_>0))

    val numberOfColumns = dataFrame.schema.length
    var i = 1
    var result = Map[Int, Iterable[Double]]()

    while (i < numberOfColumns) {
      val col = dataFrame.rdd.map(row => row.getDouble(i))

      // value -> index
      val sortedCol: RDD[(Double, Long)] = col.sortBy(v => v).zipWithIndex()

      //only keeps ranks latest value
      val ranksOnly = sortedCol
        .filter{ case (colValue, index) => ranks.contains(index + 1)}
        .keys

      val list = ranksOnly.collect()
      result += (i -> list)
      i+=1
    }
    result
  }
```

This code is rebust but very slow, since it has to sort the data once for each column。

**groupByKey  case**

GroupByKey returns an iterator of elements by each key, so to sort the elements by key we have to convert the iterator to an array and then sort the.

```scala
  def mapToKeyValuePairs(dataFrame: DataFrame) :RDD[(Int, Double)] = {
    val rowLength = dataFrame.schema.length
    dataFrame.rdd.flatMap(row => Range(1, rowLength).map(i => (i, row.getDouble(i))))
  }

def findRankStatistics(dataFrame: DataFrame, ranks:List[Long]): scala.collection.Map[Int,  Iterable[Double]] = {
    require(ranks.forall(_>0))

    val pairRDD: RDD[(Int, Double)] = mapToKeyValuePairs(dataFrame)

    val groupColumns: RDD[(Int, Iterable[Double])] = pairRDD.groupByKey()

    groupColumns.mapValues(
      iter =>  {
        val sortedIter = iter.toArray.sorted
        sortedIter.toIterable.zipWithIndex.flatMap({
          case (colValue, index) => {
            if (ranks.contains(index + 1)) {
              Iterator(colValue)
            } else {
              Iterator.empty
            }
          }
        })
    }).collectAsMap()
  }
```

This solution has several advantages.

* the correct answer.
* very short and easy to understand
* t leverages out-of-the-box Spark and Scala func‐ tions and so it introduces few edge cases and is relatively easy to test.
* rela‐ tively efficient because it only requires one shuffle in the groupByKey step and because the sorting step can be computed as a narrow transformation on the executors.

but：

* the danger of memory errors is minimal because at the point of collecting

* **groupByKey is known to cause memory errors at scale.**

  > **“groups” created by groupByKey are always iterators, which can’t be distributed. This causes an expensive “shuffled read” step in which Spark has to read all of the shuffled data from disk and into memory**. In other words, Spark has to read almost all of the shuffled data into memory。
  >
  > the following four functions—**reduceByKey, treeAggregate, aggregateByKey**, and foldByKey—are implemented to use mapside combinations, meaning that records with the same key are combined before they are shuffled. This can greatly reduce the shuffled read

**is better to choose aggregation operations that can do some map-side reduction to decrease the number of records by key before shuffling， aggragateByKey or reduceByKey**

---

**RDD without know partitioner**

> An RDD without a known partitioner will assign data to partitions according only to the data size and partition size。
>
> The partitioner object defines a mapping from the records in an RDD to a partition index， By assign‐ ing a partitioner to an RDD, we can guarantee something about the records on each partition。

there are  3 methods  that exist exclusively to change the way an RDD is partitioned

* repartition and coalesce can be used to simply change the number of partitions that the RDD uses
  * repartition shuffles the RDD with a hash partitioner and the given number of partitions
  * coalesce, on the other hand, is an optimized version of repar tition that avoids a full shuffle if the desired number of partitions is less than the current number of partitions
    * is an optimized version of repar tition that avoids a full shuffle if the desired number of partitions is less than the current number of partitions
    * if coalesce increases the number of partitions it has the same behavior as repartition
* partitionBy allows for much more control in the way that the records are partioned since the partioner  supports defining a function that assigns a partition to a  record based on the value of that key.

**In all cases, repartittion  and coalesce do  not assign a know partitioner to the RDD**

In some instances, when an RDD has a known partitioner, Spark can rely on the information about data locality provided by the partitioner to avoid doing a shuffle even if the transformation has wide dependencies（如果一个RDD由一个一直的partitioner，那么RDD 在执行操作的时候，根据partitioner 提供的信息，识别并操作本partition 中的数据(local data), 从而避免shuffle，因为一个partition 中会有一个task，所以一个partitioner 也会影响到task 的执行）

**Two partitioners**

Spark privided 2 partitions `HashPartitioner` and `RangePartitioner`， a partitioner is  a interface, its has 2 methods  `numPartitions`(define the number of partitions in the RDD after partittioning)  and `getPartition` defines  a mapping from a key to the interger index of the partition.

It is possiable to define a custom partitioner。

**Hash Partitioning**: default partitioner for pair RDD(not ordered RDD operations)

the hash partiitioner requires a partitions parameters, which determines the number of partitions in the output RDD  and the number of bins use in the hashing function, if not set spark will use `spark.default.parallelism` value in the SparkConf。

**Range Partitioning**

Range partitioning assigns records whose key  are in the same range to a given partition, `Range` partitioning  is required for sorting since it ensures that by sorting records within a given parttition, the entire RDD will be sorted, The RDD must be a tuple and the keys must have an ordering defined.

**Custom partitioning**

Spark allows the user to define a custom partitioner， you must implement the following methods:

* numPartitions: A method that returns an integer number of partitions
* getPartition: A method that takes a key returns an integer representing the index of the partition that specifies where records with that key belong
* equals: An (optional) method to define equality between partitioners.
* hashcode: This method is required only if the equals method has been overridden

---

**Preserving partitioning Information Across Transformation**

some narrow transformations，  such mapValues, preverve the partitioning of  an RDD if it exists, Unless a transformation is known to only change the value part of the key/value pair in Spark, the resulting RDD will not have a known partitioner, note that some operatos that not the key, such flatMap or map,  the resulting RDD will not have a known partitioner. Instead, if we don’t want to modify the keys, we can call the mapValues function (defined only on pair RDDs) because it keeps the keys, and therefore the partitioner

**The *mapPartitions* function will** also preserve the partition if the preserves Partitioning flag is set to true.

```scala
private val value: RDD[(String, Int)] = spark.sparkContext.parallelize(Seq(("a",1),("b",2)))
private val value1: RDD[(String, Int)] = value.sortByKey()

private val mapedTupleRDD: RDD[(String, String)] = value1.mapValues(_.toString)
require(mapedTupleRDD.partitioner.isDefined, true)

val map = mapedTupleRDD.map(pair => (pair._1, pair._2.toString))
require(map.partitioner.isEmpty, true)
```

---

**Co-located and Co-Partitioned RDD**

*Co-located* RDDs are RDDs with the same partitioner that reside in the same physical location in memory, We say that mul‐ tiple RDDs are *co-partitioned* if they are partitioned by the same known partitioner,

We say that partitions are *co-located* if they are both loaded into memory on the same machine。

---

**Secondary Sort and repartitionAndSortWithinPartitions**

repartitionAndSortWithinPartitions function is a **wide transformation** that takes a partitioner defined on the argument RDD and an implicit ordering, which must be defined on the keys of the RDD, the function partitions the data according to the partitioner argument, and then sorts the records on each partition according to the ording, ording is not required to given, spark can infer that and ording and will sort accordingly, of course we can define a ording function.

**sortByKey** it calls the reparti tionAndSortWithinPartitions function with a RangePartitioner and uses implicit ordering defined on the keys. Then repartitionAndSort WithinPartitions will sort the values on each partition (each range of data) and thus the entire result will be sorted by key

---

the records to be arranged according to two different keys

using groupByKey to ensure that the values associated with each key are coalesced and
then sorting the elements asso‐ ciated with each key as a separate step

Using repartitionAndSortWithinPartitions we can partition on the column index and sort on
the value in each column. We are then guaranteed that all the values associated with each
column will be on one partition and that they will be in sorted order of the value.

**The logic of secondary sort generalizes well beyond simply ordering data**

what we do  on `Goldilocks example` it requires us to shuffle on one key (the column index) and then order the data within each key by value。

rather than using groupByKey to ensure that the values associated with each key are coalesced and then sorting the elements asso‐ ciated with each key as a separate step。

we can use repartitionAndSortWithinPartitions，

we can partition on the column index and sort on the value in each column

We are then guaranteed that all the values associated with each column will be on one partition and that they will be in sorted order of the value.

We can simply loop through the elements on each parti‐ tion, filter for the desired rank statistics in one pass through the data, and use the groupSorted function to combine the rank statistics associated with our column.

**The ordering and partition in repartitionAndSortWithinPartitions must be defined on the keys of the RDD**

and thus we need to use the (column index, value) pairs as keys 

```scala
class ColumnIndexPartition(override val numPartitions: Int) extends Partitioner {
  override def getPartition(key: Any): Int = {
    val k = key.asInstanceOf[(Int, Double)]
    Math.abs(k._1) % numPartitions
  }
}
```

we want the elements to be ordered first by column index, and second by value. The former ensures that all the records associated with one key are on the same partition

repartitionAndSortWithinPartitions, we are able to push the work to sort each column into the shuffle stage. Since the elements are sorted after the shuffle,

if the columns are relatively long, the repartitionAndSortWithinParti tions step may still lead to failures since it still requires one executor to be able to store all of the values associated with all of the columns that have the same hash value. 

```scala
def mapToKeyValuePairs(df:DataFrame): RDD[(Int, Double)] = {
    val colLength = df.columns.length
    df.rdd.flatMap(row => Range(0, colLength).map(colIndex => (colIndex, row.getDouble(colIndex))))
  }

  def findRankStatistics(dataFrame: DataFrame, targetRanks: List[Long], partitions: Int) = {

    val pairRDD: RDD[((Int, Double), Int)] = mapToKeyValuePairs(dataFrame).map((_, 1))

    val partitioner = new ColumnIndexPartition(partitions)

    val sorted = pairRDD.repartitionAndSortWithinPartitions(partitioner)

    val filterForTargetIndex = sorted.mapPartitions(iter => {
      var currentColumnIndex = -1
      var runningTotal = 0

      iter.filter({
        case (((colIndex, value), _)) =>
          if (colIndex != currentColumnIndex) {
            currentColumnIndex = colIndex
            runningTotal = 1
          }else {
            runningTotal += 1
          }
          targetRanks.contains(runningTotal)
      })
    }.map(_._1), preservesPartitioning = true)

    groupSorted(filterForTargetIndex.collect())
  }

  // Combine the elements associated with one key
  private def groupSorted(it: Array[(Int, Double)]): Map[Int, Iterable[Double]] = {
    val res = List[(Int, ArrayBuffer[Double])]()
    it.foldLeft(res)((list, next) => list match {
    case Nil =>
      val (firstKey, value) = next
      List((firstKey, ArrayBuffer(value)))
    case head :: rest =>
      val (curKey, valueBuf) = head
      val (firstKey, value) = next
      if (!firstKey.equals(curKey)) {
        (firstKey, ArrayBuffer(value)) :: list }
      else{
        valueBuf.append(value)
      list
    }
  }).map {
      case (key, buf) => (key, buf.toIterable)
    }.toMap
  }
```

---

**More performant  solution**

let’s review some of the methods we have learned to make transformations more performant:

- Narrow transformations on key/value data are quick and easy to parallelize rela‐ tive to wide transformations that cause a shuffle.
- Partition locality can be retained across some narrow transformations following a shuffle. This applies to mapPartitions if we use preservePartitioning=true, or mapValues.
- Wide transformations are best with many unique keys. This prevents shuffles from directing a large proportion of the data to reside on one executor.
- SortByKey is a particularly good way to partition data and sort within partitions since it pushes the ordering of data on local machines into the shuffle stage.
- Using iterator-to-iterator transforms in mapPartitions prevents whole parti‐ tions from being loaded into memory.









