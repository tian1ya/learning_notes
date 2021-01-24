```scala
  private val spark: SparkSession = Commons.spark
  import spark.implicits._

  val dfVM = Seq((1,"abc", Array("a","b","c")), (2,"ABC", Array("aa","bb","cc"))).toDF("id","col1","col2")

  dfVM.show()

+---+----+------------+
| id|col1|        col2|
+---+----+------------+
|  1| abc|   [a, b, c]|
|  2| ABC|[aa, bb, cc]|
+---+----+------------+

dfVM.withColumn("col2", explode($"col2")).show()

+---+----+----+
| id|col1|col2|
+---+----+----+
|  1| abc|   a|
|  1| abc|   b|
|  1| abc|   c|
|  2| ABC|  aa|
|  2| ABC|  bb|
|  2| ABC|  cc|
+---+----+----+
```

