Spring 利用依赖注入(DI)，完成对IOC容器中各个组件的依赖关系赋值。

* @Autowire: 优先考虑类型，多个类型下，按照 id(属性名) 找
* @Qualifier: 直接使用属性名查找
* @Primary： 当一个类型有多个实例，指定优先选择哪个实例
* `JAR250` 规范中的@Resource 和 `JSR330` 中的@Inject
* 自定义组件想使用Spring 容器底层的一些组件，如ApplicationContext、BeanFactory，xxx 等，自定义组件只需要实现 xxxAware 接口
* @Profile

---

##### Autowired

> ```java
> @Autowired
> private BookDao bookDao;
> 
> @Repository
> public class BookDao {
>     public BookDao() {
>     }
> 
>     private String label = "1";
> 
>     public BookDao(String label) {
>         this.label = label;
>     }
> 
>     @Override
>     public String toString() {
>         return "BookDao.toString " + label;
>     }
> }
> 
> @Service
> public class BookService {
> 
>     @Autowired
>     private BookDao bookDao;
> 
>     public void print() {
>         System.out.println(bookDao.toString());
>     }
> }
> 
> // 执行测试方法
> @Test
> public void test1() {
>   printBeans();
> 
>   BookService bean = applicationContext.getBean(BookService.class);
>   bean.print();
> 
>   applicationContext.close();
> }
> }
> // 结果 BookDao.toString 1
> ```
>
> 默认优先按照类型去容器中找对应的组件。这个时候只有一个的 BookDao 所以可以正常执行。
>
> 
>
> 如果找到多个相同类型组件，再将属性名称作为组件的id 去容器中查找
>
> ```java
> @Autowired
> private BookDao bookDao;
> 
> @Repository
> public class BookDao {
>     public BookDao() {
>     }
> 
>     private String label = "1";
> 
>     public BookDao(String label) {
>         this.label = label;
>     }
> 
>     @Override
>     public String toString() {
>         return "BookDao.toString " + label;
>     }
> }
> 
> @Configuration
> @ComponentScan({"com.atguigu.secondCodeRecord.service",
>         "com.atguigu.secondCodeRecord.controller",
>         "com.atguigu.secondCodeRecord.dao"})
> 
> public class MainConfigAutowired {
> 
>     @Bean("bookDao2")
>     public BookDao bookDao() {
>         return new BookDao("2");
>     }
> }
> 
> @Service
> public class BookService {
> 
>     @Autowired
>     private BookDao bookDao;
> 
>     public void print() {
>         System.out.println(bookDao.toString());
>     }
> }
> 
> // 执行测试方法
> @Test
> public void test1() {
>   printBeans();
> 
>   BookService bean = applicationContext.getBean(BookService.class);
>   bean.print();
> 
>   applicationContext.close();
> }
> }
> // 结果 BookDao.toString 1
> ```
>
> 这个时候依然可以能找到BookService，打印的依然是 第一个 BookDao，因为这个时候当有多个类型相同的实例，那么就按照id去找，此时 `BookService` 中的id=bookDao，如果将其改为 bookDao2，那么测试类中就会输出 
>
> ```java
> @Service
> public class BookService {
> 
>     @Autowired
>     private BookDao bookDao2;
> 
>     public void print() {
>         System.out.println(bookDao2.toString());
>     }
> }
> // 执行测试方法
> // BookDao.toString 2
> ```
>
> 如果将bookDao2 改为 bookDao3，那么程序就会报错
>
> ```java
> @Service
> public class BookService {
> 
>     @Autowired
>     private BookDao bookDao3;
> 
>     public void print() {
>         System.out.println(bookDao3.toString());
>     }
> }
> /*
> 	No qualifying bean of type 'com.atguigu.secondCodeRecord.dao.BookDao' available: 		expected single matching bean but found 2: bookDao,bookDao2
> */
> ```

#### @Qualifier

> ```java
> @Service
> public class BookService {
> 
>     @Qualifier("bookDao2")
>     @Autowired
>     private BookDao bookDao3;
> 
>     public void print() {
>         System.out.println(bookDao3.toString());
>     }
> }
> ```

使用 @Autowire 有一个参数 `required` 默认是`true` 也就是默认spring 一定要求这个bean 是有的，否则会报错，如果设置 `false` 那么spring 并不要求这个bean 存在，只是在使用的会排除 空指针异常

#### @Primary

> ```java
> @Configuration
> @ComponentScan({"com.atguigu.secondCodeRecord.service",
>         "com.atguigu.secondCodeRecord.controller",
>         "com.atguigu.secondCodeRecord.dao"})
> 
> public class MainConfigAutowired {
> 
>     @Primary
>     @Bean("bookDao2")
>     public BookDao bookDao() {
>         return new BookDao("2");
>     }
> }
> ```

#### @Resource 和 @Inject

> ```java
> @Service
> public class BookService {
> 
>     @Resource
>     private BookDao bookDao;
> 
>     public void print() {
>         System.out.println(bookDao.toString());
>     }
> }
> // 测试类输出
> // BookDao.toString 1
> ```
>
> @Resource 默认是按照组件名称注入的，默认它不认识 @Primary 注解
>
> ```java
> @Service
> public class BookService {
> 
>     @Resource(name = "bookDao2")
>     private BookDao bookDao;
> 
>     public void print() {
>         System.out.println(bookDao.toString());
>     }
> }
> // 测试类输出
> // BookDao.toString 2
> ```
>
> 使用 @Inject 需要有依赖 `java imject` 和 Autowire 的功能一样。

---

#### @Autowired 使用范围： 不管放在哪里，实例都是从ioc 容器中获取，然后赋值。

> ```
> @Target({ElementType.CONSTRUCTOR, ElementType.METHOD, ElementType.PARAMETER, ElementType.FIELD, ElementType.ANNOTATION_TYPE})
> ```
>
> 方法、属性、接口、构造器上都可以使用
>
> ```java
> @Autowired
> public void setCar(Car car) {
>   this.car = car;
> }
> ```
>
> 标注在方法上，Spring 在创建当前的时候，会调用方法完成赋值
> 方法使用的参数(自定义类型的值)，从IOC 容器中获得.
>
> 默认加载ioc 容器上的组件，容器启动会调用无参构造器创建对象 ，在进行初始化赋值等操作，
>
> 将这个注解加在构造器上，那么构造器中所使用的实例都是去从ioc容器中获取。
>
> 也可以放在参数位置。

---

#### 自定义组件想使用Spring 容器底层的一些组件，如ApplicationContext、BeanFactory，xxx 等，自定义组件只需要实现 xxxAware 接口

在创建对象的时候，会调用接口规定的方法注入相关组件。

```java
@Component
public class Red implements ApplicationContextAware, BeanNameAware, EmbeddedValueResolverAware {

    private ApplicationContext applicationContext;
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        System.out.println(" 获取到 IOC 容器");
        applicationContext = applicationContext;
    }

    public void setBeanName(String name) {
        System.out.println("当前 bean 的名字");
    }

    public void setEmbeddedValueResolver(StringValueResolver resolver) {
        System.out.println("String 解析器 StringValueResolver");
        System.out.println("解析字符串");
        System.out.println(resolver.resolveStringValue("你好 ${os.name} 我是 #{29 * 2}"));
    }
}
```

---

#### @Profile

根据当前环境，动态的激活和切换一系列组件的功能，如dev 连接A 数据库，QA 环境连接B环境

@Profile 也可以使用在类上，只有当指定的类上的时候，才会有类的实例化
没有使用@Profile 标志的类在任何环境都会实例化



```java
@Configuration
@PropertySource("classpath:/db.properties")
public class MainConfigProfile implements EmbeddedValueResolverAware {

    private StringValueResolver resolver;
    @Value("${db.user}")
    private String userName;

    @Value("${db.password}")
    private String password;

    private String driverClass;

    public void setEmbeddedValueResolver(StringValueResolver resolver) {
        this.resolver = resolver;
        this.driverClass = this.resolver.resolveStringValue("${db.driverClass}");
    }

    @Profile("dev")
    @Bean("devDataSource")
    public DataSource dataSourceDev() {
        MysqlDataSource dataSource = new MysqlDataSource();
        dataSource.setUser(userName);
        dataSource.setPassword(password);
        // ....
        return dataSource;
    }


    @Profile("qa")
    @Bean("qaDataSource")
    public DataSource dataSourceQa() {
        MysqlDataSource dataSource = new MysqlDataSource();
        dataSource.setUser(userName);
        dataSource.setPassword(password);
        // ....

        resolver.resolveStringValue("${db.password}");

        return dataSource;
    }

    @Profile("prod")
    @Bean("prodDataSource")
    public DataSource dataSourcepROD() {
        MysqlDataSource dataSource = new MysqlDataSource();
        dataSource.setUser(userName);
        dataSource.setPassword(password);
        // ....
        return dataSource;
    }
  
      @Bean("defaultDataSource")
    public DataSource dataSourcepDefault() {
        MysqlDataSource dataSource = new MysqlDataSource();
        dataSource.setUser(userName);
        dataSource.setPassword(password);
        // ....
        return dataSource;
    }
}

/*

*/
```

@Profile 默认是 `default` 环境，所以上述注册的4个组件，只会出现 名字为 `dataSourcepDefault` 的 MysqlDataSource 实例。

**如何指定运行时环境呢？**

1. 使用命令行参数,启动sppring 的时候添加参数 `-Dspring.profile.active=dev`

2. 使用代码的方式：

   ```java
   AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext();
   
   applicationContext.getEnvironment().setActiveProfiles("dev","qa");
   applicationContext.register(MainConfigProfile.class);
   applicationContext.refresh();
   
   printBeans(applicationContext);
   
   applicationContext.close();
   ```

3. 

