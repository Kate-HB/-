<template>
  <div class="dashboard">
    <nav>
      <h1>超市管理系统</h1>
      <button @click="logout">退出</button>
    </nav>
    <main>
      <h2>控制台</h2>
      <div class="dashboard-cards">
        <div class="card" @click="navigateTo('/products')">
          <h3>商品管理</h3>
          <p>管理商品信息</p>
        </div>
        <div class="card" @click="navigateTo('/')">
          <h3>销售管理</h3>
          <p>管理销售记录</p>
        </div>
        <div class="card" @click="navigateTo('/')">
          <h3>库存管理</h3>
          <p>查看库存状态</p>
        </div>
        <div class="card" @click="navigateTo('/')">
          <h3>数据分析</h3>
          <p>销售数据统计</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  router.push('/')
}

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #f0f0f0;
}

main {
  padding: 20px;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card h3 {
  margin-bottom: 10px;
  color: #333;
}

.card p {
  color: #666;
  font-size: 14px;
}

button {
  padding: 8px 16px;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
