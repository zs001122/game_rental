// 通用工具函数

// API基础URL
const API_BASE = '/api';

// 显示消息提示
function showMessage(message, type = 'info') {
    // 创建通知容器（如果不存在）
    let notifyContainer = document.getElementById('notify-container');
    if (!notifyContainer) {
        notifyContainer = document.createElement('div');
        notifyContainer.id = 'notify-container';
        notifyContainer.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            pointer-events: none;
        `;
        document.body.appendChild(notifyContainer);
    }
    
    // 创建通知框
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = `
        position: relative;
        margin-bottom: 10px;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        pointer-events: auto;
        animation: slideIn 0.3s ease-out;
    `;
    
    notifyContainer.appendChild(alertDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 3000);
}

// 发送API请求
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(API_BASE + url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// 获取当前用户信息
async function getCurrentUser() {
    try {
        const data = await apiRequest('/auth/current');
        return data.user;
    } catch (error) {
        return null;
    }
}

// 检查登录状态
async function checkLogin() {
    const user = await getCurrentUser();
    if (!user) {
        window.location.href = '/login';
        return false;
    }
    return user;
}

// 登出
async function logout() {
    try {
        await apiRequest('/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        showMessage('登出失败', 'error');
    }
}

// 格式化金额
function formatMoney(amount) {
    return parseFloat(amount).toFixed(2);
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'available': '可租赁',
        'rented': '已租出',
        'unavailable': '不可用',
        'pending': '待支付',
        'renting': '正在租赁',
        'completed': '已组赁',
        'cancelled': '已取消'
    };
    return statusMap[status] || status;
}

// 获取状态样式类
function getStatusClass(status) {
    const classMap = {
        'available': 'status-available',
        'rented': 'status-rented',
        'unavailable': 'status-unavailable'
    };
    return classMap[status] || '';
}

// 更新导航栏用户信息
async function updateNavbar() {
    const user = await getCurrentUser();
    const navbarUser = document.querySelector('.navbar-user');
    
    if (user && navbarUser) {
        navbarUser.innerHTML = `
            <div class="balance-info">
                余额: <span class="balance-amount">¥${formatMoney(user.balance)}</span>
            </div>
            <span>${user.username}</span>
            <button class="btn btn-secondary" onclick="logout()">登出</button>
        `;
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 更新导航栏
    updateNavbar();
});
