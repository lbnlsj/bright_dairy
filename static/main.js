// 全局状态
let categories = [];
let editingCategoryId = null;
let logUpdateInterval;
let isMonitoring = false;

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 绑定按钮事件
    document.getElementById('importAccountBtn').addEventListener('click', importAccounts);
    document.getElementById('addCategoryBtn').addEventListener('click', addCategory);
    document.getElementById('cancelEditBtn').addEventListener('click', closeEditModal);
    document.getElementById('saveEditBtn').addEventListener('click', saveCategory);
    document.getElementById('startMonitorBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopMonitorBtn').addEventListener('click', stopMonitoring);

    // 初始化状态
    loadCategories();
    checkStatus();
});

// 检查当前状态
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateMonitoringStatus(data.is_running);

        if (data.is_running) {
            startLogUpdates();
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// 更新监控状态
function updateMonitoringStatus(isRunning) {
    isMonitoring = isRunning;
    const startBtn = document.getElementById('startMonitorBtn');
    const stopBtn = document.getElementById('stopMonitorBtn');

    if (isRunning) {
        startBtn.classList.add('hidden');
        stopBtn.classList.remove('hidden');
    } else {
        startBtn.classList.remove('hidden');
        stopBtn.classList.add('hidden');
    }
}

// 开始监控
async function startMonitoring() {
    if (categories.length === 0) {
        alert('请先添加要监控的类目');
        return;
    }

    try {
        const response = await fetch('/api/monitor/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                categories: categories.map(c => c.id)
            }),
        });

        const data = await response.json();
        if (data.success) {
            updateMonitoringStatus(true);
            startLogUpdates();
        } else {
            alert(data.message || '启动监控失败');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('启动监控失败');
    }
}

// 停止监控
async function stopMonitoring() {
    try {
        const response = await fetch('/api/monitor/stop', {
            method: 'POST',
        });

        const data = await response.json();
        if (data.success) {
            updateMonitoringStatus(false);
            stopLogUpdates();
        } else {
            alert(data.message || '停止监控失败');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('停止监控失败');
    }
}

// 导入账号
async function importAccounts() {
    const accountInput = document.getElementById('accountInput');
    const accounts = accountInput.value;

    try {
        const response = await fetch('/api/accounts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ accounts }),
        });

        const data = await response.json();
        alert(data.message);
        accountInput.value = '';
    } catch (error) {
        console.error('Error:', error);
        alert('导入账号失败');
    }
}

// 加载类目列表
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        categories = await response.json();
        renderCategories();
    } catch (error) {
        console.error('Error loading categories:', error);
        alert('加载类目失败');
    }
}

// 渲染类目列表
function renderCategories() {
    const categoryList = document.getElementById('categoryList');
    categoryList.innerHTML = categories.map(category => `
        <tr id="category-${category.id}">
            <td class="px-4 py-2">${category.id}</td>
            <td class="px-4 py-2">${category.name}</td>
            <td class="px-4 py-2 text-right">
                <button onclick="editCategory('${category.id}')" 
                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded mr-2">
                    编辑
                </button>
                <button onclick="deleteCategory('${category.id}')"
                    class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded">
                    删除
                </button>
            </td>
        </tr>
    `).join('');
}

// 添加类目
async function addCategory() {
    const idInput = document.getElementById('newCategoryId');
    const nameInput = document.getElementById('newCategoryName');

    const id = idInput.value.trim();
    const name = nameInput.value.trim();

    if (!id || !name) {
        alert('请填写完整的类目信息');
        return;
    }

    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id, name }),
        });

        if (response.ok) {
            await loadCategories();
            idInput.value = '';
            nameInput.value = '';
        } else {
            const error = await response.json();
            alert(error.message || '添加类目失败');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('添加类目失败');
    }
}

// 显示编辑弹窗
function editCategory(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;

    editingCategoryId = categoryId;
    document.getElementById('editCategoryId').value = category.id;
    document.getElementById('editCategoryName').value = category.name;
    document.getElementById('editModal').classList.remove('hidden');
}

// 关闭编辑弹窗
function closeEditModal() {
    editingCategoryId = null;
    document.getElementById('editModal').classList.add('hidden');
}

// 保存类目修改
async function saveCategory() {
    if (!editingCategoryId) return;

    const id = document.getElementById('editCategoryId').value.trim();
    const name = document.getElementById('editCategoryName').value.trim();

    if (!id || !name) {
        alert('请填写完整的类目信息');
        return;
    }

    try {
        const response = await fetch(`/api/categories/${editingCategoryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id, name }),
        });

        if (response.ok) {
            await loadCategories();
            closeEditModal();
        } else {
            const error = await response.json();
            alert(error.message || '更新类目失败');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('更新类目失败');
    }
}

// 删除类目
async function deleteCategory(categoryId) {
    if (!confirm('确定要删除此类目吗？')) return;

    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.message || '删除类目失败');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('删除类目失败');
    }
}

// 开始日志更新
function startLogUpdates() {
    if (!logUpdateInterval) {
        updateLogs(); // 立即更新一次
        logUpdateInterval = setInterval(updateLogs, 1000); // 每秒更新一次
    }
}

// 停止日志更新
function stopLogUpdates() {
    if (logUpdateInterval) {
        clearInterval(logUpdateInterval);
        logUpdateInterval = null;
    }
}

// 更新日志
async function updateLogs() {
    try {
        // 获取活动商品日志
        const activityResponse = await fetch('/api/logs/activity');
        const activityLogs = await activityResponse.json();

        // 获取积分商品日志
        const pointResponse = await fetch('/api/logs/points');
        const pointLogs = await pointResponse.json();

        // 更新活动商品日志
        if (activityLogs.length > 0) {
            const activityLogContent = document.getElementById('activityLogContent');
            activityLogs.forEach(log => {
                activityLogContent.innerHTML += `${log}\n`;
            });
            activityLogContent.scrollTop = activityLogContent.scrollHeight;
        }

        // 更新积分商品日志
        if (pointLogs.length > 0) {
            const pointLogContent = document.getElementById('pointLogContent');
            pointLogs.forEach(log => {
                pointLogContent.innerHTML += `${log}\n`;
            });
            pointLogContent.scrollTop = pointLogContent.scrollHeight;
        }
    } catch (error) {
        console.error('Error updating logs:', error);
    }
}

// 清除日志内容
function clearLogs() {
    document.getElementById('activityLogContent').innerHTML = '';
    document.getElementById('pointLogContent').innerHTML = '';
}