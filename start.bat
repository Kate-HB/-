@echo off
chcp 65001 >nul
title 超市管理系统

echo ============================================
echo   超市管理系统 - 启动中...
echo ============================================

set ROOT=%~dp0

echo.
echo [1/2] 启动后端 (Flask :5000)...
start "Backend" cmd /c "cd /d %ROOT%backend && python APP.py"

echo [2/2] 启动前端 (Vite :3000)...
start "Frontend" cmd /c "cd /d %ROOT%frontend && npm run dev"

echo.
echo ============================================
echo   后端: http://localhost:5000
echo   前端: http://localhost:3000
echo   初始化数据: cd backend && python seed.py
echo   默认账号: admin / admin123
echo ============================================
echo.
echo 关闭此窗口不会停止服务，请在对应窗口按 Ctrl+C 停止
pause
