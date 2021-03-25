从`代码角度理解理解 Monad、functor、functor` 等`TypeClass`

**Functors**

> functor is a type class, A functor is any data type that defines how **map** applies to it
>
> ```scala
> trait Functor[F[_]] {
>   	def map[A, B](fa: F[A])(f: A => B): F[B]
> }
> ```

**Applicative**

> **Applicative** is a type class, Applicatives is any data that define how apply applies to it
>
> Apply take a functor that has a function in it and another functor and extracts that function from the first functor and then maps it over the second one
>
> Speaking infomally you apply a function wrapped in context to a value wrapped in context
>
> ```scala
> trait Applicative[F[_]] extends Functor[F] {
>   def apply[A, B](fab: F[A => B])(fa: F[A]): F[B]
> }
> ```

**Monad**

> ```scala
> trait Monad[F[_]] extends Functor[F] {
>   def unit[A](a: => A): F[A]
>   def flatMap[A, B](ma: F[A])(f: A => F[B]): F[B]
> }
> ```
>
> Monad apply a function that returns a wrapped value to a wrapped value
>
> Monad is a type class, and is a data type that implements the flatMap, apply a function that return a wrapped value

**Monoid**

> ```scala
> trait Monoid[A] {
>   def op(a: A, b: A): A
>   def zero: A
> }
> ```

#### Are Monad powerful than Applicatives

> Applicatives and monads both model running computations in sequence, but Monad are more powerful because with applicatives  you can sequences the conputions, but monads allow you ti sequences computation with the additional property that the result of subsequent computations can depend on the result of previous computation

