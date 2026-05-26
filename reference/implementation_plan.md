# 鲜丰超市管理系统 - 完整实施方案

> 基于 `supermarket_ui_full.html` 原型设计，数据库49张表已就绪，MySQL已连接。

---

## 一、项目现状分析

### 1.1 已完成

| 层面 | 状态 | 说明 |
|------|------|------|
| 数据库 | 完成 | MySQL `supermarket` 库，49张表已建好，含测试数据 |
| 后端连接 | 完成 | `mysql+pymysql://root:123456@localhost:3306/supermarket` |
| 后端模型 | 部分 | 已定义 User/Category/Supplier/Product/Warehouse/Inventory/SalesOrder/SalesOrderItem 共8个模型 |
| 后端API | 部分 | `/api/login` `/api/register` `/api/products`(CRUD) `/api/sales`(POST) `/api/health` |
| 前端框架 | 完成 | Vue3 + Vite + Vue Router + Pinia |
| 前端页面 | 部分 | 仅 Login.vue 和 ProductManagement.vue 有实际API调用 |
| 前端路由 | 部分 | `/login` `/dashboard` `/products`，其余指向 `/` |

### 1.2 待完成模块统计

根据原型 HTML，共 **10大模块、28个子模块**：

| # | 模块 | 子模块 | 对应数据表 | 后端API | 前端页面 |
|---|------|--------|-----------|---------|---------|
| 1 | 首页仪表盘 | 1个 | 多表聚合统计 | 待开发 | 待开发 |
| 2 | 商品管理 | 3个 | products/categories/promotions | 部分完成 | 部分完成 |
| 3 | 供应商管理 | 3个 | suppliers/contracts/evaluations | 待开发 | 待开发 |
| 4 | 采购管理 | 2个 | purchase_orders/inbound_records | 待开发 | 待开发 |
| 5 | 仓库管理 | 4个 | warehouses/inventory/inbound/outbound | 待开发 | 待开发 |
| 6 | 销售管理 | 3个 | sales_orders/returns/statistics | 1个完成 | 待开发 |
| 7 | 会员管理 | 3个 | members/levels/points_records | 待开发 | 待开发 |
| 8 | 员工管理 | 3个 | employees/schedules/payrolls | 待开发 | 待开发 |
| 9 | 财务管理 | 3个 | cash_records/journal_entries/budgets | 待开发 | 待开发 |
| 10 | 系统管理 | 4个 | users/roles/permissions/logs/configs | 部分完成 | 待开发 |

---

## 二、技术架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue 3 + Vite)                │
│  port 3000                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │  Login   │ │ Dashboard│ │  28 模块页面组件      │ │
│  │  .vue    │ │  .vue    │ │  ProductManagement    │ │
│  │          │ │          │ │  SupplierManagement   │ │
│  │          │ │          │ │  PurchaseManagement   │ │
│  │          │ │          │ │  ...共28个            │ │
│  └──────────┘ └──────────┘ └──────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │              Pinia Store (状态管理)               │ │
│  │  useAuthStore / useProductStore / ...           │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │           API Service Layer (api/*.js)           │ │
│  │  统一请求封装、错误处理、Token注入                │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ /api/*
                       ▼
┌─────────────────────────────────────────────────────┐
│                  后端 (Flask + SQLAlchemy)            │
│  port 5000                                            │
│  ┌─────────────────────────────────────────────────┐ │
│  │              REST API 路由层                      │ │
│  │  /api/login  /api/products  /api/suppliers ...  │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │              SQLAlchemy 模型层 (49表)             │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              MySQL 8.0 (supermarket)                 │
│              port 3306                                │
│              49张表，完整外键约束                      │
└─────────────────────────────────────────────────────┘
```

### 技术栈明细

| 层面 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 (Composition API + `<script setup>`) | 3.x |
| 构建工具 | Vite | 5.x |
| UI样式 | Tailwind CSS (CDN) | 3.x |
| 图标库 | Font Awesome | 6.5.1 |
| 状态管理 | Pinia | 2.x |
| 路由 | Vue Router | 4.x |
| HTTP | fetch (原生) | - |
| 后端框架 | Flask | 2.3.3 |
| ORM | Flask-SQLAlchemy | 3.0.5 |
| 数据库驱动 | PyMySQL | 1.x |
| 密码哈希 | Werkzeug | - |
| 跨域 | Flask-CORS | 4.0.0 |

---

## 三、后端实施计划

### 3.1 模型补全（APP.py）

当前已定义8个模型，需补全剩余41张表的模型定义：

**需新增的模型（按依赖顺序）：**

```
Position        → positions
Employee        → employees (已有，需补字段)
SupplierContract → supplier_contracts
SupplierEvaluation → supplier_evaluations
PurchaseOrder   → purchase_orders
PurchaseOrderItem → purchase_order_items
Promotion       → promotions
PromotionProduct → promotion_products
ProductPrice    → product_prices
InventoryDetail → inventory_details
InboundRecord   → inbound_records
InboundItem     → inbound_items
OutboundRecord  → outbound_records
OutboundItem    → outbound_items
Member          → members
MemberLevel     → member_levels
MemberPointsRecord → member_points_records
PointsPolicy    → points_policies
MemberLevelPolicy → member_level_policies
Schedule        → schedules
Attendance      → attendances
Payroll         → payrolls
CashRecord      → cash_records
Account         → accounts
JournalEntry    → journal_entries
JournalEntryItem → journal_entry_items
CostRecord      → cost_records
Budget          → budgets
TaxDeclaration  → tax_declarations
Role            → roles
Permission      → permissions
UserRole        → user_roles
RolePermission  → role_permissions
SystemLog       → system_logs
OperationLog    → operation_logs
BackupRecord    → backup_records
SystemConfig    → system_configs
SalesReturn     → sales_returns
SalesReturnItem → sales_return_items
SalesStatistic  → sales_statistics
ProductSalesRanking → product_sales_rankings
```

### 3.2 API 路由设计

按模块划分，每个模块一个蓝图或路由组。以下为所有端点清单：

#### 3.2.1 认证模块 `/api`

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/login` | 用户登录 | 完成 |
| POST | `/api/register` | 用户注册 | 完成 |
| POST | `/api/logout` | 退出登录 | 待开发 |

#### 3.2.2 商品管理 `/api/products`

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/api/products` | 商品列表(分页/搜索/筛选) | 完成 |
| POST | `/api/products` | 新增商品 | 完成 |
| PUT | `/api/products/:id` | 更新商品 | 完成 |
| DELETE | `/api/products/:id` | 删除商品 | 完成 |
| GET | `/api/categories` | 分类列表 | 待开发 |
| POST | `/api/categories` | 新增分类 | 待开发 |
| PUT | `/api/categories/:id` | 更新分类 | 待开发 |
| DELETE | `/api/categories/:id` | 删除分类 | 待开发 |
| GET | `/api/promotions` | 促销列表 | 待开发 |
| POST | `/api/promotions` | 新增促销 | 待开发 |
| PUT | `/api/promotions/:id` | 更新促销 | 待开发 |
| DELETE | `/api/promotions/:id` | 删除促销 | 待开发 |

#### 3.2.3 供应商管理 `/api/suppliers`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/suppliers` | 供应商列表 |
| POST | `/api/suppliers` | 新增供应商 |
| PUT | `/api/suppliers/:id` | 更新供应商 |
| DELETE | `/api/suppliers/:id` | 删除供应商 |
| GET | `/api/supplier-contracts` | 合同列表 |
| POST | `/api/supplier-contracts` | 新增合同 |
| PUT | `/api/supplier-contracts/:id` | 更新合同 |
| DELETE | `/api/supplier-contracts/:id` | 删除合同 |
| GET | `/api/supplier-evaluations` | 评价列表 |
| POST | `/api/supplier-evaluations` | 新增评价 |

#### 3.2.4 采购管理 `/api/purchases`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/purchase-orders` | 采购订单列表 |
| POST | `/api/purchase-orders` | 新建采购订单(+明细) |
| PUT | `/api/purchase-orders/:id` | 更新订单 |
| PUT | `/api/purchase-orders/:id/approve` | 审批订单 |
| GET | `/api/inbound-records` | 入库验收列表 |
| POST | `/api/inbound-records` | 新建入库单(+明细) |

#### 3.2.5 仓库管理 `/api/warehouses`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/warehouses` | 仓库列表 |
| POST | `/api/warehouses` | 新增仓库 |
| PUT | `/api/warehouses/:id` | 更新仓库 |
| GET | `/api/inventory` | 库存查询(支持筛选) |
| POST | `/api/inventory/adjust` | 库存调整 |
| GET | `/api/inventory-details` | 库存明细(批次/库位) |
| GET | `/api/outbound-records` | 出库记录列表 |
| POST | `/api/outbound-records` | 新建出库单(+明细) |

#### 3.2.6 销售管理 `/api/sales`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sales-orders` | 销售订单列表 |
| POST | `/api/sales-orders` | 新建销售订单(+明细+扣库存) |
| GET | `/api/sales-orders/:id` | 订单详情 |
| GET | `/api/sales-returns` | 退货列表 |
| POST | `/api/sales-returns` | 新建退货(+退库存) |
| PUT | `/api/sales-returns/:id/approve` | 审批退货 |
| GET | `/api/sales-statistics` | 销售统计 |
| GET | `/api/product-rankings` | 商品销售排行 |

#### 3.2.7 会员管理 `/api/members`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/members` | 会员列表 |
| POST | `/api/members` | 新增会员 |
| PUT | `/api/members/:id` | 更新会员 |
| GET | `/api/member-levels` | 等级列表 |
| POST | `/api/member-levels` | 新增等级 |
| PUT | `/api/member-levels/:id` | 更新等级 |
| GET | `/api/member-points` | 积分记录列表 |
| POST | `/api/member-points` | 手动调整积分 |

#### 3.2.8 员工管理 `/api/employees`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/employees` | 员工列表 |
| POST | `/api/employees` | 新增员工 |
| PUT | `/api/employees/:id` | 更新员工 |
| GET | `/api/positions` | 岗位列表 |
| POST | `/api/positions` | 新增岗位 |
| GET | `/api/schedules` | 排班列表 |
| POST | `/api/schedules` | 新增排班 |
| GET | `/api/attendances` | 考勤列表 |
| POST | `/api/attendances` | 记录考勤 |
| GET | `/api/payrolls` | 工资列表 |
| POST | `/api/payrolls` | 生成工资单 |

#### 3.2.9 财务管理 `/api/finance`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/cash-records` | 收银记录列表 |
| GET | `/api/accounts` | 会计科目列表 |
| POST | `/api/accounts` | 新增科目 |
| GET | `/api/journal-entries` | 凭证列表 |
| POST | `/api/journal-entries` | 新建凭证(+分录) |
| GET | `/api/budgets` | 预算列表 |
| POST | `/api/budgets` | 新建预算 |
| GET | `/api/tax-declarations` | 税务申报列表 |
| POST | `/api/tax-declarations` | 新建税务申报 |

#### 3.2.10 系统管理 `/api/system`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users` | 用户列表 |
| POST | `/api/users` | 新增用户 |
| PUT | `/api/users/:id` | 更新用户 |
| PUT | `/api/users/:id/lock` | 锁定/解锁用户 |
| GET | `/api/roles` | 角色列表 |
| POST | `/api/roles` | 新增角色 |
| PUT | `/api/roles/:id` | 更新角色 |
| GET | `/api/permissions` | 权限列表 |
| POST | `/api/permissions` | 新增权限 |
| GET | `/api/logs` | 日志列表(操作+系统) |
| GET | `/api/system-configs` | 配置列表 |
| POST | `/api/system-configs` | 新增配置 |
| PUT | `/api/system-configs/:id` | 更新配置 |

#### 3.2.11 仪表盘 `/api/dashboard`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/kpi` | 今日销售额/库存预警/活跃会员/待审批 |
| GET | `/api/dashboard/notifications` | 公告列表 |

### 3.3 后端文件结构（建议拆分）

当前所有代码在单个 `APP.py` 中，建议按模块拆分：

```
backend/
├── APP.py                  # 入口，注册蓝图
├── config.py               # 数据库配置
├── requirements.txt        # 依赖
├── models/
│   ├── __init__.py
│   ├── user.py             # User
│   ├── product.py          # Product, Category, ProductPrice
│   ├── supplier.py         # Supplier, SupplierContract, SupplierEvaluation
│   ├── purchase.py         # PurchaseOrder, PurchaseOrderItem
│   ├── warehouse.py        # Warehouse, Inventory, InventoryDetail
│   ├── inbound.py          # InboundRecord, InboundItem
│   ├── outbound.py         # OutboundRecord, OutboundItem
│   ├── sales.py            # SalesOrder, SalesOrderItem, SalesReturn, SalesReturnItem
│   ├── promotion.py        # Promotion, PromotionProduct
│   ├── member.py           # Member, MemberLevel, MemberPointsRecord, PointsPolicy
│   ├── employee.py         # Employee, Position, Schedule, Attendance, Payroll
│   ├── finance.py          # CashRecord, Account, JournalEntry, JournalEntryItem, CostRecord, Budget, TaxDeclaration
│   └── system.py           # Role, Permission, UserRole, RolePermission, SystemLog, OperationLog, BackupRecord, SystemConfig
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── products.py
│   ├── suppliers.py
│   ├── purchases.py
│   ├── warehouses.py
│   ├── sales.py
│   ├── members.py
│   ├── employees.py
│   ├── finance.py
│   ├── system.py
│   └── dashboard.py
└── utils/
    ├── __init__.py
    ├── auth.py             # Token生成/验证装饰器
    └── errors.py           # 统一错误响应
```

### 3.4 通用CRUD模式

每个子模块遵循统一的CRUD模式以减少重复代码：

```python
# 列表：GET /api/resource?page=1&per_page=20&search=xxx&status=xxx
# 详情：GET /api/resource/:id
# 新增：POST /api/resource
# 更新：PUT /api/resource/:id
# 删除：DELETE /api/resource/:id
```

响应格式统一：
```json
// 成功
{ "success": true, "data": {...}, "message": "操作成功" }

// 列表
{ "success": true, "data": [...], "total": 100, "page": 1 }

// 失败
{ "success": false, "message": "错误描述", "error_code": "001" }
```

---

## 四、前端实施计划

### 4.1 目录结构（建议重构）

```
frontend/src/
├── main.js
├── App.vue
├── router/
│   └── index.js              # 路由配置(含导航守卫)
├── stores/
│   ├── auth.js               # 认证状态
│   ├── product.js            # 商品状态
│   └── ...                   # 各模块store
├── api/
│   ├── index.js              # fetch封装(基URL/拦截器/错误处理)
│   ├── auth.js               # 登录/注册/登出
│   ├── products.js           # 商品/分类/促销API
│   ├── suppliers.js          # 供应商/合同/评价API
│   ├── purchases.js          # 采购/入库API
│   ├── warehouses.js         # 仓库/库存/出入库API
│   ├── sales.js              # 销售/退货/统计API
│   ├── members.js            # 会员/等级/积分API
│   ├── employees.js          # 员工/排班/考勤/工资API
│   ├── finance.js            # 收银/凭证/预算API
│   ├── system.js             # 用户/角色/权限/日志API
│   └── dashboard.js          # 仪表盘API
├── components/
│   ├── AppLayout.vue         # 主布局(顶栏+侧边栏+内容区)
│   ├── AppSidebar.vue        # 侧边栏菜单(28个子模块)
│   ├── AppNavbar.vue         # 顶栏(时钟/通知/用户信息)
│   ├── DataTable.vue         # 通用表格组件(分页/搜索/筛选/排序)
│   ├── FormModal.vue         # 通用表单弹窗(新增/编辑)
│   ├── ConfirmDialog.vue     # 确认对话框
│   ├── Toast.vue             # Toast通知
│   ├── KPICard.vue           # KPI指标卡片
│   ├── StatusBadge.vue       # 状态标签
│   └── EmptyState.vue        # 空状态占位
├── views/
│   ├── Login.vue             # 登录页(已完成，需优化)
│   ├── Dashboard.vue         # 仪表盘(需重写)
│   ├── ProductManagement.vue # 商品管理(已完成，需优化)
│   ├── CategoryManagement.vue    # 分类管理
│   ├── PromotionManagement.vue   # 促销管理
│   ├── SupplierManagement.vue    # 供应商档案
│   ├── SupplierContract.vue      # 合同管理
│   ├── SupplierEvaluation.vue    # 供应商评价
│   ├── PurchaseOrder.vue         # 采购订单
│   ├── PurchaseInbound.vue       # 入库验收
│   ├── WarehouseInfo.vue         # 仓库信息
│   ├── InventoryQuery.vue        # 库存查询
│   ├── InboundManagement.vue     # 入库管理
│   ├── OutboundManagement.vue    # 出库管理
│   ├── SalesOrder.vue            # 销售订单
│   ├── SalesReturn.vue           # 退货处理
│   ├── SalesStatistics.vue       # 销售统计
│   ├── MemberManagement.vue      # 会员档案
│   ├── MemberLevel.vue           # 等级管理
│   ├── MemberPoints.vue          # 积分记录
│   ├── EmployeeManagement.vue    # 员工档案
│   ├── EmployeeSchedule.vue      # 排班考勤
│   ├── EmployeePayroll.vue       # 工资核算
│   ├── CashRecords.vue           # 收银记录
│   ├── JournalEntries.vue        # 会计凭证
│   ├── BudgetTax.vue             # 预算与税务
│   ├── UserRoles.vue             # 用户与角色
│   ├── PermissionConfig.vue      # 权限配置
│   ├── SystemLogs.vue            # 操作日志
│   └── SystemConfig.vue          # 备份与配置
└── utils/
    ├── format.js             # 日期/金额格式化
    └── constants.js          # 状态映射/枚举常量
```

### 4.2 路由设计

```javascript
const routes = [
  { path: '/login', component: Login, meta: { noAuth: true } },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: Dashboard },
      // 商品管理
      { path: 'products', component: ProductManagement },
      { path: 'products/category', component: CategoryManagement },
      { path: 'products/promotion', component: PromotionManagement },
      // 供应商管理
      { path: 'suppliers', component: SupplierManagement },
      { path: 'suppliers/contract', component: SupplierContract },
      { path: 'suppliers/evaluation', component: SupplierEvaluation },
      // 采购管理
      { path: 'purchases', component: PurchaseOrder },
      { path: 'purchases/inbound', component: PurchaseInbound },
      // 仓库管理
      { path: 'warehouses', component: WarehouseInfo },
      { path: 'warehouses/inventory', component: InventoryQuery },
      { path: 'warehouses/inbound', component: InboundManagement },
      { path: 'warehouses/outbound', component: OutboundManagement },
      // 销售管理
      { path: 'sales', component: SalesOrder },
      { path: 'sales/return', component: SalesReturn },
      { path: 'sales/statistics', component: SalesStatistics },
      // 会员管理
      { path: 'members', component: MemberManagement },
      { path: 'members/level', component: MemberLevel },
      { path: 'members/points', component: MemberPoints },
      // 员工管理
      { path: 'employees', component: EmployeeManagement },
      { path: 'employees/schedule', component: EmployeeSchedule },
      { path: 'employees/payroll', component: EmployeePayroll },
      // 财务管理
      { path: 'finance', component: CashRecords },
      { path: 'finance/journal', component: JournalEntries },
      { path: 'finance/budget', component: BudgetTax },
      // 系统管理
      { path: 'system', component: UserRoles },
      { path: 'system/permissions', component: PermissionConfig },
      { path: 'system/logs', component: SystemLogs },
      { path: 'system/config', component: SystemConfig },
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
];
```

### 4.3 通用组件设计

#### DataTable.vue（核心复用组件）

每个列表页统一使用，Props：
- `columns`: 列定义 `[{key, label, width, sortable, render}]`
- `apiUrl`: 数据获取地址
- `searchPlaceholder`: 搜索占位文字
- `filters`: 筛选选项 `[{label, value}]`
- `actions`: 行操作按钮 `[{label, handler, color}]`

Events：
- `@row-click`: 行点击
- `@add`: 点击新增按钮

#### FormModal.vue（核心复用组件）

新增/编辑通用弹窗，Props：
- `title`: 弹窗标题
- `fields`: 字段定义 `[{key, label, type, required, options}]`
- `initialData`: 编辑时的初始数据
- `visible`: 显示/隐藏

Events：
- `@submit`: 提交表单数据
- `@cancel`: 取消

### 4.4 状态管理（Pinia Store）

```
stores/
├── auth.js       # user, token, login(), logout(), checkAuth()
├── ui.js         # sidebarOpen, notifications, toastMessage
└── [module].js   # 各模块数据缓存(可选，简单页面直接用api层)
```

### 4.5 实施优先级

| 优先级 | 任务 | 原因 |
|--------|------|------|
| P0 | API封装层 (`api/index.js`) | 所有页面依赖 |
| P0 | AppLayout + AppSidebar + AppNavbar | 主框架，所有页面容器 |
| P0 | DataTable + FormModal 通用组件 | 90%页面基于这两个组件 |
| P1 | 仪表盘页面 | 登录后首页 |
| P1 | 商品管理3个页面 | 核心业务，已有基础 |
| P1 | 后端全部API | 前端依赖 |
| P2 | 供应商管理3个页面 | 采购、入库依赖供应商数据 |
| P2 | 采购管理2个页面 | 入库、库存依赖采购 |
| P3 | 仓库管理4个页面 | 依赖商品、采购 |
| P3 | 销售管理3个页面 | 依赖商品、会员、员工 |
| P3 | 会员管理3个页面 | 销售依赖会员 |
| P3 | 员工管理3个页面 | 排班、工资、销售依赖 |
| P4 | 财务管理3个页面 | 依赖销售 |
| P4 | 系统管理4个页面 | 权限、日志依赖用户 |

---

## 五、实施步骤（按天划分）

### 第1天：基础设施

1. **后端拆分** - 将 APP.py 按 models/routes 目录拆分
2. **后端全部模型** - 补全49张表的 SQLAlchemy 模型
3. **后端通用CRUD** - 为每个模块生成标准CRUD路由
4. **前端API层** - 创建 `api/index.js` 封装 fetch，自动注入错误处理
5. **前端主布局** - AppLayout + AppSidebar + AppNavbar（参照原型HTML）
6. **前端路由** - 配置全部28个子模块路由

### 第2天：通用组件 + 仪表盘

1. **DataTable 组件** - 通用表格（分页/搜索/筛选/排序/操作列）
2. **FormModal 组件** - 通用表单弹窗（动态字段生成）
3. **Toast + ConfirmDialog** - 通知和确认组件
4. **仪表盘页面** - KPI卡片 / 公告 / 快捷操作
5. **仪表盘API** - 聚合查询统计

### 第3-4天：核心业务模块

1. **商品管理**（3页）- 商品CRUD / 分类管理 / 促销管理
2. **供应商管理**（3页）- 档案 / 合同 / 评价
3. **采购管理**（2页）- 采购订单+明细 / 入库验收
4. **仓库管理**（4页）- 仓库信息 / 库存查询 / 入库 / 出库

### 第5-6天：交易与人员模块

1. **销售管理**（3页）- 销售订单 / 退货处理 / 销售统计
2. **会员管理**（3页）- 档案 / 等级 / 积分
3. **员工管理**（3页）- 档案 / 排班考勤 / 工资核算

### 第7-8天：财务 + 系统 + 收尾

1. **财务管理**（3页）- 收银记录 / 会计凭证 / 预算税务
2. **系统管理**（4页）- 用户角色 / 权限 / 日志 / 配置
3. **认证完善** - Token机制 / 导航守卫 / 权限控制
4. **联调测试** - 全流程测试 / 边界情况
5. **种子数据** - 完善各表测试数据

---

## 六、关键设计决策

### 6.1 认证方案

采用简单的 Token 机制（JWT或自定义token），登录后存入 Pinia + localStorage，所有API请求自动携带。

```javascript
// api/index.js 拦截器
async function request(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`/api${url}`, { ...options, headers });
  if (res.status === 401) { /* 跳转登录 */ }
  if (!res.ok) { const err = await res.json(); throw new Error(err.message); }
  return res.json();
}
```

### 6.2 通用CRUD一致性

所有列表页使用相同的 DataTable 组件，只需传入不同的 `columns` 和 `apiUrl` 即可完成80%的工作。

```vue
<!-- 典型页面结构 -->
<template>
  <div class="p-8">
    <div class="flex justify-between mb-6">
      <h2>{{ title }}</h2>
      <button @click="showAddModal">新增</button>
    </div>
    <DataTable :columns="columns" :api-url="apiUrl" :filters="filters" />
    <FormModal v-model:visible="modalVisible" :fields="fields" @submit="handleSubmit" />
  </div>
</template>
```

### 6.3 样式方案

直接沿用原型 HTML 中的 Tailwind CSS CDN + 自定义CSS变量，确保视觉一致性。保留原型中定义好的设计 token：
- 主色 `--primary: #2563eb` (蓝色系)
- 状态色：emerald(成功) / amber(警告) / red(危险) / indigo(信息)
- 圆角风格：`rounded-2xl` / `rounded-3xl`
- 卡片阴影：`shadow-sm` + border

### 6.4 性能考虑

- 列表页默认分页20条
- 搜索使用防抖(300ms)
- 关联数据使用后端 JOIN 而非前端多次请求
- 静态资源使用 CDN（Tailwind / Font Awesome）

---

## 七、风险与注意事项

| 风险 | 应对 |
|------|------|
| 28个页面开发量大 | 使用通用 DataTable + FormModal 组件，每个页面控制在100行以内 |
| 49张表模型定义繁琐 | 按模块分批，优先定义核心业务表 |
| 前后端字段名不一致 | 后端统一返回前端期望的字段名（API层做映射） |
| 外键约束导致删除失败 | DELETE 接口需先删子表记录（已在 APP.py 中处理） |
| 原型中部分功能仅为占位 | 优先实现CRUD操作，统计报表可后续迭代 |

---

## 八、预估工时

| 阶段 | 内容 | 预估工时 |
|------|------|---------|
| 后端模型 | 41个新增模型定义 | 4h |
| 后端API | 80+个接口实现 | 12h |
| 前端基础设施 | 布局/路由/API层/通用组件 | 8h |
| 前端28页面 | 基于通用组件批量开发 | 20h |
| 联调测试 | 全流程测试修复 | 6h |
| **合计** | | **约50小时** |

---

## 九、开发顺序建议

```
后端模型全部定义
    ↓
后端API全部实现
    ↓
前端 API层 + 路由 + AppLayout
    ↓
DataTable + FormModal 通用组件
    ↓
仪表盘 → 商品管理 → 供应商管理 → 采购管理
    ↓
仓库管理 → 销售管理 → 会员管理 → 员工管理
    ↓
财务管理 → 系统管理
    ↓
认证完善 + 联调测试
```
