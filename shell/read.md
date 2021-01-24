有时，脚本需要在执行过程中，由用户提供一部分数据，这时可以使用`read`命令。它将用户的输入存入一个变量，方便后面的代码使用。用户按下回车键，就表示输入结束。

```shell
#!/bin/bash

echo -n "输入一些文本>"
read text
echo "你的输入是: $text"

# ./readValue
# 输入一些文本>hdhdh
# 你的输入是: hdhdh
```

`read`命令的格式如下。

```
read [-options] [variable...]
```

`options`是参数选项，`variable`是用来保存输入数值的一个或多个变量名。如果没有提供变量名，环境变量`REPLY`会包含用户输入的一整行数据。

`read`可以接受用户输入的多个值

如果用户的输入项少于`read`命令给出的变量数目，那么额外的变量值为空。如果用户的输入项多于定义的变量，那么多余的输入项会包含到最后一个变量中。

`read`命令的`-t`参数，设置了超时的秒数。如果超过了指定时间，用户仍然没有输入，脚本将放弃等待，继续向下执行。

```shell
#!/bin/bash

echo -n "输入一些文本 > "
if read -t 3 response; then
  echo "用户已经输入了"
else
  echo "用户没有输入"
fi
```

`-p`参数指定用户输入的提示信息

```
read -p "Enter one or more values > "
echo "REPLY = '$REPLY'"
```

`-a`参数把用户的输入赋值给一个数组，从零号位置开始。

```
$ read -a people
alice duchess dodo
$ echo ${people[2]}
dodo
```