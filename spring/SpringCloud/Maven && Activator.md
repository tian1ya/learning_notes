**Maven 常使用执行命令**

```java
mvn clean 删除工程 target 目录下的所有文件
mvn package  将工程打包
mvn package -Dmaven.test.skip=true
mvn compile 编译工程代码，不生成Jar包
mvn install 将生成的jar包安装到本地仓库
mvn spring-boot:run 启动springboot 工程
mvn test 测试
mvn idea:idea 生成idea 项目
mvn jar:jar 只打jar包
mvn validate 检查资源是否可用
```

如何在不同的环境中使用不同的配置文件

```java
当在resource 目录下，配置了 application-test.yml/application-dev.yml 等文件之后。
然后还需要在 application.yml 中配置，spring.profiles.active: local
也就是默认在 local 下运行
当在dev环境中执行的时候，
java -jar springbootdemo.jar --spring.profiles.active=dev 就可以使用 dev 的配置文件了
```

获取`SpringBoot` 项目的信息

添加依赖

```java
<dependency>
	<groupid>
		org.springframework.boot
	</groupid> 
	<artifactid>
		spring-boot-starter-actuator
	</artifactid>
</dependency>
```

`application.yml` 文件中配置：

```yam
management: 
	port: 9001 
	security:
		enabled: false
```

配置了`SpringBoot`  启动对外暴露的REST API 接口的端口为9001，然后通过API端口可以获取信息

这些接口有 http://localhost:9091/heath

```yaml
/autoconfig  自动配置报告，记录那些自动配置条件通过来，那些没有通过
/configprops 配置属性如何注入 Bean
/beans 上下文全部的Bean及之间的关系
/dump  线程活动快照 
/env   获取全部环境变量值
/env/{name} 获取特定的环境变量值
/heath 健康指标
/info   程序信息
/mappings 描述全部的URI路径
/metrics  获取程序度量信息
/metrics/{name} 获取程序度量信息
/shutdown  关闭应用程序
/trace  基本的http请求追踪信息，时间戳 header 等
```

配置jpa

```yml
spring: 
	datasource:
		dn.ver-class-name: com.mysql.jdbc.Driver
		url : jdbc:mysql://localhost:3306/spring-cloud?useUnicode=true&characterEncoding=u 					tf8&characterSetResults=utf8
		username : root
		password : 123456 
	jpa :
		hibernate:
		ddl-auto: create #第一次简表 create 后面用 update
	show-sql: true
```

配置`Swagger2` 编写在线文档