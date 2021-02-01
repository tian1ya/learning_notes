Type Class 包含3部分内容

* **Type Class**

  > type class 代表着一个 `trait` 这个 `trait` 最小包含有一个类型参数
  >
  > ```scala
  > package with_cats.chapt01
  > 
  > import with_cats.chapt01.JsonAst.{JsObject, JsString, Json}
  > 
  > object JsonAst {
  > 
  >   sealed trait Json
  > 
  >   final case class JsObject(get: Map[String, Json]) extends Json
  > 
  >   final case class JsString(get: String) extends Json
  > 
  >   final case class JsNumber(get: Double) extends Json
  > 
  >   case object JsNull extends Json
  > 
  > }
  > 
  > case class Person(name: String, email: String)
  > 
  > trait JsonWriter[A] {
  >   def write(value: A): Json
  > }
  > 
  > object JsonWriterInstances {
  >   implicit val personWriter: JsonWriter[Person] = (value: Person) => JsObject(Map(
  >     "name" -> JsString(value.name),
  >     "email" -> JsString(value.email)
  >   ))
  > 
  >   implicit val stringWriter: JsonWriter[String] = (value: String) => JsString(value)
  > }
  > 
  > ```

* **Type Class Instance**

  > `Instance` 就是创建一个实现了 `trait` 方法的实例，并且这个实例是使用`implicit` 绑定了的
  >
  > ```scala
  > package with_cats.chapt01
  > 
  > import with_cats.chapt01.JsonAst.Json
  > import with_cats.chapt01.JsonWriterInstances._
  > 
  > 
  > object Json extends App {
  >   def toJson[A](value: A)(implicit w:JsonWriter[A]):Json = w.write(value)
  > 
  >   private val json: Json = Json.toJson(Person("Dave", "Dave@qq.com"))
  >   // 第二个参数是隐式参数，当在上下文中提供了的时候，会自己搜索并使用，不需要传入
  >   // 隐式参数的比默认参数优先使用的
  >   println(json)
  > }
  > 
  > ```

* **Type Class Interface**

  > Type class interface 是说任何我们想给用户暴露出去的方法，interfaces 是那些通用的方法，这些方法接收 type class 的 instance 做为隐式参数
  >
  > 有2中方法指定一个 interface
  >
  > * interface object： interface 对象
  > * interface Syntax:  interface 句法
  >
  > ```scala
  > package with_cats.chapt01
  > 
  > import with_cats.chapt01.JsonAst.Json
  > import with_cats.chapt01.JsonWriterInstances._
  > 
  > object JsonSyntax extends App {
  > 
  >   implicit class JsonWriterOps[A](value: A) {
  >     def toJson(implicit w: JsonWriter[A]): Json = w.write(value)
  >   }
  > 
  >   private val json: Json = Person("Dave", "Dave@qq.com").toJson
  >   // 等同于 private val json: Json = Person("Dave", "Dave@qq.com").toJson(personWriter)
  >   // 隐式类 implicit class JsonWriterOps[A](value: A) 这里使用了一个泛型
  >   // 意味着它给任何类都添加了一个 toJson 方法 
  >   // 任何类都可以调用 toJson 这个方法
  >   println(json)
  >   // JsObject(Map(name -> JsString(Dave), email -> JsString(Dave@qq.com)))
  > }
  > ```

Scala 标准库中提供了通用的 type class interface `implicitly` 它的定义非常的简单

```scala
 def implicitly[A](implicit value: A): A = value
```

可以使用它来从隐式上下文中调用任何我们需要的值：

```scala
import with_cats.chapt01.JsonWriterInstances._
implicitly(JsonWriterOps[String])// 如果这里报错那么就是说 JsonWriterOps 找不到
```

在 `cats` 中大部分的type class 都是可以被找到调用的，但是`implicitly` 可以插入到代码中，通过编译器是否报错，来判断该隐式转换是否能够被调用，

---

#### 使用Implicits

> 使用 type class 那么也意味着使用 隐式值(函数和类) 和隐式参数

为了更好的使用 `implicits` 我们需要遵循以下几点内容：

##### 组织Implicits 

按照惯例，几乎将所有标记为`implicits`  的定义几乎都放到了`object` 或者 `trait` 中，而不是放到顶层中，在上面的例子中我们将`type class instance` 都放到了`JsonWriterInstances` 的`object` 中，同样我们也可以把它放在JsonWriter的伴生对象中，这种方式在Scala中有特殊的含义，因为这些instances会直接在*implicit scope*里面，无需单独导入。

##### Implicits  的作用域

编译器根据类型搜寻备选的`type class instance`，如

```scala
Person("Dave", "Dave@qq.com").toJson
```

它会去搜寻类型 `JsonWriter[Person]`

编译器搜寻的备选`instance`的`implicit scope`区域包括

* local or inherited definitions `本地有定义`
* imported definitions `import with_cats.chapt01.JsonWriterInstances._`
* definitions in the companion object of the type class or the parameter type

如果在 `scope` 中发现有类型相同的 `implicit definitions` 那么编译器会出错

`implicit scope`精确的规则是非常复杂的，在本书<scala with cats>值需要知道上面几条就可以了，在使用的时候，值需要将 `implicit definitions` 放到以下这些地方就可了

* 放到一个 `object`  中，如我们例子中的 `JsonWriterInstances`，然后使用的时候，将其`import` 就可以了
* 放到 `trait` 中：使用的时候通过 `继承`  就能使用了
* `type class` 的伴生对象中： 本身就在 `scope` 内了
* `参数类型`的伴生对象中：本身就在 `scope` 内了

##### 递归寻找 Implicit Resolution**

之前我们是使用  `implicit val`  申明一个 `type class instances` ，显然这是比较浅显的认识，可以通过以下2种方式定义 `instances`

*  `implicit val`  声明具体类型的 `type class instances`
* 利用  `implicit methods` 从其他实例中创建一个实例

其实第一个情况就是我们之前简单的方式，这里说说第二种方式，

> 总会有这样的情况，如一个库函数值提供了 `sum(a:Int, b:Int)` 的功能，但是呢我现在需求 `sum(a:String, b: String)` 显然库是不能帮我们计算的，但是我们可以通过隐式转换，将a:Int => a:String，这样我们就可以使用库函数提供的能力了，我们需要的就是定义一个隐式转换函数

```scala
object Json {
  def toJson[A](value: A)(implicit w:JsonWriter[A]):Json = w.write(value)
}

trait JsonWriter[A] {
  def write(value: A): Json
}

object JsonWriterInstances {
  implicit val personWriter: JsonWriter[Person] = (value: Person) => 		
  	JsObject(Map(
    	"name" -> JsString(value.name),
    	"email" -> JsString(value.email)
  ))

  implicit val stringWriter: JsonWriter[String] = (value: String) => 
  	JsString(value)
}
  
import with_cats.chapt01.JsonAst.{JsNull, Json}
import with_cats.chapt01.JsonWriterInstances._


implicit def optionWriter[A](implicit writer: JsonWriter[A]): 		
		JsonWriter[Option[A]] = new JsonWriter[Option[A]] {
    	override def write(value: Option[A]): Json = value match {
      	case Some(aValue) => writer.write(aValue)
      	case None => JsNull
    }
}

println(Json.toJson(Option("a String")))
println(Json.toJson(Option(Person(name = "aa", email = "email"))))
```

上面的代码，首先我们有`Json.toJson` 方法，这个方法接收一个`JsonWriter的`隐式变量，

而`JsonWriter`是一个`trait` 我们在另外一个 `object` 中实现了2个`personWriter、stringWriter`。

而最后我们使用的 `optionWriter` 接收一个 `JsonWriter` 作为隐式变量，当我们接收的是 `string` 类型的值，那么就会去调用 `stringWriter`， 如果是一个 `person` 那么就会去调用 `personWriter`

scala 的编译器会自动去搜寻符合类型的 `隐式参数`，并将搜到的结果作为参数传进去，这个编译器完成的传参过程是优先于参数本省的默认参数的。

---

#### 练习，完成一个 Printable

```scala
# Cat.scala
package with_cats.chapt01.example

case class Cat(name: String, age: Int, color: String)

# CatEqInstances.scala
package with_cats.chapt01.example

import cats.Eq
import cats.instances.int._
import cats.syntax.eq._

object CatEqInstances {
  implicit val catEq: Eq[Cat] = Eq.instance[Cat] {
    (catA,catB) =>
      catA.age === catB.age && catA.age === catB.age && catA.age === catB.age
  }
}

# CatShowInstances.scala
package with_cats.chapt01.example

import cats.Show
import cats.instances.int._
import cats.instances.string._
import cats.syntax.show._

object CatShowInstances {

  implicit val catShow: Show[Cat]= Show[Cat] { cat =>
    s"show ${cat.name.show} is a ${cat.age.show} year-old ${cat.color.show} cat." }
}

# Printable.scala
package with_cats.chapt01.example

trait Printable[B] {
  def format(value: B): String
}

object Printable {
  def format[A](a: A)(implicit printable: Printable[A]):String = printable.format(a) 
  // 实现留给 后续需要的时候完成(extends)

  def print[A](a: A)(implicit printable: Printable[A]): Unit = println(format(a))
}

# PrintableInstances.scala
package with_cats.chapt01.example

object PrintableInstances {
  // 实现各种 类型下的 format
  implicit val stringPrintable: Printable[String] = (value: String) => value
  implicit val intPrintable: Printable[Int]       = (a: Int) => a.toString

  implicit val catPrintable: Printable[Cat] = (cat: Cat) => {
    s"printable ${Printable.format(cat.name)} is a ${Printable.format(cat.age)} year-old ${Printable
      .format(cat.color)} cat."
  }
}

# PrintableSyntax.scala
package with_cats.chapt01.example

object PrintableSyntax {

  implicit class PrintableOps[A](a: A) {
    def format(implicit printable: Printable[A]): String = printable.format(a)

    def print(implicit printable: Printable[A]): Unit = println(format)
  }
}

# Runs.scala
package with_cats.chapt01.example

import PrintableInstances._
import PrintableSyntax._
import with_cats.chapt01.example.CatShowInstances._
import with_cats.chapt01.example.CatEqInstances._
import cats.syntax.show._
import cats.syntax.eq._

object Run extends App {


  private val tomCat = Cat("Tom", 12, "red")
  private val tomCat2 = Cat("Tom", 12, "red")
  println(tomCat.format)

  tomCat.print

  Printable.print(tomCat)

  println(Printable.format(tomCat))

  println(tomCat == tomCat2)

  println(tomCat.show)

}
```

输出：

```scala
printable Tom is a 12 year-old red cat.
printable Tom is a 12 year-old red cat.
printable Tom is a 12 year-old red cat.
printable Tom is a 12 year-old red cat.
true
show Tom is a 12 year-old red cat.
```

* type class 定义行为 `trait Printable`

* type object  `object Printable` 定义方法，这些方法调用 `type class` 的行为

  而这些行为会在 type instances 中实现

* type instance 定义各种类型下的 `type class`  所规定的行为，使得这些类型具备这些行为能力，但是呢这些行为又不是对外直接暴露的，对外暴露需要通过 `type object` 中的方法

  这里实现了 `implicit` 函数

* PrintableSyntax 句法，`implicit` 类写 `type object` 中一样的函数/方法，这个隐式类接收一些类型，是的这个类型就具备了 `type object` 中定义的那些方法，而这些方法是去调的 `instance` 中的抽象行为

  > `implicit class` 定义的类，它接收一个类型参数，然后在定义类中写一些函数，那么就是扩展了这个类型，这个类型就拥有了这个类中的方法

---

#### Cats

`Cats` 使用模块化的结构，可以让我们选择使用哪个 `type Class、instances、interface method`

`import cats.instances` 包中实现了大部分类型的 `instances`

```scala
import cats.instances.int._
import cats.instances.string._
import cats.Show

object CatShowInstances extends App {

  val showInt: Show[Int] = Show.apply[Int]
  val showString: Show[String] = Show.apply[String]

  println(showString.show("aa"))
  println(showInt.show(12))
}
```

还有更简单的方式，调用`interface Syntax`

```scala
import cats.syntax.show._

println(123.show)
println("123".show)
```

---

### 总结

* 每一个 `type class`自身是一个通用的 `traits`
* 每一个 `type class` 都有自己的伴生对象，一个 `apply` 方法用于实例化伴生对象，以及还有其他的方法

关于`Cats` 这个库

* `import cats._` 导进所有的 `Cats type class`
* `cats.instances.all._` 导进所有对应标准库中的 `type class instances`
* `import cats.syntax.all._ ` 导入所有 `syntax`
* `import cats.implicits._` 导入所有标准的`type class instances`以及`syntax`



