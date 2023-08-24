# IOC

> 控制反转， Inverse of Control， 创建对象得权限，spring IOC容器创建对象，而不是人去创建。
>
> 程序解耦合，扩展性。
>
> 在项目启动得时候IOC 容器将所有得对象创建出来，包得生命周期方法全部有IOC 管理，而程序员只管使用。

查看代码  `mvn-spring`

```java
1.refresh
	1.prepareRefresh 刷新预处理
		1. 设置容器启动标志 true
    2. 设置容器关闭标志 false
  	3. initPropertySources 初始化属性，子类实现，可以自定义子类，继承 AbstractApplicationContext 然后实现该方法
  	   子类（容器）可自定义个性化属性设置
  	4.getEnvironment().validateRequiredProperties()自定义属性校验，也是空，留给子类实现
  	5.this.earlyApplicationEvents = new LinkedHashSet<>(); 保存事件
  	
  2.obtainFreshBeanFactory() 获取 BeanFactory
  	1.refreshBeanFactory 刷新 beanFactory，类型是 DefaultListableBeanFactory， 设置序列化ID值
  	2.getBeanFactory() 返回 beanFactory
  	
  3.prepareBeanFactory(beanFactory)预处理 beanFactory 进行一些设置
  	1.设置类加载器
  	2.设置表达式解析器
  	3.设置后置处理器 ApplicationContextAwareProcessor
  	4.设置忽略的自动装配的很多其他的  xxxAware
  	5.设置可以直接自动装配的类，这些类在spring环境中任意地方均可 @Autowire 注入使用
  	6.注册默认 environment(StandardEnvironment) 、
  		systemProperties( Properties[]size = 54)、
  		systemEnvironment、
  		applicationStartup()
  	7.后置处理 postProcessBeanFactory(beanFactory) 仍然是空的，带子类实现
```

**以上完成 BeanFactory的预准备工作。**

```java
	4. invokeBeanFactoryPostProcessors 执行 BeanFactory后置处理，在BeanFactory表准初始化之后进行
		1.先执行 BeanDefinitionRegistryPostProcessor
			按照顺序依次执行 PriorityOrdered、Ordered、其他的 PostProcessor
		2. 然后执行 BeanFactoryPostProcessor
			按照顺序依次执行 PriorityOrdered、Ordered、其他的 PostProcessor
```

**注册BeanPostProcess**

> 拦截 bean 的创建过程

```java
	5. registerBeanPostProcessors(beanFactory) 仅仅是注册，没有执行
		1.获取已经注册的 BPP 名字
		2.BPP 都有自己的优先级，也就是实现了接口 PriorityOrdered、Ordered 并分别将不同优先级的BPP放到不同的 list 中
			priorityOrderedPostProcessors、orderedPostProcessorNames、nonOrderedPostProcessorNames
			按照这个顺序将 PP 注册 beanFactory.addBeanPostProcessor(postProcessor)
    3.最后注册 ApplicationListenerDetector
```

**initMessageSource**

```java
	6. 国际化、消息绑定
		新建messageSource 可取出国际化取出某个 msg 信息，
		并注册到beanFactory中
```

**onRefresh**

```java
	7. 空的，留给子去实现，并调用
```

**registerListeners**

```java
	8. registerListeners 在所有注册的bean 中检查有没有Listener bean，如果有将其注册到消息广播中
```

**finishBeanFactoryInitialization**

```java
	9. finishBeanFactoryInitialization 完成BeanFatory 初始化工作（已经实例化），创建剩下的单实例Bean(非赖加载的)
     1. beanFactory.preInstantiateSingletons() 初始化剩余但实例 bean,就是我们自定义的业务 bean，从beanDefinition 
        实例化为bean
     		1. 获取所有beanNames
     		2.获取bean 的定义信息 RootBeanDefinition
     		3. 判断类型不是抽象的 && 单例的 && 非赖加载的
     		4. getBean(beanName) 创建对象
     		5. doGetBean(name, null, null, false)
        6.getSingleton(String beanName)
          1. 先从以及一级缓存拿 this.singletonObjects 中会缓存已经创建好的实例，优先去缓存中获取bean
        7. 获取不到返回null，this.alreadyCreated 中标记当前bean已经被创建
        8.获取 RootBeanDefinition
        9.获取当前bean 依赖的其他bean String[] dependsOn = mbd.getDependsOn()
        10.如果有依赖bean 那么先调用 getBean(dep) 等依赖的bean先创建出来
        11 启动单实例bean 的创建流程
        12.getSingleton， 该方法中会传入 ObjectFactory.createBean
        	1. createBean
        		1.resolveBeforeInstantiation(beanName, mbdToUse)
              置处理器返回一个bean 代理对象，如果能返回，就是直接返回，使用用。否则调用doCreateBeab 去创建bean
            2. 判断是否有 InstantiationAwareBeanPostProcessor 它可以在真正创建bean前返回一个代理的bean	
            	这样就不需要去真正的创建 doCreateBean，先执行去before方法，如果能创建出bean，也会执行after方法
          2. doCreateBean， resolveBeforeInstantiation没有返回
          	1. createBeanInstance(beanName, mbd, args)
              1. instantiateUsingFactoryMethod(beanName, mbd, args) 用对象的工厂方法或者构造器创建
            2. applyMergedBeanDefinitionPostProcessors 可以修改创建出来的bean
            3.populateBean(beanName, mbd, instanceWrapper) 为bean属性赋值
            	1. 遍历所有后置处理器，并类型是 InstantiationAwareBeanPostProcessor 的会执行其
            		 postProcessAfterInstantiation 方法
              2. applyPropertyValues(beanName, mbd, bw, pvs); 填充属性
              3. initializeBean(beanName, exposedObject, mbd) bean 初始化
              	1. invokeAwareMethods(beanName, bean) 先执行 xxxAware 方法
              	2. 执行bean上的 postProcessBeforeInitialization
              	3. invokeInitMethods(beanName, wrappedBean, mbd); // 执行自定义指定的 init 和 destroy 方法
              	4.  执行bean上的 postProcessAftrerInitialization
            4. registerDisposableBeanIfNecessary(beanName, bean, mbd) 注册bean 的销毁方法(容器关闭时候会调用)

所有的bean都创建完之后，如果bean是 SmartInitializingSingleton 那么执行他的 afterSingletonsInstantiated 方法

finishRefresh()
	initLifecycleProcessor(); 获取生命周期处理器
	getLifecycleProcessor().onRefresh(); 回调生命周期处理器
```

