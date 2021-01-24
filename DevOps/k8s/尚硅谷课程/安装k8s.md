**Note**: 虚拟机以及centos 的静态IP 的按照在安装目录下。

---

### 基本环境安装 

1. 关闭 selinux

```shell
setenforce 0

sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config
# 这一步之后 SELINUX 值修改为 disabled
```

2. 关闭swap分区交换或swap 文件

```shell
vi /etc/fstab // 注释
#/dev/mapper/centos-swap swap                    swap    defaults        0 0

swapoff -a // 临时关闭
```

3. 修改网卡配置

```shell
vi /etc/sysctl.conf

net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1

sysctl -p # 应用上述配置，会有这样的输出
net.ipv4.ip_forward = 1
sysctl: cannot stat /proc/sys/net/bridge/bridge-nf-call-iptables: No such file or directory
sysctl: cannot stat /proc/sys/net/bridge/bridge-nf-call-ip6tables: No such file or directory

# 不用管他，这些目录会在后面才会去生成
```

4. 启动内核模块

```shell
vim /etc/sysconfig/modules/ipvs.modules

modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack_ipv4

# 依次执行，使配置临时生效
$ modprobe -- ip_vs
$ modprobe -- ip_vs_rr
$ modprobe -- ip_vs_wrr
$ modprobe -- ip_vs_sh
$ modprobe -- nf_conntrack_ipv4

# 执行看配置是否生效
cut -f1 -d " " /proc/modules | grep -e ip_vs -e nf_conntrack_ipv4
```

5. 关闭防火墙

```shell
systemctl stop firewalld
systemctl status firewalld

执行开机禁用防火墙自启命令  ： systemctl disable firewalld.service
```

6. 配置 hosts

   **安装 kubectl、kubeadm、kubelet**

   1. 先替换镜像源

```shell
$ vi /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg

$ yum install -y kubelet kubeadm kubectl
```

---

安装上面的方式配置之后一直都无法联网，[解决方式如下](https://my.oschina.net/u/4307191/blog/3509400)：解决联网问题，才能安装啊。。

`添加NAT方式让虚拟机上网(enp0s3)，添加host-only方式让虚拟机与虚拟机通信(enp0s)`

```shell
安装过程中并没有对两个网卡进行配置，保持默认，系统安装好之后
Nat 克隆机器之后并没有做什么操作， Ip还是没有变，host-only 的 ip 手动进行了修改。
```

---

7. 启动 kubernetes 服务

```shell
systemctl enable kubelet #开启就启动服务谨慎开启
systemctl start kubelet  

systemctl status kubelet # 服务并没有启动, 错误码 255

# 执行 `journalctl -xe` 查看服务信息，是因为我们的集群还没有发件成功，缺少文件
```

8. [dokcer 安装](https://docs.docker.com/engine/install/centos/)

```shell
yum install -y yum-utils

yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
    
yum install docker-ce docker-ce-cli containerd.io
```

9. Docker 启动

```shell
systemctl start docker
systemctl status docker

systemctl enable docker # 尽量不设置为开启启动
```

10. 修改docker cgroup 驱动

```shell
# docker 默认使用 cgroupfs，而k8s默认的 cgroup 的驱动是 cgroupd，进行修改

cat > /etc/docker/daemon.json <<EOF
{
    "exec-opts": ["native.cgroupdriver=systemd"],
    "log-driver": "json-file",
    "log-opts": {
    "max-size": "100m"
    }
}
EOF

$ systemctl restart docker
$ docker info | grep -i cgroup
```

11. 拉去预先的镜像

```shell
# 需要的镜像
$ kubeadm config images list
k8s.gcr.io/kube-apiserver:v1.20.1
k8s.gcr.io/kube-controller-manager:v1.20.1
k8s.gcr.io/kube-scheduler:v1.20.1
k8s.gcr.io/kube-proxy:v1.20.1
k8s.gcr.io/pause:3.2
k8s.gcr.io/etcd:3.4.13-0
k8s.gcr.io/coredns:1.7.0

---

docker pull k8s.gcr.io/kube-apiserver:v1.20.1
docker pull k8s.gcr.io/kube-controller-manager:v1.20.1
docker pull k8s.gcr.io/kube-scheduler:v1.20.1
docker pull k8s.gcr.io/kube-proxy:v1.20.1
docker pull k8s.gcr.io/pause:3.2
docker pull k8s.gcr.io/etcd:3.4.13-0
docker pull k8s.gcr.io/coredns:1.7.0
```

**以上的步骤是需要在 master 和 node 节点上 都要执行的，所以到此为止，将虚拟机复制2个 ，作为节点，然后接下来的步骤是需要在master 节点上执行的**

```shell
# 注意在复制的时候是需要选择产生新的MAC 地址
# 然后修改每台机器的 hostname 以及2张 网卡 ip 地址，防止三者直接的冲突

kube-master
0800279B83A9
192.168.99.100
10.0.2.15

kube-node-1
192.168.99.100
10.0.2.15

kube-node-2
```

12. 修改主机名

```shell
hostnamectl set-hostname kube-node-1
# 需要重新登录才能生效

# 配置 hosts
192.168.99.100 kube-master
192.168.99.101 kube-node-1
192.168.99.102 kube-node-2
```

13 master 初始化

```shell
--pod-network-cidr=10.244.0.0/16 #指定使用Calico 网络
--apiserver-advertise-adddress=  #指定master 节点IP，也可以是 hosts
--kubernetes-version=v1.20.1

# 启动docker
systemctl start docker 

# 初始化 master k8s
kubeadm init --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=192.168.99.100 --kubernetes-version=v1.20.1 

# 第一次启动时候，因为docker 没有启动，所以报错，启动docker 之后还需要将 k8s 重置
kubeadm reset

# init 执行成功之后，安装提示完成
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
# vi /etc/kubernetes/admin.conf 这一步是可选的将配置中的 kube-master ip 换成是域名
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 因为我们使用的 --pod-network-cidr=10.244.0.0/16 所以网络插件需使用 flannel
# 然后在 [git](https://github.com/coreos/flannel) 看到安装 flannel 方式

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# 这个时候可以看下 pods
$ kubectl get pods --all-namespaces

kube-system   coredns-74ff55c5b-pwnjg               1/1     Running   0          11m
kube-system   coredns-74ff55c5b-q5lmt               1/1     Running   0          11m
kube-system   etcd-kube-master                      1/1     Running   0          12m
kube-system   kube-apiserver-kube-master            1/1     Running   0          12m
kube-system   kube-controller-manager-kube-master   1/1     Running   0          12m
kube-system   kube-flannel-ds-wrvjp                 1/1     Running   0          89s
kube-system   kube-proxy-nprpf                      1/1     Running   0          11m
kube-system   kube-scheduler-kube-master            1/1     Running   0          12m
```

14. 将其他2个node 加入到集群中

```shell
kubectl get node -o wide
# 只有 kube-master

# kube-master 执行
kubeadm token create --print-join-command

# 打印出 kubeadm join kube-master:6443 --token bhsnwk.h0udo1gpc0ch1up4     --discovery-token-ca-cert-hash sha256:5a2eb046eaf4c559358ae36613958bc3393de33ea1859d0dbc1c896a02c9abe5
# 在 kube-node-1 和 kube-node-2 中执行上面的命令就可以将 node 添加到集群中

# 在 执行的过程中，可以在 kube-master 中 查看添加的过程
watch kubectl get nodes -o wide

# 能够看到有新的node 加入进来你

# kube-master 执行
kubectl get pods --all-namespaces -o wide
# 能够看到 pod 在其他的 node 开始部署
```

[作者博客](https://blog.hungtcs.top/2019/11/27/23-K8S%E5%AE%89%E8%A3%85%E8%BF%87%E7%A8%8B%E7%AC%94%E8%AE%B0/#more)

[作者B站视频](https://www.bilibili.com/video/BV1BJ41197QU/?spm_id_from=autoNext)

