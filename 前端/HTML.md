#### HTML

> `hyper text markup language`：超文本标记语言。网页显示的内容。
>
> 使用
>
> > `<标签名></标签名>`
>
> 标签
>
> > 标识出网页中不同的内容
>
> 根标签:  有且仅有一个根标签
>
> > <html></html>
>
> 子标签
>
> > 在根标签中的内容都是子标签
>
> ```html
> <html>
>   <head>
>     <!-- 网页的标题显示需要，不会出现在页面显示内容中,帮助浏览器解析网页 -->
>     <title>
>       出现在标题沿的内，不显示在网页中，或者在搜索引擎页面的搜索连接中的文字现实
>     </title>
>   </head>
> 
>   <body>
>     <!-- 网页主体，所有内容都显示在这里 -->
>       <h1>回乡偶书</h1>
>       <h2>其一</h2>
>       <h2>贺知章</h2>
>       <p>少小离家老大回</p>
>       <p>乡音无改鬓毛衰</p>
>       <p>儿童相见不相识</p>
>       <p>笑问客从何处来</p>
>   </body>
> </html>
> ```
>
> 自结束标签，单独存在的标签，
>
> > ```html
> > <img>
> > 或者
> > <img/>
> > 
> > <input>
> > 或者
> > <input/>
> > ```
>
> 标签中设置属性，只能在开始标签中设置属性，而不能在结束标签中设置属性
>
> ```html
> <html>
>   <head>
>     <!-- 网页的标题显示需要，不会出现在页面显示内容中 -->
>     <title>
>       标签的属性
>     </title>
>   </head>
> 
>   <body>
>     <h1>
>       <!-- 
>         有些标签有属性值如  color='red' 使用单或者双引号值
>         有些标签是没有值如  <font color>第三个</font>
> 
>         属性之间使用空格隔开
>        -->
>       这是<font color='red' size=3>第三个</font>网页
>     </h1>
>   </body>
> </html>
> ```
>
> 文档说明: doctype
>
> > ```html
> > <!doctype html>
> > <!-- 告诉浏览器当前使用的 html 的版本，严格意义说将并不是一个标签 -->
> > 
> > <html>
> >   <head>
> >     <title></title>
> >   </head>
> > 
> >   <body>
> >   </body>
> > </html>
> > ```
>
> meta 元数据标签设置网络的字符集，避免乱码，是给浏览器看的。
>
> Name: 指定数据名称
>
> content: 指定数据的内容
>
> charset: 编码方式
>
> keyword: 网页的关键字，如在搜索引擎搜索了`购物` 就出现了京东的网页，这是因为京东的网页的关键字中有这个字。
>
> 可以同时指定多个关键字，使用逗号隔开
>
> name 和 content 的配合使用
>
> Name 指定key 的名字，content 为这个key 的value
>
> > ```html
> > <html lang="en">
> > <head>
> > <meta charset="UTF-8">
> > <meta http-equiv="X-UA-Compatible" content="IE=edge">
> > <meta name="viewport" content="width=device-width, initial-scale=1.0">
> > <meta name="desription" content="京东网站，专业的网上综合商城">
> > <meta http-equiv="refresh", content="3;url='https://www.bilibili.com/">
> >   <!-- 
> > 		重定向，过3s 之后跳转到 bilibili
> > 		使用的比较少
> > 	-->
> > <title>实体</title>
> > </head>
> > <body>
> > </body>
> > </html>
> > ```
>
> 标签转义
>
> > ```html
> > <!DOCTYPE html>
> > <html lang="en">
> > <head>
> >   <meta charset="UTF-8">
> >   <meta http-equiv="X-UA-Compatible" content="IE=edge">
> >   <meta name="viewport" content="width=device-width, initial-scale=1.0">
> >   <title>实体</title>
> > </head>
> > <body>
> >   <p>今天&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;天气不错</p>
> >   <!-- 
> >     中间空格只会显示一个
> >     网页中编写多个空格浏览器会默认解析为一个空格
> > 
> >     html 中有些情况，不能直接书写特殊符号，如 字母两侧的大于和小于符号，这属于 html 的语法
> > 
> >     需要告诉浏览器，这些就是大于号和小于号，而不是html 的一些语法
> >  需要使用到 html 的转移号 &实体的名字;
> >    
> > -->
> > 
> >       <p>
> >      大于号 &gt2;
> >         小于号 &lt2;
> >         版权符号 &copy;
> >       </p>
> >    </body>
> >    </html>
> > ```
>

主题标签

使用 `html` 是负责网页的结构，所以在使用的时候，应该关注的是标签的语义，而不是它的样式。

> ```html
> <h1>一级标题</h1>
> <h2>二级标题</h2>
> <h3>三级标题</h3>
> <h4>四级标题</h4>
> <h5>五级标题</h5>
> <h6>六级标题</h6>
> ```
>
> 如上面的内容，直接显示出来的内容，一级标题是比较大的二级标题比较小，而这个大小就是样式的问题，可以使用 `CSS`调整二者的大小，也就是二级标题可以比一级标题还要大。
>
> 这里需要专注的是标签语义。
>
> 而这里的语意就是重要性，<h1> 到 <h6> 的重要性一次递减。
>
> 一般情况一个页面只会有一个 `h1`，一般情况只会到 <h3> 的标签

> p 标签
>
> > 表示的是在页面中的一个段落
> >
> > ```html
> > <p>p 标签表示一个段落</p>
> > <p>第二个 p 标签和上一个p 标签之间会有一个间隙</p>
> > 这里还需要强调，这里并不需要在乎2个p标签知己存在一个间隙，这个间隙是可以被CSS 调整的，而去关注这里的p 表示的是一个段落。
> > ```
>
> hgroup 标签，将标题分组，可以将一组相关的标题同时放入 hgroup 中进行分组
>
> ```html
> <hgroup>
>   <h1>回乡偶书二首</h1>
>   <h2>其一</h2>
> </hgroup>
> ```
>
> 

