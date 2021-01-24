> scala 中仍然可以使用Java 线程，但是对于并发使用Actor 模型是更好的选择，Actor 模型是一个比线程更高层的抽象，，理解这种模型的抽象有助于解决手头的问题，而不是单向底层线程、锁和共享数据。
>
> 早期的Scala 版本中包含了原始的Actors 库，从2.10.0开始使用类型安全的Akka 的actors 类库，以前版本的actors类型被抛弃。

> 通过对并发和并行的高级抽象，actors类库带来很大的好处，Akka actor库还有些额外的特点。
>
> * 轻量，事件驱动处理。
> * 高容错性
> * 位置透明：Akka actor可以运行在多个JVM和服务器上，工作在分布式的环境，彼此之间使用纯消息传递。
>
> “高级别的抽象”可以解读为“易用性”。理解Actor模型并不需要太久，一旦理解就可以写出复杂的并发的应用，这比使用基础Java库更简单。

**Actor 模型 **



> * [actor]()是在创建一个基于actor系统时的最小单元，就像OOP系统中的一个对象。
>
> * actor封装了状态和行为，就像一个对象。
>
> *  actor的状态无法查看，但可以给一个actor发消息请求状态信息（就好像问一个人他感觉如何一样），但不能进去执行它的方法，或者获取它的字段。
> *  actor有一个邮箱，目的是处理里面的消息。
> *  可以通过发不变的消息与actor交流，消息会进入actor的邮箱。
> *   当actor收到消息时，会将其从邮箱中取出，打开邮件，用它的算法处理消息，然后继续处理下一封邮件。如果没有消息，actor会等待直到收到消息。
>
> 在应用程序中，actor组成的层级结构，就像一个家族，或者一个商业组织：
>
> * Typesafe团队推荐把actor想象成人，如一个在商业组织中的人。
> *  一个actor有一个长辈（管理者）：创建actor的人
> * actor可以有孩子。把这想象成一个商业组织，总裁可能有一些副总裁。那些副总裁也会有许多下属，等等。
> * actor也会有兄弟姐妹。例如，在一个组织中有10个副总裁。
> * 开发一个actor系统的最佳实践就是“委托，委托，委托”，特别是行为会阻塞的情况。在商业组织里，总裁可能想要做某些事情，那么他会把工作委托给他的副总裁。副总裁会把工作委托给经理，以此类推，直到工作最终被一个或多个下属完成。
> * 委托很重要。想象下要花几个人-年完成的工作。如果总裁不得不自己处理工作，他就无法响应其他需求了（同时副总裁和其他雇员会集体空闲）。
>
> Actor模型的最后就是错误处理。运行时，有些东西可能会出错，可能会抛出异常。发生异常时，actor和这个actor的孩子都会挂起，给管理者发一个失败的信号。
>
> 根据工作和失败的本质，actor管理者此时有四种选择：
>
> * 回复下属，保持它的内部状态。
> * 重启下属，给它明确的状态。
> * 终结下属。
> * 升级错误

**在应用程序中使用actor创建并发。**

> 集成 akka.actor.Actor 类创建一个actor，在类中实现一个receive 方法，该方法应该使用case 语句实现，这样允许actor 响应收到的不同消息。

```scala
package actor

import akka.actor.{Actor, ActorRef, ActorSystem, Props}

case object PingMessage

case object PongMessage

case object StartMessage

case object StopMessage

class Ping(pong: ActorRef) extends Actor {
  var count = 0

  def incrementAndPrint: Unit = {
    count += 1
    println("ping")
  }

  override def receive: Receive = {
    case StartMessage => {
      incrementAndPrint
      pong ! PingMessage
    }

    case PongMessage => {
      incrementAndPrint
      if (count > 99) {
        sender ! StopMessage
        println("ping stoped")
        context.stop(self)
      } else {
        sender ! PingMessage
      }
    }

    case _ => println("Ping got something unexpected.")
  }
}

class Pong extends Actor {
  override def receive: Receive = {
    case PingMessage => {
      println(" pong")
      sender ! PongMessage
    }
    case StopMessage => {
      println("pong stopped")
      context.stop(self)
    }
    case _ => println("Pong got something unexpected")
  }
}


object PingPongTest extends App {
  private val system = ActorSystem("pingPongTest")
  private val pong: ActorRef = system.actorOf(Props[Pong], name = "pong")
  private val ping: ActorRef = system.actorOf(Props(new Ping(pong)), name = "ping")

  ping ! StartMessage

  system.terminate()
}
```

上面的例子中使用到了构造器，除此之外，一个Actor 还有以下的生命周期方法

> * receive
> * preStart
> * postStop
> * preRestart
> * postRestart

```scala
package actor

import akka.actor.{Actor, ActorRef, ActorSystem, Props}

case object ForceRestart
class Kenny extends Actor {

  println("entered the kenny constructor")


  override def preStart(): Unit = {
    println("kenny preStart")
  }

  override def postStop(): Unit = {
    println("kenny postStop")
  }

  override def preRestart(reason: Throwable, message: Option[Any]): Unit = {
    println("kenny preRestart")
    println(s" REASON: ${reason.getMessage}")
    super.preRestart(reason, message)
  }

  override def postRestart(reason: Throwable): Unit = {
    println("kenny: postRestart")
    println(s" REASON: ${reason.getMessage}")
  }

  override def receive: Receive = {
    case ForceRestart => throw new Exception("xxx")
    case _ => println("kenny received a message")
  }
}

object LifeCycleDmo extends App {
  private val system = ActorSystem("LifeCycleDmo")

  val kenny: ActorRef = system.actorOf(Props[Kenny], name = "Kenny")

  println("sending kenny a message")

  kenny ! "hello"

  Thread.sleep(1000)

  println("kenny restart")
  kenny ! ForceRestart

  println("Kenny stop")
  system.stop(kenny)

  println("Kenny terminate")
  system.terminate()
}
```

输出：

```scala
sending kenny a message
entered the kenny constructor
kenny preStart
kenny received a message
kenny restart
Kenny stop
Kenny terminate
kenny postStop
[ERROR] [05/03/2020 15:03:29.711] [LifeCycleDmo-akka.actor.internal-dispatcher-2] [akka://LifeCycleDmo/user/Kenny] xxx
java.lang.Exception: xxx
```

> Akka Actor 的body 是构造函数的一部分，像任意的一个正常Scala 类，在actor 的构造函数里，pre* 和 post* 方法可以用来初始化和关闭actor需要的资源。

**创建子Actor**

**从一个actor 中创建一个子actor**

```scala
class Kenny extends Actor {
	private val child: ActorRef = context.actorOf(Props[Child], name = "child")
  ...
}
```

例子

```scala
package actor

import akka.actor.{Actor, ActorRef, ActorSelection, ActorSystem, PoisonPill, Props}

case class CreateChild(name: String)
case class Name(name: String)

class Child extends Actor {
  var name = "No name"


  override def postStop(): Unit = {
    println(s"D's oh! they kill me ${name}: ${self.path}")
  }

  override def receive: Receive = {
    case Name(name) => this.name = name
    case _ => println(s"Child $name got message")
  }
}

class Parent extends Actor {
  override def receive: Receive = {
    case CreateChild(name) => {
      println("create a child actor")
      val child = context.actorOf(Props[Child], name = s"$name")
      child ! Name(name)
    }
    case _ => println("Parent got some other message.")
  }
}

object ParentAndChildDome extends App {
  private val parentAndChildDome = ActorSystem("ParentAndChildDome")
  private val parent: ActorRef = parentAndChildDome.actorOf(Props[Parent], name = "parent")

  parent ! CreateChild("Tom")
  parent ! CreateChild("Jerry")

  Thread.sleep(500)

  println("look Tom")
  private val tmo: ActorSelection = parentAndChildDome.actorSelection("/ParentAndChildDome/user/parent/Tom")
  /*
    发送一个 PoisonPill 消息停止一个actor，该消息会在被处理时候停止 actor，这个消息会像平常的消息一样在邮箱中排队，
   */
  tmo ! PoisonPill

  parentAndChildDome.terminate()
}
```

输出：

```scala
create a child actor
create a child actor
D's oh! they kill me Tom: akka://ParentAndChildDome/user/parent/Tom
D's oh! they kill me Jerry: akka://ParentAndChildDome/user/parent/Jerry
```

---

**Future**

> 用一种简单的可以并发地运行一个或多个任务的办法，包括当任务结束时处理它们结果的办法。例如，可能要并行地发送多个网络服务调用，然后在它们都返回后处理结果。

一个简单的阻塞程序

```scala
package actor

import scala.concurrent.{Future, Await}
import scala.concurrent.duration._

/*
  这个import 会引入，默认的全局执行上下文，可以将执行上下文看成线程池，并且这是访问线程池的一个简单方式
 */
import scala.concurrent.ExecutionContext.Implicits.global
class FutureHelper {

}

object Test extends App {
  implicit val baseTime: Long = System.currentTimeMillis

  val f = Future {
    Thread.sleep(500)
    1 + 1
  }

  /*
     Await.result方法调用说明它最多等待1秒Future的返回。如果Future没有在规定时间内返回，它会抛出java.util.concurrent.TimeoutException异常。
   */
  private val res: Int = Await.result(f, 1 second)

  println(res)

  Thread.sleep(1000)
}
```

运行一个 程序，但不阻塞，使用回调

```scala
package actor

import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Success}

/*
  这个import 会引入，默认的全局执行上下文，可以将执行上下文看成线程池，并且这是访问线程池的一个简单方式
 */
import scala.concurrent.ExecutionContext.Implicits.global
class FutureHelper {

}

object Test extends App {
  private val res = Future {
    Thread.sleep(500)
    42
  }

  /*
    f.onComplete方法设定好回调。一旦Future完成，就会回调onComplete方法。
      Future要么返回期望的结果42，要么返回一个异常。
      println语句会在Future运行的同时说明其他工作在同步进行。

   因为Future在其他地方并发运行，并且不知道结果何时返回，所以这段代码的输出是不确定的
   */
//  res.onComplete {
//    case Success(value) => println("result: " + value)
//    case Failure(exception) => exception.printStackTrace()
//  }

    /*
      在不想用onComplete方法的情况下，可以使用onSuccess和onFailure回调方法，这两个方法在未来会删除
     */

  res onSuccess {
    case result => println("result: " + result)
  }

  res onFailure {
    case result => println("result: " + result)
  }

  println("a...."); Thread.sleep(100)
  println("b...."); Thread.sleep(100)
  println("c...."); Thread.sleep(100)
  println("d...."); Thread.sleep(100)
  println("e...."); Thread.sleep(100)
  println("f...."); Thread.sleep(100)

  Thread.sleep(2000)
}
```

**返回一个 futures 的方法**

```scala
package actor

import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Success}

/*
  这个import 会引入，默认的全局执行上下文，可以将执行上下文看成线程池，并且这是访问线程池的一个简单方式
 */
import scala.concurrent.ExecutionContext.Implicits.global
class FutureHelper {

}

object Test extends App {
  private val baseTime: Long = System.currentTimeMillis()

  // 返回一个 Future
  def longRunComputation(i: Int): Future[Int] = Future {
    Thread.sleep(100)
    i + 1
  }

  // 这里不会发生阻塞
  longRunComputation(11).onComplete {
    case Success(res) => println("result: " + res)
    case Failure(ex) => ex.printStackTrace()
  }

  println("future 后面，不阻塞计算逻辑，直接输出")
  Thread.sleep(1000)
}
```

**运行多个Future**

```scala
package actor

import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Random, Success}

/*
  这个import 会引入，默认的全局执行上下文，可以将执行上下文看成线程池，并且这是访问线程池的一个简单方式
 */
import scala.concurrent.ExecutionContext.Implicits.global
class FutureHelper {

}

object Test extends App {
//  private val baseTime: Long = System.currentTimeMillis()

  def run(i: Int): Future[Int] = Future {
//    Thread.sleep(Random.nextInt(500))
    val res = i + 10
    println(s"return result from cloud: $res")
    res
  }


  val r1: Future[Int] = run(1)
  val r2: Future[Int] = run(2)
  val r3: Future[Int] = run(3)

  /*
    for推导用来把结果连接在一起。当所有3个future返回时，它们的值会被赋给变量r1, r2和r3。并且这3个值的和会从yield表达式返回，然后被赋给结果变量。
    for 推导返回一个 Future
   */
  val result = for {
    rr1 <- r1
    rr2 <- r2
    rr3 <- r3
  } yield (rr1, rr2, rr3)

  result onComplete {
    case Success(res) => println("result: " + res)
    case Failure(ex) => ex.printStackTrace()
  }

  println("before sleep at the  end")
  Thread.sleep(2000)
}
```

```scala
    for推导用来把结果连接在一起。当所有3个future返回时，它们的值会被赋给变量r1, r2和r3。并且这3个值的和会从yield表达式返回，然后被赋给结果变量。
    for 推导返回一个 Future

    一个Future 就是一个并发运行计算的容器，在未来的某个时间可能会返回一个T 类型的结果或者异常
    算法的计算在Future 被创建后在某个不确定的时间开始，通过执行上下文运行在与它绑定的线程上(不是主线程)
    当Future 完成时候计算结果才可使用
    当返回一个结果时候，Future 就完成了使命，可能要么成功返回，要么失败

    一个 ExecutionContext 执行它得到的任务，可以把它看成一个线程池

    列子中的 ExecutionContext.Implicits.global 语句引入了默认的全局执行上下文对象
```

**Actor 发消息并等待回复**

