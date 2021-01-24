`SparkSQL` and its `DataFrames`  and `Datasets` interfaces are the super importance for getting the best of spark performance。

---

Compare to `RDD` the `dataframe` or `Dataset` provide additional schema information that not found in `RDD`,  this information help operations optimize, the optimizer can inspect the logical meaning rather arbitrary function。

**Compared to working with RDDs, DataFrames allow Spark’s optimizer to better understand our code and our data**

---

`SparkContext` is the entry point for all spark application

`SparkSession` serve as the entry point for spark SQL

build model to create `SparkSession`

```scala
val session = SparkSession.builder() .enableHiveSupport() .getOrCreate()
// Import the implicits, unlike in core Spark the implicits are defined // on the context.
import session.implicits._
```

getOrCreate() will return already exist  `sparkSession` is it has created， or will create new one。

---

`Schemas` are normally handled  automatically by `Spark SQL`,  either indered when loading the data or computed based on the parent `DataFrame` and the transformation heing applied。

`StructType` which contains a list of fields。

note you can nest `StructTypes`

`StructType` are defined with `Struct Field`

**how to access a specific column from a DataFrame**

```scala
pandasInfo.filter(pandasInfo("happy") !== true)

# use implicit $ operator for column lookup
pandasInfo.filter(!$("happy"))

# for multi column
pandaInfo.filter(
     pandaInfo("happy")
  	.and(pandaInfo("attributes")(0) > 		
         	pandaInfo("attributes")(1))
)
```

For accessing other structures inside of DataFrames, like nested structs, keyed maps, and array ele‐ ments, use the same apply syntax

**but keep in mind that these functions are called on columns, not values.**

---

turn an input DataFrame of PandaPlaces into a DataFrame of just PandaInfo:

```scala
  val pandaInfo = pandaPlace.explode(pandaPlace("pandas")){ case Row(pandas: Seq[Row]) =>
  pandas.map{ case (Row(
                      id: Long,
                      zip: String,
                      pt: String,
                      happy: Boolean,
                      attrs: Seq[Double])) =>
          RawPanda(id, zip, pt, happy, attrs.toArray)}}

pandaInfo.select((pandaInfo("attributes")(0) / 	
                  	pandaInfo("attributes")(1)).as("squishyness"))

# Create a row for each element in the array—often useful when working with nested JSON records
# https://stackoverflow.com/questions/32906613/flattening-rows-in-spark
# https://stackoverflow.com/questions/39275816/exploding-nested-struct-in-spark-dataframe
```

---

Beyond row-by-row transformations（Row 粒度的操作）

`dropDuplicates` : drop duplication rows of all same value

`pandas.dropDuplicates(List("id"))`drop duplication rows of specific column that has  same value。

`Aggregation` on `Dataset` have extra functionality, returning a `GroupedDataset` ， and `sum/mean/avg/min/max` is convenience function to implement to `GroupedDataset`

```scala
def maxPandaSizePerZip(pandas: DataFrame): DataFrame = { 	
  pandas.groupBy(pandas("zip")).max("pandaSize")
}
```

computes the max on a per-key basis, these aggregates can also be applied over the entire DataFrame or all numeric columns in a DataFrame

```scala
import org.apache.spark.sql.functions._
def minMeanSizePerZip(pandas: DataFrame): DataFrame = { 
  // Compute the min and mean 	
  	pandas.groupBy(pandas("zip")).agg(
      min(pandas("pandaSize")), mean(pandas("pandaSize")))
  }
```

Some other function provided by `sparkSQL` that never used but usefull is bellowing:



> **approxCountDistinct**
>
> ```scala
> df.agg(approxCountDistinct 2 (df("age"), 0.001))
> # 以一定的进度来选择值是否不一样，如
> # df("age") = DateFrame(Row(age=0.3), Row(age=0.4), Row(age=0.9))
> # df.agg(approxCountDistinct 2 (df("age"), 0.2))
> # 那么结果就是 2
> # 如果 df.agg(approxCountDistinct 2 (df("age"), 0.01))
> # 那么结果就是 3
> ```
>
> **countDistinct**
>
> ```scala
> .distince().count()
> ```
>
> **sumDistinct**
>
> ```sccala
> .distince().sum()
> ```

* 窗口函数

> https://lotabout.me/2019/Spark-Window-Function-Introduction/
>
> 单独的一篇去记录 spark 窗口函数的使用

---

####  Data Representation in DataFrames and Datasets

> RDDs： Row of objects
>
> DataFrames/Dataset ：columnar(柱状) cache format



