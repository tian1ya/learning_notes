数据的一个生命周期会经历过这样的事情，进化(``evolving``)和累加(``accumulating``)

``delta lake``  对schema 的管理主要涉及到2个方面，

* ``schema enforcement``: 防止数据被污染(混进来垃圾数据，和现有数据发生不一致，或者改变现有数据)
* ``schema evolution``： 允许数据增加列

---

#### Understanding Table Schemas

schema 是数据的蓝图(blueprint)，定义数据长什么样子，如数据的类型，列名，metadata等。在``Delta Lake`` 中 表的chema 保存在JSON  文件中，保存在事务日志中。

---

#### What is Schema Enforcement

``Schema enforcement`` 理解为schema的校验(``validation``)， 用户保证``Delta Lake`` 数据质量，那么是通过什么方式保证数据质量或者说是在什么时候对数据进行校验呢？ 那就是在写数据的时候，当对已经存在的数据进行增量写的时候，如果发现写进来的数据和以及存在的数据的schema 不一致，或者写进来的数据的schema是否以及存在于新的shema list 中，那么就拒绝写操作。

---

#### How Schema Enforcement works

``Delta Lake`` 在写数据的时候进行校验(``validation on write``)，如果写进来的数据和以及存在的数据不兼容，那么拒绝写数据，跑出异常，那么如果去决定是否``兼容``呢？ 定义了如下的操作：

* ``Cannot contain any additional columns that not present in the target tables's schema``, 不能包含目标表 schema 中不存在的列。相反，如果写入的数据没有包含所有的列是被允许的，这些空缺的列将会被赋值为 null。
* ``Cannot have column data types that differ from the column data types in the target table`` 同一个列名(写入的数据中列名同已存在的数据中的列名相同)，如果类型不同那么拒绝写操作
* ``Can not contain column names that differ only by case`` 大小写区分，spark 可以设置大小是否写敏感，``Delta Lake``  会保存 ``spark``  中大小写设置，但是``Delta Lake`` 数据保存为 ``parque `` 格式，而该中格式的存储以及返回列信息是大小写敏感的，为防止潜在的错误，数据污染和丢失问题，``Delta Lake`` 引入这个限制。

一个列子

```scala
scala> val df1 = spark.range(4,10)
df1: org.apache.spark.sql.Dataset[Long] = [id: bigint]

scala> val df1 = spark.range(5,11).select($"id".as("values"))
df1: org.apache.spark.sql.DataFrame = [values: bigint]

scala> val df2 = spark.range(5,11).select($"id".as("values"))
df2: org.apache.spark.sql.DataFrame = [values: bigint]

scala> val df1 = spark.range(4,10)
df1: org.apache.spark.sql.Dataset[Long] = [id: bigint]

scala> df2.write.format("delta").mode("append").save("/delte/range6")

scala> df1.write.format("delta").mode("append").save("/delte/range6")
org.apache.spark.sql.AnalysisException: A schema mismatch detected when writing to the Delta table.
To enable schema migration, please set:
'.option("mergeSchema", "true")'.

Table schema:
root
-- values: long (nullable = true)

Data schema:
root
-- id: long (nullable = true)


If Table ACLs are enabled, these options will be ignored. Please use the ALTER TABLE
command for changing the schema.
```

上面跑出了第二条限制中的错误。同时错误中提示可以设置 ``mergeSchema`` 为``true`` 这样新的不同名称的列就可以作为一个新列添加进来，相当于将df中有而schema没有的字段添加到schema中，也就是add column，但是添加的方式很奇怪

```scala
scala> df1.write.format("delta").mode("append").option("mergeSchema","true").save("/delte/range6")

scala> val df33 = spark.read.format("delta").load("/delte/range6").show
+------+----+
|values|  id|
+------+----+
|     9|null|
|    10|null|
|     6|null|
|     7|null|
|     5|null|
|     8|null|
|  null|   5|
|  null|   6|
|  null|   8|
|  null|   9|
|  null|   7|
|  null|   4|
+------+----+
```

这里还有一个设置，可以设置 ``mergeSchema`` 为``true``  新数据的schema 覆盖就数据的schema。

```scala
scala> df1.write.format("delta").mode("append").option("overwriteSchema","true").save("/delte/range66")

scala> spark.read.format("delta").load("/delte/range66").show
+---+
| id|
+---+
|  8|
|  9|
|  5|
|  6|
|  7|
|  4|
+---
```

---

#### How Is Schema Enforcement Useful

严格的schema 检查，保证数据在清理、转化等，而这些操作如，机器学习、BI 报表、数据可视化等领域是很重要的，``防患于未然``对数据的 ``schema`` 进行强制约束，确诊数据质量。

当然对数据的操作有时候是需要增加列的，如在ML领域。按照上面的约束，增加新列是需要跑出异常的，那么应该如何操作增加一个新列呢？

---

#### Schem Evolution

``schema evolution`` 允许用户改变当前数据的 ``schema``,  经常会用在``append``  或者 ``overwrite``  的操作。在上面的列中有提到，在save 数据的时候增

``.option("mergeSchema","true")``

就可以了，每新增加的列，包括嵌套列都会被增加进来，但并不是所有的``schema change `` 是允许的，以下的 ``schema changes`` 是允许的

* 新列增加
* 将数据类型从 ``NullType`` 改为其他类型，或者将``ByteType``往上(``upcasts``)转为``ByteType -> ShortType -> IntegerType``

而其他类型的``schema change`` 不是合格的，同时使用选项

``.option("overwriteSchema", "true")``

之间覆盖旧的 ``schema``,  例如，当将原来类型为 ``integer``  的列 ``Foo`` ，变为类型 ``StringType``， 那么所有的数据``Parqurt``数据均需要被覆盖，那么当使用覆盖``schema`` 的方式都会有哪些操作发生呢？

* Dropping a column
* Changing an existing column’s data type (in place)
* Renaming column names that differ only by case (e.g. “Foo” and “foo”)

---

#### Summary

* Schema enforcement: 确保数据质量，schema 的不变性
* schema evolution： 确保数据的schema，按照用户的意图改变。