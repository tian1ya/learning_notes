#### Vector2vec 和深度学习框架keras 中Embedding layer 的区别

* **word2vec 学习的是什么**

> `word2vec` 用于预测一个词是否属于上下文，如`milk`这个词更有可能出现在 `the cat was drinking..`句子末尾，也就是我们期望`word2vec`学习到 **You shall know a word by the company it keeps**， 也就是一个词是由他的上下文决定的，如`cat`和 `milk`经常会成对出现，或者也经常会和 `house`或者`pet` ，而`dog`也会经常和 `house`或者`pet` 一起出现，所以`cat`和 `dog`是相似的，越是结论就是：
>
> **word2vec**学习到的词向量具有语义性
>
> **Remember that word2vec refers to a very specific network setup which tries to learn an embedding which captures the semantics of words.**
>
> 回忆下，`word2vec`的输入，都是一个词和它的上下文词作为正/负样本，参与训练

* Embedding layer 学习到什么

> Embedding 就是一层普通神经网络层(a Dense layer only without bias or activation)，训练的时候减小损失函数，没有捕捉到词的语义性，它的输入适中仅仅是一个类别特征值

而且`word2vec` 是自监督的训练方式，而`Embedding`的训练是有监督的。

所以二者最大的本质的不同在于

**学习出来的词向量是否具有语义性**



