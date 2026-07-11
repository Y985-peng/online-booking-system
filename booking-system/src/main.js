import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 引入移动端适配（自动设置 rem）
import 'amfe-flexible'
// 引入 Vant 组件库样式
import 'vant/lib/index.css'
// 引入你自己的全局样式
import './assets/styles/global.css'
import './styles/responsive.css'
import './styles/mobile.css'

// 引入 Vant 所有组件
import Vant from 'vant'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Vant)

app.mount('#app')