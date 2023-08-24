### `sass/scss`

> 是建立在 css 之上的一种专门的语言，为 css 增加了编程的特性，包括有
>
> * 变量
> * 嵌套
> * 混合
> * 继承

#### 变量

> 可以将反复使用的 `css` 属性值定义为变量，然后通过变量名来引用它们。
>
> `css` 使用`$` 符号标识变量(老版本使用`!`)

##### 变量声明

```scss
$highlight-color: #F90;
// 这里赋值和 css 使用是完全一致的

$basic-border:1px solid black;

// 可以在css 规则块内定义，那么就只能在该块内使用，也可以在块外面定义

$nav-color: F90;
nav {
   $width: 100px;
   width: $width;
   color: $nav-color
}

// 定义变量和使用变量是一样的
```

##### 中划线和下划线

```scss
// 在scss 中为了兼容不同使用者偏好，中划线和下划线都是一致的
$link-color: blue;

a {
    color: $link_color;
}

// ----- 上面的定义和下面的是一样的

$link_color: blue;

a {
    color: $link-color;
}
```

#### 嵌套规则

在 `css` 中使用 `id` 选择器使用，重复太多

```css
#content article h1 { color: #333 }
#content article p { margin-bottom: 1.4em }
#content aside { background-color: #EEE }
```

但是如果使用 `scss` 使用嵌套定义，且可读性更高

```scss
#content {
    article {
        h1 { color: #333}
        p { margin-botton: 1,4m }
    }
    aside {backgroud-color: #eee}
}
```

##### 父选择器 `&`

> 生效原理：当 `&` 出现的地方，编译后，就会被其父类替换

```scss
article a {
    color: blue;
    &:hover { color: red }
}
```

上面就会给 `article a` 上绑定 `hover`  ，编译之后

```scss
article a { color:blue }
article a:hover { color: red }
```

##### 群组选择器

> 在一个容器中选择多个元素进行相同的样式

```css
// css 使用
.container h1, .container h2, .container h3 { margin-bottom: .8em }
```

`scss` 使用

```scss
.container {
    h1, h2, h3 { margin-bottom: .8em }
}
```

或者这么使用

```css
nav, aside {
    a { color: blue } 
}
```

```scss
nav a, aside a { color: blue }
```

##### 子组合选择器和同层组合选择器

`>`:  选择直接子元素

`+`: 同层项链组合选择器

`~`: 同层全体选择器

```scss
article {
  ~ article { border-top: 1px dashed #ccc }
  > section { background: #eee }
  dl > {
    dt { color: #333 }
    dd { color: #555 }
  }
  nav + & { margin-top: 0 }
}
```



#### 使用 `SASS` 文件

```scss
@import "src/styles/mixin.scss";
```



#### 默认值

```scss
$link-color: blue;
$link-color: red;
a {
color: $link-color;
}
```



#### 混入

使用 `@mixin` 标识

```scss
@mixin rounded-corners {
  -moz-border-radius: 5px;
  -webkit-border-radius: 5px;
  border-radius: 5px;
}

// 使用
notice {
  background-color: green;
  border: 2px solid #00aa00;
  @include rounded-corners;
}
```

#### 带参数的混入

```scss
@mixin link-colors($normal, $hover, $visited) {
  color: $normal;
  &:hover { color: $hover; }
  &:visited { color: $visited; }
}

// 使用

a {
  @include link-colors(blue, red, green);
}

// 默认值参数

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

