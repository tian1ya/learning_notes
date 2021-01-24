只要`yaml` 文件就可以安装各种资源

---

#### Helm

> `helm` 就是让 k8s 的应用管理可配置，能动态生成，通过动态生成 k8s 资源清单文件然后调用 `kubectl` 自动执行`k8s` 的资源部署
>
> 它是官方提供的类似于 `yum` 的包管理器，是部署环境的流程封装，它有2个重要的感念，`chart` 和 `release`
>
> * Chart 是创建一个应用的信息集合，包括各种对象的配置模板，参数定义，依赖关系，文档说明等，是应用部署的自包含逻辑单元，可以将 `chart` 想象成 `apt`等的软件安装包
> * release: 是 chart 的运行实例，代表一个正在运行的应用，当chart 被安装到 集群，就生成一个release，chart 能够多此安装到同一个集群，每次安装就是一个 release
>
> （以上概念和docker 的镜像容器很类似）
>
> 有的资料说是有3个重要概念
>
> Helm 有三个重要概念：
>
> - chart：包含了创建`Kubernetes`的一个应用实例的必要信息
> - config：包含了应用发布配置信息
> - release：是一个 chart 及其配置的一个运行实例
>
> 两个组成部分
>
> * Helm client其主要负责如下：
>   * 本地 chart 开发
>   * 仓库管理
>   * 与 Tiller sever 交互
>   * 发送预安装的 chart
>   * 查询 release 信息
>   * 要求升级或卸载已存在的 release
> * `Tiller Server`是一个部署在`Kubernetes`集群内部的 server，其与 Helm client、Kubernetes API server 进行交互。Tiller server 主要负责如下：
>   * 监听来自 Helm client 的请求
>   * 通过 chart 及其配置构建一次发布
>   * 安装 chart 到`Kubernetes`集群，并跟踪随后的发布
>   * 通过与`Kubernetes`交互升级或卸载 chart
>   * 简单的说，client 管理 charts，而 server 管理发布 release
>
> 

