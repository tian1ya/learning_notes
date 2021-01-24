当  pod 奔溃后重启，会以干净 的状态重启，意味着之前数据的丢失，同时一个Pod 中运行的多个容器，这些容器 需要共享文件。`volume` 刚好就解决了这个问题 。

---

#### 卷类型 

 k8s 支持很多的卷类型，这里举几个经常使用的卷。

##### emptyDir

> 挂载在  `Node` 的介质上(介质可以是磁盘或 SSD 或网络存储)，被创建的时候是空的，当`Pod` 被删除之后 `emptyDir` 就会被永久的删除，容器崩溃并不会导致 `pod`  的删除，所以 `emptyDir` 还是存在的
>
> 用途：
>
> - 缓存空间，例如基于磁盘的归并排序。
> - 为耗时较长的计算任务提供检查点，以便任务能方便地从崩溃前状态恢复执行。
> - 在 Web 服务器容器服务数据时，保存内容管理器容器获取的文件。

```yaml
apiVersion: v1
kind: Pod
metadata:
	name: test-pd
spec:
	containers:
		- image: spring2go/spring-petclinic
			name: test-volume
			volumeMounts:
				- mountPath: /cache # 挂载容器的目录
					name: cache-volume
	volumes:
		- name: cache-volume
			emptyDir: {}
```

##### hostPath

> 卷能将主机节点文件系统上的文件或目录挂载到你的 Pod 中。 

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - image: k8s.gcr.io/test-webserver
    name: test-container
    volumeMounts:
    - mountPath: /test-pd
      name: test-volume
  volumes:
  - name: test-volume
    hostPath:
      # 宿主上目录位置
      path: /data
      # 此字段为可选
      type: Directory
```

