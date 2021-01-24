![a](./pics/mysql_layers.png)

Mysql 默认使用 `InnoDB` 的数据库，在创建表的时候可以指定数据库

```mysql
create table tf(
	id int(4) auto_increment,
  name varchar(5),
  dept varchar(5),
  primary key(id)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

# AUTO_INCREMENT=1; 指定主键 id 的递增单位是1，也就是id的取值会是1，2，3，4
# 如果 AUTO_INCREMENT=2; 那么 id的值就会是 1,3,5 等
```

---

#### SQL 优化

* sql 性能低
* 执行时间长
* 等待时间长
* sql 语句欠佳(连接查询)
* 索引失效
* 服务器参数设置失效

##### sql 解析过程

**书写过程**

```sql
select (distinct)... from join ... on ... where ... grroup by ... having ... order by ... limit
```

**解析过程**

```sql
from .. on .. join .. where .. group by .. having .. select (distinct).. order by .. limit 
```

