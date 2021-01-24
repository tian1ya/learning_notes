####  给容器中注册组件的方式

* 包扫描 + 组件标注注解 @Controller @Service @Repository @Component

* @Bean 导入第三方包里面的主键

* @Import：快速给容器中导入 组件

  * @Import({Color.class, Red.class})
  * ImportSelector 返回需要导入的组件的全类名数组: 使用的会比较多
  * ImportBeanDefinitionRegistrar

* Spring 提供的 FactoryBean 工厂 Bean

  > 默认获取 getObject 方法返回的对象
  > 如果获取 FactoryBean 本身那么在前缀加上 &

---

##### 包扫描 + 组件标注注解 @Controller @Service @Repository @Component

```java
@Configuration
@ComponentScan(value = "com.atguigu.secondCodeRecord")
// 会将"com.atguigu.secondCodeRecord" 路径下凡是带有 @Controller @Service @Repository @Component 注解的类全部注册进来。
```

还可以在`ComponentScan` 中配置 `includeFilters` 仅仅将那些类注册进来，或者 `excludeFilters`  仅仅将那些类排除注册，注意在使用这两个功能的时候需要将`@Configuration`默认方式关闭 `useDefaultFilters = false`

```java
@Configuration
@ComponentScan(
    value = "com.atguigu.secondCodeRecord",
    includeFilters = {
  	// 定义按照注解类型排除，那么排序哪些注解呢？ 排除 Controller、Service, 用的多
  	@ComponentScan.Filter(type = FilterType.ANNOTATION, classes = {Controller.class})
  }
  ,useDefaultFilters = false
)

//--------------------

@Configuration
@ComponentScan(
    value = "com.atguigu.secondCodeRecord",
    includeFilters = {
  // 按照给定类型扫描，这里定义值扫描 BookService类型的类，用的多
  @ComponentScan.Filter(type = FilterType.ASSIGNABLE_TYPE, classes = {BookService.class}),
  }
  ,useDefaultFilters = false
)


// ----------
  @Configuration
@ComponentScan(
    value = "com.atguigu.secondCodeRecord",
    includeFilters = {
  @ComponentScan.Filter(type = FilterType.ASPECTJ, classes = {BookService.class}) 很少使用
  }
  ,useDefaultFilters = false
)
  
  
  
/// -------------
  @Configuration
@ComponentScan(
    value = "com.atguigu.secondCodeRecord",
    includeFilters = {
   // 自定义规则,需要实现一些自定义方法，放回true/false
   @ComponentScan.Filter(type = FilterType.CUSTOM, classes = {MyTypeFilter.class})
  }
  ,useDefaultFilters = false
)

public class MyTypeFilter implements TypeFilter {

    /*
        metadataReader: 读取到的当前正在扫描的类的信息
        metadataReaderFactory: 可以探索其他任何类的信息
     */
    public boolean match(MetadataReader metadataReader, MetadataReaderFactory metadataReaderFactory) throws IOException {
        // 获取当前类主机
        AnnotationMetadata annotationMetadata = metadataReader.getAnnotationMetadata();

        // 类信息
        ClassMetadata classMetadata = metadataReader.getClassMetadata();

        // 当前类资源(类的路径)
        Resource resource = metadataReader.getResource();

        String className = classMetadata.getClassName();
        System.out.println("=====>>>" + className);
        if (className.contains("er")) {
            return true;
        }
        return false;
    }
}
```

##### @Bean 导入第三方包里面的主键

```java
@Configuration
public class MainConfig2 {

    @Bean("person")
    public Person person02() {
        return new Person("aa", 23);
    }
}
```

这里可以和`@Bean` 主键一起使用的还有 `@Scope, @Lazy，@Conditional`

> `@Scope(value)`指定了实例是但实例的还是多实例的
>
> `value=prototype`: 多实例，`Bean` 在调用的时候才会创建，容器启动的时候并不会去创建
>
> ``value=singleton``: 单实例：默认，容器在启动的就会创建这个Bean，每次都是直接从容器中拿(map.get())

> `@Lazy`:  针对单实例 bean，默认在容器启动的时候创建对象，而使用赖加载这个主键，就算是单实例，那么也实在第一次使用的时候采取创建。

> `@Conditional` 可以设置注册实例的条件，当满足条件的时候才注册，否则不注册
>
> ```java
> @Conditional({WindowCondition.class})
> @Bean("bill")
> public Person person03() {
>   return new Person("Bill Gates", 62);
> }
> 
> public class WindowCondition implements Condition {
>     /*
>         context: 上下文环境
>         metadata：注释信息
>      */
>     public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata{
>         // IOC 使用的BeanFactory
>         context.getBeanFactory();
> 
>         // 获取类加载器
>         context.getClassLoader();
> 
>         // 获取当前环境信息
>         Environment environment = context.getEnvironment();
> 
>         // 获取bean 定义的注册类
>         // 可以判断容器中的 bean 注册情况，也可以给容器中注册bean
>         BeanDefinitionRegistry registry = context.getRegistry();
>         registry.containsBeanDefinition("person");
> 
>         String property = environment.getProperty("os.name");
>         if (property.contains("window")) {
>             return true; // 加载bean
>         }
>         return false;// 不加载bean
>     }
> }
> ```

#### @Import： 快速给容器中导入 组件

> ```
> @Configuration
> @Import({Color.class, Red.class, MyInportSelector.class, MyInportRegstrier.class})
> public class MainConfig2 {}
> 
> public class MyInportSelector implements ImportSelector {
>     // 返回值就是导入到容器中的组件的全类名
>     /*
>         AnnotationMetadata 当前标注 @Import 注解类的所有注解信息
>         当前标注 @Import 的类 MainConfig2 有2个注解，还有一个是 Configuration
>          在这里都可以获取到
>      */
>     public String[] selectImports(AnnotationMetadata importingClassMetadata) {
> 
>         // 方法可以返回一个空数组，但是不能返回null
>         return new String[]{"com.atguigu.secondCodeRecord.bean.Blue", "com.atguigu.secondCodeRecord.bean.Yellow"};
>     }
> }
> 
> public class MyInportRegstrier implements ImportBeanDefinitionRegistrar {
>     // AnnotationMetadata 当前类的注解信息
>     /*
>         BeanDefinitionRegistry 把所有需要添加到容器中的 bean
>             BeanDefinitionRegistry. 手动 注册进来
>      */
>     public void registerBeanDefinitions(AnnotationMetadata importingClassMetadata, BeanDefinitionRegistry registry) {
>         boolean red = registry.containsBeanDefinition("com.atguigu.secondCodeRecord.bean.Blue");
>         boolean blue = registry.containsBeanDefinition("com.atguigu.secondCodeRecord.bean.Red");
> 
>         if (red &&  blue) {
>             RootBeanDefinition rootBeanDefinition = new RootBeanDefinition(Rainbow.class);
>             registry.registerBeanDefinition("rainBow", rootBeanDefinition);
>         }
>     }
> }
> ```

#### 使用Spring 提供的 FactoryBean 工厂 Bean

> ```java
> public class ColorFactoryBean implements FactoryBean<Color> {
> 
>     // 返回 Color 对象，这个对象添加到容器中
>     public Color getObject() throws Exception {
>         System.out.println("create Color");
>         return new Color();
>     }
> 
>     public Class<?> getObjectType() {
>         return Color.class;
>     }
> 
>     // true 单实例，容器中保存一份
>     // false 多实例，每次都会调用 getObject
>     public boolean isSingleton() {
>         return true;
>     }
> }
> ```

