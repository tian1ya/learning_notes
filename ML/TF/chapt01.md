```python
1. tf1.x 中首先要创建计算图
a_ph = tf.placeholder(tf.float32, name="variable_1")
a_pb = tf.placeholder(tf.float32, name="variable_2")

创建计算图的过程就类似于通过创建公式 c=a+b 的过程，仅仅是记录了公式计算步骤
并没有实际计算公式的数值结果，童谣运行使用的输出端子，并赋值 a_ph=1, a_pb=b

c_op = tf.add(a_ph, a_pb, name = "variable_c")

2. 运行计算图阶段, 创建运行环境
sess = tf.InteractiveSession()
init = tf.global_variables_initializer()
sess.run(init)

最后才能拿到计算结果
c_numpy = sess.run(c_op, feed_dict={a_ph:2, a_pb:4})

只是计算一个简单的计算，需要做很多其他的事情，这种先计算图，然后运行的编程方式成为符号式编程
"""

"""
使用 tf2.x的计算
a = tf.constant(2.0)
b = tf.constant(2.0)

c = a + b

这种计算方式称为是命令式编程，或者是动态图模式,调式方便，开发效率也高，但是运行效率不如静态图模式
TensorFlow 2 也支持通过 tf.function 将动态图优先模式的代码转化为静态图模式，实现 开发和运行效率的双赢
"""

"""
TF 等深度学习框架三大核心功能
1. GPU 加速计算
2. 自动梯度计算
3. 常用神经网络接口：
    除了提供底层的矩阵相乘，相加等数学计算函数，还内建了常用的神经网络运算函数，常用网络层，网络训练，模型保存加载，网络部署等


基本的维度变换操作函数包含了改变视图 reshape、插入新维度 expand_dims，删除维 度 squeeze、交换维度 
transpose、复制数据 tile 等函数。

x=tf.range(96) # 生成向量
x=tf.reshape(x,[2,4,4,3]) # 改变x的视图，获得4D张量，存储并未改变

改变张量的视图仅仅是改变了张量的理解方 式，并不需要改变张量的存储顺序，这在一定程度上是从计算效率考虑的，
大量数据的写 入操作会消耗较多的计算资源。由于存储时数据只有平坦结构，与数据的逻辑结构是分离的

从语法上来说，视图变换只需要满足新视图的元素总量与存储区域大小相等即可

增加维度：
    仅仅是改变数据的理解方式，因此它其实可以理解为改 变视图的一种特殊方式。
tf.expand_dims(x, axis)可在指定的 axis 轴前可以插入一个新的维度:
tf.expand_dims 的 axis 为正时，表示在当前维度之前插入一个新维度;为 负时，表示当前维度之后插入一个新的维度
tf.squeeze(x)，那么它会默认删除所有长度为 1 的维度

删除维度：
    tf.squeeze(x, axis)函数
    
改变视图、增删维度都不会影响张量的存储，有时需要直接调整的存储顺序，即交换 维度(Transpose)
通过交换维度操作，改变了张量的存储顺序，同时也改变了张量的视图。

tf.transpose(x, perm)函数完成维度交换操作，其中参数 perm 表示新维度的顺序 List。
考虑图片张量 shape 为[2,32,32,3]，“图片数量、行、列、通道 数”的维度索引分别为 0、1、2、3，
如果需要交换为[𝑏, 𝑐, h, ]格式，则新维度的排序为 “图片数量、通道数、行、列”，对应的索引号为[0,3,1,2]
通过 tf.transpose 完成维度交换后，张量的存储顺序已经改变，视图也 随之改变，后续的所有操作必须基于新的存续顺序和视图进行


tf.tile(x, multiples)函数完成数据在指定维度上的复制操作，multiples 分别指 定了每个维度上面的复制倍数，对应位置为 1 表明不复制，为 2 表明新长度为原来长度的 2 倍，即数据复制一份，以此类推
b = tf.expand_dims(b, axis=0)
b = tf.tile(b, multiples=[2,1]) 
multiples=[2,1] 表明了b有2个维度，第一个维度也就是axis=0，复制一次，第二个维度，也就是axis=1，不复制

tf.tile 会创建一个新的张量来保存复制后的张量，
由于复制操作涉及大 量数据的读写 IO 运算，计算代价相对较高

广播机制(或自动扩展机制)
    它是一种轻量级的张量复制手段，在逻 辑上扩展张量数据的形状，但是只会在需要时才会执行实际存储复制操作。
对于大部分场 景，Broadcasting 机制都能通过优化手段避免实际复制数据而完成逻辑运算，
从而相对于 tf.tile 函数，减少了大量计算代价。

对于用户来说，Broadcasting 和 tf.tile 复 制的最终效果是一样的，操作对用户透明，
但是 Broadcasting 机制节省了大量计算资源， 建议在运算过程中尽可能地利用 Broadcasting 机制提高计算效率。

操作符+在遇到 shape 不一致的 2 个张量时，会自动考虑将 2 个张量自动扩展到 一致的 shape，然后再调用 
tf.add 完成张量相加运算

tf.add, tf.subtract, tf.multiply, tf.divide
TensorFlow 已经重载了+、 − 、 ∗ 、/运算符，一般推荐直接使用运算符来完成 加、减、乘、除运算。
整除和余除也是常见的运算之一，分别通过//和%运算符实现

矩阵相乘：
    通过@运算符可以方便的实现矩阵相乘， 还可以通过 tf.matmul(a, b)函数实现
    
矩阵批相乘
    也就是张量𝑨和𝑩的维度数可以大于 2，当张量𝑨和𝑩维度数大 于 2 时，TensorFlow 会选择𝑨和𝑩的最后两个维度进行矩阵相乘，前面所有的维度都视作 Batch 维度。
    根据矩阵相乘的定义，𝑨和𝑩能够矩阵相乘的条件是，𝑨的倒数第一个维度长度(列)和𝑩 的倒数第二个维度长度(行)必须相等。
    比如张量 a shape:[4,3,28,32]可以与张量 b shape:[4,3,32,2]进行矩阵相乘
    
    a = tf.random.normal([4,3,28,32]) 
    b = tf.random.normal([4,3,32,2])
    a@b # shape=(4, 3, 28, 2)
    
    矩阵相乘函数同样支持自动 Broadcasting 机制
        a = tf.random.normal([4,28,32])
        b = tf.random.normal([32,16])
        tf.matmul(a,b) # shape=(4, 28, 16)
    上述运算自动将变量 b 扩展为公共 shape:[4,32,16]，再与变量 a 进行批量形式地矩阵相乘，
    得到结果的 shape 为[4,28,16]

合并与分割
    可以使用拼接(Concatenate)和堆叠(Stack)操作实现，拼接操作并不会产生新 的维度，仅在现有的维度上合并，
    而堆叠会创建新维度
    tf.concat(tensors, axis)     
    tensors: 保存了所有需要合并的张量 List
    axis 参数指定需要合并的维度索引
    a = tf.random.normal([4,35,8])
    b = tf.random.normal([6,35,8]) 
    tf.concat([a,b],axis=0) # shape=(10, 35, 8)
    
    a = tf.random.normal([10,35,4])
    b = tf.random.normal([10,35,4]) 
    tf.concat([a,b],axis=2) # shape=(10, 35, 8)
    拼接合并操作可以在任意的维度上进行，唯一的约束是非合并维度的 长度必须一致

分割
    合并操作的逆过程就是分割，将一个张量分拆为多个张量
     tf.split(x, num_or_size_splits, axis)
        x参数:待分割张量。
        num_or_size_splits参数:切割方案。当num_or_size_splits为单个数值时，
            如10，表 示等长切割为 10 份;当 num_or_size_splits 为 List 时，
            List 的每个元素表示每份的长 度，如[2,4,2,2]表示切割为 4 份，每份的长度依次是 2、4、2、2
        axis参数:指定分割的维度索引号。
        
最值、均值、和
    tf.reduce_max、tf.reduce_min、tf.reduce_mean、tf.reduce_sum 函数可以求解张量
    在某个维度上的最大、最小、均值、和，也可以求全局最大、最小、均值、和信息。  
    tf.reduce_max(x,axis=0), 第一个维度的最大值，当不指定 axis的时候就是 全局的最大值
    
填充
    tf.pad(x, paddings)
        参数 paddings 是包含了多个
        [Left Padding, Right Padding]的嵌套方案 List，如[[0,0], [2,1], [1,2]]表示第一个维度不填充，
        第二个维度左边(起始处)填充两个单元，右边(结束处)填充一个单元，第三个维度左边 填充一个单元，右边填充两个单元
    
    b = tf.constant([7,8,1,6])
    b = tf.pad(b, [[0,2]]) # 句子末尾填充 2 个 0，array([7, 8, 1, 6, 0, 0])
    
    x = tf.random.normal([4,28,28,1])
    tf.pad(x,[[0,0],[2,2],[2,2],[0,0]]) # 填充效果查看截图
    
复制
    tf.tile 函数可以在任意维度将数据重复复制多份
    x = tf.random.normal([4,32,32,3])
    tf.tile(x,[2,3,3,1]) # 数据复制, 结果 shape=(8, 96, 96, 3)
  
高级操作
    tf.gather  
        实现根据索引号收集数据的目的
        4个班级，每个班级 35 个学生，8 门科目
        x = tf.random.uniform([4,35,8],maxval=100,dtype=tf.int32) # 成绩册张量
        现在需要收集第 1~2 个班级的成绩册
        tf.gather(x,[0,1],axis=0) # 在班级维度收集第 1~2 号班级成绩册
        
        如果希望抽查第[2,3]班级的第[3,4,6,27]号同学的科目 成绩，则可以通过组合多个 tf.gather 实现
        students=tf.gather(x,[1,2],axis=0) # 收集第 2,3 号班级 shape=(2, 35, 8)
        tf.gather(students,[2,3,5,26],axis=1) # 收集第 3,4,6,27 号同学 shape=(2, 4, 8)
        
        我们继续问题进一步复杂化。这次我们希望抽查第 2 个班级的第 2 个同学的所有科 目，
        第 3 个班级的第 3 个同学的所有科目，第 4 个班级的第 4 个同学的所有科目
        
    tf.gather_nd
        指定每次采样点的多维坐标来实现采样多个点的目 的
        tf.gather_nd(x,[[1,1],[2,2],[3,3]]) # shape=(3, 8)
    
    tf.boolean_mask
        可以通过给定掩码(Mask)的方式进行采样
        即采样第 1 和第 4 个班级的数据： mask = [True, False, False, True]
        tf.boolean_mask(x, mask, axis)可以在 axis 轴上根据 mask 方案进行采样
        tf.boolean_mask(x,mask=[True, False,False,True],axis=0) shape=(2, 35, 8)
        注意掩码的长度必须与对应维度的长度一致，如在班级维度上采样，则必须对这 4 个班级 是否采样的掩码全部指定，掩码长度为 4
        
        考虑与 tf.gather_nd 类似方式的多维掩码采样方式
    
        x: shape=(4, 8)
        tf.boolean_mask(x,[[True,True,False],[False,True,True]])
           
    tf.where
        tf.where(cond, a, b) cond==True ? a : b
        a = tf.ones([3,3]) # 构造 a 为全 1 矩阵
        b = tf.zeros([3,3]) # 构造 b 为全 0 矩阵
        cond = tf.constant([[True,False,False],[False,True,False],[True,True,False]])
        tf.where(cond,a,b) # 根据条件从 a,b 中采样
        分别按照cond中每一个元素的True或者False 然后返回a中或者b中的元素
        tf.where(cond)形式来获得这些元素的索引坐标
        
    一个综合实例
        需要提取张量中所有正数的数据和索引
        x = tf.random.normal([3,3]) # 构造 a
        mask=x>0
        indices=tf.where(mask) # 提取所有大于 0 的元素索引
        tf.gather_nd(x,indices) # 提取正数的元素值


tf.data.Dataset： 
    数据集对象，方便实现多线程(Multi-threading)、预 处理(Preprocessing)、随机打散(Shuffle)和批训练(Training on Batch)等常用数据集的功能。
    数据加载进入内存后，需要转换成 Dataset 对象，才能利用 TensorFlow 提供的各种便 捷功能
    Dataset.from_tensor_slices 可以将训练部分的数据图片 x 和标签 y 都转换成 Dataset 对象
        train_db = tf.data.Dataset.from_tensor_slices((x, y)) # 构建 Dataset 对象
   
    Dataset.shuffle(buffer_size)工具可以设置 Dataset 对象随机打散数据之间的顺序
        train_db = train_db.shuffle(10000) # 随机打散样本，不会打乱样本与标签映射关系
        buffer_size 参数指定缓冲池的大小，将打散的数据放入到这个缓冲池中，然后从这个池子中取数据
    
    批训练
        一次能够从 Dataset 中产生 Batch Size 数量的样本，需要设置 Dataset 为批训练方式
        train_db = train_db.batch(128)
        
    预处理
        
    循环训练
        for step, (x,y) in enumerate(train_db): # 迭代数据集对象，带 step 参数
        或者：for x,y in train_db: # 迭代数据集对象
        每次返回的 x 和 y 对象即为批量样本和标签。当对 train_db 的所有样本完 成一次迭代后，for 循环终止退出
        
        这里使用的for 迭代，迭代完数据后退出for(每次for loop 返回batch_size 个数据)
        也可以设置一个全量数据中设置多少个for loop
        train_db = train_db.repeat(20) # 数据集迭代 20 遍才终止
        
        
---
```



`Keras 模块化的全连接层`

```python
from tensorflow.keras import layers # 导入层模块
fc = layers.Dense(512, activation=tf.nn.relu)
h1 = fc(x) # 通过 fc 类实例完成一次全连接层的计算，返回输出张量 调用类的__call__方法即可
fc.kernel # 获取 Dense 类的权值矩阵
fc.bias # 获取 Dense 类的偏置向量

# fc.trainable_variables 返回待优化的参数列表
# fc.variables 返回所有参数列表
```

`张量的方式实现多层升级网络`

```python
# 隐藏层1张量
w1 = tf.Variable(tf.random.truncated_normal([784, 256], stddev=0.1))
b1 = tf.Variable(tf.zeros([256]))
# 隐藏层2张量
w2 = tf.Variable(tf.random.truncated_normal([256, 128], stddev=0.1)) b2 = tf.Variable(tf.zeros([128]))
# 隐藏层3张量
w3 = tf.Variable(tf.random.truncated_normal([128, 64], stddev=0.1)) b3 = tf.Variable(tf.zeros([64]))
# 输出层张量
w4 = tf.Variable(tf.random.truncated_normal([64, 10], stddev=0.1))
b4 = tf.Variable(tf.zeros([10]))
```

`计算时，只需要按照网络层的顺序，将上一层的输出作为当前层的输入即可，重复 直至最后一层，并将输出层的输出作为网络的输出`

```python
with tf.GradientTape() as tape: # 梯度记录器
  # x: [b, 28*28]
	# 隐藏层 1 前向计算，[b, 28*28] => [b, 256]
	h1 = x@w1 + tf.broadcast_to(b1, [x.shape[0], 256]) h1 = tf.nn.relu(h1)
	# 隐藏层 2 前向计算，[b, 256] => [b, 128]
	h2 = h1@w2 + b2
	h2 = tf.nn.relu(h2)
	# 隐藏层 3 前向计算，[b, 128] => [b, 64] h3 = h2@w3 + b3
	h3 = tf.nn.relu(h3)
	# 输出层前向计算，[b, 64] => [b, 10] h4 = h3@w4 + b4
```

`在使用Tensorflow 自动 求导功能计算梯度时，需要将前向计算过程放置在  tf.GradientTape() 环境中，从而利用GradientTape 对象的 gradient 方法自动求解参数的梯度`

`使用Keras 序列层实现(只能 实现简单的常规的全连接层)`

```python
from tensorflow.keras import layers,Sequential
fc1 = layers.Dense(256, activation=tf.nn.relu) # 隐藏层1 
fc2 = layers.Dense(128, activation=tf.nn.relu) # 隐藏层2
fc3 = layers.Dense(64, activation=tf.nn.relu) # 隐藏层3 
fc4 = layers.Dense(10, activation=None) # 输出层
x = tf.random.normal([4,28*28]) h1 = fc1(x) # 通过隐藏层 1 得到输出 
h2 = fc2(h1) # 通过隐藏层 2 得到输出
h3 = fc3(h2) # 通过隐藏层 3 得到输出 
h4 = fc4(h3) # 通过输出层得到网络输出
```

`或者`

```python
model = Sequential([
		layers.Dense(256, activation=tf.nn.relu) , # 创建隐藏层 1
  	layers.Dense(128, activation=tf.nn.relu) , # 创建隐藏层 2 
  	layers.Dense(64, activation=tf.nn.relu) , # 创建隐藏层 3
		layers.Dense(10, activation=None) , # 创建输出层 
])

out = model(x) # 前向计算得到输出
```

`实现为一个自定义网络类，只需要在初始化函数中创建各个子网络层，并 在前向计算函数 call 中实现自定义网络类的计算逻辑即可。自定义网络类继承自 keras.Model 基类，这也是自定义网络类的标准写法，以方便地利用 keras.Model 基类提供 的 trainable_variables、save_weights 等各种便捷功能`

```python
class Network(keras.Model): 
  # 回归网络模型
	def __init__(self):
			super(Network, self).__init__()
			# 创建3个全连接层
			self.fc1 = layers.Dense(64, activation='relu')
  	  self.fc2 = layers.Dense(64, activation='relu')
    	self.fc3 = layers.Dense(1)
    
  def call(self, inputs, training=None, mask=None):
    	x = self.fc1(inputs)
			x = self.fc2(x)
			x = self.fc3(x)
			return x
    
    
# 构建Dataset 对象
train_db = tf.data.Dataset.from_tensor_slices((normed_train_data.values,
train_labels.values)) # 构建 Dataset 对象
train_db = train_db.shuffle(100).batch(32) # 随机打散，批量化

model = Network() # 创建网络类实例
# 通过 build 函数完成内部张量的创建，其中 4 为任意设置的 batch 数量，9 为输入特征长度
model.build(input_shape=(4, 9))
model.summary() # 打印网络信息
optimizer = tf.keras.optimizers.RMSprop(0.001) # 创建优化器，指定学习率

for epoch in range(200): # 200个Epoch
	for step, (x,y) in enumerate(train_db): # 遍历一次训练集
			# 梯度记录器，训练时需要使用它
			with tf.GradientTape() as tape:
			out = model(x) # 通过网络获得输出
			loss = tf.reduce_mean(losses.MSE(y, out)) # 计算 
      MSE mae_loss = tf.reduce_mean(losses.MAE(y, out)) # 计算 MAE
			if step % 10 == 0: 
        # 间隔性地打印训练误差 
        print(epoch, step, float(loss))
			
      # 计算梯度，并更新
			grads = tape.gradient(loss, model.trainable_variables)
			optimizer.apply_gradients(zip(grads, model.trainable_variables))
```



`自动求导的使用` **这里注意 非 variable 变量自动求导的使用**

```python
import tensorflow as tf
# 构建待优化变量
x = tf.constant(1.)
w1 = tf.constant(2.)
b1 = tf.constant(1.)
w2 = tf.constant(2.)
b2 = tf.constant(1.)
# 构建梯度记录器
with tf.GradientTape(persistent=True) as tape:
  # 非 tf.Variable 类型的张量需要人为设置记录梯度信息 
  tape.watch([w1, b1, w2, b2])
  # 构建2层线性网络 
  y1 = x * w1 + b1 
  y2 = y1 * w2 + b2
  
  
dy2_dy1 = tape.gradient(y2, [y1])[0] 
dy1_dw1 = tape.gradient(y1, [w1])[0] 
dy2_dw1 = tape.gradient(y2, [w1])[0]

# 验证链式法则，2 个输出应相等
print(dy2_dy1 * dy1_dw1)
print(dy2_dw1)
```

---

**Keras 高层接口**

`keras 是一个高度模块化和易扩展的高层神经网络接口，使得用户可以不需要过多的专业知识就可以简洁，快速的完成模型的搭建和训练，在一开始的设计 中 keras 被设计为前端和后端部分，前段就是这里他提到的高层神经网络接口，而而后端就是以TF、CNTK 等的底层实现，在TF2.x 之后Keras 和 TF 二者融合，并且Keras 作为TF高层模块的唯一API，取代TF原来的tf.layers`



`2 个特殊的类 keras.Model 和 keras.layer.Layer  Layer 类是网络层的母类，定义了网络层的一些常见功能，如添加权值、管理权值列表等。 Model 类是网络的母类，除了具有 Layer 类的功能，还添加了保存模型、加载模型、训练 与测试模型等便捷功能。Sequential 也是 Model 的子类，因此具有 Model 类的所有功能`

**自定义Layer**

`至少实现 __init__ 方法和 call 方法`

```python
class MyDense(layers.Layer): # 自定义网络层
		def __init__(self, inp_dim, outp_dim):
				super(MyDense, self).__init__()
				# 创建权值张量并添加到类管理列表中，设置为需要优化
        # trainable=True 命名为w 的权重会被 trainable_variables 管理
        # 如果 trainable=False 则不会
				self.kernel = self.add_variable('w', [inp_dim, outp_dim], trainable=True)

    # 实现自定义类的前向计算逻辑    
		def call(self, inputs, training=None):
        # training 设置layer 状态True 那么权重会被训练 
        # training 为 False 时执行测试模式，默认参数为 None，即测试模式
      	out = inputs @ self.kernel
        out = tf.nn.relu(out)
        return out
```

**自定义网络类**

```python
class MyModel(keras.Model):
  	# 自定义网络类，继承自 Model 基类
    def __init__(self):
				super(MyModel, self).__init__() # 完成网络内需要的网络层的创建工作 
        self.fc1 = MyDense(28*28, 256) 
        self.fc2 = MyDense(256, 128) 
        self.fc3 = MyDense(128, 64)
				self.fc4 = MyDense(64, 32)
				self.fc5 = MyDense(32, 10)
        
    # 网络的前向运算逻辑
    def call(self, inputs, training=None):
      	x = self.fc1(inputs)
				x = self.fc2(x)
				x = self.fc3(x)
				x = self.fc4(x)
				x = self.fc5(x)
				return x
```

`对于常用的网络模型，如 ResNet、VGG 等，不需要手动创建网络，可以直接从 keras.applications 子模块中通过一行代码即可创建并使用这些经典模型，同时还可以通过设 置 weights 参数加载预训练的网络参数，非常方便。`



**可是化**

`TensorBoard 是需要和模型代码和浏览器相互配合`

`在模型端，首先需要写入监控数据的Summary 类，并在需要的时候写入监控数据`

```python
# 创建监控类，监控数据将写入 log_dir 目录
summary_writer = tf.summary.create_file_writer(log_dir)
```

`在前向计算完 成后，对于误差这种标量数据，我们通过 tf.summary.scalar 函数记录监控数据，并指定时 间戳 step 参数`

```python
with summary_writer.as_default(): # 写入环境
		# 当前时间戳 step 上的数据为 loss，写入到名为 train-loss 数据库中
   tf.summary.scalar('train-loss', float(loss), step=step)
```

`对于图片类型的数据，可以通过 tf.summary.image 函数写入监控图片数据`

```python
with summary_writer.as_default():# 写入环境
	# 写入测试准确率
	tf.summary.scalar('test-acc', float(total_correct/total),step=step)
	# 可视化测试用的图片，设置最多可视化 9 张图片
  tf.summary.image("val-onebyone-images:", val_images, max_outputs=9, step=step)
```

在模型中将数据写到磁盘中之后，借助`Web 浏览器` 可视化，然后使用命令

`tensorboard --logdir path` 然后根据打印出来的info，打开对于的连接可视化。

TensorBoard 还支持通过 tf.summary.histogram 查看

张量数据的直方图分布，以及通过 tf.summary.text 打印文本信息等功能

```python
with summary_writer.as_default():
		# 当前时间戳 step 上的数据为 loss，写入到 ID 位 train-loss 对象中
		tf.summary.scalar('train-loss', float(loss), step=step) 
    # 可视化真实标签的直方图分布 		
    tf.summary.histogram('y-hist',y, step=step)
		# 查看文本信息
		tf.summary.text('loss-text',str(float(loss)))
```







