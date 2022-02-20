#### 启动单独镜像

```shell
 docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql:5.7.25
```

