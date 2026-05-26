export const formatCurrency = (value) => {
  if (value == null) return '-';
  const num = Number(value);
  if (isNaN(num)) return '-';
  return '¥' + num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '-';
  return d.toLocaleDateString('zh-CN');
};

export const formatDateTime = (dateStr) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '-';
  return d.toLocaleString('zh-CN');
};

export const statusClass = (status, map = {}) => {
  const defaults = {
    'active': 'bg-emerald-100 text-emerald-700',
    'normal': 'bg-emerald-100 text-emerald-700',
    'inactive': 'bg-gray-100 text-gray-600',
    'pending': 'bg-amber-100 text-amber-700',
    'draft': 'bg-slate-100 text-slate-600',
    'approved': 'bg-blue-100 text-blue-700',
    'completed': 'bg-emerald-100 text-emerald-700',
    'ended': 'bg-gray-100 text-gray-600',
    'cancelled': 'bg-red-100 text-red-700',
    'locked': 'bg-red-100 text-red-700',
    'low': 'bg-amber-100 text-amber-700',
    'out_of_stock': 'bg-red-100 text-red-700',
    'discontinued': 'bg-gray-100 text-gray-500',
    'refunded': 'bg-purple-100 text-purple-700',
    'expired': 'bg-gray-100 text-gray-500',
    'terminated': 'bg-red-100 text-red-700',
    'shipped': 'bg-indigo-100 text-indigo-700',
    'received': 'bg-teal-100 text-teal-700',
    'resigned': 'bg-gray-100 text-gray-500',
    'failed': 'bg-red-100 text-red-700',
    'success': 'bg-emerald-100 text-emerald-700',
    'posted': 'bg-emerald-100 text-emerald-700',
    'blacklisted': 'bg-red-100 text-red-700',
    'maintenance': 'bg-amber-100 text-amber-700',
    'full': 'bg-blue-100 text-blue-700',
  };
  const merged = { ...defaults, ...map };
  return merged[status] || 'bg-gray-100 text-gray-600';
};

export const statusLabel = (status) => {
  const labels = {
    'active': '正常', 'inactive': '停用', 'pending': '待处理', 'draft': '草稿',
    'approved': '已审批', 'completed': '已完成', 'ended': '已结束', 'cancelled': '已取消',
    'locked': '已锁定', 'low': '库存低', 'out_of_stock': '缺货', 'discontinued': '停产',
    'refunded': '已退款', 'expired': '已过期', 'terminated': '已终止',
    'shipped': '已发货', 'received': '已收货', 'resigned': '已离职',
    'failed': '失败', 'success': '成功', 'posted': '已过账', 'blacklisted': '黑名单',
    'normal': '正常', 'maintenance': '维护中', 'full': '已满',
    'morning': '早班', 'afternoon': '中班', 'night': '晚班', 'rest': '休息',
    'late': '迟到', 'early': '早退', 'absent': '旷工', 'leave': '请假',
    'paid': '已支付', 'unpaid': '未支付', 'overdue': '逾期',
  };
  return labels[status] || status;
};
