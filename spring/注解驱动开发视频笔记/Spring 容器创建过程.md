```java
1. refresh()【创建刷新】
	2. prepareRefresh(); 刷新前的预处理
  	1. this.scanner.clearCache() 清缓存
    2. initPropertySources(); 初始化属性设置，子类自定义个性化的属性设置方法
    3. getEnvironment().validateRequiredProperties(); 属性校验
    4. this.earlyApplicationEvents = new LinkedHashSet<ApplicationEvent>(); 保存容器中早期
       的一些事件
  
2. beanFactory = obtainFreshBeanFactory() 获取BeanFactory
	1. refreshBeanFactory(); 属性bean 工厂
  	 创建一个 this.beanFactory = new DefaultListableBeanFactory()
    （这里是在创建容器的时候，子类调用父类构造器创建的）
  	 设置一个 id this.beanFactory.setSerializationId(getId());
  2. beanFactory = getBeanFactory() 获取上一步创建的 beanFactory，这是它里面全都是一些默认的东
     西
    
3. prepareBeanFactory(beanFactory); bf 的预准备工作，进行一些设置
    设置爱类加载器、postProcessor、忽略的自动装配接口、 注册可以解析的自动装配(直接可以在任何组件中自
    动注入)、ApplicationEventPublisher、ApplicationContext、ResourceLoader等
    还注册了一些组件 environment：ConfigurableEnvironment，systemProperties：
    
4. postProcessBeanFactory bf准备工作完成后进行的后置处理：默认空方法，子类重新这个方法来在bf 创建并
   预准备设置

以上是 bf 的创建以及预准备工作
---------------------------------

5. invokeBeanFactoryPostProcessors(beanFactory); 
   执行bf 的 postProcessor，在bf 表中初始化之后执行，有2个接口
   BeanFactoryPostProcessor、BeanDefinitionRegistryPostProcessor
   1. invokeBeanFactoryPostProcessors 处理 BeanFactoryPostProcessor 的bean
     	1. 获取所有的 BeanDefinitionRegistryPostProcessor pp
      2. 遍历每一个是否 PriorityOrdered 的pp
      3. 然后优先执行 invokeBeanDefinitionRegistryPostProcessors
      
      4. 然后在获取 Ordered 的 pp
      5. 然后遍历在执行
     
       6. 然后执行实现没有以上优先的 pp
     
6. 然后执行 BeanFactoryPostProcessor
   然后在对优先级进行分类，安装优先次序执行优先的 pp
 
7. registerBeanPostProcessors(beanFactory); 拦截干涉bean 的创建过程
   BeanPostProcessors、
   MergedBeanDefinitionPostProcessor【internalPostProcessors】
   DestructionAwareBeanPostProcessor、
   InstantiationAwareBeanPostProcessor、
   SmartInstantiationAwareBeanPostProcessor
   不同的pp 执行的时机是不一样的。
   1. 获取所有的 BeanPostProcessors，可以根据 PriorityOrdered 设置优先级接口
   2. 将每一个 pp 注册到 bf
   3. 然后注册  Ordered、以及剩下的 pp
   4. 最后注册 internalPostProcessors 的 pp
   5. 新创建一个  ApplicationListenerDetector 的 pp 检查创建好的哪个bean 是监听器

8. initMessageSource(); 国际化。消息绑定、解析
     1. 获取 bf
     2. 判断是否有 messageSource 的bean
     3. 如果有，赋值给this.messageSource 
     4. 如果没有则完成创建 new DelegatingMessageSource()
     5. 注册 bf 

9. initApplicationEventMulticaster(); 初始化事件开发器
     1. 判断 bf 中是否有 applicationEventMulticaster
     2. 没有创建 new SimpleApplicationEventMulticaster(beanFactory);
     3. 然后注册到 bf
       
10. onRefresh(); 这个初始化方法留给子类，默认是空的
      
11. registerListeners(); 给容器中将所有项目的 ApplicationListener 注册进来
      容器中获取到所有的 ApplicationListener 注册进来
      每个监听器添加到拍发器中

12. finishBeanFactoryInitialization(beanFactory) 初始化剩下的单实例
       获取容器中所有bean，一次进行初始化
       如果bean 是非抽象的、非懒加载的、单实例的
       	  是否是factoryBean是否实现实现 FactoryBean 接口
       		getBean.doGetBean.
       		先从缓存中获取单实例bean，getSingleton(beanName)
       		 	Map<String, Object> singletonObjects = 
       				new ConcurrentHashMap<String, Object>(256);
					1.缓存中没有，那么去创建
            当前bean 标记为已近创建过的，防止其他线程创建
            获取 RootBeanDefinitio
            获取该 BeanDefinitio 的依赖
            	如果有依赖的bean，那么还是调用 getBean.doGetBean. 依次将依赖的bean 创建出来
            判断是否单实例
            	getSingleton.createBean
                beanPostProcessor 拦截创建一个代理对象(实现接口
                                             InstantiationAwareBeanPostProcessor)
            		resolveBeforeInstantiation(beanName, mbdToUse);
					  2.没有返回代理对象
            3.doCreateBean.createBeanInstance
              如果有构造方法
            	instantiateUsingFactoryMethod(beanName, mbd, args);
								ConstructorResolver 构造器去创建bean，这里就调用到代码中 Bean 的new 的代码
                
             4.执行merged bean definition 的后置处理器
                  所有后置处理器 判断MergedBeanDefinitionPostProcessor
                  执行 .postProcessMergedBeanDefinition
                  
             5.populateBean 对 bean 属性赋值
            		拿到 InstantiationAwareBeanPostProcessor 后置处理器，执行
                	 postProcessAfterInstantiation
                拿到 InstantiationAwareBeanPostProcessor 后置处理器，执行
                   postProcessPropertyValues
               	applyPropertyValues 为属性利用setter方法赋值(反射方法)
             6.initializeBean 初始化
                  1. 执行 xxxAwre 方法，invokeAwareMethods(beanName, bean); 
 									2. 执行bean后置处理器初始化之前 
                    applyBeanPostProcessorsBeforeInitialization
                  3. 执行初始化方法 invokeInitMethods 实现了接口 InitializingBea
                  		@Bean 接口中指定了 init 和 destroy 的方法
             7. 执行 applyBeanPostProcessorsAfterInitialization
                     .postProcessAfterInitialization
             8. 注册销毁方法 registerDisposableBeanIfNecessary
                    这里只是注册，在容器关闭之后会调用
                实现接口 DisposableBean、
             9. 将bean 实例添加到 ioc 中
             10. 所有bean 都创建完成之后，执行 post-initialization callback
                  判断实现了接口 SmartInitializingSingleton
                  执行 afterSingletonsInstantiated

13. finishRefresh();
		initLifecycleProcessor(); 默认重容器中找是否有 LifeCycleProcessor
    没有则使用默认的
    给容器中发布容器刷新完成事件
```

#### 总结

> 1. Spring 容器在启动的事实，会先保存所有注册进来的Bean 的定义信息
>
> 2. xml 注册bean
>
> 3. 注解注册Bean
>
> 4. Spring 容器在合适的时间创建Bean
>
>    1. 用到这个bean 的时候，利用getBean 方法创建爱你，创建好之后保存到容器中
>    2. 统一创建剩下所有bean 就是 finishBeanFactoryInitialization 完成的事情
>
> 5. **后置处理器**: 增强 Bean 功能
>
>    1. 每个bean 创建完成都会使用各种后置处理器处理，来增强bean 的功能，如
>
>       AutowiredAnnotationBeanPostProcessor：自动注入工作
>
>       AnnotationAwareAspectJAutoProxyCreator：做APO 功能
>
>       还有支持异步的、任务调度的增强功能注解
>
> 6. 事件驱动模型
>
>    1. ApplicationListener

