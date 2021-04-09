* 准备步骤

>  Docker 所在机器 dongli@10.205.8.22 密码 1qaz!QAZ1qaz
>
> 使用delta jar 包路径 /home/dongli/delta-lake-demo/delta-core_2.11-0.5.0.jar 
>
> 使用minIO 单间本地私有分布式存储所需依赖路径：/home/dongli/delta-lake-demo/docker-minio-distributed/dependencies
>
> 在路径 /home/dongli/delta-lake-demo/docker-minio-distributed/ 放还放着搭建 spark集群、minIO分布式存储的docker-compose

* Run demo

> 需要将 miniIO 的依赖包拷贝到 spark-master 和 spark-worker 的路径 /spark/jars 下。
>
> Demo 程序存储位置（spark-master容器）``/spark/examples/original-deltaLake2-1.0-SNAPSHOT.jar``
>
> 在 /spark 目录下执行
>
> ```shell
> ./bin/spark-submit --master spark://spark-master:7077 \
> --conf spark.delta.logStore.class=org.apache.spark.sql.delta.storage.S3SingleDriverLogStore \
> --conf spark.hadoop.fs.s3a.endpoint=http://172.22.0.4:9000 \
> --conf spark.hadoop.fs.s3a.access.key=minio \
> --conf spark.hadoop.fs.s3a.secret.key=minio123 \
> --conf spark.hadoop.fs.s3a.path.style.access=true \
> --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
> --jars /spark/examples/delta-core_2.11-0.5.0.jar \
> --class com.delta.Run examples/original-deltaLake2-1.0-SNAPSHOT.jar s3a://spark-test/  delta21 schemaCheck21
> 
> # Run 主程序参数：S3 bucket：s3a://spark-test/  S3 bucket文件名1：delta21 S3 bucket文件名2：schemaCheck21
> ```

* 查看结果（后面需要通过mc 查看，正在进行中）

> ```shell
> ./bin/spark-shell --master spark://spark-master:7077 \
> --conf spark.delta.logStore.class=org.apache.spark.sql.delta.storage.S3SingleDriverLogStore \
> --conf spark.hadoop.fs.s3a.endpoint=http://172.22.0.4:9000 \
> --conf spark.hadoop.fs.s3a.access.key=minio \
> --conf spark.hadoop.fs.s3a.secret.key=minio123 \
> --conf spark.hadoop.fs.s3a.path.style.access=true \
> --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
> --jars /spark/examples/delta-core_2.11-0.5.0.jar 
> ```
>
> 执行
>
> ```shell
> val df = spark.read.format("delta").load("s3a://{S3 bucket}/{S3 bucket文件名}")
> df.show()
> ```

---

S3 协议同 DeltaLake 集成

> DeltaLake 本身支持基于S3协议的云存储服务，只需要在spark 中增加依赖
>
> ```java
> Hadoop 2.8.2
> HttpClient 4.5.3
> Joda Time 2.9.9
> AWS SDK For Java Core 1.11.712
> AWS SDK For Java 1.11.712
> AWS Java SDK For AWS KMS 1.11.712
> AWS Java SDK For Amazon S3 1.11.712
> ```
>
> 注意 这个时候spark 集群不是将hadoop 版本预编译进去版本，而是 spark-x.x.x-bin-without-hadoop版本
>
> 其次在运行spark 程序增加配置项
>
> ```java
> --conf spark.hadoop.fs.s3a.endpoint=http://localhost:9000 \
> --conf spark.hadoop.fs.s3a.access.key=minio \
> --conf spark.hadoop.fs.s3a.secret.key=minio123 \
> --conf spark.hadoop.fs.s3a.path.style.access=true \
> --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
> ```
>
> 然后spark 程序就可以通过delta Lake 完成基于S3协议的读写，
>
> 参考[**apache-spark-with-minio.md**](https://github.com/minio/cookbook/blob/master/docs/apache-spark-with-minio.md)

---

**CEPH**

>  Ceph 存储集群的部署都始于部署一个个**Ceph 节点**、**网络**和 **Ceph 存储集群**
>
> **Ceph OSDS** 
>
> > 功能是存储数据，处理数据的复制、恢复、回填、再均衡，并通过检查其他OSD 守护进程的心跳来向 Ceph Monitors 提供一些监控信息。当 Ceph 存储集群设定为有2个副本时，至少需要2个 OSD 守护进程，集群才能达到 `active+clean` 状态（ Ceph 默认有3个副本，但你可以调整副本数）。
>
> **Monitors**
>
> > 维护着展示集群状态的各种图表，包括监视器图、 OSD 图、归置组（ PG ）图、和 CRUSH 图。 Ceph 保存着发生在Monitors 、 OSD 和 PG上的每一次状态变更的历史信息（称为 epoch ）。
>
> **MDSs**
>
> > 为 Ceph 文件系统存储元数据（也就是说，Ceph 块设备和 Ceph 对象存储不使用MDS ）

**ceph**

> 文件存储、块设备、对象存储
>



* 问题1： 列个数不一致

> 使用的 sql 语句
>
> ```sql
> insert overwrite table test.ods_csr_calllog PARTITION (ods_insert_date='2020-05-18') select clcallid, clcalltime, clcallduration, clcustid, clivrcsr, clcalltype, clorgid,clcsrid, 358 as task_id,ods_insert_date from test.temp_ods_csr_calllog;
> ```
>
> 报错信息：
>
> ```javascript
> Error: Error while compiling statement: FAILED: SemanticException [Error 10044]: Line 1:23 Cannot insert into target table because column number/types are different ''2020-05-18'': Table insclause-0 has 9 columns, but query has 10 columns. (state=42000,code=10044)
> ```
>
> 错误分析：数据列数量不一致，select 了10列，但只有9列(除分区列之外)，将select 中的分区列 ods_insert_date 去掉就运行OK
>
> ```mysql
> 0: jdbc:hive2://zc2:10000/box> insert overwrite table test.ods_csr_calllog PARTITION (ods_insert_date='2020-05-18') select clcallid, clcalltime, clcallduration, clcustid, clivrcsr, clcalltype, clorgid,clcsrid, 358 as task_id from test.temp_ods_csr_calllog;
> ```

* 问题2： 时间字段使用引号

> ```mysql
> s"""
>    | insert overwrite table test.ods_csr_calllog PARTITION (ods_insert_date=${insertTime}) select clcallid, clcalltime, clcallduration, clcustid, clivrcsr, clcalltype, clorgid,
>    |  clcsrid, ${task.taskId} as task_id
>    |  from test.temp_ods_csr_calllog
>    |""".stripMargin
> ```
>
> 报错内容：
>
> ```java
> Exception in thread "main" org.apache.spark.sql.catalyst.parser.ParseException:
> mismatched input '-' expecting {')', ','}(line 2, pos 76)
> 
> == SQL ==
> 
>  insert overwrite table test.ods_csr_calllog PARTITION (ods_insert_date=2020-05-18) select clcallid, clcalltime, clcallduration, clcustid, clivrcsr, clcalltype, clorgid,
> ----------------------------------------------------------------------------^^^
>   clcsrid, 0 as task_id
>   from test.temp_ods_csr_calllog
> ```
>
> mismatched 那也没有很清晰的说明在时间位置那块一直无法解析。
>
> 时间变量加上变量
>
> ```mysql
> s"""
>    | insert overwrite table test.ods_csr_calllog PARTITION (ods_insert_date='${insertTime}') select clcallid, clcalltime, clcallduration, clcustid, clivrcsr, clcalltype, clorgid,
>    |  clcsrid, ${task.taskId} as task_id
>    |  from test.temp_ods_csr_calllog
>    |""".stripMargin
> ```
>
> 



[https://github.com/dragen1860/TensorFlow-2.x-Tutorials/tree/master/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0%E4%B8%8ETensorFlow%E5%85%A5%E9%97%A8%E5%AE%9E%E6%88%98-%E6%BA%90%E7%A0%81%E5%92%8CPPT](https://github.com/dragen1860/TensorFlow-2.x-Tutorials/tree/master/深度学习与TensorFlow入门实战-源码和PPT)





```
SELECT *, exec_sessions.login_name
FROM sys.dm_pdw_exec_requests exec_requests
LEFT JOIN (
  SELECT session_id, login_name
  FROM sys.dm_pdw_exec_sessions where session_id <> session_id()) exec_sessions
ON exec_requests.session_id = exec_sessions.session_id
WHERE status not in ('Completed','Failed','Cancelled')
AND exec_requests.session_id <> session_id()
ORDER BY submit_time DESC;
```