`Less`和`Sass`都是`Css`的一种预处理器。 转化成通俗易懂的话来说就是“用一种专门的编程语言，进行 `Web` 页面样式设计，再通过编译器转化为正常的 `CSS` 文件，以供项目使用

1、`Less`环境较`Sass`简单
2、`Less`使用较`Sass`简单
3、从功能出发，`Sass`较`Less`略强大一些
4、`Less`与`Sass`处理机制不一样（前者是通过客户端处理的，后者是通过服务端处理，相比较之下前者解析会比后者慢一点）
关于变量在`Less`和`Sass`中的唯一区别就是`Less用@，Sass用$`

### SCSS = CSS + 高级功能

高级功能有：

- 变量 (variables)
- 嵌套 (nested rules)
- 混合 (mixins)
- 导入 (inline imports) 
- 函数



使用 “缩进” 代替 “花括号” 表示属性属于某个选择器，用 “换行” 代替 “分号” 分隔属性，可以直接 `@import`到另一种格式中使用。

#### 使用变量

使用`$`符号来标识变量 

```scss
// 申明变量
$highlight-color: #F90;

$basic-border: 1px solid black;

// 使用变量
border: 1px solid $highlight-color;
```

变量名可以与`css`中的属性名和选择器名称相同，包括中划线和下划线。 

#### 嵌套CSS 规则

`css` 的写法

```css
#content article h1 { color: #333 }
#content article p { margin-bottom: 1.4em }
#content aside { background-color: #EEE }
```

`scss` 写法

```scss
#content {
  article {
    h1 { color: #333 }
    p { margin-bottom: 1.4em }
  }
  aside { background-color: #EEE }
}
```

 #### 父选择标识符`&`

```css
article a {
  color: blue;
  :hover { color: red }
}
```

本意是将`color: red`这条规则将会被应用到选择器`article a :hover` ，使用`&` 就可以达到效果，而是`&`被父选择器直接替换 

```css
article a {
  color: blue;
  &:hover { color: red }
}
```

编译过来的代码

```sscc
article a { color: blue }
article a:hover { color: red }
```

群组选择器的嵌套

```css
.container h1, .container h2, .container h3 { margin-bottom: .8em }

// scss
.container {
  h1, h2, h3 {margin-bottom: .8em}
}

article {
  // 等同于 article ~ article 选择所有跟在article后的同层article元素，不管它们之间隔了多少其他元素
  ~ article { border-top: 1px dashed #ccc }
  // 子选择器
  > section { background: #eee }
  dl > {
    dt { color: #333 }
    dd { color: #555 }
  }
  // 同层相邻组合选择器+选择header元素后紧跟的p元素
  nav + & { margin-top: 0 }
}
```

#### 导入`SCSS`

```javascript
@import "themes/night-sky";
```

#### 默认变量值

```css
$fancybox-width: 400px !default;

// 后续可以覆盖，当后续不覆盖直接使用的时候，就会使用默认值
.fancybox {
width: $fancybox-width;
}
```

#### 混合器`minin`

`@mixin`标识符 给一大段样式赋予一个名字，这样你就可以轻易地通过引用这个名字重用这段样式。 

```css
@mixin rounded-corners {
  -moz-border-radius: 5px;
  -webkit-border-radius: 5px;
  border-radius: 5px;
}
```

可以在你的样式表中通过`@include`来使用这个混合器，放在你希望的任何地方。 

```css
notice {
  background-color: green;
  border: 2px solid #00aa00;
  @include rounded-corners;
}

```

可以给`mixin` 传参数

```css
@mixin link-colors($normal, $hover, $visited) {
  color: $normal;
  &:hover { color: $hover; }
  &:visited { color: $visited; }
}

// 使用 
a {
  @include link-colors(blue, red, green);
}
```

可以指定默认值参数默认值使用`$name: default-value`的声明形式 

```css
@mixin link-colors(
    $normal,
    $hover: $normal,
    $visited: $normal
  )
{
  color: $normal;
  &:hover { color: $hover; }
  &:visited { color: $visited; }
}
```

#### 选择器继承 

一个选择器可以继承为另一个选择器定义的所有样式。 

```css
//通过选择器继承继承样式
.error {
  border: 1px solid red;
  background-color: #fdd;
}
.seriousError {
  @extend .error;
  border-width: 3px;
}
```

