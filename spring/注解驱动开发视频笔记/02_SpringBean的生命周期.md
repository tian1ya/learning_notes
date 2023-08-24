#### bean 的生命周期

* 创建
* 初始化
* 销毁

容器管理 bean 的生命周期，可以自定义初始化和销毁方法，容器在bean进行到当前生命周期的时候来调用我们自定义的初始化和销毁方法

* @Bean注册调用初始化、销毁方法
* Bean 实现接口 `InitializingBean` 初始化方法
* Bean 实现接口 `DisposableBean` 定义销毁方法
* 使用 `JSR250` 规范中的规定的注解 `@PostConstruct` Bean 创建完成并且属性复制完成后执行
  * `@PreDestroy`： Bean 销毁之前执行，做一些清理工作
* Spring 提供的 BeanPostProcessor bean的后置处理器，在bean执行任何初始化前后进行一些处理工作

---

#### @Bean 注解指定初始化和销毁方法

```java
public class Car {

    public Car() {
        System.out.println("car constructor");
    }

    public void init() {
        System.out.println("car ----- init");
    }

    public void destroy() {
        System.out.println("car ----- destroy");
    }
}
```

在注册 Bean 的时候就可以定义这些生命周期的方法

```java
@Configuration
public class MainConfigLifeCycle {

    @Bean(initMethod = "init", destroyMethod = "destroy")
    public Car car() {
        return new Car();
    }
}

@Test
public void test1() {
  // 容器初始化执行初始化方法
  AnnotationConfigApplicationContext applicationContext = new AnnotationConfigApplicationContext(MainConfigLifeCycle.class);
  System.out.println("容器启动完成");
  // 容器关闭调用 destroy 销毁方法
  applicationContext.close();
}

// 在单实例的在容器会管理Bean，容器关闭的时候就会调用 Bean 销毁
// 在多实例的时候，容器容器关闭不会调用销毁方法，需要手动去调用。
```

---

#### Bean 实现接口 `InitializingBean/DisposableBean` 初始化方法

```java
@Component
public class Cat implements InitializingBean, DisposableBean {
    // 销毁全调用，DisposableBean 的方法
    public void destroy() throws Exception {
        System.out.println("Cat---init........");
    }
		
    // 设置完属性后会调用， InitializingBean 的方法
    public void afterPropertiesSet() throws Exception {
        System.out.println("Cat---destroy......");
    }
}

@Configuration
@ComponentScan("com.atguigu.secondCodeRecord")
public class MainConfigLifeCycle {

    @Bean(initMethod = "init", destroyMethod = "destroy")
    public Car car() {
        return new Car();
    }
}
```

---

#### `JSR250` Java 规范中的注解

```java
@Component
public class Dog {

    public Dog() { }

    @PostConstruct
    public void init() {
        System.out.println("Dog ----- init");
    }

    @PreDestroy
    public void destroy() {
        System.out.println("Dog ----- destroy");
    }
}
```

---

#### 使用BeanPostProcessor

bean 的后置处理器，在bean 的初始化前后进行处理

```java
@Component
public class MyBeaPostProcessor implements BeanPostProcessor {

    /*
      Apply this BeanPostProcessor to the given new bean instance <i>before</i> any bean
	    initialization callbacks (like InitializingBean's {@code afterPropertiesSet}
	    or a custom init-method)
	    初始化之前进行后置处理
     */
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("postProcessBeforeInitialization: " + beanName);
        // 这里可以对对象二次包装修改
        return bean;
    }

    /*
      Apply this BeanPostProcessor to the given new bean instance <i>after</i> any bean
	    initialization callbacks (like InitializingBean's {@code afterPropertiesSet}
	    or a custom init-method)
	    初始化之后进行后置处理
     */
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("postProcessAfterInitialization: " + beanName);
        // 这里可以对对象二次包装修改
        return bean;
    }
}
```

例子：执行顺序

```java
/**
 * car constructor
 * postProcessBeforeInitialization ... car 在其他的初始化之前调用
 * car init -- InitializingBean
 * postProcessAfterInitialization ... car
 * Dog construct....
 * postProcessBeforeInitialization ... dog
 * Dog @PostConstruct ----
 * postProcessAfterInitialization ... dog
 * 容器创建完成
 */
```

在源码中的执行时机

```java
protected Object initializeBean(String beanName, Object bean, @Nullable RootBeanDefinition mbd) {
		....
			wrappedBean = applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);

			invokeInitMethods(beanName, wrappedBean, mbd); // 执行自定义指定的 init 和 destroy 方法
		
			wrappedBean = applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
		}

// 其在执行的时候，拿到所有的 PostProcessors 执行其  postProcessBeforeInitialization
// 一旦其中某个 postProcessBeforeInitialization 返回的 null 就直接跳出 for
	public Object applyBeanPostProcessorsBeforeInitialization(Object existingBean, String beanName)
			throws BeansException {

		Object result = existingBean;
		for (BeanPostProcessor processor : getBeanPostProcessors()) {
			Object current = processor.postProcessBeforeInitialization(result, beanName);
			if (current == null) {
				return result;
			}
			result = current;
		}
		return result;
	}

// 其在执行的时候，拿到所有的 PostProcessors 执行其  postProcessAfterInitialization
// 一旦其中某个 postProcessBeforeInitialization 返回的 null 就直接跳出 for
	@Override
	public Object applyBeanPostProcessorsAfterInitialization(Object existingBean, String beanName)
			throws BeansException {

		Object result = existingBean;
		for (BeanPostProcessor processor : getBeanPostProcessors()) {
			Object current = processor.postProcessAfterInitialization(result, beanName);
			if (current == null) {
				return result;
			}
			result = current;
		}
		return result;
	}

```



##### 看看Spring 中BeanPostProcessor 的使用

* ApplicationContextAwareProcessor

  > ```java
  > @Component
  > public class Dog implements ApplicationContextAware {
  > 
  >     private ApplicationContext context;
  >     public Dog() { }
  > 
  >     public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
  >         this.context = applicationContext;
  >     }
  > }
  > ```
  >
  > 当实现接口 `ApplicationContextAware` 之后 Dog 的Bean 就会用有 applicationContext 对象，也就是 ioc 容器，而这个接口的方法  `setApplicationContext` 就是在 `ApplicationContextAwareProcessor` 中调用的。

* BeanValidationPostProcessor

  > Web 中做数据校验的

* DestructionAwareBeanPostProcessor

  > 处理  `JSR250` Java 规范中的注解那@PostConstruct和@PreDestroy方法

* AutowiredAnnotationBeanPostProcessor

  > 完成 @Autowire 功能的注解。