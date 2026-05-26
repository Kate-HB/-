import { post } from './index.js';
export const login = (username, password) => post('/login', { username, password });
export const register = (username, password) => post('/register', { username, password });
export const logout = () => post('/logout');
