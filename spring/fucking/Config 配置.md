#### Config Server

都是新建服务，不是在之前联系的基础上在建服务，服务太多，机器跑不过来了

---

**本地仓库读取文件**

> 将所有的配置文件同一写在 `Config-Server` 的工程目录下，`Config-Server` 暴露API 接口，`Config-client` 会通过调用这个接口来读取配置文件。

配置 `Config-Server` 

```yam
spring:
  cloud:
    config:
      server:
        native:
          search-locations: classpath:/shared
          // 配置文件目录
  profiles:
    active: naive
  application:
    name: ConfigServer
server:
  port: 8767
```

在 `shared` 目录下建立文件 `ConfigClient-dev.yml`及配置 (文件名方法时由约定的)

```yaml
server:
  port: 8762
fool: api version 1
```

配置 `Config-Client` 新建 `bootstrap.yml` 这个配置文件是优先于 `application` 的配置文件

 ```yml
spring:
  application:
    name: ConfigClient
  cloud:
    config:
      # 有了这两个配置，就不需要使用uri 的方式去到config 服务中去找peizhi
      #  而是先去Eureka 中去找 config-server 然后再去 这个服务中去找配置
      # 
      # 会向这个地址读取配置信息，如果没有读取成功则快速失败
	  # 在 8789 中的配置文件目录下找 {spring.application.name}-{profiles.active}.yml 的文件并读取
      uri: http://localhost:8789
      enabled: true
      service-id: ConfigServer
  profiles:
    active: dev
 ```

 `Config-Client`  中 `application`  的配置

```python
server:
  port: 8790
eureka:
  client:
    defaultZone:
      service-url: http://localhost:8761/eureka/
```

这里需要注意的是，关于依赖的配置， `Config-Client`  和 `Config-Server` 中的依赖配置是不一样的。

 `Config-server`  

```yml
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-config-server</artifactId>
        </dependency>
```

 `Config-Client`  中的配置

```yam
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-config</artifactId>
        </dependency>
```

否则一值是读取不到配置服务中的信息

---

**配置GIT读取配置**

只有配置文件变化 `config-server` 的配置

````
spring:
  cloud:
    config:
      server:
        git:
          uri: https://git.oschina.net/chrywhy/test
          search-paths: spring-cloud/helloworldConfig
  application:
    name: config-server
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
server:
  port: 8789
```

`config-client` 的配置 `bootstap` 没有什么变化，只有 `application` 中的 `name` 变为 `config-client`

---

**高可用配置**

所有的服务都向 `config-service` 中发送读取请求，所以有必要将  `config-service` 做成一个高可用的服务， 新建 `Eureka-server` (操作的时候还是使用之前的   `Eureka-server` )

步骤还是和之前的一样，将这个两个服务注册到  `Eureka-server` 

如何实现高可用的框架，直接就是开启多个  `config-service`  实例，并修改 port， 发送请求的时候就会轮流发送到 不同的  `config-service`  上。

---

在 读取配置的 `Controller` 上 增加注解 `@RefreshScope ` ，然后再每次配置修改之后，发送请求

`http://localhost:8761/bus/refresh` 将读取到的配置更新。