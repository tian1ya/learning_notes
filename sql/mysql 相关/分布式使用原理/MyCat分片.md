#### 垂直分

由原有的所有业务表均在一个单数据库中，变为根据业务将不同的业务表分到不同的数据库中

![a](./pics/mycat10.png)

##### 案例，三个业务域

![a](./pics/mycat11.png)

具体表的拆分

![a](./pics/mycat12.png)

1. 根据右侧表和数据库的划分，上到下分别

```shell
3306 3307 3308 
```

脚本分别再三个数据库执行，注意这里不是在`mycat` 中执行全部脚本，而是在不同库中执行不同的脚本。

2. 配置`schema.xml` 进行垂直拆分配置

```xml
<?xml version="1.0"?>
<!DOCTYPE mycat:schema SYSTEM "schema.dtd">
<mycat:schema xmlns:mycat="http://io.mycat/">
	<schema name="ITCAST_DB" checkSQLschema="true" sqlMaxLimit="100">
        <- 一个表分配到一个dataNode 中，注意和水平分片的区别->
	   <table name="tb_areas_city" dataNode="dn1" primary_key="id" />
        <table name="tb_areas_provinces" dataNode="dn1" primary_key="id" />
        <table name="tb_areas_region" dataNode="dn1" primary_key="id" />
        <table name="tb_user" dataNode="dn1" primary_key="id" />
        <table name="tb_user_address" dataNode="dn1" primary_key="id" />
        
        <table name="tb_order_item" dataNode="dn2" primary_key="id" />
        <table name="tb_order_master" dataNode="dn2" primary_key="order_id" />
        <table name="tb_order_pay_log" dataNode="dn2" primary_key="out_trade_no" />

        <table name="tb_goods_base" dataNode="dn3" primary_key="id" />
        <table name="tb_goods_desc" dataNode="dn3" primary_key="goods_id" />
        <table name="tb_goods_item" dataNode="dn3" primary_key="id" />
	</schema>

	<dataNode name="dn1" dataHost="localhost1" database="user_db" /> 
	<dataNode name="dn2" dataHost="localhost2" database="order_db" />
	<dataNode name="dn3" dataHost="localhost3" database="goods_db" /> 

	<dataHost name="localhost1" maxCon="1000" minCon="10" balance="0"
			  writeType="0" dbType="mysql" dbDriver="native" switchType="1"  slaveThreshold="100">
		<heartbeat>select user()</heartbeat>
		<writeHost host="hostM1" url="localhost:3306" user="root" password="root"></writeHost>
	</dataHost>

  	<dataHost name="localhost2" maxCon="1000" minCon="10" balance="0"
			  writeType="0" dbType="mysql" dbDriver="native" switchType="1"  slaveThreshold="100">
		<heartbeat>select user()</heartbeat>
		<writeHost host="hostM1" url="localhost:3307" user="root" password="root"></writeHost>
	</dataHost>

  	<dataHost name="localhost3" maxCon="1000" minCon="10" balance="0"
			  writeType="0" dbType="mysql" dbDriver="native" switchType="1"  slaveThreshold="100">
		<heartbeat>select user()</heartbeat>
		<writeHost host="hostM1" url="localhost:3308" user="root" password="root"></writeHost>
	</dataHost>
	
</mycat:schema>
```

3. 配置`server.xml`

   因为换了逻辑库名字，配置文件中的 schemas 需要换

   ```xml
   <user name="root" defaultAccount="true">
   		<property name="password">root</property>
   		<property name="schemas">ITCAST_DB</property>
   </user>
   
   <user name="user">
       <property name="password">root</property>
       <property name="schemas">ITCAST_DB</property>
       <property name="usingDecrypt">true</property>
       <!-- <property name="readOnly">true</property> -->
   </user>
   ```

4. 重新启动`mycat`

   ```xml
   ./bin/mycat restart
   ```

5. mycat 表中可以查看到所有表

   ![a](./pics/mycat13.png)

   6. 在mycat 插入数据

      ```mysql
      insert  into `tb_order_pay_log`(`out_trade_no`,`create_time`,`pay_time`,`total_fee`,`user_id`,`transaction_id`,`trade_state`,`order_list`,`pay_type`) values ('1014520480276676908','2018-07-04 22:45:06',NULL,21097900,'java20',NULL,'0','1014520479974686720','1')
      ```

      从`mycat` 的客户端插入数据，根据`schema.xml` 中配置，会插入到具体的mysql 表中。

   7. 测试跨表分片的查询

      ```mysql
      SELECT order_id , payment ,receiver, province , city , area FROM tb_order_master o , tb_areas_provinces p , tb_areas_city c , tb_areas_region r
      WHERE o.receiver_province = p.provinceid AND o.receiver_city = c.cityid AND o.receiver_region = r.areaid ;
      ```

      报错

      ````shell
      1064 - invalid route in sql, multi tables found but datanode has no intersection  sql:SELECT order_id , payment ,receiver, province , city , area FROM tb_order_master o , tb_areas_provinces p , tb_areas_city c , tb_areas_region r
      WHERE o.receiver_province = p.provinceid AND o.receiver_city = c.cityid AND o.receiver_region = r.areaid
      ````

      发生跨库连接查询。

   8. 全局表

      是一张数据不多，表结构是属于全系统基础数据，很多库中的表都需要使用，**在每个节点/数据库中都会存储一份。**

      使用`navcate` 或者 数据库命令将`user` 的三张表`tb_areas_provinces p , tb_areas_city c , tb_areas_region`

      同步到其他两个库。(命令查看`./heima-mycat-note` 中关于课程老师提供的笔记)

   9. 全局表配置`schema.xml`

      ```xml
      <table name="tb_areas_city" dataNode="dn1,dn2,dn3" primaryKey="id" type="global"/>
      <table name="tb_areas_provinces" dataNode="dn1,dn2,dn3" primaryKey="id" type="global"/>
      <table name="tb_areas_region" dataNode="dn1,dn2,dn3" primaryKey="id" type="global"/>
      <- 指明 dataNode="dn1,dn2,dn3"  type="global" ->
      ```

   10. 重启`mycat`

       然后就可以夸库全局去查找了。

       ![a](./pics/mycat14.png)

   11. 更新全局表

       通过`mycat` 更新全局表之后，在3个`mysql` 中查看，也更新了。

   

#### 水平分

根据表中的数据的逻辑关系，将同一个表中的数据，按照某种条件拆分到多台数据库(主机)，多台数据库中存储的表结构是一样的，数据不一样。



#### 分片规则

