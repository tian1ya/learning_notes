#### 分析

* 观察，至少跑1天，看看生成的慢的情况
* (捕获慢SQL)开启慢查询日志，设置阈值，比如超过5s 的就是慢SQL，并将其抓取出来
* `explain` + 慢SQL 分析
* `show profile`： 查询sql 在mysql 服务器里面的执行细节和生命周期情况
* 运维经理或者DBA， SQL 数据库服务器的参数调优

---

#### 小表驱动大表

![a](./pics/031.png)

![a](./pics/032.png)

```mysql
mysql> select * from tbl_emp e where e.deptId in (select id from tbl_dept d);
+----+------+--------+
| id | name | deptId |
+----+------+--------+
|  1 | z3   |      1 |
|  2 | z4   |      1 |
|  3 | z5   |      1 |
|  4 | w5   |      2 |
|  5 | w6   |      2 |
|  6 | s7   |      3 |
|  7 | s8   |      4 |
+----+------+--------+
7 rows in set (0.04 sec)

mysql> select * from tbl_emp e where exists (select 1 from tbl_dept d where d.id=e.deptId);
+----+------+--------+
| id | name | deptId |
+----+------+--------+
|  1 | z3   |      1 |
|  2 | z4   |      1 |
|  3 | z5   |      1 |
|  4 | w5   |      2 |
|  5 | w6   |      2 |
|  6 | s7   |      3 |
|  7 | s8   |      4 |
+----+------+--------+
7 rows in set (0.04 sec)
```

#### Order by 子句

尽量使用Index 方式排序，避免使用`fileSort` 方式，尽可能在索引列上完成排序操作，遵照索引建设的嘴贱左前缀

```mysql
CREATE TABLE tblA(
	id int primary key not null auto_increment,
    age int,
    birth timestamp not null
);

insert into tblA(age, birth) values(22, now());
insert into tblA(age, birth) values(23, now());
insert into tblA(age, birth) values(24, now());

CREATE INDEX idx_A_ageBirth on tblA(age, birth);

select * from tblA;

explain select * from tblA where age>10 order by age;
explain select * from tblA where age>10 order by age, birth;
explain select * from tblA where birth>'2022-03-27 15:42:10' order by age;
-- 不会产生 filesort

explain select * from tblA order by birth;
explain select * from tblA where age>10 order by birth;
explain select * from tblA where age>10 order by birth,age;
explain select * from tblA where birth>'2022-03-27 15:42:10' order by birth;
-- 产生 filesort
-- 使用索引的过程需要和创建索引的过程一样，不能跨越
```

`order by` 优化字段

* `select *` 是大忌，只`query` 需要的店，这点很重要，这里的影响有

  * 当`query` 的字段大小总是小于`max_length_for_sort_data` 而且排序字段不是`text|blog` 类型时候，会用改进后的算法，单路排序，否则使用老算法，多路福排序

  * 两种算法的数据都有可能超过`sort_buffer` 的容量，超出之后，会创建`tmp` 文件进行合并排序，导致多次`I/O`但是单路排序算法的风险会更大，所以要加da`sort_buffer_size`

  * 尝试提高`sort_buffer_size`

    不管那种算法，提高这个参数都会提高效率，当然根据系统的能力去提高，因为这个参数是针对每个进程的

  * 尝试提高`max_length_for_sort_data`

    提高这个参数，会增加改进算法的概率，如果设置的太高，数据总量超过`sort_buffer_size` 的概率就会增大，明显症状是高的磁盘`IO` 和低的处理器使用率

#### Group by

> 实质是**先排序后进行分组**，遵照索引键的最佳左前缀，
>
> `where` 的使用高于`having` 能写在were 限定条件就不要在写到`having` 中。

#### 慢查询日志

> `mysql` 的慢查询日志是`mysql` 提高的一种日志记录，她用来记录在`mysql` 中响应时间超过阈值的语句，具体说运行时间超过`long_query_time` 值的`SQL`，则会被记录到慢查询日志中。
>
> 该值的默认值是10，单位是秒。

默认是没有开启的，如果不是调优需要的话，不建议开启

```mysql
mysql> set global slow_query_log=1;
-- 暂时设置，重启之后还会关闭，永久生效修改 my.cnf 配置文件
Query OK, 0 rows affected (0.02 sec)

mysql> show variables like '%slow_query_log%';
+---------------------+-----------------------------------+
| Variable_name       | Value                             |
+---------------------+-----------------------------------+
| slow_query_log      | ON                                |
| slow_query_log_file | /var/lib/mysql/localhost-slow.log |
+---------------------+-----------------------------------+

mysql> show variables like '%long_query_time%';
+-----------------+-----------+
| Variable_name   | Value     |
+-----------------+-----------+
| long_query_time | 10.000000 |
+-----------------+-----------+

mysql> set global long_query_time=3;
Query OK, 0 rows affected (0.00 sec)

mysql> show variables like '%long_query_time%';
+-----------------+-----------+
| Variable_name   | Value     |
+-----------------+-----------+
| long_query_time | 10.000000 |
+-----------------+-----------+
-- 这里显示还是10，需要重写连接-创建会话

-- 睡4s
select sleep(4);

-- 去日志文件中看到日志
```

```shell
cat /var/lib/mysql/localhost-slow.log
/usr/sbin/mysqld, Version: 5.7.37-log (MySQL Community Server (GPL)). started with:
Tcp port: 3306  Unix socket: /var/lib/mysql/mysql.sock
Time                 Id Command    Argument
# Time: 2022-03-27T08:56:20.178113Z
# User@Host: root[root] @ gateway [192.168.56.1]  Id:     5
# Query_time: 4.001347  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 0
SET timestamp=1648371380;
select sleep(4);
```

```mysql
-- 查看慢sql 个数
mysql> show global status like '%Slow_queries%';
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| Slow_queries  | 1     |
+---------------+-------+
```

日志分析工具`mysqldumpslow` 命令

```mysql
mysqldumpslow --help
```

常使用参数

* s：按照何种方式排序
* c: 访问次数
* l: 锁定时间
* r: 返回时间
* t: 查询时间
* al: 平均锁定时间
* ar: 平均返回记录数
* at: 平均查询时间
* t: 返回前面多少条的数据
* g: 后更一个正则表达式，大小写敏感

```shell
# 得到返回记录集最多的 10 个sql
mysqldumpslow -s r -t 10 /var/lib/mysql/mysql.sock

# 得到访问次数最多的10个sql
mysqldumpslow -s c -t 10 /var/lib/mysql/mysql.sock

# 得到按照时间排序的前10条里面含有左连接的查询数据
mysqldumpslow -s t -t 10 -g “left join”/var/lib/mysql/mysql.sock | more

# 建议结合 more 使用，有可能会爆屏
```

#### 批量数据脚本

```mysql
create database bigData;
CREATE TABLE dept(
    id int unsigned primary key auto_increment,
 	deptno int unsigned not null default 10,
	dname varchar(20) not null default "",
	loc varchar(8) not null default ""
) engine=innodb default charset=GBK;

CREATE TABLE emp
(
	id int unsigned primary key auto_increment,
	empno mediumint unsigned not null default 0,
	ename varchar(20) not null default "",
	job varchar(9) not null default "",
	mgr mediumint unsigned not null default 0,
	hiredate date not null,
	sal decimal(7,2) not null,
	comm decimal(7,2) not null,
	deptno mediumint unsigned not null default 0
)ENGINE=INNODB DEFAULT CHARSET=utf8;

-- 允许创建函数
mysql> show variables like '%log_bin_trust_function_creators%';
+---------------------------------+-------+
| Variable_name                   | Value |
+---------------------------------+-------+
| log_bin_trust_function_creators | OFF   |
+---------------------------------+-------+
1 row in set (0.07 sec)

mysql> 
mysql> set global log_bin_trust_function_creators=1;
Query OK, 0 rows affected (0.00 sec)

-- 创建函数
-- 随机产生字符串
delimiter $$ -- 这里定义的 $$ 是随机的，表示开始，需要额结尾对应上，表示开始结束
CREATE FUNCTION rand_string(n INT) RETURNS VARCHAR(255)
BEGIN
 DECLARE chars_str VARCHAR(100) DEFAULT 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM';
 DECLARE return_str VARCHAR(255) DEFAULT '';
 DECLARE i INT DEFAULT 0;
 WHILE i < n DO
  SET return_str=CONCAT(return_str, SUBSTRING(chars_str, FLOOR(1+rand()*52),1));
  SET i = i + 1;
 END while;
 RETURN return_str;
END $$  -- 符号内容需要和开始对应上

-- 随机产生部门编号
delimiter $$
CREATE FUNCTION rand_num() RETURNS INT(5)
BEGIN
  DECLARE I INT DEFAULT 0;
  SET I = FLOOR(100 + RAND() * 10);
RETURN I;
END $$;


-- 创建存储过程
delimiter $$ 
create procedure insert_emp(in start int(10),in max_num int(10))
begin
 declare i int default 0;
 set autocommit = 0;
 repeat
  set i = i+1;
  insert into emp(empno,ename,job,mgr,hiredate,sal,comm,deptno)                
  values((start+i),rand_string(6),'salesman',0001,curdate(),2000,400,rand_num());
  until i=max_num
 end repeat;
 commit;
end $$

delimiter $$ 
create procedure insert_dept(in start int(10),in max_num int(10))
begin
 declare i int default 0;
 set autocommit = 0;
 repeat
  set i = i+1;
  insert into dept(deptno,dname,loc) values((start+i),rand_string(10),rand_string(8));
  until i=max_num
 end repeat;
 commit;
end $$

select *from dept;
call insert_dept(100, 10);
call insert_emp(100, 10);
```

#### Show Profile

排查过程

1. 打开慢查询日志
2. 有问题sql 提取
3. explain 分析： 基本到这里能够找到问题，如果还找不到
4. show profile：
5. 和DBA配合，看节点参数，等服务器层面参数调优

> show profile 是 mysql 提供可以用来分析当前会话中语句执行的资源消耗情况，可以用于sql调优的测试，包括额底层物理资源的情况，包括查缓存等资源的消耗。
>
> 默认情况是关闭状态

 
