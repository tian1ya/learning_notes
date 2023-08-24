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
>    1. 用到这个bean 的时候，利用getBean 方法创建，创建好之后保存到容器中
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

---

### 本篇主要内容

1.  BeanFactory & ApplicationContext 类体系说明
2.  Spring 源码
3. 启动配置
4. refresh()方法
5. 扫描路径下的bean 

IOC容器是 Spring 中最核心的内容，创建实例、实例的配置、实例从创建到销毁整个生命周期，均是由IOC容器完成。Spring提供的两种IOC容器。

-  BeanFactory
- ApplicationContext

Spring 均提供接口，用于定义其行为规范， BeanFactory具有Bean生命周期管理能力、从配置文件中读取Bean的配置数据、完成实例化等。ApplicationContext不仅仅提供BeanFactory的能力，还提供对于应用的配置能力、资源加载、国际化等。

## BeanFactory & ApplicationContext 类体系

### BeanFactory

> SpringBean容器的根接口，提供了一些列获取bean的重载方法，提供了判断是不是单例、原型、类型是不是匹配这样的接口。

编辑切换为全宽

BeanFactory类体系

从上至下，依次接口功能为：

ListableBeanFactory

> BeanFactory的扩展接口，主要提供了获取BeanName数组、以及BeanName作key的Map，获取指定注解的BeanName数组或者Map，通过bean和注解的类型获取指定注解

HierarchicalBeanFactory

> 将BeanFactory可分等级的，父子级的Bean工厂。主要提供2个方法

```
BeanFactory getParentBeanFactory(); // 返回父BeanFactory
boolean containsLocalBean(String name); // 当前持有的 bean factory 是否包含某个bean
```

AutowireCapableBeanFactory

> 具有自动注入能力的工程，主要是将Spring管理Bean生命的能力暴露给第三方框架使用，管理在第三方框架是使用的第三方框架的bean类。

ConfigurableListableBeanFactory

> BeanFactory中的配置接口，对ConfigutableBeanFactory的扩展，主要是提供了对于分析、修改BeanDefinition的基础设置，对于单例的预加载

DefaultListableBeanFactory

> BeanFactory默认实现

### ApplicationContext

编辑切换为居中

ApplicationContext类体系

ApplicationContext

> 是一个门面类，集成了丰富的功能和功能入口，如继承 BeanFactory接口，另外还具备资源加载、国际化等功能。

## Spring 源码

### 源码入口

启动入口

```java
AnnotationConfigApplicationContext ac = new AnnotationConfigApplicationContext(MainConfigAutowired.class);
```

配置类MainConfigAutowired 

```java
@Configuration
@ComponentScan({"com.demo.bean"})
@Scope(proxyMode = ScopedProxyMode.INTERFACES, value = "singleton")
public class MainConfigAutowired {

	@Primary
	@Bean("bookDao2")
	public BookDao bookDao() {
	    return  new BookDao();;
	}
}
```

在启动后，注册配置类，扫描包 com.demo.bean，执行 new BookDao()

调用 AnnotationConfigApplicationContext构造函数 

```java
 public AnnotationConfigApplicationContext(Class<?>... componentClasses) {
	this();// 依次执行父类的构造函数
	register(componentClasses); // 注册主配置类
	refresh(); // 启动应用上下文
}
```

this()依次执行父类的构造函数，AnnotationConfigApplicationContext的父类有GenericApplicationContext 和AbstractApplicationContext 父子类无参构造器分别完成：资源加载器创建、默认BeanFactory的创建

```java
public AbstractApplicationContext() { 
        // 创建资源模型处理器,对资源路径的解析，并加载解析为Resource
	this.resourcePatternResolver = getResourcePatternResolver();
}

public GenericApplicationContext() {
	this.beanFactory = new DefaultListableBeanFactory();
}
```

新建读取注解方式定义的bean,如MainConfigAutowired配置类。以及扫描包下的bean，如注解@ComponentScan({"com.demo.bean"})  中的包路径。

```java
public AnnotationConfigApplicationContext() {
	this.reader = new AnnotatedBeanDefinitionReader(this); // 编程式读取
	this.scanner = new ClassPathBeanDefinitionScanner(this); // 扫描式
}
```

至此this() 完成Bean工厂，资源加载器，配置类和包bean的新建。 

类AnnotationConfigApplicationContext 第二步完成启动配置类的注册

```java
public AnnotationConfigApplicationContext(Class<?>... componentClasses) {
	this();
	register(componentClasses); // 注册主MainConfigAutowired 配置类
	refresh(); // 启动应用上下文
}

public void register(Class<?>... componentClasses) {
	this.reader.register(componentClasses);
}
```

完成配置类的注册，先查看主线，如何注册配置类，待后详述。到目前为止，bean工厂中的bean定义有：

beanFactory中的beanDefinition

 后续进入启动应用上下文方法，该方法是Spring逻辑中最重要的逻辑 

```
public AnnotationConfigApplicationContext(Class<?>... componentClasses) {
	this();
	register(componentClasses);
	refresh(); // 启动应用上下文
}
```

全部主要功能，整个方法被synchronized 上锁，确保Spring容器不会被多次重复执行 

```java
public void refresh() throws BeansException, IllegalStateException {
	synchronized (this.startupShutdownMonitor) {
		// Prepare this context for refreshing. 做准备工作，方便后续使用
		/**
		* 准备工作
		* 1. 设置容器的启动时间
		* 2. 设置活跃状态为 True
		* 3. 设置关闭状态为 false
		* 4. 获取 Environment 对象，并加载单签系统的属性 到 Environment 对象中
		* 6. 准备监听器和事件的集合对象，默认为空的集合
		*/
		prepareRefresh();

		// 创建 DefaultListableBeanFactory
		ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();

		// beanFactory 做初始化操作，预准备操作，设置属性值，如类加载器
		prepareBeanFactory(beanFactory);

		try {
			// 调用各种 beanFactory 准备工作完成， beanFactory 进行后置处理的操作， 这里是一个空方法，用于子类实现，
			postProcessBeanFactory(beanFactory);
                        /**
			* 【这里需要知道 BeanFactoryPostProcessor 这个知识点，Bean 如果实现了此接口，
			* 那么在容器初始化以后，Spring 会负责调用里面的 postProcessBeanFactory 方法。】
			* 这里是提供给子类的扩展点，到这里的时候，所有的 Bean 都加载、注册完成了，但是都还没有初始化
			* 具体的子类可以在这步的时候添加一些特殊的 BeanFactoryPostProcessor 的实现类或做点什么事
			*/
			// 至此完成了 beanFactory 的创建，预准备工作，以及子类实现的一些后置处理

                        // 调用 BeanFactoryPostProcessor，同时会去扫描 Bean 生成BeanDefinition
			invokeBeanFactoryPostProcessors(beanFactory); 

			//  注册Bean 处理器，仅仅是注册，没有执行
			/**
			*  注册 BeanPostProcessor 的实现类，注意看和 BeanFactoryPostProcessor 的区别, 有哪些，有什么用
			*  此接口两个方法: postProcessBeforeInitialization 和 postProcessAfterInitialization
			*  两个方法分别在 Bean 初始化之前和初始化之后得到执行。注意，到这里 Bean 还没初始化
			*/
			registerBeanPostProcessors(beanFactory);
			beanPostProcess.end();

			initMessageSource(); //springMVC，国际化的功能的时候会使用

			// 初始化当前 ApplicationContext 的事件广播器
			initApplicationEventMulticaster();

			onRefresh(); // 空的，留给子去实现，并调用

			// 在所有注册的bean 中检查有没有Listener bean，如果有将其注册到消息广播中
			registerListeners();

			// 完成BeanFactory 初始化工作（已经实例化），创建剩下的单实例Bean(非赖加载的)
			// 初始化所有的 singleton beans，就是用户自定义Bean 【重要！重要】 Bean实例化
			finishBeanFactoryInitialization(beanFactory);
			// 剩余一些没有被创建的Bean
			// Last step: publish corresponding event.
			// 最后，广播事件，ApplicationContext 初始化完成
			finishRefresh();
		   }
		}
	}
```

### 执行BeanFactoryPostProcessor 

Configuration注解注册，以及ComponentScans包扫描 

方法invokeBeanFactoryPostProcessors(beanFactory);  完成@ComponentScan({"com.demo.bean"})的扫描，注册，这个方法执行完之后，com.demo.bean包下的bean会被扫描。 

主要看看该方法的逻辑。

```java
protected void invokeBeanFactoryPostProcessors(ConfigurableListableBeanFactory beanFactory) {
	PostProcessorRegistrationDelegate.invokeBeanFactoryPostProcessors(beanFactory, getBeanFactoryPostProcessors());
        ......   
}

public static void invokeBeanFactoryPostProcessors(
	              ConfigurableListableBeanFactory beanFactory, 
                      List<BeanFactoryPostProcessor> beanFactoryPostProcessors) {
       ... 
       invokeBeanDefinitionRegistryPostProcessors(currentRegistryProcessors, registry, beanFactory.getApplicationStartup());
       ...
}
```

此时currentRegistryProcessors 是       org.springframework.context.annotation.ConfigurationClassPostProcessor  后续进入执行该postProcessor 方法 

改方法获取`@Configuration` 中的`@ComponentScan`填的包路径，并将该路径下的所有的bean加载为`BeanDefiantion`

```java
private static void invokeBeanDefinitionRegistryPostProcessors(
			Collection<? extends BeanDefinitionRegistryPostProcessor> postProcessors, BeanDefinitionRegistry registry, ApplicationStartup applicationStartup) {
	for (BeanDefinitionRegistryPostProcessor postProcessor : postProcessors) {
		postProcessor.postProcessBeanDefinitionRegistry(registry);
	}
}

public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) {
	....
        processConfigBeanDefinitions(registry);
}
```

processConfigBeanDefinitions方法执行

```java
public void processConfigBeanDefinitions(BeanDefinitionRegistry registry) {
	List<BeanDefinitionHolder> configCandidates = new ArrayList<>();
	String[] candidateNames = registry.getBeanDefinitionNames();

	for (String beanName : candidateNames) {
		BeanDefinition beanDef = registry.getBeanDefinition(beanName);
                ....
		// 检查当前bean是否有@Configuration注解
		else if (ConfigurationClassUtils.checkConfigurationClassCandidate(beanDef, this.metadataReaderFactory)) {
			configCandidates.add(new BeanDefinitionHolder(beanDef, beanName));
                         // 持有自定义 mainConfigAutowired
		}
	} 
        ....
        // Parse each @Configuration class【重点】
	ConfigurationClassParser parser = new ConfigurationClassParser(
			this.metadataReaderFactory, this.problemReporter, this.environment,
			this.resourceLoader, this.componentScanBeanNameGenerator, registry);
        do {
	    parser.parse(candidates); // 解析 Bean
            ...
        }while (!candidates.isEmpty());
    
```

方法parser.parse(candidates) 

```java
public void parse(Set<BeanDefinitionHolder> configCandidates) {
    for (BeanDefinitionHolder holder : configCandidates) {
       BeanDefinition bd = holder.getBeanDefinition();
       if (bd instanceof AnnotatedBeanDefinition) {
	   				parse(((AnnotatedBeanDefinition) bd).getMetadata(), holder.getBeanName());
				}
    }
}
```

parse方法持有的metadata ，并将metadata和beanName封装为 ConfigurationClass 

```java
protected final void parse(AnnotationMetadata metadata, String beanName) throws IOException {
		processConfigurationClass(new ConfigurationClass(metadata, beanName), DEFAULT_EXCLUSION_FILTER);
}
	
	
protected void processConfigurationClass(ConfigurationClass configClass, 
                                                      Predicate<String> filter){
       // Recursively process the configuration class and its superclass hierarchy.
	SourceClass sourceClass = asSourceClass(configClass, filter);
	do {
			sourceClass = doProcessConfigurationClass(configClass, sourceClass, filter);
	}while (sourceClass != null);
}
```

doProcessConfigurationClass 方法依次扫描 Component ComponentScans ComponentScan Import Bean等注解，这里只关注ComponentScans

```java
private SourceClass asSourceClass(ConfigurationClass configurationClass, Predicate<String> filter) throws IOException {
		AnnotationMetadata metadata = configurationClass.getMetadata();
		if (metadata instanceof StandardAnnotationMetadata) {
			return asSourceClass(((StandardAnnotationMetadata) metadata).getIntrospectedClass(), filter);
		}
		return asSourceClass(metadata.getClassName(), filter);
	} 


SourceClass asSourceClass(@Nullable Class<?> classType, Predicate<String> filter) throws IOException {
   ....
   // 校验注解
   return new SourceClass(classType);
}


protected final SourceClass doProcessConfigurationClass(
	ConfigurationClass configClass, SourceClass sourceClass, Predicate<String> filter){
     ....
     // 处理ComponentScan注解，扫描类，注册BeanDefinition
     Set<AnnotationAttributes> componentScans = AnnotationConfigUtils.attributesForRepeatable(
				sourceClass.getMetadata(), ComponentScans.class, ComponentScan.class);
                                                                                                                        
     for (AnnotationAttributes componentScan : componentScans) {
	     // 开始扫描 ComponentScans 中的包路径
	     Set<BeanDefinitionHolder> scannedBeanDefinitions =
		             this.componentScanParser.parse(componentScan, sourceClass.getMetadata().getClassName());
}
```

继续深入查看this.componentScanParser.parse 扫描类

```java
public Set<BeanDefinitionHolder> parse(AnnotationAttributes componentScan, String declaringClass) {{
    ...
   return scanner.doScan(StringUtils.toStringArray(basePackages));
}
```

经过执行findCandidateComponents(basePackage)方法之后，将basePackage包下的所有方法扫描，以及创建beanDefinition,最后注册到BeanFactory

```java
public Set<BeanDefinition> findCandidateComponents(String basePackage) {
     ...
     return scanCandidateComponents(basePackage);
}

// 从注解信息中建立BeanDefinition
private Set<BeanDefinition> scanCandidateComponents(String basePackage) {
    ...
    // packageSearchPath = classpath*:com/demo/bean/**/*.class
    String packageSearchPath = ResourcePatternResolver.CLASSPATH_ALL_URL_PREFIX +
					resolveBasePackage(basePackage) + '/' + this.resourcePattern;

    // 将packageSearchPath路径下的 .class 文件全部扫描进来，并抽象为对象Resource
    Resource[] resources = getResourcePatternResolver().getResources(packageSearchPath);
    for (Resource resource : resources) {
	  try { // 读取元数据，【如何获取元数据呢 ？】
	        MetadataReader metadataReader = getMetadataReaderFactory().getMetadataReader(resource);
		      if (isCandidateComponent(metadataReader)) { 
		      	    // 检测 component 是否复合条件，主要是针对 filter 进行相关校验
		 				    // 从注解元数据中转化为 BeanDefination
                ScannedGenericBeanDefinition sbd = new ScannedGenericBeanDefinition(metadataReader);
		 						sbd.setSource(resource);
		 						if (isCandidateComponent(sbd)) { // 进行兼容性校验
		 							candidates.add(sbd);
		 						}
		.....					
	return candidates;
}
```

以上步骤完成扫描代码中的注解信息，并扫描得到BeanDefinition ，继续看doScan 后续的动作

```java
 protected Set<BeanDefinitionHolder> doScan(String... basePackages) {
	Set<BeanDefinitionHolder> beanDefinitions = new LinkedHashSet<>();
	for (String basePackage : basePackages) {
	  // 具体扫描包路径，并获取BeanDefinition，ScannedGenericBeanDefinition 类型
		Set<BeanDefinition> candidates = findCandidateComponents(basePackage);
		
		for (BeanDefinition candidate : candidates) {
			// 获取bean的原型，是singleton单例，还是prototype
      ScopeMetadata scopeMetadata = this.scopeMetadataResolver.resolveScopeMetadata(candidate);
			candidate.setScope(scopeMetadata.getScopeName());
			String beanName = this.beanNameGenerator.generateBeanName(candidate, this.registry);
			if (candidate instanceof AbstractBeanDefinition) { 
			   // 基础属性设置
				 postProcessBeanDefinition((AbstractBeanDefinition) candidate, beanName); 
			}
			if (candidate instanceof AnnotatedBeanDefinition) { 
          // 基础属性设置,如是否赖加载。是否优先注入Primary，是否有依赖depondOn、Lazy、Description
				  AnnotationConfigUtils.processCommonDefinitionAnnotations((AnnotatedBeanDefinition) candidate);
			}
			if (checkCandidate(beanName, candidate)) { // 查看当前是否已经注册进入了，如果已经注册进入了，拿出来检测是否兼容性
			  // 包装 ScannedGenericBeanDefinition 只包括 metadata，没有 beanName，这里将二者在进行包装
				BeanDefinitionHolder definitionHolder = new BeanDefinitionHolder(candidate, beanName); 
				
				// 应用代理模式
				definitionHolder =
				     AnnotationConfigUtils.applyScopedProxyMode(scopeMetadata, definitionHolder, this.registry); 
				     
				beanDefinitions.add(definitionHolder);
				registerBeanDefinition(definitionHolder, this.registry); // 注册到容器中 beanFactory中
			}
		}
	}
	return beanDefinitions;
}
```

最主要的是registerBeanDefinition(definitionHolder, this.registry); // 注册到容器中方法，改方法将扫描得到的BeanDefinition 注册到BeanFactory中，使得BeanFactory 持有该BeanDefinition

```java
protected void registerBeanDefinition(BeanDefinitionHolder definitionHolder, BeanDefinitionRegistry registry) {
	 BeanDefinitionReaderUtils.registerBeanDefinition(definitionHolder, registry);
}

public void registerBeanDefinition(String beanName, BeanDefinition beanDefinition){
   ....
   BeanDefinition existingDefinition = this.beanDefinitionMap.get(beanName);
   if (existingDefinition != null) {
      // 检查单签BeanDefinition 是否已经在被扫描注册
   }
   ...
   synchronized (this.beanDefinitionMap) {
        // 注册BeanDefinition
	this.beanDefinitionMap.put(beanName, beanDefinition);
	List<String> updatedDefinitions = new ArrayList<>(this.beanDefinitionNames.size() + 1);
	updatedDefinitions.addAll(this.beanDefinitionNames);
	updatedDefinitions.add(beanName);
        // 更新 beanDefinitionNames
	this.beanDefinitionNames = updatedDefinitions;
	removeManualSingletonName(beanName);
  }
}
```

以上的步骤完成了Bean的扫描动作，也就是这些bean 均会存在在beanFactory中，但是还未将beanDefinition实例化为bean

###  注册BeanPostProcessor 

```java
invokeBeanFactoryPostProcessors(beanFactory); 

// 注册 BeanPostProcessor 的实现类,两个方法分别在 Bean 初始化之前和初始化之后得到执行。注意，到这里 Bean 还没初始化
// 在注册的时候，先分别将 BeanPostProcessor 按照优先级，普通BeanPostProcessor 分别注册
registerBeanPostProcessors(beanFactory); 
```

以上2个方法均是refresh 中的，其中方法 `invokeBeanFactoryPostProcessors` 以及分析过了，本次继续分析 `BeanPostProcessors` 。在开始之前，先看看`BeanFactoryPostProcessor` 和`BeanPostProcessor`

```java
@FunctionalInterface
public interface BeanFactoryPostProcessor {

	/**
     * 是个函数式接口
     * bean factory 创建后可以通过此接口修改。并且用于注册BeanDefinition
     * 均是在bean创建之前完成调用,例如类 ConfigurationClassPostProcessor  
	 */
	void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException;
}

public interface BeanPostProcessor {
  // 属性已经赋值，生命周期方法执行前调用(init && destroy 方法)
	@Nullable
	default Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
		return bean;
	}
        
  // 属性已经赋值，生命周期方法执行后调用(init && destroy 方法)
	@Nullable
	default Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
		return bean;
	}
}
```

所以`BeanFactoryPostProcessor`  是在工厂`Bean`创建后调用的，**用户修改工厂的方法**，例如注册`BeanDefinition`。

`BeanPostProcessor`  是在`Bean` 的初始化前后执行的方法，**用户修改Bean的方法**。

###   执行 finishBeanFactoryInitialization

知道到`refresh` 方法的`finishBeanFactoryInitialization` 的时候，`beanFactory `

是在该方法中完成`beanDefinition` 到`bean` 的创建。

```java
// 完成BeanFactory 初始化工作（已经实例化），创建剩下的单实例Bean(非赖加载的)
// 初始化所有的 singleton beans，就是用户自定义Bean 【重要！重要】 Bean实例化
protected void finishBeanFactoryInitialization(ConfigurableListableBeanFactory beanFactory) {
	  ....
    beanFactory.preInstantiateSingletons();
}
```

方法调用

```java
public void preInstantiateSingletons() throws BeansException {

	List<String> beanNames = new ArrayList<>(this.beanDefinitionNames);
	// Trigger initialization of all non-lazy singleton beans...
	for (String beanName : beanNames) {
	  // 获取BeanDefinition
		RootBeanDefinition bd = getMergedLocalBeanDefinition(beanName); 
		// 非抽象 && 单例的 && 非赖加载
		if (!bd.isAbstract() && bd.isSingleton() && !bd.isLazyInit()) { 
			if (isFactoryBean(beanName)) {// 是否工厂Bean
			   ......
			else { // 不是工厂Bean，开始实例化单例的Bean
			  getBean(beanName);
			}
		}
	}
 
    // SmartInitializingSingleton 类型的 Bean 又会调用其 afterSingletonsInstantiated
	  // 也就是多了一个生命周期方法
    for (String beanName : beanNames) {
		Object singletonInstance = getSingleton(beanName);
		if (singletonInstance instanceof SmartInitializingSingleton) {
	       ...
         smartSingleton.afterSingletonsInstantiated();
         ...
		}
	}
}
```

其中 `getBean(beanName)`; 是重中之中

```java
public Object getBean(String name) throws BeansException {
	return doGetBean(name, null, null, false);
} 

protected <T> T doGetBean(
			String name, @Nullable Class<T> requiredType, @Nullable Object[] args, boolean typeCheckOnly) throws BeansException {

	   String beanName = transformedBeanName(name);
	   Object beanInstance;

	  // 先从一级缓存中获取当前bean 是否已经被创建，如果能获取到说明bean 已经被创建过
	  Object sharedInstance = getSingleton(beanName);
    ...		
    if (mbd.isSingleton()) {
		  sharedInstance = getSingleton(beanName, () -> {
			    return createBean(beanName, mbd, args); // 缓存中没有Bean，开始执行这里的创建
		  });
		beanInstance = getObjectForBeanInstance(sharedInstance, name, beanName, mbd);
	}
   ....
}

protected Object createBean(String beanName, RootBeanDefinition mbd, @Nullable Object[] args)
			throws BeanCreationException {

		RootBeanDefinition mbdToUse = mbd;

		Class<?> resolvedClass = resolveBeanClass(mbd, beanName);
                    
		if (resolvedClass != null && !mbd.hasBeanClass() && mbd.getBeanClassName() != null) {
			mbdToUse = new RootBeanDefinition(mbd);
			mbdToUse.setBeanClass(resolvedClass);
		}

		try {
			// 在实例化前后执行实例化后置处理器，也就是这里的实例化后置处理器可以在前置方法中直接new Bean，否则 调用doCreateBean 去创建bean
			// 并在再new bean后还可以执行其后置方法修改bean
			// 所以对于自定义的bean，一般返回的均是 null
			Object bean = resolveBeforeInstantiation(beanName, mbdToUse);
			if (bean != null) {
				return bean;
			}

		try { // 真正的创建Bean 实例，在前面的过程中，一级缓存中没有bean，使用代理也没有建立bean，然后走到这里开始真正创建bean
			Object beanInstance = doCreateBean(beanName, mbdToUse, args);
			return beanInstance;
		}
	}
}

//【完成实例化-初始化】
protected Object doCreateBean(String beanName, RootBeanDefinition mbd, @Nullable Object[] args)
			throws BeanCreationException {

		// 【实例化】反射创建实例，此时的bean 对象是一个半成品，没有进行初始化，后续应该进入到初始化，给属性值赋值
		instanceWrapper = createBeanInstance(beanName, mbd, args);

		// 判断是否允许提前暴露半成品对象，解决循环依赖问题
		boolean earlySingletonExposure = (mbd.isSingleton() && this.allowCircularReferences &&
													isSingletonCurrentlyInCreation(beanName));
                    
		if (earlySingletonExposure) {
			  // 允许循环依赖，【提前暴露bean对象】，给三级缓存中添加环境
			  addSingletonFactory(beanName, () -> getEarlyBeanReference(beanName, mbd, bean));
		}

		// 开始初始化
		Object exposedObject = bean;
		try { 
		 // 三级缓存中存放之后，这里完成属性赋值。 然后初始化Bean，BeanPostProcessor 就在这里前后执行的
			populateBean(beanName, mbd, instanceWrapper);
			
			// 初始化-执行init方法，这里比较重要，会去执行PostProcess 以及 xxxAware 的方法
			exposedObject = initializeBean(beanName, exposedObject, mbd); 
		}
	

		if (earlySingletonExposure) {
			// 从单例池中获取对象，
			Object earlySingletonReference = getSingleton(beanName, false);
			if (earlySingletonReference != null) { // 一定发生了循环依赖
				if (exposedObject == bean) {
					// 循环依赖场景， exposedObject 初始化后的实例，bean创建的实例，正常情况下二者是一样的
					exposedObject = earlySingletonReference;
				}
				// 如果不允许忽略包装过的对象，并且有对象正在依赖当前对象， ===> 报错
				else if (!this.allowRawInjectionDespiteWrapping && hasDependentBean(beanName)) {
					String[] dependentBeans = getDependentBeans(beanName);
					Set<String> actualDependentBeans = new LinkedHashSet<>(dependentBeans.length);
					for (String dependentBean : dependentBeans) {
						if (!removeSingletonIfCreatedForTypeCheckOnly(dependentBean)) {
							actualDependentBeans.add(dependentBean);
						}
					}
				}
			}
		}

		registerDisposableBeanIfNecessary(beanName, bean, mbd);
		return exposedObject;
}



protected BeanWrapper createBeanInstance(String beanName, RootBeanDefinition mbd, @Nullable Object[] args) {
		
		// .......
    // 反射创建实例，此时的bean 对象是一个半成品，没有进行初始化，后续应该进入到初始化，给属性值赋值
		return instantiateBean(beanName, mbd);
}

protected void addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory) {
	synchronized (this.singletonObjects) {
		if (!this.singletonObjects.containsKey(beanName)) { // 一级缓存中没有包含beanName，bean还是个半成品，一级缓存中还没有该bean
			this.singletonFactories.put(beanName, singletonFactory); // 三级缓存中塞入 beanName 对应的一个 ObjectFactory
			this.earlySingletonObjects.remove(beanName); // 二级缓存中删除该bean
			this.registeredSingletons.add(beanName); // 那些对象已经注册过了
		}
	}
}

// ObjectFactory<?> singletonFactory 获取半成品bean 的一个引用
protected Object getEarlyBeanReference(String beanName, RootBeanDefinition mbd, Object bean) {
	Object exposedObject = bean;
	if (!mbd.isSynthetic() && hasInstantiationAwareBeanPostProcessors()) {
		for (SmartInstantiationAwareBeanPostProcessor bp : getBeanPostProcessorCache().smartInstantiationAware) {
			exposedObject = bp.getEarlyBeanReference(exposedObject, beanName);
		}
	}
	return exposedObject;
}

// 初始化方法 initializeBean(beanName, exposedObject, mbd);
protected Object initializeBean(String beanName, Object bean, @Nullable RootBeanDefinition mbd) {
		
		else { // 先执行自定义方法，
			invokeAwareMethods(beanName, bean);
		}

		Object wrappedBean = bean;
		if (mbd == null || !mbd.isSynthetic()) { // 后置处理器在初始化Bean 之前执行
			wrappedBean = applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);
		}

		try {
			invokeInitMethods(beanName, wrappedBean, mbd); // 执行自定义指定的 init 和 destroy 的生命周期方法
		}
		
		if (mbd == null || !mbd.isSynthetic()) { // // 后置处理器在初始化Bean 之后执行
			wrappedBean = applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
		}
		return wrappedBean;
}

// bean 完成初始化之后
protected void addSingleton(String beanName, Object singletonObject) {
		synchronized (this.singletonObjects) {
			this.singletonObjects.put(beanName, singletonObject); // 将实例化，初始化之后的完整的bean 放到一级缓存
			this.singletonFactories.remove(beanName); // 清除三级缓存
			this.earlySingletonObjects.remove(beanName); // 清除二级缓存
			this.registeredSingletons.add(beanName); // 存放注册的额beanName
		}
}

public Object getSingleton(String beanName, ObjectFactory<?> singletonFactory) {
		Assert.notNull(beanName, "Bean name must not be null");
		synchronized (this.singletonObjects) { // 单实例池/一级缓存上锁，防止此时还有人给里面 put
			// 调用上面代码中的 createBean(beanName, mbd, args)
			singletonObject = singletonFactory.getObject();
			newSingleton = true;
				
		  if (newSingleton) { // 添加到单例池
			    addSingleton(beanName, singletonObject);
			}
		}
		return singletonObject;
	}
}
```

这个方法中完成各种情况下的创建`Bean` 的方法，如原型、单例，现在先只关注单例的创建，最主要的逻辑是`createBean` 方法。

在这里引出了另外一个问题循环依赖，

`Spring` 通过三级缓存机制，解决改问题。

```java
/** 一级缓存： 缓存完整的单例对象 */
private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);

/** 三级缓存：singletonFactories 给3级缓存中塞入半成品，k-v,
 * 三级缓存中的 v 是一个函数式接口，仅有 getObject 方法，该方法可以传入函数，通过调用该方法，执行具体的获取非完整bean逻辑
 **/
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);

/** 
* 二级缓存：v 是一个不完整的单例对象，完成了实例化，没有初始化的值，从三级缓存中获取的函数式接口获取的半成平，并方到这里 
**/
private final Map<String, Object> earlySingletonObjects = new ConcurrentHashMap<>(16);
```

三步骤

1. 单例池中获取对象`getSingleton(beanName)`
2. `getSingleton(beanName, ObjectFactory)`
3. `createBean(beanName, mbd,args) `

```java
Object sharedInstance = getSingleton(beanName);
	
public Object getSingleton(String beanName) {
	return getSingleton(beanName, true);
}

protected Object getSingleton(String beanName, boolean allowEarlyReference) {
	// 一级缓存中先获取bean
	Object singletonObject = this.singletonObjects.get(beanName);
	if (singletonObject == null && isSingletonCurrentlyInCreation(beanName)) {
		// 一级环境中没有获取到，且当前对象正在被创建中，然后去二级缓存中获取
		singletonObject = this.earlySingletonObjects.get(beanName);
		
		if (singletonObject == null && allowEarlyReference) { // allowEarlyReference=true 允许提前暴露对象
			// 一级、二级缓存中都没有获取到对象
			synchronized (this.singletonObjects) {
				singletonObject = this.singletonObjects.get(beanName);
				if (singletonObject == null) {
					singletonObject = this.earlySingletonObjects.get(beanName);
					if (singletonObject == null) {
					// 从提前暴露的三级缓存中获取对象，暴露的对象是 ObjectFactory 它是一个函数式接口，getObject
						ObjectFactory<?> singletonFactory = this.singletonFactories.get(beanName);
						if (singletonFactory != null) {
							singletonObject = singletonFactory.getObject(); // ObjectFactory new 半成品bean
							this.earlySingletonObjects.put(beanName, singletonObject); // 二级缓存，存放半成品
							this.singletonFactories.remove(beanName); // 一级缓存中删除
						}
					}
				}
			}
		}
	}
	return singletonObject;
}
```

第一次调用到`getSingleton` 返回的总是`null` ，并且三级缓存中均不会去缓存，在执行到`singletonObject = singletonFactory.getObject();` 的时候，回去调用`createBean(beanName, mbd, args)`创建出一个半成品的`bean` , 调用

```java
protected void addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory) {
	synchronized (this.singletonObjects) {
		if (!this.singletonObjects.containsKey(beanName)) { // 一级缓存中没有包含beanName
			this.singletonFactories.put(beanName, singletonFactory); // 三级缓存中塞入 beanName 对应的一个 ObjectFactory
			this.earlySingletonObjects.remove(beanName); //
			this.registeredSingletons.add(beanName); // 那些对象已经注册过了
		}
	}
}
```

这里会将半成品方法放入到三级缓存，此时仅仅三级缓存中有半成品对象。

当完成属性赋值，`bean`初始化完完成之后。

```java
addSingletonFactory(beanName, () -> getEarlyBeanReference(beanName, mbd, bean));

protected void addSingleton(String beanName, Object singletonObject) {
	synchronized (this.singletonObjects) {
		this.singletonObjects.put(beanName, singletonObject); // 将实例化，初始化之后的bean 放到一级缓存
		this.singletonFactories.remove(beanName); // 清除三级缓存
		this.earlySingletonObjects.remove(beanName); // 清除二级缓存
		this.registeredSingletons.add(beanName); // 存放注册的额beanName
	}
}
```

---

