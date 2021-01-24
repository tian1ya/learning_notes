#### [断路器（Curcuit Breaker）模式](https://www.cnblogs.com/chry/p/7278853.html)

---

```java
在分布式环境下，特别是微服务结构的分布式系统中， 一个软件系统调用另外一个远程系统是非常普遍的。这种远程调用的被调用方可能是另外一个进程，或者是跨网路的另外一台主机, 这种远程的调用和进程的内部调用最大的区别是，远程调用可能会失败，或者挂起而没有任何回应，直到超时。更坏的情况是， 如果有多个调用者对同一个挂起的服务进行调用，那么就很有可能的是一个服务的超时等待迅速蔓延到整个分布式系统，引起连锁反应， 从而消耗掉整个分布式系统大量资源。最终可能导致系统瘫痪。

断路器（Circuit Breaker）模式就是为了防止在分布式系统中出现这种瀑布似的连锁反应导致的灾难。

一旦某个电器出问题，为了防止灾难，电路的保险丝就会熔断。断路器类似于电路的保险丝， 实现思路非常简单，可以将需要保护的远程服务嗲用封装起来，在内部监听失败次数， 一旦失败次数达到某阀值后，所有后续对该服务的调用，断路器截获后都直接返回错误到调用方，而不会继续调用已经出问题的服务， 从而达到保护调用方的目的, 整个系统也就不会出现因为超时而产生的瀑布式连锁反应。

close状态下， client向supplier发起的服务请求， 直接无阻碍通过断路器， supplier的返回值接直接由断路器交回给client.
    
open状态下，client向supplier发起的服务请求后，断路器不会将请求转到supplier, 而是直接返回client, client和supplier之间的通路是断的

trip: 在close状态下，如果supplier持续超时报错， 达到规定的阀值后，断路器就发生trip, 之后断路器状态就会从close进入open.
```

**扩展模式**

基本的断路器模式下，保证了断路器在open状态时，保护supplier不会被调用， 但我们还需要额外的措施可以在supplier恢复服务后，可以重置断路器。一种可行的办法是断路器定期探测supplier的服务是否恢复， 一但恢复， 就将状态设置成close。断路器进行重试时的状态为半开（half-open）状态。

---

```java
 @Service
public class HelloService {
    @Autowired RestTemplate restTemplate;

    @HystrixCommand(fallbackMethod = "serviceFailure")
    public String getHelloContent() {
        return restTemplate.getForObject("http://SERVICE-HELLOWORLD/",String.class);
    }
    public String serviceFailure() {
        return "hello world service is not available !";
    }
}
```

`@HystrixCommand` 注解定义了一个断路器，它封装了`getHelloContant()` 方法， 当它访问的`SERVICE-HELLOWORLD` 失败达到阀值后，将不会再调用`SERVICE-HELLOWORLD`， 取而代之的是返回由`fallbackMethod`定义的方法`serviceFailure（）`。`@HystrixCommand`注解定义的`fallbackMethod`方法，需要特别注意的有两点：

>1. fallbackMethod的返回值和参数类型需要和被@HystrixCommand注解的方法完全一致。否则会在运行时抛出异常。比如本例中，serviceFailure（）的返回值和getHelloContant()方法的返回值都是String。
>
>2. 当底层服务失败后，fallbackMethod替换的不是整个被@HystrixCommand注解的方法（本例中的getHelloContant), 替换的只是通过restTemplate去访问的具体服务。可以从中的system输出看到， 即使失败，控制台输出里面依然会有“call SERVICE-HELLOWORLD”

**在Feign应用中使用断路器**

> 1. Feign内部已经支持了断路器，所以不需要想Ribbon方式一样，在Spring Boot启动类上加额外注解
> 2. 用@FeignClient注解添加fallback类， 该类必须实现@FeignClient修饰的接口。

```java
@FeignClient(name = "SERVICE-HELLOWORLD", fallback = HelloWorldServiceFailure.class)
2 public interface HelloWorldService {
3     @RequestMapping(value = "/", method = RequestMethod.GET)
4     public String sayHello();
5 }
```

> 创建HelloWorldServiceFailure类， 必须实现被@FeignClient修饰的HelloWorldService接口。注意添加@Component或者@Service注解，在Spring容器中生成一个Bean,要保证错误方法和原来调用方法的返回是一致的。

```java
@Component
2 public class HelloWorldServiceFailure implements HelloWorldService {
3     @Override
4     public String sayHello() {
5         System.out.println("hello world service is not available !");
6         return "hello world service is not available !";
7     }
8 }
```

---

**Hystrix一个很重要的功能是，可以通过HystrixCommand收集相关数据指标. Hystrix Dashboard可以很高效的现实每个断路器的健康状况。**

> 在Spring Boot启动类上用`@EnableHystrixDashboard注解和@EnableCircuitBreaker注解。需要特别注意的是我们之前的Feign服务由于内置断路器支持， 所以没有**@EnableCircuitBreaker注解，但要使用Dashboard则必须加**，如果不加，Dashboard无法接收到来自Feign内部断路器的监控数据，会报“Unable to connect to Command Metric Stream”错误`

然后就可以访问`/hystrix，这个URL将`dashboard指向定义在Hystrix客户端应用中的/hystrix.stream

https://www.cnblogs.com/chry/p/7286601.html 

