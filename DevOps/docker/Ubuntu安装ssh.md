> ```shell
> docker pull ubuntu:latest
> 
> docker run -it -d ubuntu:lastest /bin/bash
> 
> # 安装 openssh-server
> apt-get update
> apt-get install openssh-server
> 
> # 启动之前需手动创建/var/run/sshd，不然启动sshd的时候会报错
> mkdir -p /var/run/sshd
> 
> # sshd 守护进行运行
> /usr/sbin/sshd -D &
> 
> # 或者这样启动 ssh
> service ssh satrt
> 
> # 安装 netstat 查看sshd是否监听22端口
> apt-get install net-tools
> netstat -apn | grep ssh
> # 如果监听了22端口，那么服务启动成功
> 
> # ssh 登录
> # docker 容器中 生成 ssh key
> ssh-keygen -t rsa
> 
> # 修改sshd-config允许root登陆
> sed -i 's+PermitRootLogin prohibit-password+PermitRootLogin yes' /etc/ssh/sshd-config
> 
> # 或者使用 vim 在 /etc/ssh/sshd-config 目录中写入
> s+PermitRootLogin prohibit-password+PermitRootLogin yes
> 
> # 设置 root 用户登录密码
> passwd root
> 
> # 修改完sshd-config之后需要重启sshd服务
> ps -aux | grep ssh
> kill -9 pid
> /usr/sbin/sshd -D &
> 
> # 或者重启方法
> service ssh restart
> ```

* Netstat

> 显示各种网络相关信息，如网络连接，路由表，接口状态 (Interface Statistics)，masquerade 连接，多播成员 (Multicast Memberships) 等等。
>
> # **常见参数**
>
> -a (all)显示所有选项，默认不显示LISTEN相关
> -t (tcp)仅显示tcp相关选项
> -u (udp)仅显示udp相关选项
> -n 拒绝显示别名，能显示数字的全部转化成数字。
> -l 仅列出有在 Listen (监听) 的服務状态
>
> -p 显示建立相关链接的程序名
> -r 显示路由信息，路由表
> -e 显示扩展信息，例如uid等
> -s 按各个协议进行统计
> -c 每隔一个固定时间，执行该netstat命令。

* sed

> 利用脚本来处理文本文件
>
> sed 可依照脚本的指令来处理、编辑文本文件。

---

* Dockerfile 给容器添加ssh 服务

run.sh 内容

```shell
#!/bin/bash
/usr/sbin/sshd -D
```

生成 authorized_keys 文件

```shell
cat ~/.ssh/id_rsa.pub > authorized_keys
```

```dockerfile
FROM ubuntu:18.04

MAINTAINER docker_user(user@docker.com)

# 更新缓存，安装 ssh 服务
RUN apt-get update \
	&& apt-get install -y openssh-server \
	&& mkdir -p /var/run/sshd \
	&& mkdir -p /root/.ssh
	
# 取消 pam 限制，禁止 root 用户登录
RUN sed -ri 's/session required pam_loginuid.so/#session required pam_loginuid.so/g' /etc/pam.d/sshd

# 复制配置文件到相应的位置，并赋予脚本可执行权限
ADD authorized_keys /root/.ssh/authorized_keys
ADD run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 22

CMD ["/run.sh"]
```

创建镜像以及启动

```shell
# build 镜像
docker build -t sshd:dockerfile .

# run
docker run -d -p 10086:22 --name sshd-test sshd:dockerfile  

# 登录
ssh root@192.168.99.105 -p 10086
```





















