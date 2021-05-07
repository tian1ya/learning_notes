```sql
show functions;

-- 自带函数
desc function upper;

-- 详细显示自带函数
desc function extened upper;
```

* 自定义函数

> UDF： 一个输入一个输出
>
> UDAF 聚合函数，多个输入，一个输出： 如count， max/min
>
> UDTF：User-Defined Table-Generating Functions) 一个输入，多个输出 如 lateral view explore
>
> 上面的多和少不是看个数，而是数据Table 的行数

* 编程步骤

> (1) 继承 org.apache.hadoop.hive.ql.UDF
>
> (2) 需要实现 evaluate 函数;evaluate 函数支持重载;
>
> (3) 在 hive 的命令行窗口创建函数
>
> ​         a)添加 jar `add jar linux_jar_path`
>
> ​		b)创建 function `create [temporary] function [dbname.]function_name AS class_name;`
>
> (4)在 hive 的命令行窗口删除函数 `Drop [temporary] function [if exists] [dbname.]function_name;`
>
> **注意事项**
>
> (1)UDF 必须要有返回类型，可以返回 null，但是返回类型不能为 void;

---

#### 编写自己的UDF

* UDF

> ```java
> // 添加依赖
> <dependency>
> <groupId>org.apache.hive</groupId>
> <artifactId>hive-exec</artifactId>
> <version>2.3.2</version>
> </dependency>
> 
> // 编写函数
> import org.apache.hadoop.hive.ql.exec.UDF;
> public class MyUdf extends UDF {
>  public int evaluate(int data) {
>      return data + 5;
>  }
> }
> 
> // 打包,注意抛出异常
> // Error while processing statement: FAILED: Execution Error, return code 1 from org.apache.hadoop.hive.ql.exec.FunctionTask
> // 是打包的时候没有把源码一起打进去
> mvn clean package -Dmaven.test.skip=true
> 
> // 上传到进群本地
> docker cp learning-1.0-SNAPSHOT.jar docker_hive-server_1:/
> // 上传到 hdfs
> hadoop fs -put hiveLearn-1.0-SNAPSHOT-jar-with-dependencies.jar /
> //添加jar包
> // add jar /learning-1.0-SNAPSHOT.jar;
> 
> // 创建函数，这里 函数创建的时候是有库名的，没有那么是给当前库中创建udf
> // 只能限于此库使用
> // [dbname].addFive
> // 或者创建一个 temporary 临时数据库，只使用一次
> // 第一第二次在 using jar 的时候总是会不成功，是因为第二次上传
> // jar 的时候这个jar路径以及被之前的占用了，需要重新改个名字，上传，然后在定义函数就可以生效
> create function addFive as 'com.learn.hive.udf.myUdf' using jar 'hiveLearn-1.0-SNAPSHOT-jar-with-dependencies.jar';
> 
> // 查看hive 上传的 jar
> list jars
> 
> // 使用udf
> select id,addFive(id) as id_add_5 from stud2;
> ```
>
> ### 基于 MR 的Hive的UDAF 和 UDTF 是真的复杂啊，各种类的继承和实现。下来学习实现
>
> 









 