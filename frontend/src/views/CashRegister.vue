<template>
  <div>
    <div class="mb-6"><h2 class="text-2xl font-bold text-slate-800">POS 收银</h2><p class="text-sm text-slate-500 mt-0.5">快速收银结算</p></div>

    <div class="grid grid-cols-3 gap-6">
      <div class="col-span-2 space-y-4">
        <div class="bg-white rounded-2xl border border-slate-100 p-4">
          <div class="flex gap-x-3">
            <select v-model="selectedProduct" class="form-input flex-1">
              <option value="">选择商品</option>
              <option v-for="p in products" :key="p.product_id" :value="p.product_id">{{ p.product_name }} (库存: {{ p.stock_quantity || 0 }})</option>
            </select>
            <input v-model.number="addQty" type="number" min="1" class="form-input w-20" placeholder="数量" />
            <button @click="addToCart" class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors">
              <i class="fa-solid fa-plus mr-1"></i>添加
            </button>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-100 overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-4 py-2.5 text-left text-xs font-semibold text-slate-500">商品</th>
                <th class="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 w-24">单价</th>
                <th class="px-4 py-2.5 text-center text-xs font-semibold text-slate-500 w-20">数量</th>
                <th class="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 w-28">小计</th>
                <th class="w-10"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!cart.length">
                <td colspan="5" class="text-center py-12 text-slate-400">暂无商品，请选择商品添加</td>
              </tr>
              <tr v-for="(item, i) in cart" :key="i" class="border-t border-slate-50">
                <td class="px-4 py-2">{{ item.product_name }}</td>
                <td class="px-4 py-2 text-right">{{ item.unit_price.toFixed(2) }}</td>
                <td class="px-4 py-2 text-center">
                  <input v-model.number="item.quantity" type="number" min="1" class="form-input text-sm py-1 w-16 text-center" />
                </td>
                <td class="px-4 py-2 text-right font-medium">{{ (item.quantity * item.unit_price).toFixed(2) }}</td>
                <td class="px-1 py-2 text-center">
                  <button @click="cart.splice(i, 1)" class="text-red-400 hover:text-red-600"><i class="fa-solid fa-times"></i></button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-100 p-5 space-y-4 h-fit">
        <div>
          <label class="text-sm font-medium text-slate-600">会员</label>
          <select v-model="memberId" class="form-input mt-1">
            <option value="">非会员</option>
            <option v-for="m in members" :key="m.member_id" :value="m.member_id">{{ m.member_name }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-slate-600">收银员</label>
          <select v-model="employeeId" class="form-input mt-1" required>
            <option value="">选择收银员</option>
            <option v-for="e in employees" :key="e.employee_id" :value="e.employee_id">{{ e.employee_name }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-slate-600">支付方式</label>
          <select v-model="paymentMethod" class="form-input mt-1">
            <option value="cash">现金</option>
            <option value="wechat">微信</option>
            <option value="alipay">支付宝</option>
            <option value="card">银行卡</option>
          </select>
        </div>

        <div class="border-t border-slate-100 pt-4">
          <div class="flex justify-between text-sm mb-2">
            <span class="text-slate-500">商品数量</span>
            <span class="font-medium">{{ cart.reduce((s, i) => s + i.quantity, 0) }}</span>
          </div>
          <div class="flex justify-between text-lg font-bold mb-1">
            <span>合计</span>
            <span class="text-blue-600">¥ {{ total.toFixed(2) }}</span>
          </div>
          <div v-if="appliedPromos.length" class="mb-3 p-2 bg-amber-50 rounded-lg text-xs space-y-0.5">
            <div class="font-medium text-amber-700">已应用促销:</div>
            <div v-for="p in appliedPromos" :key="p" class="text-amber-600">{{ p }}</div>
            <div v-if="discountAmount > 0" class="text-emerald-600 font-medium">优惠: -¥ {{ discountAmount.toFixed(2) }}</div>
          </div>
          <div>
            <label class="text-sm font-medium text-slate-600">实收金额</label>
            <input v-model.number="amountReceived" type="number" step="0.01" min="0" class="form-input mt-1 text-lg font-bold" />
          </div>
          <div v-if="change > 0" class="flex justify-between text-sm mt-2 p-2 bg-emerald-50 rounded-lg">
            <span class="text-emerald-700">找零</span>
            <span class="font-bold text-emerald-700">¥ {{ change.toFixed(2) }}</span>
          </div>
        </div>

        <button @click="checkout" :disabled="checkingOut || !canCheckout"
          class="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg transition-colors disabled:opacity-50">
          <i v-if="checkingOut" class="fa-solid fa-spinner fa-spin mr-1"></i>
          {{ checkingOut ? '结算中...' : '结算 (Enter)' }}
        </button>
        <div v-if="error" class="text-red-500 text-sm text-center">{{ error }}</div>

        <div v-if="lastOrder" class="border-t border-slate-100 pt-3 mt-3">
          <div class="text-center text-sm text-slate-500">上次交易</div>
          <div class="flex justify-between text-sm">
            <span>单号: {{ lastOrder.order_number }}</span>
            <span>找零: ¥ {{ lastOrder.change }}</span>
          </div>
          <div v-if="lastOrder.promotions && lastOrder.promotions.length" class="text-xs text-amber-600 mt-1">
            促销: {{ lastOrder.promotions.join('、') }} 优惠 ¥{{ lastOrder.total_discount || 0 }}
          </div>
          <div v-if="lastOrder.points_earned" class="text-xs text-indigo-600 mt-0.5">
            获得积分: +{{ lastOrder.points_earned }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useAuthStore } from '@/stores/auth.js';
import { cashRegister } from '@/api/sales';
import { getProducts } from '@/api/products';
import { getEmployees } from '@/api/employees';
import { getMembers } from '@/api/members';

const auth = useAuthStore();

const products = ref([]);
const employees = ref([]);
const members = ref([]);
const selectedProduct = ref('');
const addQty = ref(1);
const cart = ref([]);
const memberId = ref('');
const employeeId = ref('');
const paymentMethod = ref('cash');
const amountReceived = ref(0);
const checkingOut = ref(false);
const error = ref('');
const lastOrder = ref(null);
const appliedPromos = ref([]);
const discountAmount = ref(0);
const pointsEarned = ref(0);

const total = computed(() => cart.value.reduce((s, i) => s + (i.quantity * i.unit_price), 0));
const change = computed(() => Math.max(0, (amountReceived.value || 0) - total.value));
const canCheckout = computed(() => cart.value.length > 0 && employeeId.value && total.value > 0 && (amountReceived.value || 0) >= total.value);

onMounted(async () => {
  try { const r = await getProducts({ per_page: 1000 }); products.value = r.data || []; } catch {}
  try { const r = await getEmployees({ per_page: 1000 }); employees.value = r.data || []; } catch {}
  try { const r = await getMembers({ per_page: 1000 }); members.value = r.data || []; } catch {}
  if (auth.user?.employee_id) employeeId.value = auth.user.employee_id;
  window.addEventListener('keydown', onKeydown);
});

watch(total, (val) => { amountReceived.value = val; });

onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));

function addToCart() {
  error.value = '';
  if (!selectedProduct.value) return;
  const p = products.value.find(x => x.product_id == selectedProduct.value);
  if (!p) return;
  const qty = Math.max(Number(addQty.value) || 1, 1);
  const currentQty = cart.value.find(x => x.product_id == selectedProduct.value)?.quantity || 0;
  const availableStock = Number(p.stock_quantity || 0);
  if (currentQty + qty > availableStock) {
    error.value = '库存不足';
    return;
  }
  const existing = cart.value.find(x => x.product_id == selectedProduct.value);
  const price = parseFloat(p.sale_price || p.base_price || 0);
  if (existing) {
    existing.quantity += qty;
    existing.subtotal = existing.quantity * existing.unit_price;
  } else {
    cart.value.push({ product_id: p.product_id, product_name: p.product_name, unit_price: price, quantity: qty, subtotal: qty * price });
  }
  selectedProduct.value = '';
  addQty.value = 1;
  amountReceived.value = total.value;
}

async function checkout() {
  if (!canCheckout.value) return;
  checkingOut.value = true;
  error.value = '';
  try {
    const res = await cashRegister({
      employee_id: employeeId.value,
      payment_method: paymentMethod.value,
      amount_received: amountReceived.value,
      member_id: memberId.value || null,
      items: cart.value.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.unit_price }))
    });
    lastOrder.value = res.data;
    appliedPromos.value = res.data.promotions || [];
    discountAmount.value = res.data.total_discount || 0;
    pointsEarned.value = res.data.points_earned || 0;
    cart.value = [];
    amountReceived.value = 0;
    memberId.value = '';
  } catch (e) {
    error.value = e.message;
  } finally {
    checkingOut.value = false;
  }
}

function onKeydown(e) {
  if (e.key === 'Enter') checkout();
}
</script>
