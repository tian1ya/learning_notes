#### 关于setup

是新加的生命钩子函数，在beforeCreate钩子之前执行。原始写法应该是这样的

```javascript
export default {
    setup(){
      
    }
  }
```

可以简写为，语法糖

```javascript
<script setup></script>
```

也就是在`script` 中的内容都会在`beforeMounted` 之前执行。要定义其他的钩子函数

```javascript
<script setup>
  onMounted(() => {})
</script>
```

#### reactive和ref函数

用于在`<script setup></script>` 中，都用于构建响应式子数据，

`ref`接收简单类型或者对象类型的数据，`reactive` 用于接受对象类型，一般用`ref` 就好



#### computed 使用

```javascript
<script setup>
// 导入
import {ref, computed } from 'vue'
// 原始数据
const count = ref(0)
// 计算属性
const doubleCount = computed(()=>count.value * 2)

// 原始数据
const list = ref([1,2,3,4,5,6,7,8])
// 计算属性list
const filterList = computed(item=>item > 2)
</script>
```



#### watch 使用

```javascript
<script setup>
  // 1. 导入watch
  import { ref, watch } from 'vue'
  const count = ref(0)
  // 2. 调用watch 侦听变化
  watch(count, (newValue, oldValue)=>{
    console.log(`count发生了变化，老值为${oldValue},新值为${newValue}`)
  });

  watch([count, name], ([newCount, newName],[oldCount,oldName])=>{
    console.log(`count或者name变化了，[newCount, newName],[oldCount,oldName])
  },{
    immediate: true，deep:true
  });
</script>
```

`immediate` 配置，在侦听器创建时立即出发回调，响应式数据变化之后继续执行回调

` deep` 配置，对象的生成监听



#### 父传子

1. 父组件中给子组件绑定属性
2. 子组件内部通过props选项接收数据

```vue
// 父
const money = ref(100)
const getMoney = () => {
  money.value += 10
}

<SonCom car="宝马车" :money="money"></SonCom>

// 子
const props = defineProps({
  car: String,
  money: Number
})
```



#### 子传父

1. 父组件中给子组件标签通过@绑定事件
2. 子组件内部通过 emit 方法触发事件

```vue
// 子
const buy = () => {
  // 需要 emit 触发事件
  emit('changeMoney', 5)
}

<button @click="buy">花钱</button>

// 父
const changeFn = (newMoney) => {
  money.value = newMoney
}

<SonCom 
      @changeMoney="changeFn"
      car="宝马车" 
      :money="money">
    </SonCom>
```



#### 模板引用

模板引用(可以获取dom，也可以获取组件)

1. 调用ref函数，生成一个ref对象
2. 通过ref标识，进行绑定
3. 通过ref对象.value即可访问到绑定的元素(必须渲染完成后，才能拿到)

```javascript
const inp = ref(null)

const clickFn = () => {
  // 
  inp.value.focus()
}

// --------------------------------------
const testRef = ref(null)
const getCom = () => {
  console.log(testRef.value.count) // 调用值
  testRef.value.sayHi() // 调用方法
}

<div>
    <input ref="inp" type="text">
    <button @click="clickFn">点击让输入框聚焦</button>
</div>
<TestCom ref="testRef"></TestCom>
```

TestCom 实现

```javascript
<script setup>
const count = 999
const sayHi = () => {
  console.log('打招呼')
}

defineExpose({
  count,
  sayHi
})
</script>

<template>
  <div>
    我是用于测试的组件 - {{ count }}
  </div>
</template>
```



#### provide和inject

顶层组件向任意的底层组件传递数据和方法，实现**跨层组件通信**

```javascript
// 1. 跨层传递普通数据
provide('theme-color', 'pink')

// 2. 跨层传递响应式数据
const count = ref(100)
provide('count', count)

setTimeout(() => {
  count.value = 500
}, 2000)

// 3. 跨层传递函数 => 给子孙后代传递可以修改数据的方法
provide('changeCount', (newCount) => {
  count.value = newCount
})

</script>

<template>
<div>
  <h1>我是顶层组件</h1>
  <CenterCom></CenterCom>
</div>
</template>
```

CenterCom

```javascript
const themeColor = inject('theme-color')
const count = inject('count')
const changeCount = inject('changeCount')
// 这个函数是传递过来的，这里修改count的时候还是，count所在的组件修改的，这里仅仅是调用
// 函数的控制器还是在父亲那里
const clickFn = () => {
  changeCount(1000)
}
</script>

<template>
<div>
  <h3>我是底层组件-{{ themeColor }} - {{ count }}</h3>
  <button @click="clickFn">更新count</button>
</div>
</template>
```

#### 使用pnpm

npm install -g pnpm 



#### 配置代码风格

1. **安装了插件 ESlint，开启保存自动修复，用于校验错误, 创建工程的时候勾选上**
2. **禁用了插件 Prettier，并关闭保存自动格式化，用于美化代码**

项目中二者配合使用

```javascript
// ESlint插件 + Vscode配置 实现自动格式化修复
"editor.codeActionsOnSave": {
    "source.fixAll": true
},
"editor.formatOnSave": false,
```

**配置文件 .eslintrc.cjs**

1. prettier 风格配置 [https://prettier.io](https://prettier.io/docs/en/options.html )
   1. 单引号
   2. 不使用分号
   3. 每行宽度至多80字符
   4. 不加对象|数组最后逗号
   5. 换行符号不限制（win mac 不一致）
2. vue组件名称多单词组成（忽略index.vue）
3. props解构（关闭）

```javascript
  rules: {
    'prettier/prettier': [
      'warn',
      {
        singleQuote: true, // 单引号
        semi: false, // 无分号
        printWidth: 80, // 每行宽度至多80字符
        trailingComma: 'none', // 不加对象|数组最后逗号
        endOfLine: 'auto' // 换行符号不限制（win mac 不一致）
      }
    ],
    'vue/multi-word-component-names': [
      'warn',
      {
        ignores: ['index'] // vue组件名称多单词组成（忽略index.vue）
      }
    ],
    'vue/no-setup-props-destructure': ['off'], // 关闭 props 解构的校验
    // 💡 添加未定义变量错误提示，create-vue@3.6.3 关闭，这里加上是为了支持下一个章节演示。
    'no-undef': 'error'
  }
```



#### husky

husky 是一个 git hooks 工具  ( git的钩子工具，可以在特定时机执行特定的命令 )

在代码提交到仓库之前进行规范性检查

```javascript
pnpm dlx husky-init && pnpm install
```

修改 .husky/pre-commit 文件

```javascript
pnpm lint
// 这个命令在 package.json 中配置，
// 点开可以看到具体执行了那些事情
"lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs --fix --ignore-path .gitignore",
```

**问题：**默认进行的是全量检查，耗时问题，历史问题。**lint-staged 配置**

只对 git 暂存区的代码进行校验，暂存区是你编辑了的代码，也就是只会对你编辑后的代码进行检查。

```javascript
pnpm i lint-staged -D
```

配置 `package.json`

```javascript
{
  // ... 省略 ...
  "lint-staged": {
    "*.{js,ts,vue}": [
      "eslint --fix"
    ]
  }
}

{
  "scripts": {
    // ... 省略 ...
    "lint-staged": "lint-staged"
  }
}
```

#### element-ui 组件库

```javascript
pnpm add element-plus
```

**使用的组件自动按需：**

安装一下两个插件

```javascript
pnpm add -D unplugin-vue-components unplugin-auto-import
```

然后把下列代码插入到你的 `Vite` 配置文件中

```javascript
...
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    ...
    AutoImport({
      resolvers: [ElementPlusResolver()]
    }),
    Components({
      resolvers: [ElementPlusResolver()]
    })
  ]
})

```

#### Pinia 

构建用户仓库 和 持久化

```javascript
pnpm add pinia-plugin-persistedstate -D

// 在mian.js 中
import persist from 'pinia-plugin-persistedstate'
...
app.use(createPinia().use(persist))
```

使用 pinia

Pinia中的 getters 直接使用 computed函数 进行模拟, 组件中需要使用需要把 getters return出去

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

// 用户模块
export const useUserStore = defineStore(
  'big-user',
  () => {
    const token = ref('') // 定义 token
    const setToken = (t) => (token.value = t) // 设置 token

    return { token, setToken }
  },
  {
    persist: true // 持久化
  }
)

```

然后再使用的时候，直接将`useUserStore` 导入，然后执行`useUserStore()` 就可以获取到`return` 的数据

