#### 预定义的 Source 和 Sink

* 基于文件的Source

> `readTextFile(path)`
>
> `readFile(fileInputFormat, path)`

* 基于文件的Sink

> `writeAsText`
>
> `writeAsCsv`

* 基于Socket

> `socketTextStream`
>
> `writeToSocket`

* 基于 `Collections/Iterators`

> `fromCollection`
>
> `fromElements`

* 标准输出、错误

> `print`
>
> `printToError`

#### Bundled Connectors

> `Flink` 项目提供的，但是并没有在`Runtime` 中包含的，需要引入第三方`jar` 包。

#### 异步IO

> 和外部数据库等进行一些关联。用于访问外界数据。

---

#### Flink Kafka Connector

* 反序列化数据
* 消费起始位置设置
* `Topic` 和 `Partition` 动态发现
* `Commit Offset` 方式
* `Timestamp Extraction/watermark` 生成

#### Fink Kafka Producer

* `Producer` 分区
* 容错

