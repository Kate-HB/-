import { get } from './index.js';
export const getDashboardKpi = () => get('/dashboard/kpi');
export const getDashboardCharts = () => get('/dashboard/charts');
export const getDashboardNotifications = () => get('/dashboard/notifications');
