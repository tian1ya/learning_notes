#### 路由网关 Zuul

---

致力于 动态路由、过滤、监控、弹性伸缩和安全。

**为什么需要Zuul**

重要性主要体现在一下几个方面：

> 1. Zuul 和 Ribbon 及 Eureka 相结合，可以实现只能路由和负载均衡，Zuul 能够将请求流量按照某种策略分发到集群状态的某个服务实例。
> 2. 网关将所有服务的API 统一聚合，并统一对外暴露，外界系统调用API接口时，都是由网关对外暴露，外界并不需要知道微服务系统中各个服务之间相互调用的复杂性，微服务系统也保护器内部微服务单元的API接口，防止其它被外界直接调用，导致敏感信息对外暴露。
> 3. 网关服务可以做用户身份认证和权限认证，防止非法请求操作API接口。
> 4. 实时监控功能，实时日志输出。
> 5. 流量监控

---

**Zuul 工作原理**

> Zuul 的核心是一系列过滤器，可以在http请求的发起和响应返回期间执行一系列的过滤，主要有一下四中过滤器
>
> 1. PRE 过滤器，请求路由到具体的服务之前执行的，这种类型的过滤器可以做安全验证
> 2. ROUTING 过滤器，用于将请求路由到具体的微服务实例
> 3. POST 过滤器， 请求已被路由到微服务之后执行。
> 4. ERROR 过滤器，发送错误时候执行
>
> 过滤器之间不能相互通信，需要通过RequestContext 共享数据。

---

**Zuul 执行过程**

> 当客户端Request 请求进入Zuul 网关服务时，网关先进入 `pre filter` 进行一系列的验证、操作、或者判断
>
> 然后交给 `routing filter` 进行路由转发，并转发到具体的服务实例进行逻辑处理，返回数据。
>
> 最有由 `post filter` 进行处理，该类型的处理结束之后将 Response 返回给客户端

---

**配置**

> ```
> @EnableZuulProxy
> @EnableEurekaClient
> @SpringBootApplication
> ```
>
> --
>
> 配置路由
>
> ```
> server:
>   port: 8766
> 
> spring:
>   application:
>     name: EurekaZuul
> 
> eureka:
>   client:
>     service-url:
>       defaultZone: http://localhost:8761/eureka/
> 
> // 路由转发，凡是 http://localhost:8766/hiapi/** 的路由都会转发到 EurekaClient 的服务实例中去。
> zuul:
>   routes:
>     hiapi:
>       path: /hiapi/**
>       serviceId: EurekaClient
>   
> // 配置依赖
> <dependency>
>             <groupId>org.springframework.cloud</groupId>
>             <artifactId>spring-cloud-starter-zuul</artifactId>
>             <version>1.4.3.RELEASE</version>
> </dependency>
> ```

上面的配置会做负载均衡，如果不做负载均衡：

> zuul:
> routes:
> hiapi:
> path: /hiapi/**
> Url: /

直接转发到 指定的url，如果即想做指定的转发和负载均衡，那么需要自己维护一份注册列表。

也可以指定api 的版本号

> zuul:
> 	routes:
> 		hiapi:
> 			path: /hiapi/**
> 			serviceId: EurekaClient
>
> ​	zuul.prefix:/v1
>
> 访问的时候：
>
> http://localhost:8766/v1/hiapi/

---

**Zuul 配置熔断器**

> Zuul 作为 Netflix 组件，可以与Ribbon、Eureka、和Hystrix 等组件结合实现负载均衡、熔断器功能。默认情况下 Zuul 和 Ribbon 相结合，实现类负载均衡的功能，实现熔断机制功能需要实现 `ZuulFallBackProvoder` 的接口，重写两个方法 `getRoute()` 指定熔断功能应用于哪些路由的服务，`fallbackResponse()` 为进入熔断功能时候执行的逻辑。
>
> `ZuulFallBackProvoder` 这个接口已经将会被删除，新的接口应该是 `FallbackProvider`

```java
@Component
public class fallBack12 implements FallbackProvider {
    @Override
    public String getRoute() {
        // 熔断同于哪个服务，如果所有的服务中都需要熔断那么   return "**";
        return "EurekaClient";
    }
    @Override
    public ClientHttpResponse fallbackResponse(String route, Throwable cause) {
        // 进入熔断之后的功能
        return new ClientHttpResponse() {
            @Override
            public HttpStatus getStatusCode() throws IOException {
                return HttpStatus.OK;
            }
            @Override
            public int getRawStatusCode() throws IOException {
                return 200;
            }
            @Override
            public String getStatusText() throws IOException {
                return "OK";
            }
            @Override
            public void close() {

            }
            @Override
            public InputStream getBody() throws IOException {
                return new ByteArrayInputStream("oooops! error, i'am the fallback".getBytes());
            }
            @Override
            public HttpHeaders getHeaders() {
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                return headers;
            }
        };
    }
}
```

然后再测试的时候将 服务 `EurekaClient` 关闭 发送 `http://localhost:8766/hiapi/` 请求就可以看见 `oooops! error, i'am the fallback` 错误提示了。

---

**配置过滤器**

```java
@Component
public class MyFilter extends ZuulFilter {
    @Override
    public String filterType() {
        // 过滤类型
        // ERROR_TYPE = "error";  发生错误的时候执行
    	// POST_TYPE = "post";    路由到具体的微服务实例 之后执行
    	// PRE_TYPE = "pre";      请求路由到具体的微服务之前执行
    	// ROUTE_TYPE = "route";  路由到具体的微服务实例的时候执行
        return PRE_TYPE;
    }
    @Override
    public int filterOrder() {
        return 0; // 过滤顺序，越小，越早执行
    }
    @Override
    public boolean shouldFilter() {
        return true; // true 会执行run 方法， false 则不执行。
    }
    @Override
    public Object run() throws ZuulException {
        RequestContext context = RequestContext.getCurrentContext();
        HttpServletRequest request = context.getRequest();
        String token = request.getParameter("token");
        if (token == null){
            context.setSendZuulResponse(false);
            context.setResponseStatusCode(401);
            try {
                context.getResponse().getWriter().write("token is exmpty");
            } catch (IOException e) {
                return null;
            }
        }
        return null;
    }
}
```







