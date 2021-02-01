卷积神经网络利用数据的局部相关性和权值共享的思想大大减少了网络的参数量，非 常适合于图片这种具有空间(Spatial)局部相关性的数据，已经被成功地应用到计算机视觉领 域的一系列任务上。自然界的信号除了具有空间维度之外，还有一个时间(Temporal)维度。 具有时间维度的信号非常常见，比如我们正在阅读的文本、说话时发出的语音信号、随着 时间变化的股市参数等。这类数据并不一定具有局部相关性，同时数据在时间维度上的长 度也是可变的，卷积神经网络并不擅长处理此类数据。
