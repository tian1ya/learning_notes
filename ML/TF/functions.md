* SpatialDropout1D

  ```python
  ary = np.arange(35.0).reshape((1, 7, 5)) 
  imput = tf.Variable(ary)
  print(imput)
  
  input_shape = tf.shape(imput)
  
  noise_shape = (input_shape[0],1,input_shape[2])
  a = tf.nn.dropout(imput, 0.5, noise_shape)
  print(a)
  ```

  ```
  <tf.Variable 'Variable:0' shape=(1, 7, 5) dtype=float64, numpy=
  array([[[ 0.,  1.,  2.,  3.,  4.],
          [ 5.,  6.,  7.,  8.,  9.],
          [10., 11., 12., 13., 14.],
          [15., 16., 17., 18., 19.],
          [20., 21., 22., 23., 24.],
          [25., 26., 27., 28., 29.],
          [30., 31., 32., 33., 34.]]])>
  tf.Tensor(
  [[[ 0.  2.  0.  6.  8.]
    [ 0. 12.  0. 16. 18.]
    [ 0. 22.  0. 26. 28.]
    [ 0. 32.  0. 36. 38.]
    [ 0. 42.  0. 46. 48.]
    [ 0. 52.  0. 56. 58.]
    [ 0. 62.  0. 66. 68.]]], shape=(1, 7, 5), dtype=float64)
  ```

  在第二个维度任意挑一列全部置0，然后对其他的元素 /0.5

  ```python
  ary[0,:,4]
  array([ 4.,  9., 14., 19., 24., 29., 34.])
  ```

  > noise_shape = (input_shape[0],1,input_shape[2]) 效果就是将值为1的拿了置为1，而在其他维度上必须使用tf.shape[n] 取出维度值，也就是 Tensor.，而将要置0 的那个维度使用实数1指出

  ```python
  ary = np.arange(35.0).reshape((1, 7, 5)) 
  imput = tf.Variable(ary)
  print(imput)
  
  input_shape = tf.shape(imput)
  
  noise_shape = (input_shape[0].numpy,1,input_shape[2].numpy)
  a = tf.nn.dropout(imput, 0.5, noise_shape)
  print(a)
  ```

  > 在这个例子中就可以说明，将noise_shape全部取实数，就运行错误
  >
  > ```
  > ValueError: Attempt to convert a value (<bound method _EagerTensorBase.numpy of <tf.Tensor: shape=(), dtype=int32, numpy=1>>) with an unsupported type (<class 'method'>) to a Tensor.
  > ```

  而`SpatialDropout1D`  就是给`dropout` noise_shape(Tensor(1),1,Tensor(2)) 的效果，

  `This version performs the same function as Dropout, however it drops entire 1D feature maps instead of individual elements.`

  同样还有 `SpatialDropout2D` 函数 `This version performs the same function as Dropout, however it drops entire 2D feature maps instead of individual elements`

* **Embedding** 方法中的 `mask_zero` 参数的使用

  先来一个比较普通的使用方式

  ```python
  import tensorflow as tf
  import numpy as np
  
  data_int = np.array([[1,2,0,0]])
  
  x = tf.keras.layers.Input(shape=(4,))
  e = tf.keras.layers.Embedding(5,5)(x)
  
  m = tf.keras.Model(inputs=x, outputs=e)
  p = m.predict(data_int)
  
  p.shape # (1, 4, 5)
  ```

  p 的输出

  ```numpy
  array([[[ 0.04345674, -0.02596427,  0.03457153, -0.03886087,0.00179408],
          [-0.04239723, -0.02314651,  0.02268988,  0.04586181,0.04670281],
          [ 0.024183  , -0.03745509,  0.04569806, -0.01675672,-0.00906407],
          [ 0.024183  , -0.03745509,  0.04569806, -0.01675672,-0.00906407]]], dtype=float32)
  ```

  而`Embedding`层的权重矩阵为：

  ```numpy
  [array([[ 0.024183  , -0.03745509,  0.04569806, -0.01675672, -0.00906407],
          [ 0.04345674, -0.02596427,  0.03457153, -0.03886087,  0.00179408],
          [-0.04239723, -0.02314651,  0.02268988,  0.04586181,  0.04670281],
          [-0.00444181,  0.0062336 , -0.04583638,  0.03504047, -0.03163216],
          [ 0.04218059, -0.02495784,  0.00560266,  0.00161899,  0.04371682]],
         dtype=float32)]
  ```

  所以在输入数据 `data_int`的时候，输入是按照行索引取到的值，也证明`Embedding` 是从行索引0开始取的值。

  现在在添加一个参数 `mask_zero=true`， 发送改动的代码：

  ```python
  x = tf.keras.layers.Input(shape=(4,))
  e = tf.keras.layers.Embedding(5,5, mask_zero=True)(x)
  ```

  这时候 p 的输出

  ```numpy
  array([[[-0.00410727,  0.00784992,  0.02696501, -0.02534198,-0.02118553],
          [-0.0423721 , -0.0113678 ,  0.02849133,  0.02704692,-0.04198414],
          [-0.03106972, -0.02895627,  0.039416  ,  0.0314062 ,-0.045304  ],
          [-0.03106972, -0.02895627,  0.039416  ,  0.0314062 ,-0.045304  ]]], dtype=float32)
  ```

  这个时候`Embedding` 层的

  ```numpy
  [array([[-0.03106972, -0.02895627,  0.039416  ,  0.0314062 , -0.045304  ],
          [-0.00410727,  0.00784992,  0.02696501, -0.02534198, -0.02118553],
          [-0.0423721 , -0.0113678 ,  0.02849133,  0.02704692, -0.04198414],
          [-0.00363597, -0.03117173,  0.04628457, -0.02881472, -0.00046559],
          [-0.04645482,  0.03606473, -0.02998245, -0.03561486, -0.04216773]],
         dtype=float32)]
  ```

  `data_int` 的从 `Embedding` 取值和上述的逻辑还是一样的。从取值的角度来看，这里 `mask_zero` 并不会对结果有影响，都会是从行索引0开始取行。

  但是如果对于序列模型，如`LSTM`等后面的输入会将前面的输入加入进来一起进行计算，这个时候`mask_zero=True` 就会发生影响。

  ```python
  x = tf.keras.layers.Input(shape=(4,))
  e = tf.keras.layers.Embedding(5,5, mask_zero=True)(x)
  rnn = tf.keras.layers.LSTM(3, return_sequences=True)(e)
  
  m = tf.keras.Model(inputs=x, outputs=rnn)
  p = m.predict(data_int)
  ```

  这时候 p 的输出

  ```python
  array([[[-0.00342235, -0.00257274, -0.00320503],
          [ 0.00693269, -0.00041692,  0.00547119],
          [ 0.00693269, -0.00041692,  0.00547119],
          [ 0.00693269, -0.00041692,  0.00547119]]], dtype=float32)
  ```

  这个时候`Embedding` 层的

  ```python
  [array([[-0.03106972, -0.02895627,  0.039416  ,  0.0314062 , -0.045304  ],
          [-0.00410727,  0.00784992,  0.02696501, -0.02534198, -0.02118553],
          [-0.0423721 , -0.0113678 ,  0.02849133,  0.02704692, -0.04198414],
          [-0.00363597, -0.03117173,  0.04628457, -0.02881472, -0.00046559],
          [-0.04645482,  0.03606473, -0.02998245, -0.03561486, -0.04216773]],
         dtype=float32)]
  ```

  根据 `p`的输出结果，当输入 `data_int` 的值为0 的部分，计算得到的结果和`data_int` 中值取2的时候是一样的，也就是说当 `mask_zero=Ture`的时候，输入值为0的部分序列将会被过滤掉不会参与到计算中来。

  需要注意的是这里的`data_int` 别认为是一列4行的数据(4个取值点)，而是一个 取值点，这个取值点是一个序列取值，这里取了4个时间点上的序列。

  也就是`mask_zero=True`的作用就是在计算一个序列的时候，当序列中有取值为0的时候，会忽略计算。

  [参考链接1](https://blog.csdn.net/songbinxu/article/details/80150019)

  [参考链接2](https://stackoverflow.com/questions/47485216/how-does-mask-zero-in-keras-embedding-layer-work)

  ---

  * **tensordot**

  > 在 `numpy`  中和 `Tensorflow` 中都有这个函数

  **Numpy**

  ```python
  import tensorflow as tf
  import numpy as np
  
  np.random.seed(10)
  A = np.random.randint(0,9,(3,4,5))
  B = np.random.randint(0,9,(4,5,2))
  
  np.tensordot(A, B, [(1,2), (0,1)])
  
  array([[233,  89],
         [250, 234],
         [199, 244]])
  
  np.sum(A[0]*B[:,:,0])
  233
  ```

  `tensordot` 中的函数参数 `[(1,2), (0,1)]`

  > (1,2) 是对A而言，不是取第1，2轴，而是除去1,2 轴，所以要取的是第0轴
  > (0,1) 是对B而言，不是取第0，1轴，而是除去0,1 轴，所以要取的是第2轴
  >
  > A的形状是(3,4,5)，第0轴上有3个元素，取法上面讲了；B的形状(4,5,2)，第2轴上有2个元素，所以结果形状是(3,2)
  >
  > Tensordot 的作用就是把取出的子数组做点乘操作，即是 np.sum(a*b) 操作。
  > 我们来验证一下，上述的说法看结果形状（3，2）的第一个元素：A第0轴上第一个元素与B第2轴上的第一个元素点乘。

  **Tensorflow**

  ```python
  tf.tensordot(
      a,
      b,
      axes,
      name=None
  )
  """
  Args:
      a:类型为float32或者float64的tensor
      b:和a有相同的type,即张量同类型,但不要求同维度
      axes:可以为int32,也可以是list,为int32,表示取a的最后几个维度,与b的前面几个维度相乘,再累加求和,消去（收缩）相乘维度
          为list,则是指定a的哪几个维度与b的哪几个维度相乘,消去（收缩）这些相乘的维度
      name:操作命名
  """
  ```

  ****

* **tf.sequence_mask()**

> ```python
> # 函数定义
> sequence_mask(
>     lengths,
>     maxlen=None,
>     dtype=tf.bool,
>     name=None
> )
> # 返回数据
> return mask类型数据
> ```
>
> 1.返回值`mask`张量：默认`mask`张量就是布尔格式的一种张量表达，只有**True**和 **False** 格式，也可以通过参数`dtype`指定其他数据格式。
>
> 2.参数`lengths`：顾名思义表示的是长度；可以是**标量**，也可以是**列表 [ ]** ，也可以是**二维列表[ [ ],[ ] ,…]**，甚至是**多维列表…**。一般列表类型的用的比较多
>
> 3.参数`maxlen`：当默认`None`，默认从`lengths`中获取最大的那个数字，决定返回`mask`张量的长度；当为N时，返回的是N长度。
>
> * 当参数lenghts是标量
>
> ```python
> import tensorflow as tf
> 
> lenght = 4 
> mask_data = tf.sequence_mask(lengths=lenght)
> # 输出结果,输出结果是长度为4的array，前四个True
> array([ True,  True,  True,  True])
> 
> # 定义maxlen时
> mask_data = tf.sequence_mask(lengths=lenght,maxlen=6)
> # 输出结果,输出结果是长度为6的array，前四个True
> array([ True,  True,  True,  True, False, False])
> 
> # 定义dtype时
> mask_data = tf.sequence_mask(lengths=lenght,maxlen=6,dtype=tf.float32)
> # 输出结果,输出结果是长度为6的array，前四个1.0
> array([1., 1., 1., 1., 0., 0.], dtype=float32)
> ```
>
> * 当参数lenghts是[ *list* ]，**这个形式的非常常用，主要是针对数据填充用的非常多**。比如我一个`batch_data`有10个数据，每个数据是一个句子，每个句子不可能是一样长的，肯定有短的需要填充**0**元素，那么`lengths`就专门记录每个句子的长度的。
>
> ```python
> # 比如这个lenght就是记录了第一个句子2个单词，第二个句子2个单词，第三个句子4个单词
> lenght = [2,2,4] 
> mask_data = tf.sequence_mask(lengths=lenght)
> # 长度为max(lenght)
> array([[ True,  True, False, False],
>        [ True,  True, False, False],
>        [ True,  True,  True,  True]])
> 
> # 定义maxlen时
> mask_data = tf.sequence_mask(lengths=lenght,maxlen=6)
> # 长度为maxlen
> array([[ True,  True, False, False, False, False],
>        [ True,  True, False, False, False, False],
>        [ True,  True,  True,  True, False, False]])
> 
> # 定义dtype时
> mask_data = tf.sequence_mask(lengths=lenght,maxlen=6,dtype=tf.float32)
> # 长度为maxlen，数据格式为float32
> array([[1., 1., 0., 0., 0., 0.],
>        [1., 1., 0., 0., 0., 0.],
>        [1., 1., 1., 1., 0., 0.]], dtype=float32)
> ```
>
> 注意输出的大小等于 [len(lenght),max(lenght)]
>
> * 当参数lenghts是[[ *list* ]…] **在NLP中用的比较少，我就举一个例子**
>
> ```python
> lenght = [[2,2,4],[3,4,5]]
> mask_data = tf.sequence_mask(lengths=lenght)
> # 输出
> array([[[ True,  True, False, False, False],
>         [ True,  True, False, False, False],
>         [ True,  True,  True,  True, False]],
> 
>        [[ True,  True,  True, False, False],
>         [ True,  True,  True,  True, False],
>         [ True,  True,  True,  True,  True]]])
> ```
>
> 