可以利用`transform`功能实现文字或图像的旋转、缩放、倾斜、移动这4中类型的变形处理。

#### 旋转

使用rotate方法，在参数中加入角度值，角度值后面跟表示角度单位的“deg”文字即可，旋转方向为顺时针方向。

```css
transform：rotate（45deg）；
```



#### 缩放

使用scale方法来实现文字或图像的缩放处理，在参数中指定缩放倍率。

```css
transform：scale（0.5）；//缩小一半
```

可以分别指定元素的水平方向的放大倍率与垂直方向的放大倍率

```css
transform：scale（0.5，2）；//水平方向缩小一半，垂直方向放大一倍。
```

#### 倾斜

使用skew方法实现文字或图像的倾斜处理，在参数中分别指定水平方向上的倾斜角度与垂直方向上的倾斜角度。

```css
transform：skew（30deg，30deg）；//水平方向上倾斜30度，垂直方向上倾斜30度。
```



#### 移动

使用translate方法来移动文字或图像，在参数中分别指定水平方向上的移动距离与垂直方向上的移动距离。

```css
transform：translate（50px，50px）；// 水平方向上移动50px，垂直方向上移动50px
```



#### 对一个元素使用多种变形的方法

```css
transform：translate（150px，200px） rotate（45deg） scale（1.5）；
```



#### 指定变形的基准点

在使用transform方法进行文字或图像变形的时候，是以元素的中心点为基准点进行变形的。

transform-origin属性
使用该属性，可以改变变形的基准点。

```css
transform：rotate（45deg）；

transform-origin：left bottom；//把基准点修改为元素的左下角
```

指定属性值

基准点在元素水平方向上的位置：`left、center、right`

基准点在元素垂直方向上的位置：`top、center、bottom`

---

#### 3D变形功能

旋转

分别使用`rotateX`方法、`rotateY`方法、`rotateZ`方法使元素围绕`X`轴、`Y`轴、`Z`轴旋转，在参数中加入角度值，角度值后面跟表示角度单位的deg文字即可，旋转方向为顺时针旋转。

```css
transform：rotateX（45deg）；

transform：rotateY（45deg）；

transform：rotateZ（45deg）；

transform：rotateX（45deg） rotateY（45deg） rotateZ（45deg）；

transform：scale（0.5） rotateY（45deg） rotateZ（45deg）；
```

* 缩放

分别使用`scaleX`方法、`scaleY`方法、`scaleZ`方法使元素按`X`轴、`Y`轴、`Z`轴进行缩放，在参数中指定缩放倍率。

* 倾斜

分别使用skewX方法、skewY方法使元素在X轴、Y轴上进行顺时针方向倾斜（无skewZ方法），在参数中指定倾斜的角度



