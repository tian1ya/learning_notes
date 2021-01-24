### 集成学习

背景：来源于生活中的故事

> 假设我正在一个炒股票的路上，正在下决心买那个股票，于是我就去请教很多很多个的人，告诉我明天的股票会涨还是跌，那么我请教的人中有的人股票玩的特别好，有的人玩的不是很好，所以预估可能会准确，可能不准确，选择的方式可能会有
>
> 1. 基于他之前的炒股输赢选择我的一个最信任的人的意见，**--validation**
> 2. 如果请教的朋友都很厉害，那我会使用一种uniformly 的投票方式 **--vote**
> 3. 也会有很多人值得信赖，有的人强，有的人弱，那么强的人我应该多点的投票个数，弱的人则少点的投票个数  **--non-uniformly**
> 4. 我请教的人中有的人擅长科技股，有的人擅长 教育股，那么在不同的条件下，去相信不同的人， **--conditionally**

![aggregation](./pic/aggregation.png)

> 上面是基于生活上的决策，那么回归到生活中。
>
> 第一种方式，当有多个模型的时候，那么这些模型可能就需要在一个validation set (g-)上去做一个评估，然后选出表现最好的那个。
> 第二种方式：给所有模型一个投票结果。
>
> 第三种方式：给每个模型的票数是有一个函数(alph)去决定
>
> 第四中方式：每个模型的投票与否投所少票，由一个函数(q)去决定。q 函数是和输入x有关

![aggregation](./pic/aggeration2.png)

在单模型的时候，做模型选择的时候，经常会在validation 的数据及中选择中一个最强的模型，**而aggregate中做的就是将一些较弱的模型经过某种方法提升为强模型**。

![aggregation](./pic/aggeration3.png)

**为什么 aggregate 可以工作呢？**

motivation 的一些角度讲讲

1. 如左侧下分类，两个只能画出横线和竖线的弱分类器，经过一定的结果就可能将单独横线或者是竖线不能做到的事情做到，一堆弱弱合起来就能变强

2. 一堆的分界线，感觉都还不错，不同的模型会有不同的选择标准，选择一条，那么这么多的线经过一些投票的方式，就最终得到一个中庸的结果(正则化)。

![aggregation](./pic/aggeration4.png)

集成学习，具有一些特征模型转化，以及一些正则化的效果。

![aggregation](./pic/HW.png)

---

**Uniform Blending** 少数服从多数

![aggregation](./pic/aggeration5.png)

上图红色部数据，三条线分类线，第一条会将其右侧选择为蓝色类，第二条分类线会将该数据也选择为蓝色类，第三条分类线会将数据点投票为红色xx类（其点在第三条线左侧），经过投票，那么它就被分类到蓝色类中了。

如果是regression 问题。那么应该平均下投票

![aggregation](./pic/aggeration6.png)

而且在投票(平均)出结果，每一个都应该是经历的不同，差异性要尽量大。

**数学理论上的证明经过aggeration 之后误差的期望值会降低。**

![aggregation](./pic/aggeration7.png)

投票的过程就是消除bias 的过程，bias 是投票过程中消除的各种各样的杂声

![aggregation](./pic/aggeration8.png)

---

**linear Blending**： 做一个线性组合

![aggregation](./pic/linearBlending.png)

在模型选择的时候，会选择一个 best of best 的模型。在计算投票的那个权重的时候，不要用训练数据集(overfitting)，而是验证数据集。

![aggregation](./pic/blending.png)

linear Blending VS Any Blending（stacking），这里Any 可能是另外一个模型。但是注意Blending 特别容易overfitting

![aggregation](./pic/blending2.png)

![aggregation](./pic/testChap.png)

* 公平的投票，uniform blending -> voting/averaging
* 非公平的投票 non-uniform -> linear
* 条件投票          stacking

上面提到的是，先将所有的g 模型找出来，然后某种方式blending

**那么是否可以是一边找到 g模型，一边将这些g 模型blending 呢？**

---

学习g的过程中，各个g之间的差异性是非常中重要的，一下几种方式，可以得到不同的g

![aggregation](./pic/diversity.png)

使用 bootstrapping 的方式从一份数据中产生，不同的数据，去训练算法，得到不同的模型(参数不同)

> **bootstrapping** : 有放回的随机抓取数据，抓出来的数据成为 bootstrap sample。

![aggregation](./pic/bagging.png)



















