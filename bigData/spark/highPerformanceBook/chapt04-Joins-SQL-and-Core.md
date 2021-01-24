#### Core Spark Joins

* Focus on RDD type joins

Join 操作是非常耗费资源的，如果 key 在同一个`partition` 那么 `join` 操作就可以在本地执行，否则就需要有`shuffle` 操作， 包含有相同`key` 的RDD 在同一个`partition` 中。

**guide lines of use Joins**

* Both RDD has duplicate keys: the join can cause the size of the data  to expand dramatically, It may better to perform a `distinct` or `combineByKey` to reduce the key space or to reuse cogroup to handle duplicate keys
* Keys not present in both RDD: risk to losing data, It may safer to use an outer join, than filter the data after the join

****

```scala
// Return an RDD containing all pairs of elements with matching keys in `this` and
// `other`. Each pair of elements will be returned as a (k, (v1, v2)) tuple, where (k, //v1) is in `this` and (k, v2) is in `other`.

def joinScoreWithAddress1(scoreRDD: RDD[(Long, Double)],
                            addressRDD: RDD[(Long, String)]):RDD[(Long, (Double, String))] = {
    val joinedRDD = scoreRDD.join(addressRDD)
    joinedRDD.reduceByKey((x,y) => if (x._1 > y._1) x else y)
  }
```

**Pre-filter before join**

```scala
def joinScoreWithAddress2(scoreRDD: RDD[(Long, Double)],
                            addressRDD: RDD[(Long, String)]):RDD[(Long, (Double, String))] = {
    val bestScoreRDD = scoreRDD.reduceByKey((x,y) => if (x._1 > y._1) x else y)
    bestScoreRDD.join(addressRDD)
  }
```

**outer join to keep all data **

> perform a left outer join to keep all keys for processing even those missing in the right RDD by using **leftOuterJoin** in place of join,  Spark also has **fullOuterJoin** and **rightOuterJoin** depending on which records we wish to keep. Any missing values are None and present values are Some('x').

```scala
def outerJoinScoreWithAddress(scoreRDD: RDD[(Long, Double)],
                                addressRDD: RDD[(Long, String)]): RDD[(Long, (Double, Option[String]))] = {
    val joindRDD = scoreRDD.leftOuterJoin(addressRDD)
    joindRDD.reduceByKey((x,y) => if (x._1 > y._1) x else y)
  }
```

**avoid shuffle if**

* Both RDDs have a know partitioner
* One of the datasets is small enougth to fit in memory, in which case we can do a broadcast has join

**如果RDD 是并列在同一个分区，那么网络中数据传输就可以避免了**

> 使用 aggregateByKey  或者  reduceByKey，在进行操作之前就将需要的数据persist 到partition local，而避免shuffle

```scala
  def joinScoreWithAddress3(scoreRDD: RDD[(Long, Double)],
                            addressRDD: RDD[(Long, String)]):RDD[(Long, (Double, String))] = {

    /*
        If addressRDD has a known partitioner we should use that,
        otherwise it has a default hash parttioner, which we can reconstruct by
        getting the number of partitions.
     */
    val addressDataPartitioner = addressRDD.partitioner match {
      case (Some(p)) => p
      case (None) => new HashPartitioner(addressRDD.partitions.length)
    }

 /*
   	you can prevent the shuffle by adding a hash partitioner with the same number of 
   	partitions as an explicit argument to the first operation and persisting the RDD 
   	before the join
 */
    val bestScoreDate = scoreRDD.reduceByKey(addressDataPartitioner, (x,y) => if (x > y) 
    x else y)
    bestScoreDate.join(addressRDD)
  }
```

**using a broadcast hash join to speeding up joins**

> 将数据比较小的RDD 读到内存中 广播开来 ，然后这个小的广播变量会在大的RDD的map端完成join，spark core 并不支持 broadcast hash join，不过可以自己写一个

```scala
def manualBoradCastHashJoin[K: Ordering: ClassTag, V1: ClassTag, V2: ClassTag](bigRDD: RDD[(K, V1)],
                                                                                 smallRDD: RDD[(K,V2)]) = {
    val smallRDDLocal: collection.Map[K, V2] = smallRDD.collectAsMap()
    
    bigRDD.sparkContext.broadcast(smallRDDLocal)
    
    bigRDD.mapPartitions(iter => {
      iter.flatMap{
        case (k, v1) => smallRDDLocal.get(k) match {
          case None => Seq.empty[(K, (V1, V2))]
          case Some(v2: V2) => Seq((k, (v1, v2)))
        }
      }
    }, preservesPartitioning = true)
  }
```

----

**Spark SQL will do joins more efficient,  or the other hand, you do not control the partitioner for DF or DS, so you  can not manually avoid shuffles**

```scala
case class example(name: String, size: Double)
case class example1(name: String, zip: String)
object SQLJoins extends App {
  private val spark: SparkSession = Commons.spark
  import spark.implicits._
  
  val left = Seq(
    ("Happy", 1.0),
    ("Sad", 0.9),
    ("Happy", 1.5),
    ("Coffee", 3.0))

  val right = Seq(
    ("Happy", "94110"),
    ("Happy", "94103"),
    ("Coffee", "10504"),
    ("Tea", "07012")
  )

  val leftDF = spark.sparkContext.parallelize(left).map(row => example(row._1, row._2)).toDF
  val rightDF = spark.sparkContext.parallelize(right).map(row => example1(row._1, row._2)).toDF

// require the key be present in both tables, or the result is dropped
+------+----+------+-----+
|  name|size|  name|  zip|
+------+----+------+-----+
|Coffee| 3.0|Coffee|10504|
| Happy| 1.0| Happy|94110|
| Happy| 1.0| Happy|94103|
| Happy| 1.5| Happy|94110|
| Happy| 1.5| Happy|94103|
+------+----+------+-----+
  
+------+----+------+-----+
|  name|size|  name|  zip|
+------+----+------+-----+
|Coffee| 3.0|Coffee|10504|
| Happy| 1.0| Happy|94110|
| Happy| 1.0| Happy|94103|
| Happy| 1.5| Happy|94110|
| Happy| 1.5| Happy|94103|
+------+----+------+-----+
```

Spark’s supported join types are `inner,` `left_outer` (aliased as `outer`), `left_anti,` `right_outer,` `full_outer,` and `left_semi.`

 With the exception of `left_semi` these join types all join the two tables, but they behave differently when handling rows that do not have keys in both tables.

`inner`: **is default, require the key be present in both tables, or the result is dropped.**

**left_outer**: result will keep all of keys from the left table, and any rows without matching keys in the right table will have null values ,but row keeps in right table not in left table will not present in result,  **right_outer  is same way**, 左侧不存在的右侧存在不会存在在结果中，左侧的值会全部保留，如果左侧存在右侧不存在那么join之后，右侧部分会是null

```scala
val frame1: DataFrame = leftDF.join(rightDF,
    leftDF.col("name")===rightDF.col("name"),
    "left_outer")

+------+----+------+-----+
|  name|size|  name|  zip|
+------+----+------+-----+
|   Sad| 0.9|  null| null|
|Coffee| 3.0|Coffee|10504|
| Happy| 1.0| Happy|94110|
| Happy| 1.0| Happy|94103|
| Happy| 1.5| Happy|94110|
| Happy| 1.5| Happy|94103|
+------+----+------+-----+
```

If want to keep  all row use **full outer join**

```scala
val frame1: DataFrame = leftDF.join(rightDF,
    leftDF.col("name")===rightDF.col("name"),
    "full_outer")

+------+----+------+-----+
|  name|size|  name|  zip|
+------+----+------+-----+
|  null|null|   Tea|07012|
|   Sad| 0.9|  null| null|
|Coffee| 3.0|Coffee|10504|
| Happy| 1.0| Happy|94110|
| Happy| 1.0| Happy|94103|
| Happy| 1.5| Happy|94110|
| Happy| 1.5| Happy|94103|
+------+----+------+-----+
```

**left_semi_join**: only have values from the left table, is same as filtering the left table for only with keys present in the right table，根据右侧过滤左侧，将左侧中那些不存在在右侧的数据过滤

```scala
  val frame1: DataFrame = leftDF.join(rightDF,
    leftDF.col("name")===rightDF.col("name"),
    "left_semi")

// records that is present in right table
+------+----+
|  name|size|
+------+----+
|Coffee| 3.0|
| Happy| 1.0|
| Happy| 1.5|
+------+----+
// only Coffee、Happy is present in right table
```

**left_anti_join**：only have values from the left table, but that values, is only has records that are not present in the right table. is same as filtering the left table for only with keys present not in the right table，

根据右侧过滤左侧，保留左侧中不存在在右侧的数据

```scala
  val frame1: DataFrame = leftDF.join(rightDF,
    leftDF.col("name")===rightDF.col("name"),
    "left_anti")

+----+----+
|name|size|
+----+----+
| Sad| 0.9|
+----+----+
// only Sad is not present in right table
```

**self join**

```scala
  leftDF.as("a").join(leftDF.as("b")).where($"a.name"===$"b.name").show()

|  name|size|  name|size|
+------+----+------+----+
|   Sad| 0.9|   Sad| 0.9|
|Coffee| 3.0|Coffee| 3.0|
| Happy| 1.0| Happy| 1.0|
| Happy| 1.0| Happy| 1.5|
| Happy| 1.5| Happy| 1.0|
| Happy| 1.5| Happy| 1.5|
+------+----+------+----+
```









