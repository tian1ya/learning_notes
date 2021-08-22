ES2017 标准引入了 async 函数，使得异步操作变得更加方便。



通过`async` 可以指定一个函数为异步函数 , 执行异步函数后才能使用`await.`
`await`的作用其实就是替代了`then`方法，将`resolve`的值直接返回，使用起来更加方便。



使用 `async` 标识的函数，会返回`promise` 对象，所以 该函数内部，可以添加任何的异步操作代码。可以将 `async` 函数，看做是多个异步操作，封装的 `promise` 对象，而await 表达式，就是`then`的语法糖。

```javascript
// promise 定义的异步操作
var p = new Promise(function(suc){
    setTimeout(function(){ // setTimeout 模仿一个异步操作
        suc(123)
    },3000)
})
// then 执行回调函数，也就是p实例化时，传入的suc 函数，then 回调函数的参数，作为 p 对象的返回值
p.then(function(num){console.log('end:',num)})  


// 整改成 async 方式
// 1. 先定义异步操作,异步操作有个返回值，作为回调函数的参数
function asyncFunction(){
    setTimeout(function(){
        return 123
    },3000)
}
async function main(){
    let num = await asyncFunction() ; // 返回 123
    nsole.log('end:',num); // 上文中，then 中的执行代码
}
```

