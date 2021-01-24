### Function && Closures

---

* 函数式的编程风格要求函数要小，一个函数只做一个具体的事情，这样的好处就是多个函数的复合方便

但是一个class或者 object 中函数太多也带来一些问题，函数名称的冲突。

scala 解决这个问题的方法是在函数中定义函数(这在Java 中是不可以的)

---

**闭包**

> ```scala
> import scala.io.Source
>   
>     object LongLines {
>   
>       def processFile(filename: String, width: Int) = {
>   
>         def processLine(line: String) = {
>           if (line.length > width)
>             println(filename + ": " + line.trim)
>         }    
>   
>         val source = Source.fromFile(filename)
>         for (line <- source.getLines())
>           processLine(line)
>       }
>     }
> ```
>
> 局部函数可以访问它的闭包函数，也就是说上面的例子中在函数processLine 中可以访问它的闭包函数 processFile 中的 参数 filename

---

**函数式一等公民**

> * 可以作为参数进行传递及返回，赋值
>
> ```scala
> var increase = (x: Int) => x + 1
> increase(10)
> ```
>
> **=>** 理解为一种映射，这里参数 x 定义的是var 类型，如果函数体较长，那么可以使用 {} 包裹
>
> ```scala
> increase = (x: Int) => {
>            println("We")
>            println("are")
>            println("here!")
>            x + 1
>          }
> ```

**简略函数**

> * 可以不写函数的类型
>
>   ```scala
>   someNumbers.filter((x) => x > 0)
>   // 这里的匿名函数 (x) => x > 0 就没有写类型，这是因为scala 编译器可以从someNumbers的类型中推断到类型。
>   // 这里圆括号也是可以去掉的
>   someNumbers.filter(x => x > 0)
>   ```
>
> * 使用下划线 _, 当一个参数在一个函数中只会出现一次那么久可以使用下滑下(placeholder)
>
>   ```scala
>   someNumbers.filter(_ > 0)
>   someNumbers.foreach(println _)
>   ```

> 当给函数中传入参数的时候，实际上是将函数 apply 到这些参数到

> **函数还可以这么使用**
>
> ```scala
> def sum(a: Int, b: Int, c: Int) = a + b + c
> val a = sum _ // 先给函数一些不需要的参数 None
> a(1, 2, 3)
> // a(1, 2, 3) 等通与 a.apply(1,2,3)
> ```
>
> apply 函数是scala 编译器自动产生的，当你执行 val a = sum _
>
> 以上的用法就是scala 中的**偏函数**的语法，函数可以分步传入，上面的使用方法是，第一次传入一个空，然后后面将剩余的参数传递。
>
> 也可以这么使用：
>
> ```scala
> val b = sum(1, _: Int, 3)
> ```
>
> 解读上面的代码就是：scala编译器产生一个心得函数类，它的apply 方法只接受一个参数
>
> ```scala
> b(2)
> ```

> ```scala
> val addMore1 = (x: Int) => x + more
> // 直接函数赋值称为是 function values，
> ```
>
> 上面的函数值(object) 也是有"闭包的语法"
>
> ```scala
> val addMore2 = (x: Int) => x + 1
> ```
>
> 但是这里就没有了闭包的语法。
>
> 所谓闭包就是一个函数值它并没有关闭，有对外的引用(capture any free variables)，第一个 ```addMore1``` 它有对外的应用，并没有关闭，但是 ```addMore2``` 并没有对外的引用，当完成定义和赋值之后函数就关闭了，之后就可以使用。
>
> 当闭包中应用的值发生了变化，more 发生变化，闭包还是会按照完成函数赋值/创建时候的那个值计算

> **重复参数**
>
> ```scala
> def echo(args: String*) = 
>            for (arg <- args) println(arg)
> ```
>
> 在函数内部，重复参数实际上是一个Array
>
> **默认参数**
>
> ```scala
> def printTime(out: java.io.PrintStream = Console.out) =
>       out.println("time = " + System.currentTimeMillis())
> ```
>
> **尾递归**
>
> ```scala
> def approximate(guess: Double): Double = 
>     if (isGoodEnough(guess)) guess
>     else approximate(improve(guess))
> ```
>
> 等价于
>
> ```scala
> def approximateLoop(initialGuess: Double): Double = {
>     var guess = initialGuess
>     while (!isGoodEnough(guess))
>       guess = improve(guess)
>     guess
>   }
> ```
>
> 如果测试时间，二者几乎一样。
>
> scala 的编译器当遇到尾递归的时候，会替换当前递归跳回到最初的函数调用，然后使用新值更新函数参数。
>
> 在别写函数的时候，应该尽可能的使用递归的方法，尤其是尾递归的方法，更加的直观，精确。

---

**高阶函数**

**reduce code duplication**

> 假如现在有一个文件过滤code：
>
> ```scala
> object FileMatcher {
>     private def filesHere = (new java.io.File(&quot;.&quot;)).listFiles
>   
>     def filesEnding(query: String) =
>       for (file &lt;- filesHere; if file.getName.endsWith(query))
>         yield file
>     def filesContaining(query: String) =
>       for (file &lt;- filesHere; if file.getName.contains(query))
>         yield file
>     def filesRegex(query: String) =
>       for (file &lt;- filesHere; if file.getName.matches(query))
>         yield file
>   }s
> ```
>
> 似乎有多少种情况，就需要些多少个函数，但是呢，这里函数会有很多的重复代码，而且只有过滤条件不同，每一次过滤条件不同，那么久需要写一个方法，显然过于冗余了。
>
> 这里如果将每一个过滤逻辑当做是 functional value 传递给函数，那么久只需要写一个函数就能解决这个问题了。
>
> ```scala
> object FileMatcher {
>       private def filesHere = (new java.io.File(".")).listFiles
>   
>       private def filesMatching(matcher: String => Boolean) =
>         for (file <- filesHere; if matcher(file.getName))
>           yield file
>   
>       def filesEnding(query: String) =
>   // underscore which means they are taken from arguments to the function
>   // of filesMatching
>         filesMatching(_.endsWith(query))
>   
>       def filesContaining(query: String) =
>         filesMatching(_.contains(query))
>   
>       def filesRegex(query: String) =
>         filesMatching(_.matches(query))
>     }
> ```

再来一个使用高阶函数减少code数量的例子

> ```scala
> def containsNeg(nums: List[Int]): Boolean = {
>     var exists = false
>     for (num <- nums)
>       if (num < 0)
>         exists = true
>     exists
>   }
> ```
>
> ```scala
> def containsNeg(nums: List[Int]) = nums.exists(_ < 0)
> ```
>
> ```scala
> def containsOdd(nums: List[Int]): Boolean = {
>     var exists = false
>     for (num <- nums)
>       if (num % 2 == 1)
>         exists = true
>     exists
>   }
> ```
>
> ```scala
>   def containsOdd(nums: List[Int]) = nums.exists(_ % 2 == 1)
> ```

**柯里化**

> ```scala
> def first(x: Int) = (y: Int) => x + y
> ```
>
> ```scala
> def curriedSum(x: Int)(y: Int) = x + y
> ```
>
> ```scala
> def twice(op: Double => Double, x: Double) = op(op(x))
> ```

**复合和继承**

> **abstract**
>
> ```scala
> abstract class Element {
>       def contents: Array[String]
>     }
> ```
>
> 关键字 abstract 意味着这个类包含着抽象成员，这个成员并没有倍implement，那么这个class 就不能被初始化，这里方法 contents 并没有abstract 关键字，是因为在scala 中方式没有被实现的函数，都是抽象的。
>
> **parameterless method**
>
> ```scala
> abstract class Element {
>     def contents: Array[String]
>     val height = contents.length
>     val width = 
>       if (height == 0) 0 else contents(0).length
>   }
> ```
>
> 无参数函数并不会写为 height():Int
>
> 这样的做法就是同一入口，对于客户端而言，调用方法 content 或者 属性 height 都是一样的
>
> **extends**
>
> ```scala
> class ArrayElement(conts: Array[String]) extends Element {
>       def contents: Array[String] = conts
>     }
> ```
>
> ArrayElement 会继承Element 中所有的非私有member，所有的class 都是AnyRef 的子类(和Java 的 Object 类似)，
>
> 继承意味着，superclass 的member 也都是属于subclass 的
>
> * private member 除外
> * 如果子类中有和父类中相同名称，参数的方法，那么这个方法不会继承父类，而是沿用子类方法。如果父类中的这个方法是abstract，那么子类中的方法是父类的oberride
>
> **override method and fields**
>
> ```scala
> class ArrayElement(conts: Array[String]) extends Element {
>       val contents: Array[String] = conts
>     }
> ```
>
> 在Element 中 contents 是一个def，但是在子类中可以将其实现为一个变量 val，这里也就显示paramaterless 的method 和 var 是可以想通的，也就是说在scala 中定义一个没有参数的函数如 ```def f()``` 和一个变量名称为 ```f```  是禁止的(这在Java 中试允许的)。
>
> ```scala
> class WontCompile {
>     private var f = 0 // Won't compile, because a field 
>     def f = 1         // and method have the same name
>   }
> ```
>
> 这里就涉及到了命名空间 namespace。
>
> 在Java 中有4种namespace，分别是 fields, methods, types, and packages
>
> 但是在scala 中只有2中： 
>
> - values (fields, methods, packages, and singleton objects)
> - types (class and trait names)
>
> fields 和 method 是属于同一种的 namespace，所以上面定义 f 的时候回出错
>
> 这样也就可以使用 def 去 override 一个 var 的。同时返过来也是可以的。