```python
def dateTimeSubtractDays(currentDateTime, days):
    return datetimeToStrFormat(currentDateTime - dt.timedelta(days))
    
def datetimeToStrFormat(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

def strToDateTime(strDateTime):
    return dt.datetime.strptime(strDateTime,'%Y-%m-%d %H:%M:%S')

def strDateTimeSubtractDays(strDateTime, days):
    strDateTime = strToDateTime(strDateTime)
    return dateTimeSubtractDays(strDateTime, days)
```

**——slots——**使用 

> ```
> python 作为动态语言，可以在实例化之后给实例临时添加属性或者方法
> __slots__ 来限制该class实例能添加的属性：
> __slots__ = ('name', 'age') 只允许刚给实例添加 name 和 age 的属性
> __slots__ = () 不允许给实例添加任何属性
> ```

**__new__ 和 __init__**

> ```
> __new__ 才是python 中真正的构造函数，而不是 __init__
> __init__方法做的事情是在对象创建好之后初始化变量, 也就是先会执行构造函数，然后再去执行 __init__ 方法
> 当返回对象时会自动调用__init__方法进行初始化。
> __new__方法是静态方法，而__init__是实例方法
> ```

**@property**

```python
@property 
装饰器就是负责把一个方法变成属性调用的，
主要解决
1. 如果直接获取该属性 VarLenSparseFeat.name 那么可能会出某些错误，如对该字段的一些校验等
2. 也可以写一个 get_name 的方法，去增加逻辑
该装饰器就是结合上述的2点

还可以有 setter 装饰器
    @name.setter
    """
    @property
    def name(self):
        return self.sparsefeat.name
# 在这个列子中xx.name 的时候就会调用这个方法，也已在方法中增加一些业务逻辑
```

