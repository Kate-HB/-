<template>
  <div class="product-management">
    <nav>
      <h1>超市管理系统</h1>
      <button @click="logout">退出</button>
    </nav>
    <main>
      <div class="container">
        <h2>商品管理</h2>
        
        <div class="tabs">
          <button 
            :class="{ active: activeTab === 'add' }"
            @click="activeTab = 'add'"
          >
            商品录入
          </button>
          <button 
            :class="{ active: activeTab === 'list' }"
            @click="activeTab = 'list'"
          >
            商品列表
          </button>
        </div>
        
        <!-- 商品录入表单 -->
        <div v-if="activeTab === 'add'" class="form-container">
          <h3>商品信息录入</h3>
          <form @submit.prevent="addProduct">
            <div class="form-group">
              <label for="name">商品名称</label>
              <input 
                type="text" 
                id="name" 
                v-model="product.name" 
                required 
                placeholder="请输入商品名称"
              />
            </div>
            
            <div class="form-group">
              <label for="price">商品价格</label>
              <input 
                type="number" 
                id="price" 
                v-model.number="product.price" 
                required 
                min="0" 
                step="0.01"
                placeholder="请输入商品价格"
              />
            </div>
            
            <div class="form-group">
              <label for="quantity">库存数量</label>
              <input 
                type="number" 
                id="quantity" 
                v-model.number="product.quantity" 
                required 
                min="0"
                placeholder="请输入库存数量"
              />
            </div>
            
            <div class="form-group">
              <label for="category">商品分类</label>
              <select id="category" v-model="product.category" required>
                <option value="">请选择分类</option>
                <option value="食品">食品</option>
                <option value="饮料">饮料</option>
                <option value="日用品">日用品</option>
                <option value="电子产品">电子产品</option>
                <option value="其他">其他</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button type="submit" class="btn-primary">保存</button>
              <button type="button" class="btn-secondary" @click="resetForm">重置</button>
            </div>
          </form>
          
          <div v-if="message" :class="['message', messageType]">
            {{ message }}
          </div>
        </div>
        
        <!-- 商品列表 -->
        <div v-else-if="activeTab === 'list'" class="list-container">
          <h3>商品列表</h3>
          <div class="search-bar">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜索商品名称或分类"
            />
          </div>
          
          <table class="product-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>商品名称</th>
                <th>价格</th>
                <th>库存</th>
                <th>分类</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProducts" :key="product.id">
                <td>{{ product.id }}</td>
                <td>{{ product.name }}</td>
                <td>¥{{ product.price.toFixed(2) }}</td>
                <td>{{ product.quantity }}</td>
                <td>{{ product.category }}</td>
                <td>
                  <button class="btn-edit" @click="editProduct(product)">编辑</button>
                  <button class="btn-delete" @click="deleteProduct(product.id)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="filteredProducts.length === 0" class="empty-state">
            <p>暂无商品数据</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态管理
const activeTab = ref('add')
const product = ref({
  name: '',
  price: 0,
  quantity: 0,
  category: ''
})
const products = ref([])
const searchQuery = ref('')
const message = ref('')
const messageType = ref('success')

// 计算属性：过滤商品列表
const filteredProducts = computed(() => {
  if (!searchQuery.value) {
    return products.value
  }
  const query = searchQuery.value.toLowerCase()
  return products.value.filter(product => 
    product.name.toLowerCase().includes(query) || 
    product.category.toLowerCase().includes(query)
  )
})

// 方法：获取商品列表
const fetchProducts = async () => {
  try {
    const response = await fetch('/api/products')
    if (response.ok) {
      products.value = await response.json()
    }
  } catch (error) {
    console.error('获取商品列表失败:', error)
  }
}

// 方法：添加商品
const addProduct = async () => {
  try {
    const response = await fetch('/api/products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(product.value)
    })
    
    if (response.ok) {
      message.value = '商品添加成功'
      messageType.value = 'success'
      resetForm()
      fetchProducts()
      
      // 3秒后清除消息
      setTimeout(() => {
        message.value = ''
      }, 3000)
    } else {
      message.value = '商品添加失败'
      messageType.value = 'error'
    }
  } catch (error) {
    console.error('添加商品失败:', error)
    message.value = '网络错误，请稍后重试'
    messageType.value = 'error'
  }
}

// 方法：编辑商品
const editProduct = (productData) => {
  // 这里可以实现编辑功能，例如打开编辑对话框
  console.log('编辑商品:', productData)
}

// 方法：删除商品
const deleteProduct = async (id) => {
  if (confirm('确定要删除这个商品吗？')) {
    try {
      const response = await fetch(`/api/products/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        message.value = '商品删除成功'
        messageType.value = 'success'
        fetchProducts()
        
        // 3秒后清除消息
        setTimeout(() => {
          message.value = ''
        }, 3000)
      } else {
        message.value = '商品删除失败'
        messageType.value = 'error'
      }
    } catch (error) {
      console.error('删除商品失败:', error)
      message.value = '网络错误，请稍后重试'
      messageType.value = 'error'
    }
  }
}

// 方法：重置表单
const resetForm = () => {
  product.value = {
    name: '',
    price: 0,
    quantity: 0,
    category: ''
  }
}

// 方法：退出登录
const logout = () => {
  router.push('/')
}

// 组件挂载时获取商品列表
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-management {
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

.container {
  max-width: 1000px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  transition: all 0.3s;
}

.tabs button.active {
  border-bottom-color: #1890ff;
  color: #1890ff;
  font-weight: bold;
}

.form-container {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary {
  padding: 10px 20px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-secondary {
  padding: 10px 20px;
  background: #f0f0f0;
  color: #333;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #e0e0e0;
  border-color: #b3b3b3;
}

.message {
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  text-align: center;
}

.message.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.message.error {
  background: #fff1f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

.list-container {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-bar {
  margin-bottom: 16px;
}

.search-bar input {
  width: 100%;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.product-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.product-table th,
.product-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e8e8e8;
}

.product-table th {
  background: #fafafa;
  font-weight: 600;
  color: #333;
}

.product-table tr:hover {
  background: #f5f5f5;
}

.btn-edit {
  padding: 6px 12px;
  background: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 8px;
  transition: background-color 0.3s;
}

.btn-edit:hover {
  background: #73d13d;
}

.btn-delete {
  padding: 6px 12px;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-delete:hover {
  background: #ff7875;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
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