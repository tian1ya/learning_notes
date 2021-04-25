#### keyBy之后的操作

1. `keyBy` 之后可以使用 `.process` 对分组之后每一个来的数据进行操作
2. `keyBy` 之后，上窗口 `.window`， 然后再窗口中对数据进行聚合操作



#### `keyBy` 之后 `.process`

```scala
windowAggStream
.keyBy(data -> data.getWindowEnd())
.process( new TopNHotItems(5))
```

`process(KeyedProcessFunction<KEY, T, R> keyedProcessFunction)`

`Process`这里是一个`Flink` 最底层的`API`, 接受的也是一个`KeyedProcessFunction` , 这是一个抽象类，所以`TopNHotItems` 继承了它，需要实现一个方法

`public abstract void processElement(I value, Context ctx, Collector<O> out) `

数据流中，每来一条数据就会调用这个方法，这个方法可以是返回一个或者0个数据。

因为这是`Flink` 最底层的api，所以还有其他的东西，包括获得当前的上下文`ctx`, 生命周期方法`open`，以及一些定时器功能。

```scala
public class TopNHotItems extends KeyedProcessFunction<Long, ItemViewCount, String> {
    private int topN;

    public TopNHotItems(int topN) {
        this.topN = topN;
    }

    ListState<ItemViewCount> itemViewCountListState;

    @Override
    public void open(Configuration parameters) throws Exception {
      // 生命周期方法，用于初始化状态。
        itemViewCountListState = getRuntimeContext().getListState(new ListStateDescriptor<ItemViewCount>("ItemViewCount", ItemViewCount.class));
    }

    @Override
    public void processElement(ItemViewCount value, Context ctx, Collector<String> out) throws Exception {
        // 定义状态，保存当前窗口所有输出的 ItemViewCount
        // 每来一条数据都会掉用这个方法，并注册定时器，
        itemViewCountListState.add(value);
        // 同一个窗口中的所有数据的 getWindowEnd 都是一样的，在Flink 底层是以时间作为唯一表示的
        // 所以同一个窗口中的多条数据多次注册定时器，等于是注册了一个定时器
        ctx.timerService().registerEventTimeTimer(value.getWindowEnd() + 1);
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<String> out) throws Exception {
        // 定时器触发，当前已收集到所有的数据，排除输出
        ArrayList<ItemViewCount> itemViewCounts = Lists.newArrayList(itemViewCountListState.get());
        itemViewCounts.sort(new Comparator<ItemViewCount>() {
            @Override
            public int compare(ItemViewCount o1, ItemViewCount o2) {
                return (o2.getCount().intValue() - o1.getCount().intValue());
            }
        });

        StringBuilder builder = new StringBuilder();
        builder.append("current windowEnd: " + new Timestamp(timestamp - 1));
        for (int i = 0; i < Math.min(this.topN, itemViewCounts.size()); i++) {
            ItemViewCount viewCount = itemViewCounts.get(i);
            builder.append("{ ").append("ItemId: " + viewCount.getItemId()).append(", count: " + viewCount.getCount()).append("} \n");
        }

        out.collect(builder.toString());
    }
}
```

看看另外一个例子

```java
public class LoginFailedDetectWarning extends KeyedProcessFunction<Long, LoginEvent, LoginFailWarning> {

    // 最大连续登陆失败次数
    private int maxLoginFailTimes;

    public LoginFailedDetectWarning(int maxLoginFailTimes) {
        this.maxLoginFailTimes = maxLoginFailTimes;
    }

    ListState<LoginEvent> loginEventListState;
    // 保存注册的定时器时间戳
    ValueState<Long> timerTSState;

    @Override
    public void open(Configuration parameters) throws Exception {
        loginEventListState = getRuntimeContext().getListState(new ListStateDescriptor<LoginEvent>("login event list", LoginEvent.class));
        timerTSState = getRuntimeContext().getState(new ValueStateDescriptor<Long>("timer ts state", Long.class));
    }

    @Override
    public void processElement(LoginEvent value, Context ctx, Collector<LoginFailWarning> out) throws Exception {
        // 判断当前登陆事件类型

        if ("fail".equals(value.getLogInState().toLowerCase(Locale.ROOT))) {
            loginEventListState.add(value);

            // 如果没有定时器，注册一个2秒的定时器

            if (timerTSState.value() == null) {
                long futureTimer = value.getTimestamp() + 2 * 1000;
                ctx.timerService().registerEventTimeTimer(futureTimer);
                timerTSState.update(futureTimer);
            }
        } else {
            // 登陆成功，删除定时器，清空状态，重新开始
            if ( timerTSState.value() != null) {
                ctx.timerService().deleteEventTimeTimer(timerTSState.value());
            }
             loginEventListState.clear();
            timerTSState.clear();
        }
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<LoginFailWarning> out) throws Exception {
        // 至少you2s 内有登陆失败
        // 判断 登陆失败个数
        ArrayList<LoginEvent> loginFailEvents = Lists.newArrayList(loginEventListState.get());
        int loginFailedCount = loginFailEvents.size();

        if (loginFailedCount >= maxLoginFailTimes) {
            out.collect(new LoginFailWarning(ctx.getCurrentKey(),
                    loginFailEvents.get(0).getTimestamp(),
                    loginFailEvents.get(loginFailedCount - 1).getTimestamp(), "login fail in 2s for: " + loginFailedCount + " times"));

        }
        loginEventListState.clear();
        timerTSState.clear();
    }
}

streamOperator
  .keyBy(data -> data.getUserId())
  .process( new LoginFailedDetectWarning(2))
```



#### `keyBy` 之后使用 `window` 以及聚合操作

```java
dataStream
  .keyBy(data -> data.getItemId())
  .window
  .aggregate
```

`window` 部分可以定义各种窗口

`aggregate` 在窗口中进行聚合操作

其可调用的接口有

1. `aggregate(AggregateFunction<T, ACC, R> function)`
2. `apply(WindowFunction<T, R, K, W> function)`
3. `aggregate(AggregateFunction<T, ACC, V> aggFunction, WindowFunction<V, R, K, W> windowFunction)`
4. `aggregate(AggregateFunction<T, ACC, V> aggFunction, ProcessWindowFunction<V, R, K, W> windowFunction)`

##### aggregate(AggregateFunction<T, ACC, R> function)

```java
public class ItemCountAgg implements AggregateFunction<UserBehiver, Long, Long> {
    @Override
    public Long createAccumulator() {
        return 0L;
    }

    @Override
    public Long add(UserBehiver value, Long accumulator) {
        return accumulator + 1;
    }

    @Override
    public Long getResult(Long accumulator) {
        return accumulator;
    }

    @Override
    public Long merge(Long a, Long b) {
        return a + b;
    }
}

dataStream
.keyBy(data -> data.getItemId())
.window(SlidingEventTimeWindows.of(Time.seconds(5), Time.seconds(5)))
.aggregate(new ItemCountAgg())
```

聚合函数接受数据流中的数据，每来一个数据聚合一次，当窗口触发的时候，输出聚合结果，**这里的聚合函数 `AggregateFunction` 只能获取到当前数据。**

##### apply(WindowFunction<T, R, K, W> function)

`aggFunction` 还是和上面的是一样的。不同的是这里多了一个 `windowFunction`, 该函数可以获取接受到的每一条数据，并缓存下来，触发窗口操作的时候进行计算，以及`keyBy` 的 `key` 除此之外还有一个窗口信息。

```java
public interface WindowFunction<IN, OUT, KEY, W extends Window> extends Function, Serializable {
	void apply(KEY key, W window, Iterable<IN> input, Collector<OUT> out) throws Exception;
}
```

注意这里的 `apply` 中还有一个 `input` 是数据流中的数据，这里仅仅是做收集使用的，也就是说使用窗口函数会将窗口中的数据进行收集，在窗口触发操作的时候对这里收集到的数据进行操作。

```java
public class UVCountResult implements WindowFunction<UserBehiver, String, Long, TimeWindow> {

    // 全窗口函数Note that this function requires that all data in the windows is buffered until the window is evaluated,
    // as the function provides no means of incremental aggregation.
    // 缺陷比较大啊，需要缓存全部的数据
    @Override
    public void apply(Long aLong, TimeWindow window, Iterable<UserBehiver> input, Collector<String> out) throws Exception {
        // 完成去重, 在出发计算的时候，已经是将窗口中的数据全部收集其了

        HashSet<Long> set = new HashSet<>();
        for (UserBehiver userBehiver : input) {
            set.add(userBehiver.getUserId());
        }

        PageViewCount uv = new PageViewCount("uv", window.getEnd(), (long) set.size());
        out.collect(uv.toString());
    }
}

dataStream
  .keyBy(UserBehiver::getItemId)
  .window(TumblingEventTimeWindows.of(Time.seconds(5)));
	.apply(new UVCountResult());
```

所以这里在实现 `apply` 的时候可以非常的灵活，因为在操作的时候，已经是收集到了所有的数据了。

但是同时也带来了问题，收集到所有数据，意味着会`OOM`, 有些场景下数据是非常多的，即使是只有把个小时甚至是分钟级别的窗口。

上面提到的 `aggregate` 的方法是对每来的一条数据进行聚合操作，在窗口触发的时候输出聚合结果，中间是不缓存数据的，只保留聚合结果的，但是这里并获取不到窗口上下问中的信息。如果你有需要需要将结果和窗口结合，那单纯的聚合是满足不了需求的。

还有刚提到的`WindowFunction` 窗口内会缓存所有的数据，会有`OOM` 的问题。

##### aggregate(AggregateFunction<T, ACC, V> aggFunction, WindowFunction<V, R, K, W> windowFunction)

聚合函数还可以接受2个方法函数，第一个是`AggregateFunction` 用于对每来的一条数据进行聚合，在窗口触发的时候输出聚合结果。

`WindowFunction` 窗口的聚合函数，其输入就是第一个聚合函数`AggregateFunction`的输出。

这个方法结合上面2个方法的优点，窗口中不会缓存所有的结果，只保留聚合结果，然后再最终的输出中还可以获取窗口的信息。

```java
public class ItemCountAgg implements AggregateFunction<UserBehiver, Long, Long> {
    @Override
    public Long createAccumulator() {
        return 0L;
    }

    @Override
    public Long add(UserBehiver value, Long accumulator) {
        return accumulator + 1;
    }

    @Override
    public Long getResult(Long accumulator) {
        return accumulator;
    }

    @Override
    public Long merge(Long a, Long b) {
        return a + b;
    }
}

public class WindowItemCountResult implements WindowFunction<Long, ItemViewCount, Long, TimeWindow> {

    @Override
    public void apply(Long tuple, TimeWindow window, java.lang.Iterable<Long> input, Collector<ItemViewCount> out) throws Exception {
        Long itemId = tuple;
        long windowEnd = window.getEnd();
        Long count = input.iterator().next(); // 这里不会缓存所有的窗口信息，之后有一条聚合结果，所以这里 .next, 获取结果
        out.collect(new ItemViewCount(itemId, windowEnd, count));
    }
}

dataStream
  .keyBy(data -> data.getItemId())
  .window(SlidingEventTimeWindows.of(Time.seconds(5), Time.seconds(5)))
  .aggregate(new ItemCountAgg(), new WindowItemCountResult());
```

##### `aggregate(AggregateFunction<T, ACC, V> aggFunction, ProcessWindowFunction<V, R, K, W> windowFunction)`

另外还可以使用更加底层的 `process api`

和上面不同的是这里的窗口函数变为 `ProcessWindowFunction`, 该函数和 `WindowFunction` 不同的是多了`process` 的上下文，所以这里既可以获取窗口的上下文，有可以有生命周期以及定时器等方法。

```java
public class MarketCountAgg implements AggregateFunction<MarketUserBehivor, Long, Long> {
    @Override
    public Long createAccumulator() {
        return 0L;
    }

    @Override
    public Long add(MarketUserBehivor value, Long accumulator) {
        return accumulator + 1;
    }

    @Override
    public Long getResult(Long accumulator) {
        return accumulator;
    }

    @Override
    public Long merge(Long a, Long b) {
        return a + b;
    }
}

public class MarketingCountResult extends ProcessWindowFunction<Long, ChannelClickCount, Tuple2<String, String>, TimeWindow> {

    @Override
    public void process(Tuple2<String, String> stringStringTuple2, Context context, Iterable<Long> elements, Collector<ChannelClickCount> out) throws Exception {
        String behavior = stringStringTuple2.f0;
        String channel = stringStringTuple2.f1;

        long windowEnd = context.window().getEnd();

        Long count = elements.iterator().next();
        ChannelClickCount result = new ChannelClickCount(behavior, channel, windowEnd, count);
        out.collect(result);
    }
}

andWatermarks
  .keyBy(new Tuple2KeySelector())
  .window(TumblingEventTimeWindows.of(Time.seconds(10), Time.seconds(2)));
  .aggregate(new MarketCountAgg(), new MarketingCountResult())
```

