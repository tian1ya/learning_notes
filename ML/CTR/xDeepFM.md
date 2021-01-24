FM: 计算交叉特征，泛化未出现的sample

DNN: 隐式bite-wise 构造特征交叉

**CIN**

> 显示的vector-wise构建组合特征， `CIN` 涉及到`CNN`  和 `RNN` 的一些思想。

**传统的构建交叉特征的方式存在的难点**

> 1. 高质量的特征交叉意味着高投入： 特征交叉和业务场景息息相关
> 2. 数据量大，使得提取所有的特征交叉难度大
> 3. 人为很难提取到那些隐式的特征交叉

```javascript
FM 将特征i隐射到向量 vi1，vi2...vin, FM 只构建了2个维度的特征交叉，没有做更高层次的交叉，主要原因是
1. 高特征交叉，计算复杂度高
2. 很多没有的交叉特征，翻到是一项噪音
```

**一些之前构建特征交叉 方法模型的特点**

> * PNN/FNN
>
>   > 只聚焦在高层特征交叉
>
> * Wide & Deep / DeepFM
>
>   > Wide & Deep 首次提出了混合模型，一部分构建高层特征交叉，一部分构建底层特征交叉
>
> 上述使用的NN去构建特征交叉，但是NN构建的特征交叉都是一些隐式的方式，而且构建了多少中的特征交叉并不得而知，且无理论支撑说构建多少等的交叉是好的。
>
> 并且NN 构建特征交叉都是基于 `bite-wise` 的，这和`FM` 中提出的`vector-wise` 不一致的(FM 是首次使用隐向量自动构建交叉特征)。
>
> 基于此分析： `CIN` 提出了基于`vector-wise` 的显式的构建特征交叉方法。

> xDeepFM 的提出是基于 DCN 的

---

**Embedding layer**

> 将`one-hot` 之后的特征映射到低维稠密空间，如果有多个域那么 将每个域中映射得到的向量在输出层进行组合。
>
> ![a](./imgs/xdeepfm.png)

**FNN/PNN/wide && deep 是怎么处理embedding layer 的输出呢**

> `PNN/FNN`直接将`embedding layer` 的输出作为`NN` 网络的输入，前向计算
>
> ![a](./imgs/xdeepfm1.png)
>
> 这个式子就是文中一直提到的 `bite-wise` 计算方式，一个域中的值，输出一个多维向量，然后这个向量和其他域的向量一起组合输入到`NN`  中，那么就会发生这样的事情同一个域(向量)中的值会影响彼此的计算。
>
> `DeepFM` 做的就比较多了。
>
> ![a](./imgs/xdeepfm2.png)
>
> 这里右侧就是`pnn/fnn`做的事情，左侧是`fm` 做的事情，也就是`DeepFM` 既有`bite-wise` 计算 又有 `vector-wise` 的计算。
>
> 还是如上面一直说的，`DeepFM` 只做了底层的二维交叉，和高维的隐式多交叉。

**DCN**

> `Cross Network` 提出的网络，显示的构建多维交叉
>
> ![a](./imgs/xdeepfm3.png)
>
> 网络中每层计算输出是 这样计算的。
>
> ![a](./imgs/xdeepfm4.png)
>
> 所以在计算的时候每层输出都在计算特征交叉，第l层得到了l阶的特征交叉。
>
> 而在`xDeepFM` 的作者看来，使用公式3得到的特征交叉，其实每层的输出就是第一层乘以一个标量的计算而已。作者证明如下：
>
> ![a](./imgs/xdeepfm5.png)
>
> 在这里还是那个问题`bite-wise` 的学习。

**CIN**

> 1. `vector-wise` 的作为输入
> 2. 显示构建多为交叉
>
> formulate the output of field embedding as a matrix
>
> 计算公式只有一个：
>
> ![a](./imgs/xdeepfm6.png)
>
> ![a](./imgs/xdeepfm7.png)
>
> 可以将D理解为`cnn` 中的通道，每一次`feature map` 一个通道输出一个值，多个通道就输出了一个向量。
>
> 上c图，l层表示构建第l阶交叉，然后将所有构建的层都输出concate。
>
> 那么一层需要多少个参数呢？
>
> ![a](./imgs/xdeepfm8.png)

**CIN 和 DNN 组合**

> 沿用`DeepFM` 和 `Deep & Wide`  使用混合网络。`DIN` 和 `DNN` 二者互补，能够做到的事情
>
> * 低维交叉(`CIN`)高维交叉(`CIN` 和 `DNN`)
> * 显式交叉(`CIN`)隐式交叉(`DNN`)
>
> ![a](./imgs/xdeepfm9.png)
>
> 模型称为`xDeepFM` 但是文中开头作者是`xDeepFM` 主要是对`CIN`的改进，名字却称为是`xDeepFM` 那么它和`FM` 或者`DeepFM` 有什么联系呢？
>
> 如果将上图左侧的`CIN` 的深度以及`FeatureMap` 都变为1，那么左侧部分就 退化成了`FM`

---

在左CIN计算的时候：

```python
now_tensor = tf.split(cin_layers[-1], D * [1], 2)
dot_result_m = tf.matmul(split_tensor_0, now_tensor, transpose_b=True)

# 翻译哈使用个公式
x = tf.Variable([[[1,2,1,2,4,2,1],[2,1,3,4,1,3,4]],[[1,2,1,2,4,2,1],[2,1,3,4,1,3,4]]])
# [2, 2, 7]
field_size = 2
embedding_size = 7
nn_input=x
cin_layers = [nn_input]
cin_layers
```

输出

```
[<tf.Variable 'Variable:0' shape=(2, 2, 7) dtype=int32, numpy=
 array([[[1, 2, 1, 2, 4, 2, 1],
         [2, 1, 3, 4, 1, 3, 4]],
 
        [[1, 2, 1, 2, 4, 2, 1],
         [2, 1, 3, 4, 1, 3, 4]]], dtype=int32)>]
```

```python
split_tensor_0 = tf.split(nn_input, embedding_size * [1], 2)
split_tensor_0 #(2, 2, 1) * embedding_size  == (7, 2, 2, 1)
```

输出：

```
[<tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[1],
         [2]],
 
        [[1],
         [2]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[2],
         [1]],
 
        [[2],
         [1]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[1],
         [3]],
 
        [[1],
         [3]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[2],
         [4]],
 
        [[2],
         [4]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[4],
         [1]],
 
        [[4],
         [1]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[2],
         [3]],
 
        [[2],
         [3]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[1],
         [4]],
 
        [[1],
         [4]]], dtype=int32)>]
```

```shell
now_tensor = tf.split(cin_layers[-1], embedding_size * [1], 2)
now_tensor # (2, 2, 1) * embedding_size 7, 2, 2, 1
```

输出

```
[<tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[1],
         [2]],
 
        [[1],
         [2]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[2],
         [1]],
 
        [[2],
         [1]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[1],
         [3]],
 
        [[1],
         [3]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[2],
         [4]],
 
        [[2],
         [4]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[4],
         [1]],
 
        [[4],
         [1]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[2],
         [3]],
 
        [[2],
         [3]]], dtype=int32)>, <tf.Tensor: shape=(2, 2, 1), dtype=int32, numpy=
 array([[[1],
         [4]],
 
        [[1],
         [4]]], dtype=int32)>]
```

计算

```python
dot_result_m = tf.matmul(split_tensor_0, now_tensor, transpose_b=True)
dot_result_m # (7, 2, 2, 2)
```

输出

```
<tf.Tensor: shape=(7, 2, 2, 2), dtype=int32, numpy=
array([[[[ 1,  2],
         [ 2,  4]],

        [[ 1,  2],
         [ 2,  4]]],


       [[[ 4,  2],
         [ 2,  1]],

        [[ 4,  2],
         [ 2,  1]]],


       [[[ 1,  3],
         [ 3,  9]],

        [[ 1,  3],
         [ 3,  9]]],


       [[[ 4,  8],
         [ 8, 16]],

        [[ 4,  8],
         [ 8, 16]]],


       [[[16,  4],
         [ 4,  1]],

        [[16,  4],
         [ 4,  1]]],


       [[[ 4,  6],
         [ 6,  9]],

        [[ 4,  6],
         [ 6,  9]]],


       [[[ 1,  4],
         [ 4, 16]],

        [[ 1,  4],
         [ 4, 16]]]], dtype=int32)>
```

这里在计算向量的外乘的时候 做了一个比较巧妙的方式。做个比喻，原来有2条记录[[a,b].[c,d]]， 然后经过编码之后映射为：每一个值隐射为7维的向量。

```
[<tf.Variable 'Variable:0' shape=(2, 2, 7) dtype=int32, numpy=
 array([[[1, 2, 1, 2, 4, 2, 1],
         [2, 1, 3, 4, 1, 3, 4]],
 
        [[1, 2, 1, 2, 4, 2, 1],
         [2, 1, 3, 4, 1, 3, 4]]], dtype=int32)>]
```

然后经过split之后，在最内侧的维度，比如第一条记录 [[1],[2]]，1为原始记录中的第一个维度(a)隐射到向量之后的第一个值，2为原始记录中第二个维度(b)经过隐射到向量之后的第二个值。 还有第二 条记录[[1],[2]], 含义和第一条记录是一样的，然后对着两个对内侧的维度进行矩阵相乘(2 x 1) * (1,2) = (2 x 2) 于是就生成了矩阵[[1,2],[2,4]] 这里就完成公式(6) 中的括号内，

这里还提一点，因为按照隐变量将张量进行了split，然后在上述的最内侧维度相乘的时候是对应位置的隐变量向相乘，也就是说2个隐变量之间的相乘(vector-wise)， 而不是一个隐变量元素之间相乘(bite-wise)。