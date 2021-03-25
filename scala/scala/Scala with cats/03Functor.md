#### Functor

> 理解`Functor` 就是一个包含着`map` 操作的抽象
>
> `map` 会对`structure` 中每个元素进行 `transformation` 操作，整个数据结构是都不会变的。
>
> 这个抽象允许我们在一个上下文中实现一个序列的操作，如对`List(1,2,3) 进行加和操作`，那么这个时候`序列操作`就是说`对1，2，3进行求和操作`，而上下文就是说`List` 容器。
>
> 注意这里`Monoid` 是类型进行直接操作，这个类似是一阶的类型如`Int`而`Functor` 是对高阶类型的操作`List` 等。
>
> 后续的例子也可以看出`Monoid` 只能做泛型，而`Functor` 做到高阶泛型(`higher kinked types`)

#### type 和 type constructor

> `List` 是一个 **Type Constructor**, `List[Int]` 是 `Type`
>
> , *List is a type constructor with one hole. We fill that hole by specifying a parameter to produce a regular type like List[Int] or List[A].*
>
> scala 语言中可以使用下划线的语法 定义 `type`
>
> ```scala
> def myMethod[f[_]] = {
>   	val functor = Functor.apply[F]
> }
> ```

`Cats` 定义的 `Functor` 允许我们对任何但超参数类型构造器创建 `instancce`.

---

* Option—the value may or may not be present; 

* Either—there may be a value or an error;

* List—there may be zero or more values.

```scala
private val ints = List(1, 2, 4)
private val value: Functor[List] = Functor[List]
// 根据类型，返回 ListInstances
private val ints1: List[Int] = value.map(ints)(a => a * 3)
/*
 然后在 ListInstances 中实现了最基础的 map 方法
 override def map[A, B](fa: List[A])(f: A => B): List[B] =
        fa.map(f)
 这里的 fa 就是我们传进去的 ints 的list， f 就是传进去的那个匿名函数
*/

// lift 方法 F[A] => F[B]
// Lift a function f to operate on Functors
private val function: Option[Int] => Option[Int] = Functor[Option].lift((x:Int) => x + 1)
println(function(Option(1))) // Some(2)


// 这里的 map 函数来源于 functor，因为这里找到了隐式超参数 Functor[F]
def doMath[F[_]](start: F[Int])(implicit functor: Functor[F]): F[Int] = {
    val start1 = start
    start1.map(n => n + 1)
/*
	函数会执行到 def map[B](f: A => B): F[B] =typeClassInstance.map[A, 
	B](self)(f)这里 self 就是 start1， typeClassInstance 就是 functor 	 也就是ListInstances，
	
	*/
}

//  println(doMath(Option(12))) // Some(13)
println(doMath(List(1, 2, 3))) //  List(2, 3, 4)


// 自定义变量添加方法
implicit val optionFunctor: Functor[Box] = new Functor[Box] {
      override def map[A, B](fa: Box[A])(f: A => B): Box[B] = 
  		Box(f(fa.value))}

private val value1: Box[Int] = Box[Int](123)
println(value1.map(a => a * 2))
```

以上的操作都是`eager`计算的，还有异步的`Functor`

##### Futures

`future` 也是一个 `functors` 只不过是异步的，`Future` 并不具备纯函数的编程，并没有引用透明，`Future` 总是计算，并将结果缓存下来，所以得到的结果总不是可预测的。

Map 可以作为一连串的 `transformation` 操作

```scala
private val future: Future[String] = Future(123).map(n => n+1).map(n=>n * 2).map(n => n + " !")
Await.result(future, 1.second)
println(future)
```

#### 什么是Functor呢

```scala
import scala.language.higherKinds

trait Functor[F[_]] {
  def map[A,B](fa: F[A])(f: A => B): F[B]
}
```

需要满足

* *identity*： ` fa.map(a => a) == fa`

* `Composition`: 

  ```scala
   fa.map(g(f(_))) == fa.map(f).map(g)
  ```

---

#### Functors in Cats

也是有同样的几个抽象

* `type class: import scala.language.higherKinds`

* `instances: `

  ```scala
  import cats.instances.list._   // for Functor
  import cats.instances.option._ // for Functor
  
  // 自定义自己的 Functors， 那么值需要实现一个 map 方法就可以了
  implicit val optionFunctor: Functor[Option] =
    new Functor[Option] {
  	def map[A, B](value: Option[A])(func: A => B): Option[B] = 				value.map(func)
  }
  
  implicit val treeFunctor: Functor[Tree] = new Functor[Tree] {
        override def map[A, B](fa: Tree[A])(f: A => B): Tree[B] = fa match {
          case Branch(left, right) => Branch(map(left)(f), map(right)(f))
          case Leaf(value) => Leaf(f(value))
        }
      }
  
  // println(Leaf(100).map(a => a * 2))
  // 这个时候编译器会出错，因为他只能识别 Functor[Tree] 而无法识别 
  // Functor[Leaf] 和 Functor[Branch]
  
  def branch[A](left: Tree[A], right: Tree[A]): Tree[A] = Branch(left, right)
  
  def leaf[A](value: A): Tree[A] = Leaf(value)
  
  println(branch(Leaf(10), Leaf(20)).map(a => a * 2))
  println(leaf(2).map(a => a * 2))
  ```

* `syntax`

