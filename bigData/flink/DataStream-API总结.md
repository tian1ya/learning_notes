### 运行整体流程

>  Source -> Transformation -> Sink

#### 操作概览

![a](./pics/transform.png)

操作算子是说将一个或者多个 DataStream 转换为一个新的DataStream

![a](./pics/transform_1.png)

**理解 keyedStream 是理解整个DataStreamAPI 的重中之重**

#### 数据流向的物理分组

![a](./pics/transform_2.png)

* `global`

![a](./pics/transform_21.png)

相当于是强制将下游的算子的并行度设置为了1。

* `boradcast`

![a](./pics/transform_2_2.png)

相当于就是将上游某个实例的数据发给下游的全部实例。使用的时候非常小心，相当于是将数据流复制n份(下游有n个实例)

* `forward`

上下游并行度一样的时候才可以使用。如果在编译期间上下游并行度不一样，那么就会报错。

* `shuffle`

做一个随机分配，每一个实例都知道自己的下游有几个实例，那么将一条数据随机选择下游的一个实例发过去，可以达到负载均衡的效果。

* `reblance`

和 shuffle 的作用差不多，不同的地方是`reblance` 是轮询的方式。

* `rescale`

和 `reblance`一样的做法，不同的是上面提到的 `reblace` 和 `rescale` 是会考虑所有的下游实例，如上面的例子中`A1 `  不止会考虑 `B1/B2` 还会考虑 `B3/B4/B5`

而这里的`rescale` 只会考虑本地的下游实例，也就是`A1` 只会考虑`B1/B2` 去分发数据，而`A2` 只会考虑  `B3/B4/B5`

* partitionCustome

自定义数据路由的逻辑，根据选择下游分区的逻辑返回下游的一个分区，然后将数据分发到下游的一个分区。



#### 类型系统

`Flink` 是强类型的，这个它的序列化/反序列化相关的，作为一个框架，理解的数据的类型越多，那么这个框架一定意义上越高效。有时候甚至需要给出  `TypeInformation`

```java
OutputTag<Order> outputTag = new OutputTag<>("seriousList", TypeInformation.of(Order.class));
```

在使用`scala` 编程或者使用`java` 调 `scala` 的时候，需要`scala` 的隐士转换，完成类型推到。

而在使用`Java` 写程序的时候，没有隐士转换，且`java` 运行期间类型擦除，那么就需要比较繁琐的给出类型

```java
SingleOutputStreamOperator<Tuple2<String, Integer>> word1Pair = words
  .map((String value) -> Tuple2.of(value, 1))
  .returns(Types.TUPLE(Types.STRING, Types.INT));
```

![a](./pics/transform_3.png)



#### API 原理

![a](./pics/transform_4.png)



![a](./pics/transform_5.png)

Function: 是真正执行逻辑的代码，也是我们写代码的时候关注的点。

API 越抽象，**那么表达能力越低，但是一致性越强**，所谓一致性越强就是api 适应性越强，假如说你使用Table API 写了一个功能，如果你的flink 版本发生变化，那么在下一个版本中还可以工作能力越强。相反表达能力越若，因为其灵活性降低，很多底层Api processFunction 可以做的事情，这个时候它不一样能够做的到。

而越底层的api，在版本发生变化的时候其变化的可能越大，到下一个版本中还可以使用的可行性就越低。

---

#### Source

```scala
class MySensorSource extends SourceFunction[SensorReading]{

  // 定义一个标志位flag，用来表示数据源是否正常运行，发出数据
  var running:Boolean = true
  var count = 0

  override def run(sourceContext: SourceFunction.SourceContext[SensorReading]): Unit = {
    // 定义无线循环，不停的产生数据，除非被 cancel 掉

    val rand = new Random()

    var currentTemp: immutable.Seq[(String, Double)] = 1 to 10 map(i => (s"sensor_$i", rand.nextDouble() * 100))

    while (running) {
      // 模拟微调
      currentTemp = currentTemp.map(data => (data._1, data._2 + rand.nextGaussian()))
    // 获取时间戳
    val curTimestamp: Long = System.currentTimeMillis()
    currentTemp.foreach(data =>
      sourceContext.collect(SensorReading(data._1, curTimestamp, data._2))
    )
    Thread.sleep(1000)
    }
  }


  override def cancel(): Unit = {
    running = false
  }
}

// 运行
env.addSource(new MySensorSource())
```

---

#### Transformation

比较常规的有 `map,flatmap,filter,sum,min,max,minBy,maxBy,reduce` 等

```scala
dataStream
      .keyBy("id")
      .reduce((curState, newData) => SensorReading(curState.id, newData.timestamp, curState.temperature.min(newData.temperature))
      )

dataStream.map(data => (data.id * 2, data.timestamp))

dataStream.flatMap(data => {data.id.split("_")})

dataStream
.map(data => (data.id, data.timestamp, data.temperature))
.keyBy(_._1)
.sum(2)

dataStream
.map(data => (data.id, data.timestamp, data.temperature))
.keyBy(_._1)
.min(2)

dataStream
.map(data => (data.id, data.timestamp, data.temperature))
.keyBy(_._1)
.minBy(2)
```

#### 注意 min 和 minBy 的区别

> ```
> min:   min 那个字段为当前为止最小值, 其他字段(除keyBy的字段)始终都是stream中的第一次出现的那个值
> minBy: minBy 那个字段为当前为止最小值, 其他字段都更随着最小值的那行其它的数据，所以 minBy 找最小值的行是最准确的。
> 
> maxBy 也是一样的
> ```

#### 合流和分流

```scala
// 查看代码中
// java.transformations
```

#### 使用类

```scala
dataStream.filter(new MyFilter)

// 自定义一个函数类
class MyFilter extends FilterFunction[SensorReading] {
  override def filter(t: SensorReading): Boolean = {
    t.temperature > 10
  }
}

class MyReduceFuntion extends ReduceFunction[SensorReading] {
  override def reduce(t: SensorReading, t1: SensorReading): SensorReading =
    SensorReading(t.id, t1.timestamp, t.temperature.min(t1.temperature))
}
```

> 相同的还有 `ReduceFunction MapFunction`

#### 使用富函数

> 富函数和普通的函数的区别在于：**可以获取运行环境的上下文，并拥有一些生命周期方法，所以可以实现更复杂的功能。**

```scala
class MyRichMapper extends RichMapFunction[SensorReading, String] {

  override def open(parameters: Configuration): Unit = {
    // 假如说这里想去操作下数据库, 可以在这里建立连接，这里操作
    // map 操作是来一条数据操作一遍，那么操作数据库那就太过于频繁了
    // 而使用 RichFunction 在open 生命周期做一些初始化操作
    // 是当前函数类创建的时候就去执行构造器调用之后调用
    // 然后在调用 close 做收尾动作
  }

  override def map(in: SensorReading): String = {
    in.id + " temperature"
  }

  override def close(): Unit = {
    // 做收尾工作，如 关闭连接，或者情况状态
  }
}
```

#### 使用状态

> 因为状态是需要在环境上下文中建立的，所以在使用的时候，需要在可以获取环境上下文的地方使用，
>
> 如`ProcessFunction, RichFunction`

##### 使用本身带有状态的算子

```scala
dataStream
      .keyBy(_.id)
      //      .flatMap(new TempChangeAlert(10.0))// 无状态的 flateMap
      .flatMapWithState[(String, Double, Double), Double]({ // 有状态的 flatMap 必须是在 keyBy 之后调用
        case (data: SensorReading, None) => (List.empty, Some(data.temperature))
        case (data: SensorReading, lastTemp: Some[Double]) => {
          val lastTempValue = lastTemp.get

          val diff = (data.temperature - lastTempValue).abs

          if (diff > 10.0)
            (List((data.id, data.temperature, data.temperature)), Some(data.temperature))
          else
            (List.empty, Some(data.temperature))
        }})


    dataStream
      .keyBy(_.id)
      .mapWithState[SensorReading, Double]({
        case (data:SensorReading, None) => ((SensorReading(data.id, 0L, 0.0)), Some(data.temperature))
        case (data:SensorReading, state:Some[Double]) => {
          val lastValue = state.get
          val currentValue = data.temperature
          if ((currentValue-lastValue).abs > 10.0)
            (data, Some(data.temperature))
            else
            (SensorReading(data.id, 0L, 0.0), Some(0.0))
        }
      })
  }
```

##### 自定义使用算子

```scala
class TempChangeAlert(threadHold: Double) extends RichFlatMapFunction[SensorReading, (String, Double, Double)] {

  /*
    定义状态，保存上一次的温度值
    这里可以使用 lazy 的方式创建状态，也可以在先定义一个类型然后 open 的周期方法中初始化，这个时候环境上下文getRuntimeContext以及可以获取到
    因为使用 lazy 创建的时候并没有立即初始化，而是在 flatMap 方法中使用，这个时候环境上下文getRuntimeContext以及可以获取到
    
    getRuntimeContext 是在执行完构造函数后才可以获取到的
   */
  lazy val lastTempState: ValueState[Double] = 
    getRuntimeContext.getState(new ValueStateDescriptor[Double]("lastState", classOf[Double]))

  override def flatMap(value: SensorReading, out: Collector[(String, Double, Double)]): Unit = {
    val lastTempValue = lastTempState.value()

    val diff = (value.temperature - lastTempValue).abs

    if (diff > threadHold)
      out.collect((value.id, lastTempValue, value.temperature))

    // 更新
    lastTempState.update(value.temperature)
  }
}

class MyRichMapper11 extends RichMapFunction[SensorReading, String] {


  /*
    getRuntimeContext:必须是在类的生命周期过程中调用，而不能在构造函数中调用，这样是获取不到 getRuntimeContext的
    应该将其放 到 open 生命周期中
   */

  var valueState: ValueState[Double] = _
  lazy val listState: ListState[Int] = getRuntimeContext.getListState(new ListStateDescriptor[Int]("listState", classOf[Int]))
  lazy val mapState: MapState[String, Double] =
    getRuntimeContext.getMapState(new MapStateDescriptor[String, Double]("mapState", classOf[String], classOf[Double]))

  lazy val reduceStage: ReducingState[SensorReading] = getRuntimeContext.getReducingState(new ReducingStateDescriptor[SensorReading]("reduceState", (curRes, newData) => SensorReading(curRes.id, newData.timestamp, curRes.temperature.min(newData.temperature)), classOf[SensorReading]))

  override def open(parameters: Configuration): Unit = {
    valueState = getRuntimeContext.getState(
      new ValueStateDescriptor[Double]("valueState", classOf[Double]))
  }

  override def map(value: SensorReading): String = {
    // 完成状态的读写
    val v = valueState.value()
    valueState.update(value.temperature)
    listState.add(1)
    listState.addAll(util.Arrays.asList(1, 2, 3, 4))
    listState.update(util.Arrays.asList(5)) // 直接替换

    val iterable: lang.Iterable[Int] = listState.get()
    iterable.forEach(el => println(el))

    val isEmpty = mapState.isEmpty

    value.id
  }
}
```

状态分为2大类：

* Managed State

* Raw Satate

  Managed State 分为2中

* Keyed State: 

  > DataStream 经过 keyBy 之后就变为KeyedStream， 每一个Key 对应一个state，一个Operator 的实例处理多个Key，访问多个State，所以有了Keyed State，它只能使用在KeyedStream 上

* Operator State

  > Operator State 可以用于所有算子，通过RuntimeContext 访问，这需要 Operator 是一个 Rich Function。Operator  State 需要自己实现 CheckpointedFunction 或 ListCheckpointed 接口

---

#### ProcessFunction

> 是最底层的流处理操作，允许访问所有流应用程序的基本构件:
>
> * event：数据流中的元素
> * state: 状态，用于仍错和一致性，仅仅用于 keyed stream
> * timers: 定时器，支持时间时间和处理时间，用于keyed stream

Flink 提供了8 个 ProcessFunction

- ProcessFunction：dataStream
- KeyedProcessFunction：用于KeyedStream，keyBy之后的流处理
- CoProcessFunction：用于connect连接的流
- ProcessJoinFunction：用于join流操作
- BroadcastProcessFunction：用于广播
- KeyedBroadcastProcessFunction：keyBy之后的广播
- ProcessWindowFunction：窗口增量聚合
- ProcessAllWindowFunction：全窗口聚合

```scala
class SplitTempProcess(threshold: Double) extends ProcessFunction[SensorReading, SensorReading] {
  override def processElement(value: SensorReading, ctx: ProcessFunction[SensorReading, SensorReading]#Context, out: Collector[SensorReading]): Unit = {
    if (value.temperature > threshold) {
      // 温度高输出到主流
      out.collect(value)
    } else {
      // 低温度输出到侧流
      ctx.output(new OutputTag[(String, Long, Double)]("low"), (value.id, value.timestamp, value.temperature))
    }
  }
}

dataStream.process(new SplitTempProcess(30.0))
```

* KeyedProcessFunction

```scala
class TempIncreaseWarning(interval: Long) extends KeyedProcessFunction[String, SensorReading, String] {

  // 定义状态，保存上一个问题值进行比较，保存注册定时器的时间戳，用于删除

  lazy val lastTempState: ValueState[Double] = getRuntimeContext.getState(new ValueStateDescriptor[Double]("lastState", classOf[Double]))
  lazy val timerTSState: ValueState[Long] = getRuntimeContext.getState(new ValueStateDescriptor[Long]("timerTSState", classOf[Long]))


  override def processElement(value: SensorReading, ctx: KeyedProcessFunction[String, SensorReading, String]#Context, out: Collector[String]): Unit = {
    // 取出状态
    val lastTemp = lastTempState.value()
    val timerTs = timerTSState.value()

    lastTempState.update(value.temperature)

    if (timerTs == 0 && value.temperature > lastTemp) {
      // 如果温度上升且没有定时器，那么注册当前数据时间戳10s之后的定时器
      val ts = ctx.timerService().currentProcessingTime() + interval
      ctx.timerService().registerProcessingTimeTimer(ts)
      timerTSState.update(ts)
    } else if (value.temperature < lastTemp) {
      // 温度下降，则删除定时器
      ctx.timerService().deleteProcessingTimeTimer(timerTs)
      timerTSState.clear()
    }
  }

  override def onTimer(timestamp: Long, ctx: KeyedProcessFunction[String, SensorReading, String]#OnTimerContext, out: Collector[String]): Unit = {
    val key = ctx.getCurrentKey
    val value = interval / 1000
    out.collect(s"传感器 $key 的温度连续 $value 秒连续上升")
    timerTSState.clear()
  }
}


dataStream
.keyBy(_.id)
.process(new TempIncreaseWarning(10000L)) // 10000m = 10s
```

#### 窗口中的API

* 窗口的生命周期

> **窗口创建**：当属于这个窗口的第一条数据到来的时候，就窗口该窗口。
>
> **窗口移除**：当该窗口所属的时间全部已经走完，并且设置的允许延迟时间也过去了，那么这个窗口就会被移除
>
> 窗口的移除只限于那些基于时间的窗口，如`global window` 是不会被移除的。
>
> 每一个窗口都有一个 `triggers` 函数，它包括应用在这个窗口数据中的计算方法，以及什么时候出发这个计算的`triggering policy`,以及决定何时消除窗口中的内容。
>
> 每一个窗口也有一个 `Evictor` 负责决定在函数应用在窗口中的元素之前或者之后移除窗口中的元素
>
> 窗口的什么周期主要有4部分
>
> * 窗口建立
> * 窗口收集够了数据出发计算
> * 窗口移除数据
> * 窗口移除

* keyed 以及 Non-keyed Window

> 在调用窗口函数之前，如果使用了`keyed` 算子，那么后续的窗口就变为了`keyedWindow` 否则就是`non-keyed window`
>
> 使用了`keyed` 算子的好处是将Stream 并行化，一个keyedStream 分配到了一个 task，这些task 之间是可以并行化运行的。
>
> 没有使用了`keyed` 算子，那么Stream 只会在一个task中计算，并行度是1。
>
> 使用了`keyed` 算子那么使用`API window `
>
> 没有使用了`keyed` 算子，那么使用`api windowAll`

* Window Assigners

> 使用了`keyed` 算子那么使用`API window `
>
> 没有使用了`keyed` 算子，那么使用`api windowAll`
>
> 也可以自己定义窗口，实现接口`WindowAssigner`

* 四类窗口

> *tumbling windows*: 
>
> *sliding windows* 
>
> *session windows* 
>
>  *global windows*
>
> 基于时间的窗口期时间的范围左闭右开的。`*start timestamp* (inclusive) and an *end timestamp* (exclusive) t`

> 定义好窗口，就需要对每个窗口中中的数据进行逻辑计算，Window Function 有4中
>
> * ReduceFunction: 完成增量聚合，**获取不上窗口的上下文信息**
> * AggregationFunction: 完成增量聚合，**获取不上窗口的上下文信息**
> * FoldFunction：以后会移除
> * ProcessWindowFunction: 提供一个Iterasble 迭代器，可以获得一个窗口的所有元素以及元素的元数据信息，它的执行效率不是很好，因为需要缓存窗口中的所有元素，**但是它可以获取到窗口的上下文信息**
>
> 可以将增量聚合和缓存窗口内所有数据进行结合使用

* ReduceFunction

  > 需要传入一个聚合函数
  >
  > ```scala
  > reduce(function: (T, T) => T)
  > ```
  >
  > 函数要求输入和输出的类型一样

```scala
dataStream.map(data => (data.id, 1))
.keyBy(_._1)
.timeWindow(Time.seconds(5), Time.seconds(3))
.reduce((curRes, newData) => (curRes._1, curRes._2 + newData._2))
```

* AggregationFunction

  > 需要传入一个 AggregateFunction 的函数类

  > ```scala
  > aggregate(aggregateFunction: AggregateFunction[T, ACC, R])
  > 
  > public interface AggregateFunction<IN, ACC, OUT> extends Function, Serializable {
  >   ACC merge(ACC a, ACC b);
  > }
  > ```
  >
  > AggregateFunction 需要实现 merge 函数，实现聚合操作，从上面的类型来看
  >
  > AggregateFunction 是比 ReduceFunction 更加的一般化，输入，输出，聚合类型都可以不一样

```scala
class countTemperatureAggregation extends AggregateFunction[(String,Long), (String, Long), (String, Long)] {
  // 初始化聚合结果
  override def createAccumulator(): (String, Long) = ("", 0L)
  // 分区内的聚合结果和新数据的计算
  override def add(value: (String, Long), accumulator: (String, Long)): (String, Long) = (value._1, accumulator._2 + value._2)
  // 分区间聚合结果计算
  override def getResult(accumulator: (String, Long)): (String, Long) = accumulator

  override def merge(a: (String, Long), b: (String, Long)): (String, Long) = (a._1, a._2 + b._2)
}


dataStream.map(data => (data.id, 1L))
      .keyBy(_._1)
      .timeWindow(Time.seconds(5), Time.seconds(3))
      .aggregate(new countTemperatureAggregation)
      .print("aggeragate count")
```

* ProcessWindowFunction

```scala
class countTemperatureProcessWindowFunction extends ProcessWindowFunction[(String, Long), (String, Long), String, TimeWindow] {
  override def process(key: String, context: Context, elements: Iterable[(String, Long)], out: Collector[(String, Long)]): Unit = {
    // elements 缓存下了窗口中的所有元素
    println("当前分组的 key: " + key)
    println("当前窗口内元素： " + elements.size)
    val window = context.window
    println("当前窗口：" + window.getStart + " -> " + window.getEnd)

    out.collect((elements.head._1, elements.map(_._2).sum))
  }
}


dataStream.map(data => (data.id, 1L))
.keyBy(_._1)
.timeWindow(Time.seconds(5), Time.seconds(3))
.process(new countTemperatureProcessWindowFunction)
```

* ProcessWindowFunction 和 AggeragationFunction/ReduceFunction 混合使用

```scala
dataStream.map(data => (data.id, 1L))
.keyBy(_._1)
.timeWindow(Time.seconds(5), Time.seconds(3))
.aggregate(new countTemperatureAggregation, new countTemperatureProcessWindowFunction)

// countTemperatureAggregation 和 countTemperatureProcessWindowFunction
// 都在上面的代码中有贴出来
```

在这里先经过一个聚合函数进行聚合，这样一个窗口中输出的数据就只有一个了，

然后这个时候将这一个结果在输出到 `ProcessWindowFunction` 函数中，然后就可以获取到窗口的上下文了

---

#### 全窗口函数和窗口函数

全窗口函数是说，DataStream 只有一个并行度，

窗口函数是DataStream 是多个并行度的，如经过keyBy 操作之后的DataStream 获取KeyedStream 一个keyedStream 就是一个并行度

```scala
class MyWindowFunction extends WindowFunction[(String, Double, Long), String, String, TimeWindow] {
  override def apply(key: String, window: TimeWindow, input: Iterable[(String, Double, Long)], out: Collector[String]): Unit = {
    out.collect(window.getStart + "->" + window.getEnd + " " + window.toString)
  }
}

.timeWindow(Time.seconds(5), Time.seconds(3))
.apply(new MyWindowFunction)
```

