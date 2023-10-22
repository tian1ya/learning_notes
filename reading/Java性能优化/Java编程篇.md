

```java
String str1 = "abc"; 
// 第一种创建字符串方式， 常量池中没有abc，创建一个放池子中，同时也返回
String str2 = new String("abc"); 
// 第二种创建字符串方式，堆中创建 abc
String str3 = str2.intern(); 
// 常量池中有abc则返回，否则在池子中创建一个，并返回
```

从`java9` 开始`String` 后端均是使用`byte[]` 数组存储，之前均是`char[]`

`String` 对象的不可变形，在源码中是被`final private` 修饰的，`final` 修饰则对象是不可被继承的，`private` 修饰则是私有的，其他地方不可改变。

使用第一种创建字符串的时候`JVM` 首先检测该对象是否在字符串常量池中，如果在则直接返回该对象应用，否则新的字符串在常量池中被创建，这种方式可以减少同一个值的字符串对象的重复创建。

使用第二种方式，在编译类文件的时候常量`abc` 在常量池中被创建，其次在调用`new` 时候，`JVM` 命令将会调用`String` 的构造函数，同时引用常量池中的`abc`字符串，在堆内存中创建一个`String` 对象。

所以上面的输出

```java
System.out.println(str1 == str2); 
// false
System.out.println(str1 == str3); 
// true 
System.out.println(str2 == str3); 
// false
```

下面的代码是执行成功的

```java
String str1 = "abc"; 
String str1 = "bcd"; 
```

上面提到`String` 是不可变的，但是这里`String` 变量`str1` 却发生的变化。

这里要理解`Java` 中的关于对象和引用，`str1` 是一个引用，并不是值`abc` 本身，所谓引用就是一个指向内存的地址，在内存中存放着值。所谓的不可变是说`String` 的值不可变，也就是内存中存放的值，而不是应用。

引用是一个指针，是可以指向任何地方的。



#### String 的优化

1. 如何构建超大字符串

```java
String str = "ab" + "cd" + "ef";
```

这里代码的执行是这样的，会先生成`ab`，然后再生成`abc` 然后再生成`abcdef`.

我们要的只是最后的`abcdef` 中间的那几个是冗余的。但是最后编译出来的代码是这样的

```java
String str = "abcdef";
```

编译器给我们优化了的。

一般在字符串拼接的时候建议使用`String Builder`，这也是编译器内部优化的时候使用的。

如果在多线程编程中涉及到线程安全，可以使用`StringBuffer`他是加锁的线程安全的。

```java
String str1 = "abc";
String str2 = new String("abc");

String str22 = new String("abc").intern();
String str23 = new String("abc").intern();
// new String 会在堆内存中建abc 对象，
// 调用intern 方法但是会先去常量池中去拿
// 堆中建的对象会被GC回收

System.out.println(str22 == str23); // true
System.out.println(str1 == str23); // true
System.out.println(str2 == str23); // false
```

所以总结下来`String` 的优化策略主要2点

1. 使用`intern` 方法
2. 字符串拼接使用`stringBuilder/StringBuffer`

---

#### 慎重使用正则表达式

正则表达式在使用贪婪模式、分支选择(如(a|b|c)的表达式)、捕获组的模式下可能会引起回溯匹配。

所以在使用的时候尽量避免使用正则表达式，如果一定要用那么一定要做好性能测试。

---

#### List 的使用

在新增、删除元素的时候`LinkedList` 的效率要高于`ArrayList`, 而在遍历的时候`ArrayList` (基于数组实现)是要高于`LinkedList`(基于双向列表实现)

> `ArrayList` 在新增的时候，当内部数组不够大的时候，会进行新增。在遍历的时候最好使用迭代器

使用`Stream` 处理`List` 的时候能够提供遍历效率

---

#### 并发

`synchronized` 是基于操作系统的`Mutex Lock` 实现的，在`jdk6`之后对它进行了很大的优化，在某些场景下性能甚至超过`Lock`。而`Lock` 接口均是`Java` 实现的。

尽量使用乐观锁。



