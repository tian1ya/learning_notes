#### 为什么分区

> Kafka 的消息组织方式实际上是三级结构，主题 -> 分区 -> 消息
>
> 主题下的每个消息只会保存在某一个分区中，而不会再多个分区中保存多份。
>
> 那么为什么要分区呢？
>
> 主要的一个原因就是`实现系统的高伸缩性(scalability)`, 不同的分区可以放到不同的机器上，**而数据的读写也都是针对分区粒度而进行的**，这样每个节点的机器都可以独立的执行各自分区的读写请求处理。并且可以通过添加新的节点机器来增加整理系统的吞吐量。

#### 分区策略

> **分区是实现负载均衡和高吞吐量的关键**
>
> 分区策略就是决定将消息发送到哪个分区的算法。kafka 有自定义的分区算法，同时用户可也可自己定义分区策略，需要显示的配置分区策略实现类`partitioner.class`， 你需要些一个类，这个类实现`org.apache.kafka.clients.producer.Partitioner`  接口，它有2个方法
>
> `partition/close`
>
> ```java
> public class partition1 implements Partitioner {
> 
>     /*
>         这里又必要查看下，默认的分区 DefaultPartitioner 的方法
>         cluster 可以拿到当前集群的一些信息,如有多少主题，多少 broker 等
>      */
>     @Override
>     public int partition(String topic, Object key, byte[] bytes, Object value, byte[] bytes1, Cluster cluster) {
> //Integer partitionCnt = cluster.partitionCountForTopic(topic);
> //return key.hashCode() % partitionCnt;
> // 这里具体如何分区写数据，是根据具体业务逻辑去写的
>         return 1;
>     }
> 
>     @Override
>     public void close() {
>     }
> 
>     @Override
>     public void configure(Map<String, ?> map) {
>     }
> }
> ```
>
> * 轮询策略
>
> > 也称 Round-robin 策略，即顺序分配。
> >
> > 轮询策略有非常优秀的负载均衡表现，它总是能保证消息最大限度地被平均分配到所有分区上，故默认情况下它是最合理的分区策略，也是我们最常用的分区策略之一
>
> * 随机策略
>
> > 也称 Randomness 策略。所谓随机就是我们随意地将消息放置到任意一个分区上，如下面这张图所示。
>
> * 按消息键保序策略
>
> > Kafka 允许为每条消息定义消息键，简称为 Key。这个 Key 的作用非常大，它可以是一个有着明确业务含义的字符串，比如客户代码、部门编号或是业务 ID 等
> >
> > ```java
> > List partitions = cluster.partitionsForTopic(topic);
> > return Math.abs(key.hashCode()) % partitions.size();
> > ```

#### kafka 的消息格式及其压缩

> 现在有 v1 和 v2 2种消息格式，其中 v2 是对 v1 的一些弊端做了些修改。
>
> 就是把消息的公共部分抽取出来放到外层消息集合里面，这样就不用每条消息都保存这些信息了。
>
> 还有一个就是压缩算法的改进。
>
> kafka 中的压缩算法可以是发送在2个地方，生成者端和 Broker 端。
>
> 
>
> ```java
> Properties props = new Properties(); 
> props.put("bootstrap.servers", "localhost:9092"); 
> props.put("acks", "all"); 
> props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer"); props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer"); 
> // 开启GZIP压缩 
> props.put("compression.type", "gzip");
> 
> Producer producer = new KafkaProducer<>(props);
> ```
>
> 然后在消费者端进行解压缩，消费者在读取消息的时候就可以读到数据的压缩格式，然后在解压缩。
>
> **Producer 端压缩、Broker 端保持、Consumer 端解压缩。**
>
> 如果 `Producer` 运行机器本身 `CPU` 已经消耗殆尽了，那么启用消息压缩无疑是雪上加霜，只会适得其反。压缩就是以时间换空间，CPU 压缩需要消耗时间，然后在后续的IO读取上就节省很多。
>
> 如果你的环境中带宽资源有限，那么我也建议你开启压缩。事实上我见过的很多 Kafka 生产环境都遭遇过带宽被打满的情况

#### kafka 做到不丢失数据

> Kafka 是能做到不丢失消息的，只不过这些消息必须是已提交的消息，而且还要满足一定的条件。
>
> **生产者程序丢失数据**
>
> > `producer.send(msg)` 异步发送消息的时候就会导致数据丢失，所以建议使用有回调的方式发送数据。
> >
> > **Producer 永远要使用带有回调通知的发送 API**，也就是说不要使用 producer.send(msg)，而要使用 producer.send(msg, callback)。
>
> 消费者程序丢失数据
>
> > 主要体现在 Consumer 端要消费的消息不见了。Consumer 程序有个“位移”的概念，表示的是这个 Consumer 当前消费到的 Topic 分区的位置
> >
> > 要对抗这种消息丢失，办法很简单：维持先消费消息（阅读），再更新位移（书签）的顺序即可。