##### Composition and Inheritance

---

> Scala 的抽象类中，只要存在一个抽象函数，那么需要将这个类使用关键字 abstract
>
> 但是和Java 不同的是，scala 中抽象函数不需要使用关键字 abstract，只需要定义就好

> Scala 的函数当没有参数的时候，调用函数可以直接.函数名，就能调用函数，而不是使用Java 中的 .函数名(), 前者在scala 中称为 paramaterless， 后者称为 empty paramater，
>
> 如果函数会产生 side effect，那么五参数函数还是需要使用empty paramater 的方式，反之就可以使用 paramaterless 方式。还有就是如果函数式一个操作，那么也应该有限使用 paramaterless，但是如果函数式涉及到 access property，那么推荐使用 empty paramater方式
>
> ```scala
> abstract class Element {
>   def contents: Array[String]
>   def height: Int = contents.length
>   def width: Int = if (height == 0) 0 else  contents(0).length
> }
> 
> class ArrayElement(conts: Array[String]) extends Element {
> 	override def contents: Array[String] = conts
> }
> 或者
> class ArrayElement(conts: Array[String]) extends Element {
>   val contents: Array[String] = conts
> }
> ```
>
> 如上，继承抽象类，如果有一个 paramaterless 的抽象方法，那么在子类中这个方法可以被实现为 函数或者变量。
>
> **所以在scala 中同一个类中不允许有名称相同的方法和变量**

上面的内容就拉出来scala 和 Java 中不同的语法，那就是**命名空间**

> > Java 中的命名空间有： fields、methods、type、packages
> >
> > 但是scala ：values(fields、methods、packages、singleton objects)
> >
> > types: class trait
>
> fields 和 method 都是在同一个命名空间中的，所以二者的名称是不能相同的。

---

> 在构建class 的时候，如果将参数的类型设置为 val， 那么直接就在这个类中创建了这个参数的 fields，var 类型的并不会去创建，如果使用var 类型参数，需要在类中定义这个 fields。
>
> ```scala
> class Tiger(param1: Boolean, param2: Int) extends Cat {
>     override val dangerous = param1
>     private var age = param2
>   }
> ```

> 如果不想一个父类的方法被子类覆盖，那么在父类的方法中使用 **final**修饰即可。

---

### scala 的继承关系