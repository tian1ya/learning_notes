---
typora-root-url: Png
---

[TOC]

## RS 与 RC 与 Deployment 关联

**RC （ReplicationController ）主要的作用就是用来确保容器应用的副本数始终保持在用户定义的副本数 。即如果有容器异常退出，会自动创建新的Pod来替代；而如果异常多出来的容器也会自动回收** 

**Kubernetes 官方建议使用 RS（ReplicaSet ） 替代 RC （ReplicationController ） 进行部署，RS 跟 RC 没有本质的不同，只是名字不一样，并且 RS 支持集合式的 selector**



### RC 控制器

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: php-redis
        image: wangyanglinux/myapp:v1
        env:
        - name: GET_HOSTS_FROM
          value: dns
          name: zhangsan
          value: "123"
        ports:
        - containerPort: 80
```



### RS 控制器

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - name: myapp
        image: wangyanglinux/myapp:v1
        env:
        - name: GET_HOSTS_FROM
          value: dns
        ports:
        - containerPort: 80
```



#### selector.matchExpressions

rs 在标签选择器上，除了可以定义键值对的选择形式，还支持 matchExpressions 字段，可以提供多种选择。
目前支持的操作包括：

- In：label 的值在某个列表中
- NotIn：label 的值不在某个列表中
- Exists：某个 label 存在
- DoesNotExist：某个 label 不存在

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-demo
spec:
  selector:
    matchExpressions:
      - key: app
        operator: Exists
  template:
    metadata:
      labels:
        app: spring-k8s
    spec:
      containers:
        - name: rs-c1
          image: wangyanglinux/myapp:v1
          ports:
            - containerPort: 80
```

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-demo
spec:
  selector:
    matchExpressions:
      - key: app
        operator: In
        values:
        - spring-k8s
        - hahahah
  template:
    metadata:
      labels:
        app: sg-k8s
    spec:
      containers:
        - name: rs-c1
          image: wangyanglinux/myapp:v1
          ports:
            - containerPort: 80
```



## RS 与 Deployment  的关联

[![T2PZIH.png](https://s4.ax1x.com/2021/12/29/T2PZIH.png)](https://imgtu.com/i/T2PZIH)



## Deployment 

**Deployment 为 Pod 和 ReplicaSet 提供了一个声明式定义(declarative)方法，用来替代以前的ReplicationController 来方便的管理应用。典型的应用场景包括：** 

- **定义Deployment来创建Pod和ReplicaSet**
- **滚动升级和回滚应用**
- **扩容和缩容**
- **暂停和继续Deployment**



**Ⅰ、部署一个简单的 Nginx 应用**

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: wangyanglinux/myapp:v1
        ports:
        - containerPort: 80
```

```shell
kubectl create -f https://kubernetes.io/docs/user-guide/nginx-deployment.yaml --record
## --record参数可以记录命令，我们可以很方便的查看每次 revision 的变化
```

**Ⅱ、扩容**

```shel
kubectl scale deployment nginx-deployment --replicas 10
```

**Ⅲ、如果集群支持 horizontal pod autoscaling 的话，还可以为Deployment设置自动扩展**

```shell
kubectl autoscale deployment nginx-deployment --min=10 --max=15 --cpu-percent=80
```

 **Ⅳ、更新镜像也比较简单** 

```shel
kubectl set image deployment/nginx-deployment nginx=nginx:1.9.1
```

**Ⅴ、回滚** 

```she
kubectl rollout undo deployment/nginx-deployment
```



## 更新 Deployment

<!--注意： Deployment 的 rollout 当且仅当 Deployment 的 pod template（例如.spec.template）中的label更新或者镜像更改时被触发。其他更新，例如扩容Deployment不会触发 rollout-->

**假如我们现在想要让 nginx pod 使用`nginx:1.9.1`的镜像来代替原来的`nginx:1.7.9`的镜像**

```she
$ kubectl set image deployment/nginx-deployment nginx=nginx:1.9.1
deployment "nginx-deployment" image updated
```

**可以使用`edit`命令来编辑 Deployment** 

```
$ kubectl edit deployment/nginx-deployment
deployment "nginx-deployment" edited
```

**查看 rollout 的状态**

```shell
$ kubectl rollout status deployment/nginx-deployment
Waiting for rollout to finish: 2 out of 3 new replicas have been updated...
deployment "nginx-deployment" successfully rolled out
```

**查看历史 RS**

```shell
$ kubectl get rs
NAME                          DESIRED   CURRENT   READY   AGE
nginx-deployment-1564180365   3         3         0       6s
nginx-deployment-2035384211   0         0         0       36s
```



## Deployment 更新策略

**Deployment 可以保证在升级时只有一定数量的 Pod 是 down 的。默认的，它会确保至少有比期望的Pod数量少一个是up状态（最多一个不可用）** 

**Deployment 同时也可以确保只创建出超过期望数量的一定数量的 Pod。默认的，它会确保最多比期望的Pod数量多一个的 Pod 是 up 的（最多1个 surge ）** 

**未来的 Kuberentes 版本中，将从1-1变成25%-25%** 

```
$ kubectl describe deployments
```



### 更新策略声明

kubectl explain deploy.spec.strategy.type

- Recreate 
- rollingUpdate
  - maxSurge：指定超出副本数有几个，两种方式：1、指定数量 2、百分比
  - maxUnavailable ： 最多有几个不可用

```json
kubectl patch deployment  nginx-deployment -p '{"spec":{"strategy":{"rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}'
```



### 金丝雀部署

```shell
$ kubectl set image deploy  nginx-deployment nginx=wangyanglinux/myapp:v2 && kubectl rollout pause deploy  nginx-deployment

$ kubectl rollout resume deploy  nginx-deployment
```







## Rollover（多个rollout并行）

**假如您创建了一个有5个`niginx:1.7.9` replica的 Deployment，但是当还只有3个`nginx:1.7.9`的 replica 创建出来的时候您就开始更新含有5个`nginx:1.9.1` replica 的 Deployment。在这种情况下，Deployment 会立即杀掉已创建的3个`nginx:1.7.9`的 Pod，并开始创建`nginx:1.9.1`的 Pod。它不会等到所有的5个`nginx:1.7.9`的 Pod 都创建完成后才开始改变航道** 



## 回退 Deployment

<!--只要 Deployment 的 rollout 被触发就会创建一个 revision。也就是说当且仅当 Deployment 的 Pod template（如`.spec.template`）被更改，例如更新template 中的 label 和容器镜像时，就会创建出一个新的 revision。其他的更新，比如扩容 Deployment 不会创建 revision——因此我们可以很方便的手动或者自动扩容。这意味着当您回退到历史 revision 时，只有 Deployment 中的 Pod template 部分才会回退-->

```shell
kubectl set image deployment/nginx-deployment nginx=nginx:1.91
kubectl rollout status deployments nginx-deployment
kubectl get pods
kubectl rollout history deployment/nginx-deployment
kubectl rollout undo deployment/nginx-deployment
kubectl rollout undo deployment/nginx-deployment --to-revision=2   ## 可以使用 --revision参数指定某个历史版本
kubectl rollout pause deployment/nginx-deployment    ## 暂停 deployment 的更新
```

**您可以用`kubectl rollout status`命令查看 Deployment 是否完成。如果 rollout 成功完成，`kubectl rollout status`将返回一个0值的 Exit Code** 

```shell
$ kubectl rollout status deploy/nginx
Waiting for rollout to finish: 2 of 3 updated replicas are available...
deployment "nginx" successfully rolled out
$ echo $?
0
```



## 清理 Policy

**您可以通过设置`.spec.revisonHistoryLimit`项来指定 deployment 最多保留多少 revision 历史记录。默认的会保留所有的 revision；如果将该项设置为0，Deployment 就不允许回退了**



