有这么一个概念：

**强可学习(strongly learnable) 和 弱可学习(weakly learnable)**

> 强可学习： 一个概念/类，如果存在一个多项式的学习算法能够学习，并且正确率很高，那么就称这个概念/类强可学习的
>
> 弱科学习，一个概念/类，如果存在一个多项式的学习算法能够学习，学习的正确率仅仅比随机猜测要好点，那么称是弱可学习的。
>
> 并且证明二者是等价的

**问题：**

> 二者证明可等价，那么如何让二者等价呢，如果将弱学习器提升为强学习器？
>
> Adaboot 便是其中一个典型的提升算法。

**思想**

对于一个分类问题而言，给定一个训练样本集，求比较粗糙的分类规则(弱分类器)要比求一个精确的分类规则容易的多，提升方法就是从弱学习算法出发，反复学习，得到一系列弱分类器，然后组合这些弱分类器，构成一个强分类器，大多数的提升方法都是改变训练数据的概率分布(训练数据的权值分布)，针对不同的训练数据分布调用弱学习算法的一系列弱分类器。

**Adaboost 的两个问题**

> * 如何改变数据的权值分布
>
> > Adaboost 的做法是提高那些被前一轮弱分类器错误分类样本的权值，而降低那些被正确分类样本的权限，这样那些没用呗正确分类的样本，由于权值大而在下次的训练中受到更大的关注
>
> * 弱分类器，如何组合起来
>
> > Adaboost 使用加权多数表决的方法，加大分类误差小的弱分类器的组合时期在表决中其较大的作用，减小分类误差概率大的弱分类器的权值，使其在表决中其较小的作用。

现在有一些数据：

![adaboostSample](./pic/adaboostSample.png)

经过boostraping的数据采集。得到蓝色的数据。同时使用另外一个变量记录数据的个数，并且将每笔的数据和模型的结果计算得到的误差对应起来。

二者证明可等价，那么如何让二者等价呢，如果将弱学习器提升为强学习器？

![adaboostSample](./pic/AdaboostInitWeight.png)

**Weighted base Algorithm**

![adaboostSample](./pic/wea.png)

现在解决第一个问题，**如何改变数据的权值分布** 也就是上面提到的 u。

![adaboostSample](./pic/firstproblem.png)

g(t) 是在 u(t)的分布上得到，并且g(t) 在 u(t+1)的表现是比较差的，所以这个时候是学习到g(t+1), 也就是g(t) 个 g(t+1) 是不一样的。

那么如何将g(t) 在下一轮的表现很差，表现很差，相当于是随机猜测， 和丢铜板没啥两样，于是：

g(t) 在 u(t+1)下得到的结果如同是丢铜板一样。

![adaboostSample](./pic/firstproblem1.png)

![adaboostSample](./pic/firstproblem2.png)

那么需要将犯错误的和没有犯错误的应该reweight 到相同。

也就是犯错误的点 * 正确率。 正确的点 * 错误率

![adaboostSample](./pic/firstproblem3.png)

![adaboostSample](./pic/firstproblem4.png)

但是在实际中使用的是另外一个相同的效果的式子，且有更好的物理意义

当错误率比较好(<1/2)， 那么得到的值是大于1 的，所以错误率 * 大于1的值，得到大的加权，相反正确率得到一个小的加权。

![adaboostSample](./pic/firstproblem5.png)

![adaboostSample](./pic/firstproblemDone.png)

目前解决了第一个问题，将数据的 reweight 得到解决，并计算到每一轮迭代的基模型，那么如何将他们合并呢？

![adaboostSample](./pic/secondproblem.png)

一个直观的概念是，好的基模型给他多点票，坏点的基模型，给少点票。

![adaboostSample](./pic/secondproblem1.png)

![adaboostSample](./pic/AdaboostDone.png)

![ ](./pic/AdaboostDone1.png)

---

Adaboost 还有一个解释是，可以任务Adaboost 是模型为加法模型，损失函数为指数函数，学习算法为前向分布算法时的二分类学习方法。

![adaboostSample](./pic/AdaboostAdditionMethod.png)

**从这个角度理解，Adaboot 算法的损失函数是指数损失函数。**















