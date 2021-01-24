* Namespace 原理
* kube-DNS 域名服务器，服务名到 `ClusterIP` 的转换

---

Namespace：

> 资源隔离机制，namespace 之间资源是独立的，

`kubectl get ns` 查看 `namespacce`

支持 `k8s` 本身运行的那些组件就运行在 `kube-system ` 命名空间下。

`kubectl get all -n kube-system`  查看指定命名空间下的资源情况，如果不指定则查看的是 `default` 的命名空间。在这个空间下可以找到

`kube-dns、etcd等`在访问 `ClusterIP` 类型的`service`，先是通过域名到 `kube-dns` 找到 `IP` 然后在去访问对应的 `service`

