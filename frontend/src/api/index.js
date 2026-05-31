const BASE_URL = import.meta.env.VITE_API_URL || '/api';

let redirectingToLogin = false;

async function request(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE_URL}${url}`, { ...options, headers });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    console.error('[API] JSON解析失败, status:', res.status, 'url:', url, 'response:', text.substring(0, 500));
    throw new Error('服务器响应异常 (HTTP ' + res.status + ')');
  }
  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('permissions');
    if (!redirectingToLogin && window.location.pathname !== '/login') {
      redirectingToLogin = true;
      window.location.href = '/login';
    }
    throw new Error(data.message || '未登录');
  }
  if (!res.ok || !data.success) {
    throw new Error(data.message || '请求失败');
  }
  return data;
}

export const get = (url, params) => {
  const query = params ? '?' + new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== '' && v != null)
  ).toString() : '';
  return request(url + query);
};
export const post = (url, body) => request(url, { method: 'POST', body: JSON.stringify(body) });
export const put = (url, body) => request(url, { method: 'PUT', body: JSON.stringify(body) });
export const del = (url) => request(url, { method: 'DELETE' });
