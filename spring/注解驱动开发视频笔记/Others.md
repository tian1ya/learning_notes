#### Spring 三大扩展点

* `BeanPostprocessor`
* `FactoryBean`
* `BeanFactoryPostProcessor`

----

**容器总览**

接口`ApplicationContext` 代表`Spring IOC` 容器，它负责实例化、配置、组合`Bean`，容器从配置的元数据`configuration medadata`读取数据，从而完成实例化、配置、组合。

`Java` 注解、`XML`配置用于描述`configuration metadata`，也就是说，作为开发，使用`Java` 注解或者`XML`配置文件，告诉`Spring`, 让`Spring` 如何实例化、配置业务对象。

---

**`BeanDefinition`  **

> 可以包含如下信息
>
> Class 、Name 、[ Bean Scopes](https://docs.spring.io/spring-framework/docs/5.2.22.RELEASE/spring-framework-reference/core.html#beans-factory-scopes) 、Autowiring mode 、Lazy initialization mode、Initialization method 、Destruction method。

* `A package-qualified class name `

* `Bean behavioral configuration elements `

  > which state how the bean should behave in the container (scope, lifecycle callbacks, and so forth). 

* `dependencies `

---

* `factory`

  > provides basic functionality for managing and manipulating beans 

* `context`

  > extends the `BeanFactory` interface, in addition to extending other interfaces to provide additional functionality in a more application framework-oriented style 

  `ApplicationContext` 接口扩展了`BeanFactory` 接口，扩展功能有

  * `MessageSource` 国际化
  * `ResourceLoader` 加载文件
  * `ApplicationListener` 接口，事件发布
  * 多次`Context`,

---

**BeanDefinition在哪里扫描的**

1. 框架自带的`beanDefinition`
2. 自定义`BeanDefinition`

---

**循环依赖**

1. 什么是循环依赖
2. 解决循环依赖的关键点
3. 如何解决循环依赖问题 ？ 分场景
4. 基于构造方法的依赖注入能不能解决循环依赖 ？
5. IOC 场景下，原型模式下能不能解决循环依赖 ？
6. 循环依赖需要几级缓存才能解决问题 ？
7. 三级缓存都有什么作用 ？