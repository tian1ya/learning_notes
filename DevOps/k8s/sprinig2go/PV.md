**持久卷（PersistentVolume，PV）**

是集群中的一块存储（对存储的抽象），可以由管理员事先供应，或者 使用[存储类（Storage Class）](https://kubernetes.io/zh/docs/concepts/storage/storage-classes/)来动态供应。 持久卷是集群资源，就像节点也是集群资源一样。PV 持久卷和普通的 Volume 一样，也是使用 卷插件来实现的，只是它们拥有独立于任何使用 PV 的 Pod 的生命周期。

`PV` 独立于 `Pod` 生命周期之外。

* 静态pv

> 持久卷申领（PersistentVolumeClaim，PVC）表达的是用户对存储的请求。概念上与 Pod 类似。 Pod 会耗用节点资源，而 PVC 申领会耗用 PV 资源。Pod 可以请求特定数量的资源（CPU 和内存）；同样 PVC 申领也可以请求特定的大小

* 动态Pv

> 如果管理员所创建的所有静态 PV 卷都无法与用户的 PersistentVolumeClaim 匹配， 集群可以尝试为该 PVC 申领动态供应一个存储卷。 这一供应操作是基于 StorageClass 来实现的：PVC 申领必须请求某个 [存储类](https://kubernetes.io/zh/docs/concepts/storage/storage-classes/)，同时集群管理员必须 已经创建并配置了该类，这样动态供应卷的动作才会发生。 如果 PVC 申领指定存储类为 `""`，则相当于为自身禁止使用动态供应的卷。

**（PersistentVolumeClaim，PVC）**

表达的是用户对存储的请求。概念上与 Pod 类似。 Pod 会耗用节点资源，而 PVC 申领会耗用 PV 资源。Pod 可以请求特定数量的资源（CPU 和内存）；同样 PVC 申领也可以请求特定的大小。

`PVC` 寻找一个合适的`PV`  进行绑定。

* 绑定

> `pv` 和 `pvc`  是一一对应的，二者一旦建立绑定关系，就是排他性的。

* 保护使用中的存储 对象

> 被使用中的存储对象，是被保护的，是不能够删除了的，确保数据不丢失
>
> 删除被`Pod` 使用的 `PVC ` 对象，不会被立马删除，直到 `pvc`  不被任何 `pod` 使用，最后才会被删除

---

* PV 访问模式

> 每个 PV 卷的访问模式都会设置为 对应卷所支持的模式值。 例如，NFS 可以支持多个读写客户，但是某个特定的 NFS PV 卷可能在服务器 上以只读的方式导出。每个 PV 卷都会获得自身的访问模式集合，描述的是 特定 PV 卷的能力。官方文档提供了很多卷类型支持的访问模式
>
> 访问模式有：
>
> - ReadWriteOnce(缩写：RWO) -- 卷可以被一个节点以读写方式挂载；
> - ReadOnlyMany(缩写：ROX) -- 卷可以被多个节点以只读方式挂载；
> - ReadWriteMany (缩写：RWX)-- 卷可以被多个节点以读写方式挂载。

* PV 回收策略

> 当用户不再使用其存储卷时，他们可以从 API 中将 PVC 对象删除，从而允许 该资源被回收再利用。PersistentVolume 对象的回收策略告诉集群，当其被 从申领中释放时如何处理该数据卷。 目前，数据卷可以被 Retained（保留）、Recycled（回收）或 Deleted（删除）。
>
> * Retained: 手动回收
> * Recycled:  回收策略 `Recycle` 已被废弃。取而代之的建议方案是使用动态供应。
> * Deleted: 删除动作会将 PersistentVolume 对象从 Kubernetes 中移除

* 卷的状态

> * Available: 一块存储设备还没有被任何声明绑定
> * Bound: 绑定，卷已经被声明绑定
> * Release：已释放，声明被删除，但是资源还没有集群重新声明
> * Failed: 自动回收失败

---

* 使用 `nfs` 后端存储能力，建立 `pv/pvc`  的实验

> 1. 在第三台机器(`ip: 192.168.99.102`)上安装 `nfs： yum install -y nfs-utils rpcbind`
> 2. `mkdir -r /opt/nfs`
> 3. `chmod 777 nfs/`
> 4. `vi /etc/expose` 文件中写入`/opt/nfs *(rw,no_root_squash,no_all_squash,sync)`
> 5. `systemctl start rpcbind`
> 6. `systemctl start nfs`
> 7. 在其他几个节点中，安装 `nfs` 的客户端 `yum install -y nfs-utils rpcbind`
> 8. 在机器 `192.168.99.100` 查看 `nfs： showmount -e 192.168.99.102`， 就能看到挂载的目录
> 9. 机器 `192.168.99.100`和 `192.168.99.102` 完成挂载 `mount -t nfs 192.168.99.102:/opt/nfs /opt/mound_test` 
> 10. 测试，随便在哪台机器上的挂载目录中进行生产一个文件，然后在另外一个机器上挂载的目录下也能看到这样的相同的一个问题
> 11. 上面的第10步，主要是完成 `nfs` 的测试功能，测试通过之后，将机器之间的挂载删除 `umount /opt/mound_test`

*  `nfs` 封装 `pv`

> ```yaml
> apiVersion: v1
> kind: PersistentVolume
> metadata:
> 	name: nfspv1
> spec:
> 	capacity:
> 		storage: 100Mi
> 	accessModes:
> 		- ReadWriteOnce
> 	persistentVolumeReclaimPolicy: Retain
> 	storageClassName: nfs
> 	nfs:
> 		path: /opt/nfs
> 		server: 192.168.99.102
> ```
>
> `kubectl get pv`  查看可使用 `pv`

* pvc

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-pvc
  namespace: nfs-pvc-test
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: nfs
  resources:
    requests:
      storage: 90Mi
```















