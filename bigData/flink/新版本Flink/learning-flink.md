#### 4 critical concept

* Continous proccess of streaming data
* Event data
* Stateful streaming processinig
* State snapshot(checkpoint)

#### 2 patterns between operators

* One-to-one like map operator
* redistributor streams like keyby(repartitions by key hash),*broadcast()*, or *rebalance()* (which re-partitions randomly).

---

#### what can be Streeamed

Flink serializer is used for:

* Basic types, String/Long/Integer/Boolean/Array
* Composite types, Tuples/POJO/scala case classes

**POJO**

> * Class is public and standalone, no static innner class
> * the class has a public no argument constructor
> * All non-static, non-transient fields in the class (and all superclasses) are either public (and non-final) or have public getter- and setter- methods that follow the Java beans naming conventions for getters and setters.