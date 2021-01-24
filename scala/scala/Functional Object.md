#### Functional Object

**a class that define functional objects, or objetcs that do not have any mutable state**

---

#### 以创建 Rational 为例

```scala
class Rational(n: Int, d: Int)
```

> 这里你就创建了一个 Rational 的类，如果这个类没有其他的body，那么可以不写 {}(可选的)，
>
> 这里有俩个参数n: Int, d:Int， scala 会为类的参数列表创建一个原始构造器(primary constructor)，这个原始构造器会将所有的class 参数列表作为参数。
>
> Immutable object 的好处：
>
> * 更容易推断类型
> * immutable 在复制等传输的时候更加自由
> * 线程安全
> * hashtable 的key 值更加安全
>
> 缺点：
>
> * 可能在复制的时候回需要很大的对象图
>
>   **(they sometimes require that a large object graph be copied)**， 这可能会就会出现一些性能问题
>
> class 的参数列表直接在class 中都是可以直接使用的
>
> scala 将class 中定义的任何 code 都编译进 初始构造器**(primary constructor)**

```scala
class Rational(n: Int, d: Int) {
    println("Created " + n + "/" + d)
  }
```

> 在编译的时候，初始构造器会去调用  ```println("Created " + n + "/" + d)```

重写函数

```scala
class Rational(n: Int, d: Int) {
    override def toString = n + "/" + d
  }
```

> 在scala 中重写函数，必须要加上关键字 ```override```

> 上面提到的，class 函数体内的所有code 都会编译进初始构造器，如我现在需要 **Rational** 的分母不为0，那么我就需要在初始构造器中加入 条件判断，而且这个判断最好是能放在 class 的最开始的地方，如果一旦没有买足情况，那么就会抛出错误，就不会去编译其它代码了。
>
> 当不满足情况的时候就会抛出 **IllegalArgumentException.**

```scala
class Rational(n: Int, d: Int) {
    require(d != 0)
    override def toString = n + "/" + d
  }
```

**增加方法**

```scala
class Rational(n: Int, d: Int) { // This won't compile
    require(d != 0)
    override def toString = n + "/" + d
    def add(that: Rational): Rational =
      new Rational(n * that.d + that.n * d, d * that.d)
  }
```

> 但是这里会出现问题，目前n和 d 都仅仅是在参数列表中，并不是 **Rational** 的中的 **fields** 所以当使用 **that.n** 或者 **that.d**  的时候报错。所以应该做的是， 在 Rational 中添加fields

```scala
class Rational(n: Int, d: Int) {
  require(d != 0)
  val numer: Int = n
  val denom: Int = d
  override def toString = numer + "/" + denom
  def add(that: Rational): Rational =
  new Rational(
    numer * that.denom + that.numer * denom,
    denom * that.denom
  )
}
```

**This**

> This 会指向当前对象的引用，在 class 里面定义的时候，使用class fields 的时候也是可以省略掉 this 的。

```scala
def lessThan(that: Rational) = 
    this.numer * that.denom < that.numer * this.denom

def max(that: Rational) = 
    if (this.lessThan(that)) that else this
```

---

**辅助构造器**

```scala
class Rational(n: Int, d: Int) {
  require(d != 0)
  val numer: Int = n
  val denom: Int = d
  def this(n: Int) = this(n, 1) // auxiliary constructor
  override def toString = numer + "/" + denom
  def add(that: Rational): Rational =
  new Rational(
    numer * that.denom + that.numer * denom,
    denom * that.denom
  )
}
```

> 辅助构造器，必须以 ```def this(...)``` 开始，scala 中每一个辅助构造器必须在辅助构造器内部第一行先执行其它的构造器，也就是如我们的 辅助构造器 ```def this(n: Int)``` 内部首先调用了 ```this(n, 1)```,  这样做的目的就是，每次调用构造器的时候，需要去调用初始化构造器，因为一个类都编译进来初始化构造器。

**private**

```scala
class Rational(n: Int, d: Int) {
  
      require(d != 0)
  
      private val g = gcd(n.abs, d.abs)
      val numer = n / g
      val denom = d / g
  
      def this(n: Int) = this(n, 1)
  
      def add(that: Rational): Rational =
        new Rational(
          numer * that.denom + that.numer * denom,
          denom * that.denom
        )
  
      override def toString = numer + "/" + denom
  
      private def gcd(a: Int, b: Int): Int = 
        if (b == 0) a else gcd(b, a % b)
    }
```

> g、numer、demon 都是存放为 Rational 的三个初始构造器中，其中g是私有变量，
>
> 凡事定义为 **private** 的变量或者方法，都只能在class 的内部使用。

**定义一些操作**

```scala
class Rational(n: Int, d: Int) {
  
      require(d != 0)
  
      private val g = gcd(n.abs, d.abs)
      val numer = n / g
      val denom = d / g
  
      def this(n: Int) = this(n, 1)
  
      def + (that: Rational): Rational =
        new Rational(
          numer * that.denom + that.numer * denom,
          denom * that.denom
        )
      def + (i: Int): Rational =
            new Rational(numer + i * denom, denom)
  
      def * (that: Rational): Rational =
        new Rational(numer * that.numer, denom * that.denom)
  
      override def toString = numer + "/" + denom
  
      private def gcd(a: Int, b: Int): Int = 
        if (b == 0) a else gcd(b, a % b)
    }
```

在调用的时候可以这样调用

> a + b /  a.+(b) 
>
> Scala 是支持函数重载的，但是这个时候参数类型需要不同，scala 更具传入的参数类型的不同区载入需要的函数

---

**implicit conversions： 隐式转换**

>  目前你可以执行 ：
>
> ```adscala
> dval x = new Rational(2, 3)
> x + 2
> ```

> 但是不能执行：
>
> ```scala
> dval x = new Rational(2, 3)
> 2 + x
> ```

> 那么解决这个问题，就需要隐式转换，你需要定义一个 Int 到  Rational 转换的函数，这样当执行 2 + x 的时候，就会将 Int 转换为 Rational的了。

```implicit def intToRational(x: Int) = new Rational(x)```

> 你并不能讲这个转换定义在 class 中，而是应该在 compier 中，这样才能在他的计算范围之内。
>
> 这里在定义隐式转换的时候，命名并不重要，重要的是这个函数输出类型和输出类型，当自爱调用 2 + Rational(2, 3) 的时候，编译器首先回在 Int 的方法中找 + 这个操作，看是否有这样的一个函数，如果没有，那么就去去找 Int -> Rational 类型转换的函数，如果也没有，最后才报错。









