Most of spark programs are structed on RDDs, the involve reading data from stable storage into the RDD format, performing a number of computions and data transformations on the RDD, and writing the result RDD to stable storage or collection  to the driver.

**The most of power of spark comes from its transformation: operations that are defined on RDD and return RDDs**

---

**narrow transformations**:  the child partitions (the partitions in the resulting RDD) depend on a known subset of the parent partitions. **each partition of the parent RDD is used by at most one partition of the child RDD.**



transformations with **wide dependencies as transformations** in which “multiple child par‐ titions may depend on [each partition in the parent].



**compute the map step**, each child partition depends on just one parent, since the data doesn’t need to be moved between partitions for the operation to be computed

**groupByKey step**, Spark needs to move an arbitrary number of the records so that those with the same key are in the same partition in order to combine records corresponding to a single key into one iterator。

**narrow dependencies are faster to execute partly because narrow transforma‐ tions can be combined and executed in one pass of the data**

The **coalesce operation** is used to change the number of partitions in an RDD.

**RDD record type is important** because many operation is on specific records type, for example RDD[(Any, String)] will not worked for groupByKey operator

**losing type often leading problems when working with DataFrames as RDDs, DataFrames can be implecitly converted to RDDs of Rows**



**suppose that we wanted to do some custom aggregation that is not already defined in Spark**

**aggregateByKey** function, which takes three arguments: a zero value that represents an empty accu‐ mulator, a sequence function that takes the accumulator and a value and adds the value to the accumulator, and a combine operator that defines how the accumulators should be combined

zeroValue：输出结果的初始值，

seqOp：定义一个函数，这个函数接收zeroValue，和分区中的一个row，然后计算出一个和zeroValue类型一样的结果，这个结果继续和分区中的后续 一条数据继续操作，直到将这个分区中的所有数据计算完，输出zeroValue类型的结果。

combOp：接收seqOp的输出，也就是接收每一个分区中的结果，将每个分区中数据聚合，得到最后的结果。

```scala
def aggregateByKey[U: ClassTag](zeroValue: U)(seqOp: (U, V) => U, combOp: (U, U) => U)
```

```scala
/*
  Let’s say that we have an RDD of key/value pairs where the keys are the panda’s instructors
  and the values are the pupils’ panda report cards. For each instructor we want to know the
  length of the longest word used, the average number of words used per report card, and the
  number of instances of the word “happy.”
 */
 
 package com.bigData.spark.SQL

import org.apache.spark.rdd.RDD

case class ReportCartMetrics(longestWords: Int, happyMetions: Int, averageWords: Double)

class MetricsCalculator(
                         totalWords:Int,
                         longestWords: Int,
                         happyMentions: Int,
                         numberReportCards: Int) extends Serializable {

  def sequenceOp(reportCardContent: String): MetricsCalculator = {
    val words = reportCardContent.split(" ")
    val tW = words.length
    val lW = words.map(w => w.length).max
    val hW = words.count(w => w.toLowerCase().equals("happy"))

    new MetricsCalculator(
      tW + totalWords,
      Math.max(longestWords, lW),
      hW + happyMentions,
      numberReportCards + 1
    )
  }

  def compOp(other: MetricsCalculator): MetricsCalculator = {
    new MetricsCalculator(
      this.totalWords + other.totalWords,
      Math.max(this.longestWords, other.longestWords),
      this.happyMentions + other.happyMentions,
      this.numberReportCards + other.numberReportCards)
  }

  def toReportCardMetrics =
    ReportCartMetrics(longestWords, happyMentions, totalWords.toDouble / numberReportCards)
}

object MetricsCalculator extends App {

  def calculateReportCardStatistics(rdd: RDD[(String, String)]): RDD[(String, ReportCartMetrics)] = {

    rdd.aggregateByKey(
      new MetricsCalculator(0, 0, 0, 0))(
      seqOp=(reportCardMetrics, reportCardText) => reportCardMetrics.sequenceOp(reportCardText), combOp = (x,y) => x.compOp(y)
    ).mapValues(a => a.toReportCardMetrics)
  }
}
```

**这里有个问题，就是在执行 aggregateByKey 的时候  compOp sequenceOp 和都会给结果创建一个新对象，这回带来一定的性能问题，解决方法是每次都在原来的基础上执行，然后将当前对象返回, 记得将变量都变为可变变量 **

```scala
package com.bigData.spark.SQL

import org.apache.spark.rdd.RDD

case class ReportCartMetrics(longestWords: Int, happyMetions: Int, averageWords: Double)

class MetricsCalculator(
                         var totalWords:Int,
                         var longestWords: Int,
                         var happyMentions: Int,
                         var numberReportCards: Int) extends Serializable {

  def sequenceOp(reportCardContent: String): MetricsCalculator = {
    val words = reportCardContent.split(" ")
    totalWords = words.length + totalWords
    longestWords =  Math.max(longestWords, words.map(w => w.length).max)
    happyMentions = words.count(w => w.toLowerCase().equals("happy"))
    numberReportCards += 1
    this
  }

  def compOp(other: MetricsCalculator): MetricsCalculator = {
    totalWords += other.totalWords
    longestWords = Math.max(longestWords, other.longestWords)
    happyMentions += other.happyMentions
    numberReportCards += other.numberReportCards
    this
  }

  def toReportCardMetrics =
    ReportCartMetrics(longestWords, happyMentions, totalWords.toDouble / numberReportCards)
}

object MetricsCalculator extends App {

  def calculateReportCardStatistics(rdd: RDD[(String, String)]): RDD[(String, ReportCartMetrics)] = {

    rdd.aggregateByKey(
      new MetricsCalculator(0, 0, 0, 0))(
      seqOp=(reportCardMetrics, reportCardText) => reportCardMetrics.sequenceOp(reportCardText), combOp = (x,y) => x.compOp(y)
    ).mapValues(a => a.toReportCardMetrics)
  }
}
```

注意的事情：

**Reduce (which calls aggregate) and the fold operations (foldLeft, fold, foldRight) can also benefit from object reuse. However, these aggregation functions are unique. It is best to avoid mutable data structures in Spark code (and Scala code in general) because they can lead to serialization errors and may have inaccurate results. For many other RDD functions, particularly narrow transformations, modifying the first value of the argument is not safe because the transformations may be chained together with lazy evaluation and may be evaluated multiple times. For example, if you have an RDD of mutable objects, modifying the arrays with a map function may lead to inaccurate results since the objects may be reused more times than you expect —especially if the RDD is recomputed.**

按照这里的说法，考虑性能使用可变变量，在分布式环境中，也会带来一些问题。

---

**Using Smaller Data Structures**

spark  save data in  memory , An important way to optimize spark jobs for both time and space is to stick to **primitive types rather than customer classes, and use Arrays rather than case classes or tuple, arrays is the most memory-efficient of the scala collection types, Its better to use 2 or 3 element array rather than a tuple or case class**。

```scala
package com.bigData.spark.SQL

import org.apache.spark.rdd.RDD

class MetricsCalculatorUseArray extends Serializable {
  val totalWordsIndex = 0
  val longestWordIndex = 1
  val happyMentionsIndex = 2
  val numberReportCardsIndex = 3

  def sequenceOp(reportCardMetrics: Array[Int], reportCardContent: String): Array[Int] = {
    val words = reportCardContent.split(" ")
    reportCardMetrics(totalWordsIndex) = words.length
    reportCardMetrics(longestWordIndex) = Math.max(reportCardContent(longestWordIndex), words.map(w => w.length).max)
    reportCardMetrics(happyMentionsIndex)  += words.count(w => w.toLowerCase.contains("happy"))
    reportCardMetrics(numberReportCardsIndex) += 1
    reportCardMetrics
  }

  def compOp(x: Array[Int], y: Array[Int]): Array[Int] = {
    x(totalWordsIndex) += y(totalWordsIndex)
    x(longestWordIndex) = Math.max(x(longestWordIndex), y(longestWordIndex))
    x(happyMentionsIndex) += y(happyMentionsIndex)
    x(numberReportCardsIndex) += y(numberReportCardsIndex)
    x
  }

  def toReportCarMetrics(ar: Array[Int]): ReportCartMetrics =
    ReportCartMetrics(
      ar(totalWordsIndex),
      ar(longestWordIndex),
      ar(happyMentionsIndex) / ar(numberReportCardsIndex))
}

object MetricsCalculatorUseArray extends App {

  def calculateReportCardStatisticsWithArrays(rdd: RDD[(String, String)]): RDD[(String, ReportCartMetrics)] = {
    rdd.aggregateByKey(Array.fill[Int](4)(0))(
      // 这里应该是将 MetricsCalculatorUseArray 写为一个 object
      // 这样使用sequenceOp、compOp、toReportCarMetrics可以直接使用了
      // 而不是new MetricsCalculatorUseArray 对象出来
      seqOp = (reportCarMetrics, reportCardText) => (new MetricsCalculatorUseArray).sequenceOp(reportCarMetrics, reportCardText),
      combOp = (x,y) => (new MetricsCalculatorUseArray).compOp(x,y)

    ).mapValues(x => (new MetricsCalculatorUseArray).toReportCarMetrics(x))
  }
}
```

**it is often beneficial to avoid intermediate object creation. It is important to remember that converting between types (such as between different flavors of Scala collections) creates intermediate objects**

---

**RDD mapPartitions** function takes as its argument a function from an iterator of records The mapPartitions transformation is one of the most powerful in Spark，it is important to represent your functions inside of mapPartitions in such a way that your functions do not force loading the entire par‐ tition in-memory。mapPartitions can use simple  and complex way to process data.

**MapParttitiona**: Iterator to iterator transformations. using one of these iterator “trans‐ formations” to return a new iterator。

**space and time Adavantages**

主要是map和foreach这类的是针对一个元素调用一次我们的函数，也即是我们的函数参数是单个元素，假如函数内部存在数据库链接、文件等的创建及关闭，那么会导致处理每个元素时创建一次链接或者句柄，导致性能底下，很多初学者犯过这种毛病。

而foreachpartition是针对每个分区调用一次我们的函数，也即是我们函数传入的参数是整个分区数据的迭代器，这样避免了创建过多的临时链接等，提升了性能。

下面的例子都是1-20这20个数字,经过map或者MapPartition然后返回a*3。

```scala
val a = sc.parallelize(1 to 20, 2)
def mapTerFunc(a : Int) : Int = {
    a*3
}
val mapResult = a.map(mapTerFunc)
```

## mappartition低效用法

```scala
val a = sc.parallelize(1 to 20, 2)
  def terFunc(iter: Iterator[Int]) : Iterator[Int] = {
    var res = List[Int]()
    while (iter.hasNext)
    {
      val cur = iter.next;
      res.::= (cur*3) ;
    }
    res.iterator
  }
val result = a.mapPartitions(terFunc)
```

## mappartition的高效用法

3中的例子，会在mappartition执行期间，在内存中定义一个数组并且将缓存所有的数据。假如数据集比较大，内存不足，会导致内存溢出，任务失败。 对于这样的案例，Spark的RDD不支持像mapreduce那些有上下文的写方法。下面有个方法是无需缓存数据的，那就是自定义一个迭代器类。

```scala
class CustomIterator(iter: Iterator[Int]) extends Iterator[Int] {
    def hasNext : Boolean = {
      iter.hasNext
    }

    def next : Int= {
    val cur = iter.next
     cur*3
    }
  }
  
  val result = a.mapPartitions(v => new CustomIterator(v))
  println(result.collect().mkString(","))
```

### Set Operations

> union: merely combines its arguments
>
> intersection:
>
> subtract: 

### Share variable

* Broadcase Variablea 

> way to take a local value on the driver and distribute a read-only copy to each machine rather than shipping a new copy with each task.

* Accumulators

> second type of Spark’s shared variables

```scala
def computeTotalFuzzyNess(sc: SparkContext, rdd: RDD[RawPanda]): (RDD[(String, Long)], Double) = {
val acc = sc.doubleAccumulator("fuzzyNess")
val transformed = rdd.map{x => acc.add(x.attributes(0)); (x.zip, x.id)} 

transformed.count()
(transformed, acc.value)
}
```

To use an accumulator of a different type, you need to implement the AccumulatorV2[Input Type, ValueType] interface and provide reset, copy, isZero, value , merge, and add methods.

```scala
def computeMaxFuzzyNess(sc: SparkContext, rdd: RDD[RawPanda]): (RDD[(String, Long)], Option[Double]) = {
class MaxDoubleAccumulator extends AccumulatorV2[Double, Option[Double]] { 

var currentVal: Option[Double] = None
override def isZero = currentVal.isEmpty

override def reset() = {currentVal = None }

def copy() = {
	val newCopy = new MaxDoubleAccumulator() 
  newCopy.currentVal = currentVal
	newCopy
}

override def copyAndReset() = { 
  new MaxDoubleAccumulator()
}
override def add(value: Double) = { 
  currentVal = Some(currentVal.map(acc => Math.max(acc, value)).getOrElse(value))
}
  
override def merge(other: AccumulatorV2[Double, Option[Double]]) = { 
  other match {
case otherFuzzy: MaxDoubleAccumulator =>
	otherFuzzy.currentVal.foreach(value => add(value))
case _ => throw new Exception("Unexpected merge with unsupported type" + other)
	}
}

override def value = currentVal 
}

val acc = new MaxDoubleAccumulator()
sc.register(acc)
val transformed = rdd.map{x => acc.add(x.attributes(0)); (x.zip, x.id)}
transformed.count() 
(transformed, acc.value)
}
```

This still requires that the result is the same as the type we are accumulating. If we wanted to collect all of the distinct elements，we would likely want to collect a set and the types would be different.

```scala
def uniquePandas(sc: SparkContext, rdd: RDD[RawPanda]): HashSet[Long] = { class UniqParam extends AccumulatorV2[Long, HashSet[Long]] {
	var accValue: HashSet[Long] = new HashSet[Long]()
	
  def value = accValue 
  
  override def copy() = {
		val newCopy = new UniqParam() 
    newCopy.accValue = accValue.clone 
    newCopy
}
  
	override def reset() = {
		this.accValue = new HashSet[Long]() 
  }
	
  override def isZero() = accValue.isEmpty
  
  override def copyAndReset() = {
  	new UniqParam() 
  }
  
  override def add(value: Long) = { 
    accValue += value
  }

  override def merge(other: AccumulatorV2[Long, HashSet[Long]]) = { 
    other match {
  			case otherUniq: UniqParam => accValue = accValue ++ otherUniq.accValue
  			case _ => throw new Exception("only support merging with same type")
  		}
  	}
  }
                                                                         
  val acc = new UniqParam()
  sc.register(acc, "Unique values")
  val transformed = rdd.map{x => acc.add(x.id); (x.zip, x.id)}                                                               
  transformed.count() 
  acc.value
}
```

---

### Resuse RDDs

* persisting
* caching
* Check-pointing

All of these are not automatically execute.

 the most important cases for reuse are:

* using an RDD many times; 
* performing multiple actions on the same RDD; 
* and for long chains of (or very expensive) transformations.



#### Iterative computations

**For transformations that use the same parent RDD multiple times**, reusing an RDD forces evaluation of that RDD and so can help avoid repeated computations. For example, if you were performing a loop of joins to the same dataset, persisting that dataset could lead to huge performance improvements since it ensures that the parti‐ tions of that RDD will be available in-memory to do each join.

```scala
val testSet: Array[RDD[(Double, Int)]] = Array(
validationSet.mapValues(_ + 1), validationSet.mapValues(_ + 2), validationSet)
validationSet.persist() //persist since we are using this RDD several times val 
errors = testSet.map( rdd => rmse(rdd.join(validationSet).values))
```

**Multiple actions on the  same RDD**

If you do not reuse an RDD, each action called on an RDD will launch its own Spark job with the full lineage of RDD transformations. **Persisting and checkpointing breaks the RDD’s lineage,**

```scala
val sorted = rddA.sortByKey() 
val count = sorted.count() 
val sample: Long = count / 10 
sorted.take(sample.toInt)
```

The sortByKey (and presumably the read operation) needed to create the RDD, sorted, will occur twice if we do not store the RDD: ***once* in the job called by count and again in the job called by take**

```scala
val sorted = rddA.sortByKey() 
val count = sorted.count() 
val sample: Long = count / 10 
rddA.persist() sorted.take(sample.toInt)
```

if we add a persist or checkpoint call before the actions, the transformation will only be executed once, **since Spark builds a lineage graph from either an RDD’s creation or a persisted/checkpointed RDD.**



**If the cost to compute each partition is very high**



