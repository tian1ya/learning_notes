### 负载均衡 Ribbon && Feign

---

**RestTemplate**

>`RestTemplate`  是 `Spring Resource` 中一个访问第三方 `Restful`  api 接口的网络请求框架，`RestTemplate` 是用来消费REST 服务的。与`http` 协议的一些方法紧密连接，例如`HEAD GET POST PUT DELETE OPTIONS` 等，这些方法对象在`RestTemplate` 类中的方法为 `headForHeaders() getForObject() postForObject() put() delete()` 等。
>
>如：
>
>```java
>@RestController
>public class RestTestController{
>    @GetMapping("/testRest")
>    public String testRest(){
>        RestTemplate restTemplate = new RestTemplate();
>        return restTemplate.getForObject("https://www.baidu.com/", String.class);
>    }
>}
>```

**Ribbon 和 RestTemplate 结合实现负载均衡**

负载均衡将负载分摊到多个执行单元上，常见的负载均衡有两种方式：

>1. 独立进程单元，通过负载策略将请求转发到不同的执行单元上，如 Ngnix
>2. 将负载逻辑以代码的形式封装到服务消费者的客户端上，服务消费者客户端维护了一份服务提供者的信息列表，有了信息列表，通过负载均衡策略将请求分摊给多个服务提供者。 如 Ribbon
>
>Ribbon 有两种使用方式，一种是和 `RestTemplate` 相结合，另外一种是和 `Feign` 相结合

这里有一点注意的是，在配置Eureka 的时候

>
>
>```
>server:
>  port: 8761
>
>eureka:
>  instance:
>    hostname: localhost  # EurekaService 需要这个配置，其它服务就不需要了
>  client:
>#    一下俩项配置，eureka 不将自己注册
>    register-with-eureka: false
>    fetch-registry: false
>#    服务中心
>    service-url:
>      defaultZone: http://${eureka.instance.hostname}:${server.port}/eureka}
>
>server:
>  port: 8764
>eureka:
>#  instance:
>#  hostname: EurekaRibbon 如果也加入这个配置，那么注册中心并不能得到这个 EurekaRibbon
>  client:
>    service-url:
>      defaultZone: http://localhost:8761/eureka
>spring:
>  application:
>    name: EurekaRibbon
>    
>// 两个 Client 实例  
>server:
>  port: 8762
>eureka:
>  client:
>    service-url:
>      defaultZone: http://localhost:8761/eureka
>spring:
>  application:
>    name: EurekaClient
>     
>server:
>  port: 8763
>eureka:
>  client:
>    service-url:
>      defaultZone: http://localhost:8761/eureka
>
>spring:
>  application:
>    name: EurekaClient
>```

当在 `http://localhost:8764/hi` 经过上面的两个Client 的配置，我访问 `Ribbon` 负载均衡的时候，`Ribbon` 的负载均衡会将请求分别发送到这两个实例。

同时也可以在 `Ribbon`  服务中，

```java
@RestController
public class testRibbon {
    @Autowired
    private LoadBalancerClient balancerClient;
    @GetMapping("/testRibbon")
    private String testRibbon(){
        // 以下这个方法可以获取客户端的信息，也就是Ribbon 当前将请求发送到了Client 的那个实例
        // 那个实例 的信息。
        ServiceInstance client = balancerClient.choose("EurekaClient");
        return client.getHost() + " : " + client.getPort();
    }
}
```

> `LoadBalancerClient` 这个类是从 `Eureka Client` 中获取注册表信息(每个 `Eureka client` 都可以从 `Eureka service`获取全部的注册信息)，并将服务注册信息都缓存了一份，从而进行负载均衡，当然也可以不从   `Eureka client`  中获取注册列表，这时候需要自己维护一份注册列表信息。

Ribbon 的负载均衡主要是通过  `LoadBalancerClient`   实现负载均衡

---

---





















