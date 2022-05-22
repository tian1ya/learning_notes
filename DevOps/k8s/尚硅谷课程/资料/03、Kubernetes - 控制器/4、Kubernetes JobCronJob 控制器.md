## Job

**Job 负责批处理任务，即仅执行一次的任务，它保证批处理任务的一个或多个 Pod 成功结束**



##### 特殊说明

- **spec.template格式同Pod**
- **RestartPolicy仅支持Never或OnFailure**
- **单个Pod时，默认Pod成功运行后Job即结束**
- **`.spec.completions`标志Job结束需要成功运行的Pod个数，默认为1**
- **`.spec.parallelism`标志并行运行的Pod的个数，默认为1**
- **`spec.activeDeadlineSeconds`标志失败Pod的重试最大时间，超过这个时间不会继续重试**



**Example**

求 π 值

算法：马青公式

```python
π/4=4arctan1/5-arctan1/239
```

这个公式由英国天文学教授 约翰·马青 于 1706 年发现。他利用这个公式计算到了 100 位的圆周率。马青公式每计算一项可以得到 1.4 位的 十进制精度。因为它的计算过程中被乘数和被除数都不大于长整数，所以可以很容易地在计算机上编程实现

```python
# -*- coding: utf-8 -*-
from __future__ import division
# 导入时间模块
import time
# 计算当前时间
time1=time.time()
# 算法根据马青公式计算圆周率 #
number = 1000
# 多计算10位，防止尾数取舍的影响
number1 = number+10
# 算到小数点后number1位
b = 10**number1
# 求含4/5的首项
x1 = b*4//5
# 求含1/239的首项
x2 = b // -239
# 求第一大项
he = x1+x2
#设置下面循环的终点，即共计算n项
number *= 2
#循环初值=3，末值2n,步长=2
for i in xrange(3,number,2):
  # 求每个含1/5的项及符号
  x1 //= -25
  # 求每个含1/239的项及符号
  x2 //= -57121
  # 求两项之和
  x = (x1+x2) // i
  # 求总和
  he += x
# 求出π
pai = he*4
#舍掉后十位
pai //= 10**10
# 输出圆周率π的值
paistring=str(pai)
result=paistring[0]+str('.')+paistring[1:len(paistring)]
print result
time2=time.time()
print u'Total time:' + str(time2 - time1) + 's'
```

```dockerfile
FROM hub.c.163.com/public/python:2.7
ADD ./main.py /root
CMD /usr/bin/python /root/main.py
```

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    metadata:
      name: pi
    spec:
      containers:
      - name: pi
        image: maqing:v1
      restartPolicy: Never
```

<!--查看日志，可以显示出答应的 2000 位  π 值-->



## CronJob Spec

- **spec.template 格式同 Pod**
- **RestartPolicy仅支持Never或OnFailure**
- **单个Pod时，默认Pod成功运行后Job即结束**
- **`.spec.completions`标志Job结束需要成功运行的Pod个数，默认为1**
- **`.spec.parallelism`标志并行运行的Pod的个数，默认为1**
- **`spec.activeDeadlineSeconds`标志失败Pod的重试最大时间，超过这个时间不会继续重试**



## CronJob

***Cron Job* 管理基于时间的 Job，即：** 

- **在给定时间点只运行一次**
- **周期性地在给定时间点运行**



**使用条件：当前使用的 Kubernetes 集群，版本 >= 1.8（对 CronJob）** 



**典型的用法如下所示：**

- **在给定的时间点调度 Job 运行**
- **创建周期性运行的 Job，例如：数据库备份、发送邮件**



## CronJob Spec

- **`.spec.schedule`：调度，必需字段，指定任务运行周期，格式同 Cron**

- **`.spec.jobTemplate`：Job 模板，必需字段，指定需要运行的任务，格式同 Job**

- **`.spec.startingDeadlineSeconds` ：启动 Job 的期限（秒级别），该字段是可选的。如果因为任何原因而错过了被调度的时间，那么错过执行时间的 Job 将被认为是失败的。如果没有指定，则没有期限**

- **`.spec.concurrencyPolicy`：并发策略，该字段也是可选的。它指定了如何处理被 Cron Job 创建的 Job 的并发执行。只允许指定下面策略中的一种：**

  - **`Allow`（默认）：允许并发运行 Job**
  - **`Forbid`：禁止并发运行，如果前一个还没有完成，则直接跳过下一个**
  - **`Replace`：取消当前正在运行的 Job，用一个新的来替换**

  **注意，当前策略只能应用于同一个 Cron Job 创建的 Job。如果存在多个 Cron Job，它们创建的 Job 之间总是允许并发运行。**

- **`.spec.suspend` ：挂起，该字段也是可选的。如果设置为 `true`，后续所有执行都会被挂起。它对已经开始执行的 Job 不起作用。默认值为 `false`。**

- **`.spec.successfulJobsHistoryLimit` 和 `.spec.failedJobsHistoryLimit` ：历史限制，是可选的字段。它们指定了可以保留多少完成和失败的 Job。默认情况下，它们分别设置为 `3` 和 `1`。设置限制的值为 `0`，相关类型的 Job 完成后将不会被保留。**



**Example**

```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure
```

```shell
$ kubectl get cronjob
NAME      SCHEDULE      SUSPEND   ACTIVE    LAST-SCHEDULE
hello     */1 * * * *   False     0         <none>
$ kubectl get jobs
NAME               DESIRED   SUCCESSFUL   AGE
hello-1202039034   1         1            49s

$ pods=$(kubectl get pods --selector=job-name=hello-1202039034 --output=jsonpath={.items..metadata.name})

$ kubectl logs $pods
Mon Aug 29 21:34:09 UTC 2016
Hello from the Kubernetes cluster

# 注意，删除 cronjob 的时候不会自动删除 job，这些 job 可以用 kubectl delete job 来删除
$ kubectl delete cronjob hello
cronjob "hello" deleted
```



## CrondJob 本身的一些限制

**创建 Job 操作应该是 *幂等的***
