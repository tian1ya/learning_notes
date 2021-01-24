回顾下Adaboot 算法的步骤

![recallAda](./pic/recallAda.png)

回顾在介绍Adaboot 的时候，数据的权值是来源于数据被我们取出来几份(采样的时候，同一个数据被采到多此)，在这里更加泛华的权重是，权重是我们采样的比例。

Adaboot-DTree， Adaboot 算法和 DTree 都没有动，动的是对数据的采样方式

![recallAda](./pic/AdaDTree.png)

Adaboot 中基函数的权重，红色框所示。

如果是一颗完全长成的树，这时候树的错误率那么就是0，也就是基函数的权重变成了无限，这个时候表示这个完全生长的树就能完全做预测，也就是这个时候继承模型退化成了一个完全生长的树模型，这就和集成模型/方法没什么事了。

这个时候首先就是完全生长的树剪枝，也就是我们要一个简单的树模型，或者使用少部分数据训练一个弱模型。

![recallAda](./pic/AdaDTree2.png)

那么什么是弱的树，Decision stump

![recallAda](./pic/AdaDTree3.png)

使用了DecisionStump 也就是之前介绍的 Adaboost 。

---

AdaBoot 中数据的权重变化，红色框内容，公式中，方块t和alpha t之间的关系查看adaboot笔记 的内容

![recallAda](./pic/AdaDTree4.png)

adaboot 可以看做是linear blending 的延伸，这里可以这么看G(x) ，其中alpha 似乎可以看做是线性模型中的权重，而gt(x) 似乎能看成是对输入特征的一次转换(特征工程)

![recallAda](./pic/AdaDTree5.png)

上面的截图上引出来了Adaboot 的损失函数的来源，也就是adaboot 中想要voting score 正且大，于是就出现了指数损失函数来达到这个目的，

![recallAda](./pic/AdaDTree6.png)

经过转化之后，将指数损失函数最小化，那么自然就是梯度下降法了。

这里稍有不同的是，在梯度下降法中，梯度使用一个向量，但是在这里我们需要使用表示成的式子样子是，在当前的voting score 之下，在增加一个基函数使得指数函数能够得到减少，也就是这里的”梯度下降方向“是使用一个函数，表示的。

(可以这里理解函数和向量，向量是 index -> value 的对应， 函数是 实数(输入) -> h(输入) 的对应)

<img src="./pic/泰勒公式.png" alt="recallAda" style="zoom:150%;" />

![recallAda](./pic/AdaDTree7.png)

到这里的推导就得到了最终想要优化的式子

![recallAda](./pic/AdaDTree8.png)

找到最近的基函数，然后求最佳的基函数的权重

![recallAda](./pic/AdaDTree9.png)

这里注意新的感念，基于函数的梯度法。

推导出来最终的损失函数之后，如果延伸一下，将指数损失函数改为其他的：

![recallAda](./pic/AdaDTree10.png)

于是就得到了我们的GradientBoost

![recallAda](./pic/gdt1.png)

![recallAda](./pic/gdt2.png)

![recallAda](./pic/gdt3.png)

![recallAda](./pic/gdt4.png)

![recallAda](./pic/summary1.png)

那么具体的算法有

