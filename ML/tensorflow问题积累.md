[多维矩阵相乘](https://stackoverflow.com/questions/48100954/why-does-tf-matmula-b-transpose-b-true-work-but-not-tf-matmula-tf-transpos)

* [多维矩阵满足什么条件的时候才能相乘](https://zhuanlan.zhihu.com/p/138731311)

> **多维的 tf.matmul(a, b) 的维度有如下两个要求：**
>
> **1、a的axis=-1的值（~只可意会~）和b的axis=-2的值需要相等。**
>
> **2、a和b的各维度的值（除了axis=-1和-2的值），在任意维度上，都需要“相等”或“有一个是1”。**

* 一个实例

问题：

```python
x = tf.constant([1.,2.,3.], shape = (3,2,4))
y = tf.constant([1.,2.,3.], shape = (3,21,4))
tf.matmul(x,y)                     # Doesn't work. 
tf.matmul(x,y,transpose_b = True)  # This works. Shape is (3,2,21)
tf.matmul(x,tf.transpose(y))   
```

回答

> tf.batch_matmul() 是被移除了，现在应该使用matmul做多维矩阵相乘。
>
> 默认情况下：tf.transponse(a) 做这样的操作
>
> 假如a的维度是[1, 2, 3, 4] 那么tf.transponse(a)  之后维度就变为[4,3,2,1]
>
> 也可以是这么做，使用perm 参数控制 变换的维度 tf.transponse(a, per=[4,3,2,1])
>
> 所谓上述的列子中，使用显示的transpose 之后的，并不能满足上 述的多维矩阵相乘的条件。

```python
tf.matmul(x,y,transpose_b = True)
```

在还是内部先做 了这么一件事情

```python
tf.transpose(y,perm=[0, 2, 1])
```

> 也就是只转换了最后两个维度。你怎么这样转置之后，就满足多维矩阵相乘的条件了。

