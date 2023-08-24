tr，translate的简写，主要用于压缩重复字符，删除文件中的控制字符以及进行字符转换操作

```shell
tr [OPTION]... SET1 [SET2]
# -s 压缩重复字符
# -d：delete，删除SET1中指定的所有字符，不转换
# -t：truncate，将SET1中字符用SET2对应位置的字符进行替换，一般缺省为-t

[root@slave2 ~]# echo "aaaabbbbb   ccccc" | tr -s [abc" "]
ab c

# 可以使用这一特点，删除文件中的空白行

[root@slave2 ~]# echo "123aAfdFRSaaabbbbb   ccccc" | tr -d [a-z][A-Z]
123

[root@slave2 ~]# echo "aaaabbbbb   ccccc" | tr -t [abc] [ABC]       AAAABBBBB   CCCCC


```
