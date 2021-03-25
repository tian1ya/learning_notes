[这里有数学意义上的Semigroup 和 Monoid](/Users/xuxliu/Desktop/notes/noteToGit/scala/scala/Monad.md)

#### Monoid

> `monoid` 是一个 `Type` 有2个定律
>
> * `op(a,op(b,c)) = op(op(a,b),c)` 也就是满足结合律(`associative`)，函数表达为 `(A,A) =>A`,这类也满足了封闭性，经过op运算，结果值在在同一个范畴之中
> * 最小单元, 任何元素`ele`和它操作都会等于元素`ele` 本身(`identity`)

```scala
trait Monoid[A] {
  def combine(x: A, y: A):A
  def empty: A
}
```

如加、乘、字符串拼接等都是`Monoid` 但是减法就不是了

2条定律表现在代码中就是

```scala
def associativeLaw[A](x: A, y: A, z:A)(implicit m: Monoid[A]): Boolean = {
    m.combine(x, m.combine(y, z)) == m.combine(m.combine(z,y),z)
}

def identityLaw[A](x: A) (implicit m:Monoid[A]): Boolean = {
    m.combine(x, m.empty) == m.combine(m.empty, x)
  }
```

#### Semigroup

> 只满足结合律，没有单位元定律称为 `半群`

```scala
trait Semigroup[A] {
  def combine(x: A, y: A): A
}

// Monoid = Semigroup + empty
trait Monoid[A] extends Semigroup[A] {
  def empty: A
}

object Monoid extends App {

  def apply[A](implicit monoid: Monoid[A]): Monoid[A] = {
    monoid
  }

  implicit def setUnionMonoid[A]: Monoid[Set[A]] = new Monoid[Set[A]] {
    override def empty: Set[A] = Set.empty[A]

    override def combine(x: Set[A], y: Set[A]): Set[A] = x union y
  }

  private val intSetMonoid: Monoid[Set[Int]] = Monoid[Set[Int]] 
  // Monoid[Set[Int]].apply
  private val strSetMonoid: Monoid[Set[String]] = Monoid[Set[String]] 
  // Monoid[Set[String]].apply

  println(intSetMonoid.combine(Set(1, 2), Set(2, 3)))
  println(strSetMonoid.combine(Set("a", "b"), Set("c", "d")))
}
```

---

#### Monoid in Cats

在进入`monoid in cats` 之前应该先了解了解那3个主要的概念

* `type class`: `cats.Monoid`继承自`cats.Semigroup`

* `instances`: 

  `if we want the monoid instance for String`

  ```java
  import cats.Monoid
  import cats.instances.string._ 
  // for Monoid
  
  Monoid[String].combine("Hi ", "there")
  
  // res0: String = Hi there
  Monoid[String].empty
  // res1: String = ""
    
  // 代码等同于
  Monoid.apply[String].combine("Hi ", "there") 
  // res2: String = Hi there
  Monoid.apply[String].empty
  // res3: String = ""
    
  // Monoid 是来源于 Semigroup，如果不需要 empty，可以
  import cats.Semigroup
  Semigroup[String].combine("Hi ", "there")
  // res4: String = Hi there  
  ```

* `interface`

  需要使用`syntax`

  ```java
  import cats.instances.string._ // for Monoid
  import cats.syntax.semigroup._ // for |+|
  val stringResult = "Hi " |+| "there" |+| Monoid[String].empty 
  
  // stringResult: String = Hi there
  
  import cats.instances.int._ 
  // for Monoid
  val intResult = 1 |+| 2 |+| Monoid[Int].empty
  // intResult: Int = 3
    
  private val map: Map[String, Int] = Map("a" -> 1, "b" -> 2)
  private val map2: Map[String, Int] = Map("b" -> 3, "d" -> 4)
  
  private val stringToInt: Map[String, Int] = map |+| map2
  // Map(b -> 5, d -> 4, a -> 1)
  
  private val tuple: (String, Int) = ("hello", 12)
  private val tuple2: (String, Int) = ("word", 22)
  println(tuple |+| tuple2)
  ```

这是一段 `Cats` 的`StringMonoid`代码

```scala
import cats.Monoid
import cats.instances.string._

object CatsExample extends App {
  
  println(Monoid[String].combine("a","b"))
  # 相当于下面的过程
  private val value: Monoid[String] = Monoid.apply[String]
  value.combine("A","b")
}
```

看看这个过程是咋样的

```scala
private val value: Monoid[String] = Monoid.apply[String]
# 这里返回的是一个 StringMonoid， 主要是看看这个 StringMonoid 是如何返回的
```

`Monoid.apply[String] 源码`

```scala
# cats.kernel.Monoid
@inline final def apply[A](implicit ev: Monoid[A]): Monoid[A] = ev
```

这里使用了隐式参数，当给了类型`String` 的时候，返回了一个 `StringMonoid`，也就是 `ev`，它是一个隐式参数，所以会去上下文中去找`String` 类型的 `Monoid`

在 `trait StringInstances`  中有 `implicit val`

`implicit val catsKernelStdMonoidForString: Monoid[String] = new StringMonoid`

然后在同个文件中实现了 `class StringMonoid` 然后就有了 `combine` 这个方法

```scala
  private val maybeInt = Option(12)
  private val maybeInt1 = Option(34)
  
  private val maybeInt2: Option[Int] = Monoid.combine(maybeInt, maybeInt1)
  println(maybeInt2)

# 源码中的函数
def combine[@sp(Int, Long, Float, Double) A](x: A, y: A)(implicit ev: S[A]): A = ev.combine(x, y)

# 也是根据给进来的类型，然后去上下文中找到具体的 Monoid，
```

#### Monoid Syntax

> 给某个类型直接添加某个方法，就是将某个类型作为成员变量，然后实现一个 `implicit class`

`Cat` 给类型中提供的 `combine` 方法使用 `|+|` 符号，`combine` 方法来自于 `semigroup` 所以在使用这个符号的时候，需要`import` 进来 `cats.syntax.semigroup`

```scala
import cats.syntax.semigroup._

private val str: String = "Hi " |+| " there"
private val i: Int = 1 |+| 2
println(str)
println(i)
```

#### 练习

```scala
import cats.Monoid
import cats.instances.int._
import cats.instances.option._
import cats.instances.string._
import cats.syntax.semigroup._

case class Order(totalCost: Double, quantity: Double)

object CatsExample extends App {

  def add(items: List[Int]): Int = items.foldRight(Monoid[Int].empty)(_ |+| _)

  println(add(List(1, 2, 3, 4)))

  // 这里可能会去计算那个类型就需要将那个类型的 instances import 进来到当前的上下文中
  def add2[A](items: List[A])(implicit monoid: Monoid[A]): A =
    items.foldRight(monoid.empty)((e, z) => monoid.combine(e, z))

  // combine 和 |+| 是一样的，一个 instance 一个 syntax
  def add3[A](items: List[A])(implicit monoid: Monoid[A]): A =
    items.foldRight(monoid.empty)((e, z) => e |+| z)


  println(add2(List(Option(1), Option(2), Option(3))))
  println(add3(List(Option(1), Option(2), Option(3))))
  println(add3(List(Some(1), Some(2), None, Some(3))))

  // println(add3(List(Some(1), Some(2), Some(3))))
  // 这里会出错，因为推断出来的类型是 List[Some(a:Int)]， 而Monoid 只接收 Option
  println(add3(List(1, 2, 3)))

  // 现在要将 case class Order 进行相加
  // 还是使用上面的 add3 方法，
  implicit val orderCombine: Monoid[Order] = new Monoid[Order] {
    override def empty: Order = Order(0.0, 0.0)

    override def combine(x: Order, y: Order): Order =
      Order(x.totalCost + y.totalCost, y.quantity + y.quantity)
  }

  println(add3(List(Order(1.0, 1.0), Order(2.0, 2.0), Order(3.0, 3.0))))

  println(Monoid[String].combine("a", "b"))
  private val value: Monoid[String] = Monoid.apply[String]
  value.combine("A", "b")

  private val maybeInt = Option(12)
  private val maybeInt1 = Option(34)

  private val maybeInt2: Option[Int] = Monoid.combine(maybeInt, maybeInt1)
  println(maybeInt2)

  private val str: String = "Hi " |+| " there"
  private val i: Int = 1 |+| 2
  println(str)
  println(i)
}
```

---

#### Monoid

`monoid` 也就是一个`trait`带着一个`单位元`和一个 `combine/add` 方法，但是它有什么用呢？

在大规模数据计算的时候会非常有用，分别在一个分区中计算结果，然后在将每一个分区中的结果进行汇总，因为可以实现并行计算



