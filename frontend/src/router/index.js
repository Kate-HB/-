import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/products',
    name: 'products',
    component: () => import('@/views/ProductManagement.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
