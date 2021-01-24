#### BeanFactoryPostProcessor

和它相关的还有一个 `BeanPostProcessor` 它的作用是bean 创建对象前后进行拦截工作的。

`BeanFactoryPostProcessor` 是 `BeanFactory`的后置处理器，是在beanFactory 表中初始化之后，所谓标准初始化就是，所有的bean 配置都已经被保存加载到BeanFactory，但是还没有bean 没有被初始化

```java
@Configuration
@ComponentScan("com.atguigu.secondCodeRecord.ext")
public class ExtConfig {

    @Bean
    public Blue blue() {
        return new Blue();
    }
}

public class Blue {

    public Blue() {
        System.out.println("Blue constructor...");
    }

    public void init() {
        System.out.println("Blue ----- init");
    }

    public void destroy() {
        System.out.println("Blue ----- destroy");
    }

    @Override
    public String toString() {
        return "Blue{---- Blue -----}";
    }
}

@Component
public class MyBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        System.out.println("MyBeanFactoryPostProcessor");

        int definitionCount = beanFactory.getBeanDefinitionCount();
        System.out.println("definitionCount: " + definitionCount);
        String[] names = beanFactory.getBeanDefinitionNames();
        System.out.println(Arrays.asList(names));
    }
}

ublic class ExtTest {

    AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext(ExtConfig.class);
    @Test
    public void test() {

        applicationContext.close();
    }
}
```

测试跑起来之后的输出

```javascript
MyBeanFactoryPostProcessor 
definitionCount: 9
[org.springframework.context.annotation.internalConfigurationAnnotationProcessor, org.springframework.context.annotation.internalAutowiredAnnotationProcessor, org.springframework.context.annotation.internalRequiredAnnotationProcessor, org.springframework.context.annotation.internalCommonAnnotationProcessor, org.springframework.context.event.internalEventListenerProcessor, org.springframework.context.event.internalEventListenerFactory, extConfig, myBeanFactoryPostProcessor, blue]
Blue constructor...
```

MyBeanFactoryPostProcessor 打印的时机实在实例化bean 之前，所以它实在bean加载了，但是实例化之前。

代码执行流程：

```java
1. refresh()
	1. invokeBeanFactoryPostProcessors(beanFactory)
  2. PostProcessorRegistrationDelegate.invokeBeanFactoryPostProcessors
  	 1. 将bean 分为你 ordered、noordered 的几类，然后分别执行回调
     2. for (BeanFactoryPostProcessor postProcessor : postProcessors) {
						postProcessor.postProcessBeanFactory(beanFactory);
				}
		 3. 
```

---

##### BeanDefinitionRegistryPostProcessor

```java
interface BeanDefinitionRegistryPostProcessor extends BeanFactoryPostProcessor
```

`BeanDefinitionRegistryPostProcessor` 中新定义了一个方法 `postProcessBeanDefinitionRegistry`

在容器中bean 将要被被加载之前，但是还没有初始化之前，允许修改应用上下文内部bean 定义注册中心。

```java
@Component
public class MyBeanDefinitionRegistryPostProcessor implements BeanDefinitionRegistryPostProcessor {

    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException {
        System.out.println("MyBeanDefinitionRegistryPostProcessor");
        System.out.println("bean 定义信息的保存中心，beanFactory 就是根据 这个bean 定义保存中心中的信息创建bean 实例");

        // 创建一个 bean 定义信息
        RootBeanDefinition beanDefinition = new RootBeanDefinition(Blue.class);
        // 将信息放到bean 信息中心
        registry.registerBeanDefinition("hello", beanDefinition);

        // 也可以这种方式创建
        AbstractBeanDefinition beanDefinition1 = BeanDefinitionBuilder
                .rootBeanDefinition(Blue.class)
                .getBeanDefinition();

        registry.registerBeanDefinition("hello1", beanDefinition1);

    }

    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        System.out.println("MyBeanFactoryPostProcessor");

        int definitionCount = beanFactory.getBeanDefinitionCount();
        System.out.println("definitionCount: " + definitionCount);
    }
}
```

还是执行上面例子提到的测试，打印信息

```javascript
MyBeanDefinitionRegistryPostProcessor
bean 定义信息的保存中心，beanFactory 就是根据 这个bean 定义保存中心中的信息创建bean 实例
MyBeanFactoryPostProcessor
definitionCount: 12
MyBeanFactoryPostProcessor
definitionCount: 12
[org.springframework.context.annotation.internalConfigurationAnnotationProcessor, org.springframework.context.annotation.internalAutowiredAnnotationProcessor, org.springframework.context.annotation.internalRequiredAnnotationProcessor, org.springframework.context.annotation.internalCommonAnnotationProcessor, org.springframework.context.event.internalEventListenerProcessor, org.springframework.context.event.internalEventListenerFactory, extConfig, myBeanDefinitionRegistryPostProcessor, myBeanFactoryPostProcessor, blue, hello, hello1]
Blue constructor...
Blue constructor...
Blue constructor...
```

MyBeanDefinitionRegistryPostProcessor 先执行、然后是 MyBeanFactoryPostProcessor，可以利用

BeanDefinitionRegistryPostProcessor 给容器中添加组件。

其调用链

```java
1. refresh()
   1.invokeBeanFactoryPostProcessors(beanFactory);
   	 2.invokeBeanFactoryPostProcessors
   		 3.invokeBeanDefinitionRegistryPostProcessors
```

---

#### ApplicationListener： 事件驱动模型开发

应用监听器，Spring 基于事件驱动的功能，通过监听容器中发布的一些事件，事件的发生，通过触发回调完成事件驱动开发。

```java
interface ApplicationListener<E extends ApplicationEvent> extends EventListener
```

监听 `EventListener` 及其下面的子事件

基于事件开发

1. 写一个监听器监听某个事件(ApplicationListener)

2. 监听时间加入到容器

3. 只要容器中有相关时间的发布，就可以监听到这个事件，spring 中的 容器事件有

   1. ContextRefreshedEvent： 容器刷新事件
   2. ContextClosedEvent：容器关闭事件

4. 自定义发布事件

   ```java
   @Component
   public class MyApplicationListener implements ApplicationListener<ApplicationEvent> {
   
       public void onApplicationEvent(ApplicationEvent event) {
           System.out.println("收到事件： " + event);
       }
   }
   
   @Test
   public void test() {
   
     applicationContext.publishEvent(new ApplicationEvent(new String("我发布的事	
                                                                     件")){} );
                                                                     applicationContext.close();
                                                                     }
   ```

#### 发布事件原理

```java
1. 首先受到事件 ContextRefreshedEvent
   1. 创建容器
   2. refresh()
   3. finishRefresh();
   4. publishEvent(new ContextRefreshedEvent(this));
   		1. 获取时间的多播器 getApplicationEventMulticaster()
      2. 派发事件 .multicastEvent(applicationEvent, eventType)
      	 1. 获取所有 listener
         2. 如果当前有 Exector，那么Exector 异步执行，否则当前线程同步执行
         3. invokeListener -> doInvokeListener(listener, event)
         4. listener.onApplicationEvent(event); 回调函数

2. 然后受到事件自定义发布的事件，和上面的流程是一样的
        
3. ContextClosedEvent 容器关闭的事件
        
----
事件的多播器 如何拿到
1. refresh()
2. initApplicationEventMulticaster();
   1. 先从容器中找该组件
   2. 如果没有那么就创建一个
     
----
容器中有哪些监听器
1. 容器创建对象，refresh()
2. registerListeners()
      从容器中拿到所有的监听器，把他们注册到 appliicationMulticaster 中
      将 listerner 注册到 applicationEventMulticaster 中
```

除了上面提到的实现接口式的写一个监听器，还可以使用注解的方式实现。`@EventListener`

```java
@Service
public class UserService {

    @EventListener(classes = {ApplicationEvent.class})
    public void listen(ApplicationEvent event) {
        System.out.println("UserService: " + event);
    }
}
```

原理

```java
使用处理器 EventListenerMethodProcessor 处理有 @EventListener 注解的方法
class EventListenerMethodProcessor implements SmartInitializingSingleton, ApplicationContextAware
  
接口SmartInitializingSingleton 有一个方法 afterSingletonsInstantiated 当所有的但实例对象全部都创建完成之后执行。
1. 创建容器对象
2. refresh();
3. finishBeanFactoryInitialization(beanFactory); 初始化剩下的但实例 bean
4. beanFactory.preInstantiateSingletons();
5. for (String beanName : beanNames) {
			Object singletonInstance = getSingleton(beanName);
			if (singletonInstance instanceof SmartInitializingSingleton) {
         ...
					smartSingleton.afterSingletonsInstantiated();
				}
			}
		}
 		大概的含义就是创建完但实例对象之后，然后去判断每个但实例对象是否是 SmartInitializingSingleton
    如果是，那么就执行其 afterSingletonsInstantiated 方法。
```



