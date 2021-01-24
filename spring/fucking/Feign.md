#### Feign

---

添加依赖和注解

```java
server:
  port: 8765

spring:
  application:
    name: EurekaFeign

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/

<dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>

@EnableEurekaClient
@EnableFeignClients
```

以上的步骤一个应用就具备了Feign 的功能

```java
@FeignClient(value = "EurekaClient", configuration = FeignConfig.class)
public interface FeignClientOP {

    @GetMapping("/")
    public String sayHi();
注意不要写为 value = "/EurekaClient"
```

这样当访问：http://localhost:8764/hi 的时候。就会出现

```java
hello： 8763
hello： 8762
.....
的切换，这里还是和之前的情况一样运行俩个 EurekaClient 实例
```

---

> `FeignClient` 注解使用创建申明式API接口，在上面的代码中，value会和name(另外一个参数)一样，是被调用服务的 `ServiceId` , configuration 指向`FeignClient`   的配置类，在默认情况下，这个类注入默认的 `Decoder Encoder Contract` 等配置的 `Bean` , `fallback()` 为配置熔断器的处理类。

**FeignClient 配置**

>默认的配置类为 `FeignClientsConfiguration` 打开这个类，里面里面注入了很多配置类，如果按照我们上面的方式，重写一个配置类，那么这个类就不会生效了，在默认配置类中，当请求失败之后，不会再发生请求 `Retryer.NEVER_RETRY` 如在上面我们的配置累中当失效之后还会发送5次请求，重试间隔为100航秒，最大重试时间是1秒。
>
>在`Feign`中，`Client ` 是非常重要的一个组件，`Feign`  最终是发送 `Request` 请求和接受 `Response` 响应都是由这个组件实现的。

**Feign 如何实现负载均衡**

>在 `FeignRibbonClientAutoConfiguration` 类配置了 `Client` 的类型(包括 `HttpURLConnection` `okHttp` 和 `HttpClient` ) 最终容器中注入的是 `Client`的实现类，`LoadBalancerFeignClient` 这就是负载均衡客户端，在这个类中的 `excute` 方法，就是请求执行的方法，这个方法中执行 `RibbonRequest` 而这个请求时发到了 `Ribbon` 组件中，也就是说 `Feign` 最终是通过 `Ribbon` 实现负载均衡。



  



















