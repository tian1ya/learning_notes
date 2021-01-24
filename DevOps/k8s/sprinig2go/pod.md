```yaml
apiVersion: v1
kind: Pod
metadata:
  name: petclinic
spec:
  containers:
    - name: petclinic
      image: spring2go/spring-petclinic:1.0.0.RELEASE
      ports:
      - containerPort: 8080
        hostPort: 8080
```

启动

`kubectl apply -f pod-example.yaml`

查看

`kubectl get pods -o wide`

`kubectl describe pod petclinic`

上面的 `petclinic` 使用 `spring-boot` 默认 `8080` 端口，使用`http://localhost:8080/` 在本地机器直接访问，是访问不到的，在集群外是不能直接访问到 `pod` 的.

这里配置将 `Pod` 的端口隐射到物理主机的 `8080` 端口

我使用的是3台虚拟机的 `K8s` 集群，其中 `Pod` 是部署在了 `192.168.99.102` 机器，然后访问 `http://192.168.99.102:8080/` 就可以访问到主页了。

---

[k8s集群外部访问Pod或Service](https://blog.csdn.net/l1028386804/article/details/106847280)

`Pod` 或者是 `Service` 是虚拟的概念，所以在集群外侧是访问不到的，可以通过以下方法使得集群外部访问到 `pod` 里面

**将容器应用的端口号映射到物理机**

1. 通过设置容器级别的hostPort，将容器应用的端口号映射到物理机上

   就是上面 `yaml` 中配置的方法

2. 通过设置 `Pod` 级别的 `hostNetwork=true`， 改 `Pod` 中所有的容器的端口号都将直接映射到物理机器上，该设置需要注意在容器的 `ports` 定义部分，如果不指定 `hostPort`， 则默认等于 `containerPort`， 如果制定了`hostPort`，则 `hostPort`  必须等于 `containerPort` 的值。

---

[波波的博客](https://blog.csdn.net/yang75108/article/details/101101384)





