* FM

**背景**

> `CTR` 预估中交叉特征是非常关键的，而使用`LR` 构建交叉特征的时候会非常的不适合。
>
> 类别特征经过`one-hot` 编码之后会变的非常稀疏，而在稀疏特征之上构建交叉特征：
>
> * 训练样本不足，参数难以学习到
>
> ![aa](./pic/fm.png)
>
> 如上 式子，学习交叉特征的权重w，由于 x的稀疏性，w 学习值。
>
> 而且需要引入 n^2/2 个参数需要训练，训练需要很多样本，而现有的样本右是比较稀疏的，满徐xi和xj都是非0的样本比较少，训练样本不足。观测权重wij，其实一个对称矩阵wij = wji,而且是稀疏的，因为绝大部分的组合特征都是无用的，其系数应该为0，对wij 进行矩阵分解。
>
> ![aa](./pic/fm1.png)
>
> 

* 代码实现

**将数据集进行转转换**

```python
def build_filed_dict(self):
    for col in self.df.columns:
        if col in self.cat_columns:
            c_uniue_v = self.df[col].unique()
            self.field_dict[col] = dict(zip(c_uniue_v, 
                    range(self.feature_nums, self.feature_nums + len(c_uniue_v))))
            self.feature_nums += len(c_uniue_v)

        else:
            self.field_dict[col] = self.feature_nums
            self.feature_nums += 1
            
def transform_data(self, file_path, label=None):
    df_v = pd.read_csv(file_path)
    if label:
        if label in df_v.columns:
            label = df_v[[label]].values.astype('float32')

    df_v = df_v[self.cat_columns + self.continuation_columns]
    df_v[self.cat_columns].fillna("-1", inplace=True)
    df_v[self.continuation_columns].fillna(-999, inplace=True)

    df_i = df_v.copy()
    for col in df_v.columns:
        if col in self.cat_columns:
            df_i[col] = df_i[col].map(self.field_dict[col])
            df_v[col] = 1.0    
        else:
            df_i[col] = self.field_dict[col]
    features = {
        'df_i': df_i.values.astype("int32"),
        'df_v': df_v.values.astype("float32")
    }

    return features, label
```

**FM 计算**

```python
def _line_result(self, df_i, df_v):
    # feature_size * 1
    self.line_weigths = tf.Variable(tf.random.normal([self.feature_nums,1], 0.0, 0.01),
                          name="feature_embeddings")
    # None * feature_size  
    self.line_bias = tf.Variable(tf.zeros([1,1]))
    batch_weight = tf.nn.embedding_lookup(self.line_weigths, df_i) #None * 6 * 1
    batch_weight = tf.squeeze(batch_weight, axis=2) # None * 6 
    line_result = tf.multiply(batch_weight, df_v) # #None * 6 
    a = tf.reduce_sum(line_result, axis=1,keepdims=True) # None * 1
    return tf.add(self.line_bias, a)

def _fm_result(self, df_i, df_v):
    # feature_nums * embedding_size
    # 每一个unique cat value 都有一个 embedding_size 维的向量，每一列数值特征有一
    # embedding_size 维的向量
    self.fm_embedding = tf.Variable(
        tf.random.normal([self.feature_nums, self.embedding_size],0.0,0.01,),
        name="embeddings")

    # None * feature_nums * embedding_size  (32, 6, 3)
    batch_embedding = tf.nn.embedding_lookup(self.fm_embedding, df_i)

    # (32, 6, 1)
    df_v = tf.expand_dims(df_v, axis=2)

    # None * feature_nums * embedding_size  (32, 6, 3)
    self.xv = tf.multiply(batch_embedding, df_v)

    # None * embedding_size (32, 3)
    sum_square = tf.square(tf.reduce_sum(self.xv,axis=1))
    # None * embedding_size 
    square_sum = tf.reduce_sum(tf.square(self.xv), axis=1)
    # None * embedding_size
    fm_result = 0.5 * tf.subtract(sum_square, square_sum)
    return tf.reduce_sum(fm_result, axis=1, keepdims=True) # (32, 1)
```

**FM 主要思想**：解决稀疏数据下的特征组合问题

> 将表示交叉关系的权重值，投射到embedding_size 维的向量空间中，以前表示特征a和b的权重wij，变成了向量内积 vi * vj，是通过多个维度去表示的(a和b的关系好不好不仅仅是由a个 b说了算，还通过和a和b相关的c、d、e等说了算 )。就好比是word2vector，一个词是由这个词的上下文表示的，这样学习的向量参数具有更强的泛化能力。
>
> `LR` 一个N 维度的 sample 学习到N维度的权重向量，而`FM` 中学习到N * embedding_size 的矩阵。

---

**FFM**：`FM` 的基础之上增加了域的信息。`FFM` 将相同性质的属性归到一个域中，可以理解`FM` 是 `FFM` 的一种特殊情况，在`FM`中稀疏化的特征中xi和xj 的特征交叉是右向量vi和vj得到的，而在学习vi和vj 的时候是将所有数据都同等考虑去学习的，而`FFM` 中vi 和 vj 的交叉特征是通过矩阵vif(j) 和 vjf(i) 计算得到，也就是在学习这个矩阵的时候没一个域下边学习了一个分量。

https://tech.meituan.com/2016/03/03/deep-understanding-of-ffm-principles-and-practices.html

`FFM` 的作者认为特征a 和 特征 b的交叉关系不仅仅可以由和和a相关的b、c、d 特征决定的，而且所决定的粒度是不一样的(有点集成学的思想)。

`FFM` 是如何做组合的。

![aa](./pic/ffm.png)

如上式子隐矩阵vif(j) ：表示向量xi和向量xj所在的域的隐向量。FFM 的二次项不能化简，复杂度O(k

n^2)比`fm O(kn)` 高.

![aa](./pic/ffm2.png)

![aa](./pic/ffm3.png)

* 此处应该有代码

```python
class FFM(object):
def __init__(self, 
             feature_nums, 
             field_nums,
             embedding_size):

    self.feature_nums = feature_nums
    self.embedding_size = embedding_size
    self.field_nums = field_nums

def line_section(self, df_i, df_v):
    self.weights = tf.Variable(tf.random.normal([self.feature_nums,1], 
                                           stddev=0.01))

    self.bias = tf.Variable(tf.zeros([1,1]))
    # None * feature_nums * 1
    batch_weights = tf.nn.embedding_lookup(weights, df_i) 

    # None * feature_nums
    batch_weights = tf.squeeze(batch_weights, aixs=2)

    # None * feature_nums
    line_result = tf.multiply(df_v, batch_weights)

    # None * 1
    return tf.add(tf.reduce_sum(batch_weights, axis=1, keepdims=True), self.bias)

def ffm_fection(self, df_i, df_v):
    self.embeddings = tf.Variable(
        # field, feature, embedding
        # 没一个field 下面有全部的 特征值，也就是每个field中的特征值在当前field中的向量分量
        tf.random.normal([self.field_nums, self.feature_nums, self.embedding_size]))

    ffm_result = None;
    for i in range(self.field_nums):
        for j in range(i+1, self.field_nums):
            # None * embedding_size
            vi_fj = tf.nn.embedding_lookup(self.embeddings[j], df_i[:,i])
            vj_fi = tf.nn.embedding_lookup(self.embeddings[i], df_i[:,j])

            wij = tf.multiply(vi_fj, vj_fi)

            # None * 1
            x_i = tf.expand_dims(df_v[:,i], 1)
            x_j = tf.expand_dims(df_v[:,i], 1)

            xij = tf.multiply(x_i, x_j)
            if ffm_result is None:
                # tf.multiply(wij,xij) None * embedding_size
                # ffm_result : None * 1
                ffm_result = tf.reduce_sum(tf.multiply(wij,xij), aixs=1, keepdims=True)
            else:
                ffm_result += tf.reduce_sum(tf.multiply(wij,xij), aixs=1, keepdims=True)

    return ffm_result
```

* `FFM` 数据格式

> 为了使用FFM方法，所有的特征必须转换成“field_id:feat_id:value”格式，field_id代表特征所属field的编号，feat_id是特征编号，value是特征的值。数值型的特征比较容易处理，只需分配单独的field编号，如用户评论得分、商品的历史CTR/CVR等。categorical特征需要经过One-Hot编码成数值型，编码产生的所有特征同属于一个field，而特征的值只能是0或1，如用户的性别、年龄段，商品的品类id等。



