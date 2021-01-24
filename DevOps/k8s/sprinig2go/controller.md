* ReplicaSet

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
	name: petclinic
	labels:
		app: petclinic
spec:
	replicas: 3
	selector:
		matchLabels:
			app: petclinic
	template:
		metadata:
			labels:
				app: petclinic
		spec:
			containers:
				- name: petclinic
					image: spring2go/spring-petclinic:1.0.0.RELEASE
```

```yaml
apiVersion: v1
kind: Service
metadata:
	name: petclinic
spec:
	selector: 
		app: petclinic
	type: NodePort
	ports:
		- name: http
			port: 8080
			targetPort: 8080
			nodePort: 31080
```

这样启动了3个 `Pod` 然后通过 `service` 可以访问到后台的2个`Pod`， 如果删除一个 `pod` 那么 `RS` 还是可以将删除的Pod，重新拉起来， 甚至可以全部删除，`RS` 也可以将他们全部拉起来。保持`Pod` 和配置文件中的数据始终一致。

`kubectl describe rs petclinic`

可以查看整个 `rs` 过程中的事件。

删除 `rs`

`kubectl delete rs petclinic`

`Pod` 也是会渐渐自动删除了的。

---

#### Deployment

基于 `rs` 的抽象

* Rolling Update
* Deployment 实现滚动发布原理
* 操练

前2个点，查看 `尚硅谷视频`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
	name: petclinic
spec:
	selector:
		matchLabels:
			app: petclinic
	minReadySeconds: 10
	replicas: 3
	template:
		metadata:
			labels:
				app: petclinic
		spec:
			containers:
				- name: petclinic
					image: spring2go/spring-petclinic:1.0.0.RELEASE
```

`minReadySeconds`:  pod 起来10s之后才能就绪， 方便查看滚动效果

```yaml
apiVersion: v1
kind: Service
metadata:
	name: petclinic
spec:
	selector: 
		app: petclinic
	type: NodePort
	ports:
		- name: http
			port: 8080
			targetPort: 8080
			nodePort: 31080
```

然后修改 `Deployment`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
	name: petclinic
spec:
	selector:
		matchLabels:
			app: petclinic
	minReadySeconds: 10
	replicas: 3
	template:
		metadata:
			labels:
				app: petclinic
		spec:
			containers:
				- name: petclinic
					image: spring2go/spring-petclinic:1.0.1.RELEASE
```

直接在执行

`kubectl apply -f pet-deployment.yaml`

`kubectl rollout undo petclinic` 回退到上个版本

`kubectl rollout status petclinic`  回滚过程中的状态

`kubectl rollout hiistory petclinic`  回退历史

`kubectl rollout undo petclinic --to-revision=2` 回到指定的版本

`kubectl delete deploy petclinic` 删除

