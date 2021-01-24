```
1. 可以写基本数值 @Value("张三")
2. Spring 的表达式 #{} 等
3. ${} 取出配置文件中的值，在运行环境变量里面的值
```

Spring 完成属性赋值的操作

* 可以写基本数值 @Value("张三")
* Spring 的表达式 #{} 等
* ${} 取出配置文件中的值，在运行环境变量里面的值

---

##### @Value

```java
@Value("张三")
private String name;
```

---

##### ${} 取出配置文件中的值,在运行环境变量里面的值

先需要使用 `@PropertySource` 将配置文件import

```java
@Configuration
@PropertySource(value ={"classpath:/person.properties"} )
public class MainConfigSetPropertyValues {

    @Bean
    public Person person() {
        return new Person();
    }
}
```

然后可以根据变量

```java
@Value("${nicks}")
private String nickName;
```

Person.properties 配置文件

```java
nicks=dsdsd
```

这些使用 @PropertySource 全部将配置都已经加载到环境变量中了，所以也可以在容器中获取到

```java
ConfigurableEnvironment environment = applicationContext.getEnvironment();
String property = environment.getProperty("nicks");
System.out.println(property);
```

