`cm`: 一般的配置

secret`: 针对敏感数据配置，密码，证书等。

同时支持环境变量和

 `volume` (热加载)的方式存储。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
	name: petclinic-config
data:
	SPRING-PROFILES_ACTIVE: mysql
	DATASOUREC_URL: jdbc:mysql://mysql/petclinic
	DATASOURCE_INIT_MODE: always
	TEST_CONFIG: test_config_v1
	
----

apiVersion: V1
kind: Secret
metadata:
	name: petclinic-secret
type: Opaque
#data:
#	DATASOURCE_USERNAME: cm9vdA==
#	DATASOURCE_PASSWORD: cGV0Y2xpbmlj
stringData:
	DATASOURCE_USERNAME: root
	DATASOURCE_PASSWORD: petclinic
```

如果是使用 `data` 那么其值需要使用  `base64 编码`

`echo -n root | base64`

`echo -n petclinic | base64`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
	name: petclinic
spec:
	selector:
		matchLabels:
			app: petclinic
	replicas: 1
	template:
		metadata:
			labels:
				app: petclinic
		spec:
			containers:
				- name: petclinic
					image: spring2go/spring-petclinic:1.0.1.RELEASE
					envFrom:
						- configMapRef:
							name: petclinic-config
						- secretRef:
							name: petcclinic-secret
```

---

`Secret` 对象类型用来保存敏感信息，例如密码、OAuth 令牌和 SSH 密钥。 将这些信息放在 `secret` 中比放在 [Pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-overview/) 的定义或者 [容器镜像](https://kubernetes.io/zh/docs/reference/glossary/?all=true#term-image) 中来说更加安全和灵活，

Secret 是一种包含少量敏感信息例如密码、令牌或密钥的对象。 这样的信息可能会被放在 Pod 规约中或者镜像中。 用户可以创建 Secret，同时系统也创建了一些 Secret。

[**Secret 类型**](https://kubernetes.io/zh/docs/concepts/configuration/secret/#secret-types)

| `Opaque`                              | 用户定义的base64编码的任意数据(默认)     |
| ------------------------------------- | ---------------------------------------- |
| `kubernetes.io/service-account-token` | 服务账号令牌                             |
| `kubernetes.io/dockercfg`             | `~/.dockercfg` 文件的序列化形式          |
| `kubernetes.io/dockerconfigjson`      | `~/.docker/config.json` 文件的序列化形式 |
| `kubernetes.io/basic-auth`            | 用于基本身份认证的凭据                   |
| `kubernetes.io/ssh-auth`              | 用于 SSH 身份认证的凭据                  |
| `kubernetes.io/tls`                   | 用于 TLS 客户端或者服务器端的数据        |
| `bootstrap.kubernetes.io/token`       | 启动引导令牌数据                         |

