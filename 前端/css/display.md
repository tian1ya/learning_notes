主要用来控制元素的布局，通过 `display` 属性您可以设置元素是否显示以及如何显示。

根据元素类型的不同，每个元素都有一个默认的` display` 属性值，例如`<div>`默认的 `display` 属性值为 `block`（块级元素），而`<span>`默认的 display 属性值为` inline`（行内元素），您也可以手动将元素的 `display` 属性转换为其它值。`display` 属性的可选值如下：



| none               | 隐藏元素                                                     |
| ------------------ | ------------------------------------------------------------ |
| block              | 将元素设置为块级元素                                         |
| inline             | 将元素设置为内联元素                                         |
| list-item          | 将元素设置为列表项目                                         |
| inline-block       | 将元素设置为行内块元素                                       |
| table              | 将元素设置为块元素级的表格（类似`<table>`）                  |
| inline-table       | 将元素设置为内联元素级的表格（类似`<table>`）                |
| table-caption      | 将元素设置为表格的标题（类似`<caption>`）                    |
| table-cell         | 将元素设置为表格的单元格（类似`<td>`和`<th>`）               |
| table-row          | 将元素设置为表格的行（类似`<tr>`）                           |
| table-row-group    | 将元素设置为表格的内容部分（类似`<tbody>`）                  |
| table-column       | 将元素设置为表格的列（类似`<col>`）                          |
| table-column-group | 将元素设置为表格中一个或多个列的分组（类似`<colgroup>`）     |
| table-header-group | 将元素设置为表格的头部（类似`<thead>`）                      |
| table-footer-group | 将元素设置为表格的脚（类似`<tfoot>`）                        |
| box                | CSS3 中新增的属性值，表示将对象设置为弹性伸缩盒（伸缩盒的最老版本） |
| inline-box         | CSS3 中新增的属性值，表示将对象设置为内联元素级的弹性伸缩盒（伸缩盒的最老版本） |
| flexbox            | CSS3 中新增的属性值，表示将对象设置为弹性伸缩盒（伸缩盒的过渡版本） |
| inline-flexbox     | CSS3 中新增的属性值，表示将对象设置为内联元素级的弹性伸缩盒（伸缩盒的过渡版本） |
| flex               | CSS3 中新增的属性值，表示将对象设置为弹性伸缩盒（伸缩盒的最新版本） |
| inline-flex        | CSS3 中新增的属性值，表示将对象设置为内联元素级的弹性伸缩盒（伸缩盒的最新版本） |
| run-in             | 根据上下文来决定将元素设置为块级元素或内联元素               |
| inherit            | 从父元素继承 display 属性的值                                |



---



下面通过几个常用的属性值来介绍以下 `display` 属性的使用：

## display: none

在隐藏元素的同时，它还会将元素所占的位置一并隐藏

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        div {
            width: 350px;
            height: 100px;
            background-color: #AAA;
        }
    </style>
</head>
<body>
    <div id="box"> box
    </div>
    <button onclick="change_box(this)">隐藏</button>
    <script>
        function change_box(obj){
            var box = document.getElementById('box');
            if(box.style.display == 'none'){
                box.style.display = "";
                obj.innerHTML = "隐藏";
            }else{
                box.style.display = "none";
                obj.innerHTML = "显示";
            }
        }
    </script>
</body>
</html>
```

## display: block

display 属性的属性值 block 可以将元素强制转换为块级元素，示例代码如下：

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        a{
            display: block;
            width: 150px;
            height: 50px;
            background-color: #ACC;
            line-height: 50px;
            text-align: center;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <a href="">这是一个链接</a>
</body>
</html>
```

## display: inline

display 属性的属性值 inline 可以将元素强制转换为行内元素，让元素拥有行内元素的特性，例如可以与其他行内元素共享一行等，示例代码如下：

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        div {
            width: 50px;
            height: 50px;
            background-color: #ACC;
            border: 1px solid black;
        }
        .inline {
            display: inline;
        }
    </style>
</head>
<body>
    <div></div>
    <div></div>
    <div class="inline">display: inline;</div>
    <div class="inline">display: inline;</div>
</body>
</html>
```

## display: inline-block

display 属性的属性值 inline-block 可以将元素强制转换为行内块元素，inline-block 既具有 block 能够设置宽高的特性又具有 inline 不独占一行的特性，示例代码如下：

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        div {
            width: 130px;
            height: 50px;
            background-color: #ACC;
            border: 1px solid black;
        }
        .inline-block {
            display: inline-block;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div></div>
    <div></div>
    <div class="inline-block">display: inline-block;</div>
    <div class="inline-block">display: inline-block;</div>
</body>
</html>
```

#### display:flex 

是一种布局方式。它即可以应用于容器中，也可以应用于行内元素。是W3C提出的一种新的方案，可以简便、完整、响应式地实现各种页面布局。目前，它已经得到了所有浏览器的支持。

Flex是Flexible Box的缩写，意为"弹性布局"，用来为盒状模型提供最大的灵活性。设为Flex布局以后，子元素的float、clear和vertical-align属性将失效。

