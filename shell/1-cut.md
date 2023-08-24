grep 命令是在文件中提取符合条件的行，也就是分析一行的信息，如果行中包含需要的信息，就把该行提取出来。**而如果要进行列提取，就要利用 cut 命令了**

虽然 cut 命令用于提取符合条件的列，但是也要一行一行地进行数据提取。也就是说，先要读取文本的第一行数据，在此行中判断是否有符合条件的字段，

然后再处理第二行数据。我们也可以把 cut 成为字段提取命令

```shell
cut [选项] 文件名
# -f 列号，提取第几列
# -d 分隔符，按照指定分隔符分割列；默认 \tab
# -c 字符范围：不依赖分隔符来区分列，而是通过字符范围（行首为 0）来进行
#   字段提取。"n-"表示从第 n 个字符到行尾；"n-m"表示从第 n 个字符到
#    第 m 个字符；"-m"表示从第 1 个字符到第 m 个字符；

# student.txt
# ID	Name	gender	Mark
# 1	Liming	M	86
# 2	Sc	M	90
# 3	Gao	M	83

[root@slave2 ~]# cut -f 2 student.txt
Name
Liming
Sc
Gao

[root@slave2 ~]# cut -f 2,3 student.txt
Name    gender
Liming  M
Sc      M
Gao     M

#提取取每行从第8个字符到行尾，好像很乱啊，那是因为每行的字符个数不相等
[root@slave2 ~]# cut -c 8- student.txt
        gender  Mark
g       M       86
90
        83

# 以":"作为分隔符，提取/etc/passwd文件的第一列和第三列
cut -d":" -f 1,3 /etc/passwd
```
