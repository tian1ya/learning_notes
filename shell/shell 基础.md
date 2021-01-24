**cp**

> move them into other directories to organize them, or rename them. One command to do this is `cp`, which is short for "copy".

**mv**

> `mv` moves it from one directory to another, just as if you had dragged it in a graphical file browser. It handles its parameters the same way as `cp`, so the command:

```shell
mv seasonal/spring.csv seasonal/summer.csv ./backup/
```

> `mv` can also be used to rename files. If you run:One warning: just like `cp`, `mv` will overwrite existing files. If, for example, you already have a file called `old-course.txt`, then the command shown above will replace it with whatever is in `course.txt`

**rm**

> `mv` treats directories the same way it treats files: if you are in your home directory and run `mv seasonal by-season`, for example, `mv` changes the name of the `seasonal` directory to `by-season`. However, `rm` works differently.
>
> If you try to `rm` a directory, the shell prints an error message telling you it can't do that, primarily to stop you from accidentally deleting an entire directory full of work. Instead, you can use a separate command called `rmdir`. For added safety, it only works when the directory is empty, so you must delete the files in a directory *before* you delete the directory. (Experienced users can use the `-r` option to `rm` to get the same effect

**cat**

> Before you rename or delete files, you may want to have a look at their contents. The simplest way to do this is with `cat`, which just prints the contents of files onto the screen. (Its name is short for "concatenate", meaning "to link things together", since it will print all the files whose names you give it, one after the other.)

**less**

> You can use `cat` to print large files and then scroll through the output, but it is usually more convenient to **page** the output. The original command for doing this was called `more`, but it has been superseded by a more powerful command called `less`. (This kind of naming is what passes for humor in the Unix world.) When you `less` a file, one page is displayed at a time; you can press spacebar to page down or type `q` to quit.
>
> If you give `less` the names of several files, you can type `:n` (colon and a lower-case 'n') to move to the next file, `:p` to go back to the previous one, or `:q` to quit.

**head**

> We can do this in the shell using a command called `head`. As its name suggests, it prints the first few lines of a file (where "a few" means 10), so the command:
>
> `head` will only display the first three lines of the file. If you run `head -n 100`, it will display the first 100 (assuming there are that many), and so on.

**ls**

> ls -R
>
> In order to see everything underneath a directory, no matter how deeply nested it is, you can give `ls` the flag `-R` (which means "recursive")

**tail**

> tail -n +7 seasonal/spring.csv

> `head` and `tail` let you select rows from a text file. If you want to select columns, you can use the command `cut`. It has several options (use `man cut` to explore them)

```shell
cut -f 2-5,8 -d , values.csv
```

> which means "select columns 2 through 5 and columns 8, using comma as the separator". `cut` uses `-f` (meaning "fields") to specify columns and `-d` (meaning "delimiter") to specify the separator. You need to specify the latter because some files may use spaces, tabs, or colons to separate columns.

```she
cut -d, -f1 seasonal/spring.csv
cut -d, -f 1 seasonal/spring.csv
```

> `cut` is a simple-minded command. In particular, it doesn't understand quoted strings. If, for example, your file is:
>
> > me,Age
> > "Johel,Ranjit",28
> > "Sharma,Rupinder",26
>
> cut -f 2 -d , sam
>
> > Age
> > Ranjit"
> > Rupinder"
>
> rather than everyone's age, because it will think the comma between last and first names is a column separator.

**rerun**

> You can also re-run a command by typing an exclamation mark followed by the command's name, such as `!head` or `!cut`, which will re-run the most recent use of that command.

还可以这样: Re-run `head` again using `!` followed by a command number.

```shell
history
    1  head sum.csv
    2  head summer.csv
    3  head seasonal/summer.csv
    4  pwd
    5  cd seasonal/
    6  head seasonal/summer.csv
    7  head summer.csv
    8  head summer.csv
    9  history
$ !8
```

**grep**

> `grep` can search for patterns as well; we will explore those in the next course. What's more important right now is some of `grep`'s more common flags:

```shell
-c: print a count of matching lines rather than the lines themselves
-h: do not print the names of files when searching multiple files
-i: ignore case (e.g., treat "Regression" and "regression" as matches)
-l: print the names of files that contain matches, not the matches
-n: print line numbers for matching lines
-v: invert the match, i.e., only show lines that don't match
```

> Invert the match to find all of the lines that *don't* contain the word `molar` in `seasonal/spring.csv`, and show their line numbers. Remember, it's considered good style to put all of the flags *before* other values like filenames or the search term "molar".
>
> > cat seasonal/spring.csv | grep -n -v molar
>
> Count how many lines contain the word `incisor` in `autumn.csv` and `winter.csv` combined. (Again, run a single command from your home directory.)
>
> > grep -c incisor seasonal/autumn.csv seasonal/winter.csv

**\>**

> The greater-than sign `>` tells the shell to redirect `head`'s output to a file. It isn't part of the `head` command; instead, it works with every shell command that produces output.

> Suppose you want to get lines from the middle of a file. More specifically, suppose you want to get lines 3-5 from one of our data files. You can start by using `head` to get the first 5 lines and redirect that to a file, and then use `tail` to select the last 3:

**pipe**

```shell
head -n 5 seasonal/summer.csv | tail -n 3
cut -d , -f 2 seasonal/summer.csv | grep -v Tooth
cut -d , -f 2 seasonal/summer.csv | grep -v Tooth | head -n 1
```

**wc**

> The command `wc` (short for "word count") prints the number of **c**haracters, **w**ords, and **l**ines in a file. You can make it print only one of these using `-c`, `-w`, or `-l` respectively.
>
> -l --lines: pring new line counts
>
> -w pring words counts

> grep 2017-07 seasonal/spring.csv | wc -l



**How can I specify many files at once?**

> Most shell commands will work on multiple files if you give them multiple filenames. For example, you can get the first column from all of the seasonal data files at once like this
>
> use wildcars（通配符）

```shell
cut -d , -f 1 seasonal/winter.csv seasonal/spring.csv
cut -d , -f 1 seasonal/*.csv
head -n 3 seasonal/s*.csv
```

> The shell has other wildcards as well, though they are less commonly used:
>
> - `?` matches a single character, so `201?.txt` will match `2017.txt` or `2018.txt`, but not `2017-01.txt`.
> - `[...]` matches any one of the characters inside the square brackets, so `201[78].txt` matches `2017.txt` or `2018.txt`, but not `2016.txt`.
> - `{...}` matches any of the comma-separated patterns inside the curly brackets, so `{*.txt, *.csv}` matches any file whose name ends with `.txt` or `.csv`, but not files whose names end with `.pdf`.

**sort**

> As its name suggests, `sort` puts data in order. By default it does this in ascending alphabetical order, but the flags `-n` and `-r` can be used to sort numerically and reverse the order of its output, while `-b` tells it to ignore leading blanks and `-f` tells it to **f**old case (i.e., be case-insensitive). Pipelines often use `grep` to get rid of unwanted records and then `sort` to put the remaining records in order.

```shell
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort -r
```

**remove duplicated lines**

> Another command that is often used with `sort` is `uniq`, whose job is to remove duplicated lines. More specifically, it removes *adjacent* duplicated lines

```shell
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort | uniq -c
# -c line number of occurence
```

**shell store information**

> Like other programs, the shell stores information in variables. Some of these, called **environment variables**, are available all the time. Environment variables' names are conventionally written in upper case, and a few of the more commonly-used ones are shown below.

```shell
set | grep HISTFILESIZE
# 查询存储的值， 输出  2000
```

**变量**

```shell
training=seasonal/summer.csv
head -n 1 $testing
```

**for loop**

```shell
for filetype in gif, png; do echo $filetype; done
for filename in seasonal/*.csv; do echo $filename; done
for filename in people/*; do echo $filename; done

for file in seasonal/*.csv; do head -n 2 $file | tail -n 1; done
for file in seasonal/*.csv; do grep 2017-07 $file | tail -n 1; done
```

---

* **find**

```shell
内容查找
find . -name demo.tf 区分大小写查找
find . -iname demo.tf 不区分大小写查找
```

* tar

```shell
tar -cvf 压缩文件
tar -tvf 建压缩
```

* df (Disk space Free)

```shell
df 查看系统中磁盘的使用情况，硬盘已用和可用的存储空间以及它存储设备。 可以使用df -h将结果以人类可读的方式显示。
```

* ps （ProcessS）

```shell
显示系统的运行进程
```

* top (top processes)

```shell
安装cpu 的占用情况，显示较大的进程，可以使用top -u 查看某个用户的CPU 使用排序情况
```

* **free**

```shell
查看内存使用情况
```

