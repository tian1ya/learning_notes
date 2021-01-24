#### 熔断器 Hystrix

---

**什么是熔断器**

> 在分布式系统中服务于服务错综复杂，一种不可避免的情况是某些服务会出现故障，导致依赖于它们的其它服务出现远程调度的线程阻塞，`Hystrix` 提供了熔断器功能，能够组织防止分布式系统中出现联动故障，`Hystrix`  通过隔离服务的访问点阻止联动故障的。并提供了故障的解决方案。

**Hystrix 解决了什么问题**

> 如果某些不可用的服务不隔离，那么导致整个系统的不可用，就是因为整个系统之间的服务回事相互依赖的关系，尤其是在高并发的情况下，单个服务的延迟会导致整个请求处理延迟状态，可能在几秒钟就是的整个服务处理线程负载和的状态。整个服务都是处于阻塞的状态，最终的结果就是整个服务的线程资源耗尽，就是 **雪崩效应** 。
>
> 就是为了解决**雪崩效应** 而产生了熔断器模式，

**Hystrix 设计原则**

> 1. 防止单个服务的故障耗尽整个服务的 `Servlet` 容器(如 Tomcat) 的线程资源。
> 2. 快速失败机制，如果某个服务出现故障，则调用该服务的请求快速失败，而不是等待
> 3. 提供回退 (fallback) 方式
> 4. 使用熔断机制，防止故障扩展到其它服务
> 5. 提供熔断器的监控组件 `Hystrix Dashboard`  可以实时监控熔断器的状态。

**Hystrix的工作机制**

> 当某个API接口的失败次数在一定时间内小于设定的阈值，那么熔断器处理关闭状态，API工作正常
>
> 如果失败次数在一定时间内大于设定的阈值，那么打卡熔断器，这个API工作出现故障，该接口会迅速执行失败的逻辑(fallback 回退的逻辑)不执行业务逻辑，且请求不会处于阻塞状态
>
> 一段时间之后失败的 API 会处于办打开状态，并将一定数量的请求执行正常逻辑，如果这些请求依然快速失败，那么熔断器继续打开，如果成功的话，熔断器就会关闭。

---

**在Ribbon构建熔断器hystrix**

```java
// 依赖      
<dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-hystrix</artifactId>
            <version>1.3.5.RELEASE</version>
</dependency>

// 注解， 使用hystrix
@EnableHystrix
```

在Feign 上使用

>Feign 的依赖中已经有了 Hystrix 组件，只需要在配置文件中开启 熔断器
>
>```
>feign:
>  hystrix:
>    enabled: true
>```

然后：

> ```
> @FeignClient(value = "EurekaClient", configuration = FeignConfig.class, fallback = fallbackConfig.class)
> public interface FeignClientOP {
>     @GetMapping("/")
>     public String sayHi();
> }
> ```

并实现配置类 `fallbackConfig`，这里这个类一定要`implement` `FeignClientOP` 这个类

```java
@Component
public class fallbackConfig implements FeignClientOP {
    @Override
    public String sayHi() {
        return "error messagexxx";
    }
}
```

这个时候如果请求发给的是 EurekaClient 服务，将这个服务停掉，那么当发送给这个服务请求的时候，就会出现配置类中的错误信息。

---



