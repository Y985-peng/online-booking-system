import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

// 导入所有页面组件
import Home from '../views/Home.vue'
import ServiceDetail from '../views/ServiceDetail.vue'
import Booking from '../views/Booking.vue'
import Profile from '../views/Profile.vue'
import Orders from '../views/Orders.vue'
import Review from '../views/Review.vue'
import Publish from '../views/Publish.vue'
import Dashboard from '../views/Dashboard.vue'
import TimeSettings from '../views/TimeSettings.vue'
import Login from '../views/Login.vue'   // 新增
import Payment from '../views/Payment.vue'
import Admin from '../views/Admin.vue'
import Chat from '../views/Chat.vue'
import ChatConversation from '../views/ChatConversation.vue'
import PostList from '../views/PostList.vue'
import MyServices from '../views/MyServices.vue'
import PostDetailPage from '../views/PostDetailPage.vue'
import CategoryList from '../views/CategoryList.vue'

const routes = [
  
    {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }   // 登录页不需要认证
  },
  
    {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  
    {
  },
  
    {
    path: '/service/:id',
    name: 'ServiceDetail',
    component: ServiceDetail,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/booking',
    name: 'Booking',
    component: Booking,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/review',
    name: 'Review',
    component: Review,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/publish',
    name: 'Publish',
    component: Publish,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/time-settings',
    name: 'TimeSettings',
    component: TimeSettings,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/payment',
    name: 'Payment',
    component: Payment,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/chat/:id',
    name: 'ChatConversation',
    component: ChatConversation,
    meta: { requiresAuth: true }
  },
  
    
  {
    path: '/my-services',
    name: 'MyServices',
    component: MyServices,
    meta: { requiresAuth: true }
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: PostDetailPage,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/posts',
    name: 'PostList',
    component: PostList,
    meta: { requiresAuth: true }
  },
  
    {
    path: '/categories',
    name: 'Categories',
    component: CategoryList,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const isLoggedIn = !!userStore.token

  if (to.meta.requiresAuth && !isLoggedIn) {
    // 需要登录但未登录，跳转到登录页，并携带目标路径
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && isLoggedIn) {
    // 已登录时访问登录页，直接跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
