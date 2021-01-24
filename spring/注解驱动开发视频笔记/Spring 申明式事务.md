1. 添加依赖

   ```java
   <dependency>
     <groupId>org.springframework</groupId>
     <artifactId>spring-jdbc</artifactId>
     <version>4.3.12.RELEASE</version>
     </dependency>
   
   
   ```

2. docker 中运行sql

   ```dockerfile
   docker run -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:5.7
   docker exec -it 3fc5854358df bash
   mysql -uroot -p123456
   ```

3. 配置数据源、JdbcTemplate(Spring 提供的简化数据库操作的工具)操作数据

代码如下

```java
@Configuration
@ComponentScan({"com.atguigu.secondCodeRecord.tx"})
public class TxConfig {

    @Bean
    public DataSource dataSource() throws PropertyVetoException {
        ComboPooledDataSource dataSource = new ComboPooledDataSource();
        dataSource.setUser("root");
        dataSource.setPassword("123456");
        dataSource.setDriverClass("com.mysql.jdbc.Driver");
        dataSource.setJdbcUrl("jdbc:mysql://localhost:3306/test");
        return dataSource;
    }

    @Bean
    public JdbcTemplate jdbcTemplate() throws PropertyVetoException {
        /*
            @Configuration 给容器中农加组件的方法，多此调用 都只是从容器中找组件
            dataSource() 这里相当于是从容器中找组件，而不是再创建一个 bean
         */
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource());
        return jdbcTemplate;
    }
}


@Repository
public class UserDao {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public void insert() {
        String sql = "insert into `user` values(?,?)";
        String uname = UUID.randomUUID().toString().substring(0, 5);
        Random random = new Random();
        int nextInt = random.nextInt(1000);
        jdbcTemplate.update(sql,nextInt, uname);
    }
}


@Service
public class UserService {

    @Autowired
    public UserDao userDao;

    public void insertUser() {
        userDao.insert();
        System.out.println("插入完成");
    }
}

@Test
public void test() {
  UserService userService = applicationContext.getBean(UserService.class);
  userService.insertUser();

}
```

这个时候还没有加入事务，上述的测试方法能够执行成功。

添加事务

1. 开启事务 `@EnableTransactionManagement`
2. 注册 `PlatformTransactionManager` 管理数据源

```java
@Configuration
@ComponentScan({"com.atguigu.secondCodeRecord.tx"})
@EnableTransactionManagement
public class TxConfig {

    @Bean
    public DataSource dataSource() throws PropertyVetoException {
        ComboPooledDataSource dataSource = new ComboPooledDataSource();
        dataSource.setUser("root");
        dataSource.setPassword("123456");
        dataSource.setDriverClass("com.mysql.jdbc.Driver");
        dataSource.setJdbcUrl("jdbc:mysql://localhost:3306/test");
        return dataSource;
    }

    @Bean
    public JdbcTemplate jdbcTemplate() throws PropertyVetoException {
        /*
            @Configuration 给容器中农加组件的方法，多此调用 都只是从容器中找组件
            dataSource() 这里相当于是从容器中找组件，而不是再创建一个 bean
         */
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource());
        return jdbcTemplate;
    }

    // 注册事务管理器
    @Bean
    public PlatformTransactionManager transactionManager() throws PropertyVetoException {
        return new DataSourceTransactionManager(dataSource());
    }
}

@Service
public class UserService {

    @Autowired
    public UserDao userDao;

    @Transactional
    public void insertUser() {
        userDao.insert();
        System.out.println("插入完成");
        int i = 3/0;
    }
}
```

注解启动事务功能

1. ```
   @EnableTransactionManagement: AdviceMode mode() default AdviceMode.PROXY;
   	@Import(TransactionManagementConfigurationSelector.class) 容器中导入
   	selector 中根据 AdviceMode 导入对应的组件
   			PROXY:AutoProxyRegistrar，ProxyTransactionManagementConfiguration
   			
   ```

