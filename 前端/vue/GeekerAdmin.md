#### Vite 

启动命令

```shell
# 运行
# 以下两个命令都可以
pnpm dev
pnpm serve


# 打包
# 开发环境
pnpm build:dev

# 测试环境
pnpm build:test

# 生产环境
pnpm build:pro
```

配置

```javascript
// 开发服务器 (dev 命令) 运行在 development (开发) 模式，而 build 命令则运行在 production (生产) 模式
// mode：是生产/功能/开发环境配置
// command: 是当前项目的运行模式，开发模式返回 serve，生产环境返回 build
export default defineConfig(({ mode, command }) => {

  // 获取所有的环境变量，是一个大obj
  const env = loadEnv(mode, process.cwd())
  
 }
```

NProgress 

是一个轻量级的进度条组件,使用简便,可以很方便集成到单页面应用中 

`TypeScript 中的type 和 interface 语法`

> interface（接口） 是 TS 设计出来用于定义对象类型的，可以对对象的形状进行描述 
>
> type (类型别名)，顾名思义，类型别名只是给类型起一个新名字。**它并不是一个类型，只是一个别名而已** 
>
> 都可以定义一个对象或函数
>
> ```javascript
> type addType = (num1:number,num2:number) => number
> 
> interface addType {
>     (num1:number,num2:number):number
> }
> 
> const add:addType = (num1, num2) => {
>     return num1 + num2
> }
> ```
>
> 都允许继承（extends）
>
> ```javascript
> interface Person { 
>   name: string 
> }
> interface Student extends Person { 
>   grade: number 
> }
> 
> const person:Student = {
>   name: 'lin',
>   grade: 100
> }
> ```
>
> 类型别名会给一个类型起个新名字。 类型别名有时和接口很像，但是可以作用于原始值，联合类型，元组以及其它任何你需要手写的类型 
>
> ```javascript
> type Name = string                              // 基本类型
> 
> type arrItem = number | string                  // 联合类型
> 
> const arr: arrItem[] = [1,'2', 3]
> 
> type Person = { 
>   name: Name 
> }
> 
> type Student = Person & { grade: number  }       // 交叉类型
> 
> type Teacher = Person & { major: string  } 
> 
> type StudentAndTeacherList = [Student, Teacher]  // 元组类型
> 
> const list:StudentAndTeacherList = [
>   { name: 'lin', grade: 100 }, 
>   { name: 'liu', major: 'Chinese' }
> ]
> ```
>
> interface 可以，但是type不可以
>
> ```javascript
> interface Person {
>     name: string
> }
> 
> interface Person {         // 重复声明 interface，就合并了
>     age: number
> }
> 
> const person: Person = {
>     name: 'lin',
>     age: 18
> }
> ```

* interface 和 type 被 TS 设计出来，是完全不同的东西，有各自的职责。
* interface 是**接口**，用于描述一个对象。
* type 是**类型别名**，用于给各种类型定义别名，让 TS 写起来更简洁、清晰。
* 只是有时候两者都能实现同样的功能，才会经常被混淆，相信看完本文你能分清他俩了。
* 平时开发中，一般**使用组合或者交叉类型**的时候，用 type。
* 一般要用类的 **extends** 或 **implements** 时，用 interface。
* 其他情况，比如定义一个对象或者函数，就看你心情了。

pinia

有两种写法

* Option Store

```javascript
export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  getters: {
    double: (state) => state.count * 2,
  },
  actions: {
    increment() {
      this.count++
    },
  },
})
// 你可以认为 state 是 store 的数据 (data)，getters 是 store 的计算属性 (computed)，而 actions 则是方法 (methods)
```

Setup Store

可以传入一个函数，该函数定义了一些响应式属性和方法，并且返回一个带有我们想暴露出去的属性和方法的对象 

```javascript
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  function increment() {
    count.value++
  }

  return { count, increment }
})
```

在 *Setup Store* 中：

- `ref()` 就是 `state` 属性
- `computed()` 就是 `getters`
- `function()` 就是 `actions`

