### fpscala control

Scala 内置的控制语句有：

* if
* while
* for
* try
* match

---

```scala
// for 和 yield 的配合使用
// Producing a new collection
def scalaFiles =
    for {
      file <- filesHere
      if file.getName.endsWith(".scala")
    } yield file

```

> Each time the body of the for expression executes, it produces one value, in this case simply file. When the for expression completes, the result will include all of the yielded values contained in a single collection. 

**for 和 if 配置使用**

```scala
for (file <- filesHere if file.getName.endsWith(".scala")) {
    yield file  // Syntax error!
  }
```

**try catch**  try-catch-finally

```scala
 import java.io.FileReader
    import java.io.FileNotFoundException
    import java.io.IOException
  
    try {
      val f = new FileReader("input.txt")
      // Use and close file
    } catch {
      case ex: FileNotFoundException => // Handle missing file
      case ex: IOException => // Handle other I/O error
    }
--------------------------------------------------------------------------------
val half =
    if (n % 2 == 0)
      n / 2
    else
      throw new RuntimeException("n must be even")
---------------------------------------------------------------------------------
import java.io.FileReader
    val file = new FileReader("input.txt")
    try {
      // Use the file
    } finally {
      file.close()  // Be sure to close the file
    }
```

---

**match**

> ```
> cala 正则匹配几种语法
>    正则匹配：
>        val Pattern="(s.*)".r
>        val v1="spark";
> 
>        val r=v1 match  {
>          case Pattern(v1)=> "begin s*"
>          case "2"=> "2"
>          case _=> "default"
> 
>     等值匹配
>          val v1=1
> 
>          val r=v1 match  {
>            case 1=> "1"
>            case _=> "default"
>          }
> 
>      范围匹配
>          val v1=3
> 
>          val r=v1 match  {
>            // 如果 v1 包含于 1  1 until 5
>            case v1 if 1 until 5 contains v1=> "1-5"
>            case v1 if 5 until 10 contains v1=> "5-10"
>            case _=> "not found"
>          }
> 
>      变形语法：
>          val v1=3
> 
>          val r=v1 match  {
>            case v1 if (v1>0 && v1<=5) => "1-5"
>            case v1 if (v1>5 && v1<=10)=> "5-10"
>            case _=> "not found"
>          }
> 
>     多值匹配：
>       def glob(x:Any):Any= x match {
>              case   1 | "1" | "one"  => "one "
>              case "two"=> 2
>              case s:String => "String"
>              case _ => "其他"
>            }
> 
>     下划线的使用
>          ((a, b) => a + b))
>                    (_ + _))
>          在匿名函数中，当 a，b 可被推断的时候，才是可以使用下划线的方式。
>          在使用的时候，一般在哪些变量只出现并使用一次的情况下，才会使用下划线的方式
> 
>          但是也需要谨慎使用这种方式，原因在于，使用会导致不清晰
>          scala 在 匿名函数中推荐使用 常规的有名函数参数，这样阅读起来更加的清晰
> 
> 
>     在Scala 的 List 标准库中使用的是 右结合
> 
> 
>     ADT 代数数据类型，由一个或者多个数据结构所定义的数据类型，每个构造器可以包含零个或者多个构造器
> 
>     数据类型：是其数据构造器的累加或者联合，每个数据构造器优势他的参数的乘积
> ```

