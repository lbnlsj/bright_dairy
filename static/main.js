// 全局变量存储监控状态
let isMonitoring = false;

// 加载区域配置
function loadAreaConfig() {
    fetch('/api/config/areas')
        .then(response => response.json())
        .then(areaConfig => {
            const select = document.getElementById('newCategoryId');
            // 清空现有选项，保留默认选项
            select.innerHTML = '<option value="">请选择区域</option>';
            // 添加从后端获取的区域选项
            Object.entries(areaConfig).forEach(([name, id]) => {
                const option = document.createElement('option');
                option.value = id;  // 值为区域ID
                option.textContent = name;  // 显示区域名称
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading area config:', error);
            alert('加载区域配置失败');
        });
}

// 加载类目列表
function loadCategories() {
    Promise.all([
        fetch('/api/categories').then(res => res.json()),
        fetch('/api/config/areas').then(res => res.json())
    ])
        .then(([categories, areaConfig]) => {
            const categoryList = document.getElementById('categoryList');
            categoryList.innerHTML = categories.map(category => {
                // 从区域配置中查找区域名
                const areaName = Object.entries(areaConfig).find(([name, id]) => id === category.area_id)?.[0] || category.area_id;
                return `
                    <tr>
                        <td class="px-4 py-2">${areaName}</td>
                        <td class="px-4 py-2">${category.name}</td>
                        <td class="px-4 py-2 text-right">
                            <button onclick="deleteCategory('${category.monitor_id}')" 
                                    class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm">
                                删除
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        })
        .catch(error => {
            console.error('Error loading categories:', error);
            alert('加载监控列表失败');
        });
}

// 删除类目
function deleteCategory(monitorId) {
    if (!confirm('确定要删除此监控项吗？')) {
        return;
    }

    fetch(`/api/categories/${monitorId}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                loadCategories(); // 重新加载类目列表
            }
            alert(result.message);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('删除失败');
        });
}

// 清空日志
function clearLogs() {
    document.getElementById('activityLogContent').innerHTML = '';
    document.getElementById('pointLogContent').innerHTML = '';
}

// 启动日志轮询
let activityLogInterval;
let pointLogInterval;

function startLogging() {
    // 活动商品日志
    activityLogInterval = setInterval(function () {
        fetch('/api/logs/activity')
            .then(response => response.json())
            .then(logs => {
                if (logs.length > 0) {
                    const activityLogContent = document.getElementById('activityLogContent');
                    activityLogContent.innerHTML += logs.join('\n') + '\n';
                    activityLogContent.scrollTop = activityLogContent.scrollHeight;
                }
            })
            .catch(error => console.error('Error fetching activity logs:', error));
    }, 1000);

    // 积分商品日志
    pointLogInterval = setInterval(function () {
        fetch('/api/logs/points')
            .then(response => response.json())
            .then(logs => {
                if (logs.length > 0) {
                    const pointLogContent = document.getElementById('pointLogContent');
                    pointLogContent.innerHTML += logs.join('\n') + '\n';
                    pointLogContent.scrollTop = pointLogContent.scrollHeight;
                }
            })
            .catch(error => console.error('Error fetching point logs:', error));
    }, 1000);
}

// 停止日志轮询
function stopLogging() {
    clearInterval(activityLogInterval);
    clearInterval(pointLogInterval);
}

// 监控状态检查
function checkMonitorStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(status => {
            const startBtn = document.getElementById('startMonitorBtn');
            const stopBtn = document.getElementById('stopMonitorBtn');

            if (status.is_running) {
                startBtn.classList.add('hidden');
                stopBtn.classList.remove('hidden');
                if (!isMonitoring) {
                    isMonitoring = true;
                    startLogging();
                }
            } else {
                stopBtn.classList.add('hidden');
                startBtn.classList.remove('hidden');
                if (isMonitoring) {
                    isMonitoring = false;
                    stopLogging();
                }
            }
        })
        .catch(error => console.error('Error checking monitor status:', error));
}

// 初始化页面事件监听器
document.addEventListener('DOMContentLoaded', function () {
    // 加载初始数据
    loadAreaConfig();
    loadCategories();
    checkMonitorStatus();

    // 设置定期检查监控状态
    setInterval(checkMonitorStatus, 5000);

    // 加载已保存的账号
    fetch('/api/accounts')
        .then(response => response.json())
        .then(accounts => {
            const accountInput = document.getElementById('accountInput');
            accountInput.value = accounts.map(account =>
                `${account.phone},${account.password}`
            ).join('\n');
        })
        .catch(error => console.error('Error fetching accounts:', error));

    // 导入账号按钮事件
    const importAccountBtn = document.getElementById('importAccountBtn');
    if (importAccountBtn) {
        importAccountBtn.addEventListener('click', function () {
            const accountInput = document.getElementById('accountInput');
            const accounts = accountInput.value;

            if (!accounts.trim()) {
                alert('请输入账号信息');
                return;
            }

            fetch('/api/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({accounts})
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert(result.message);
                    } else {
                        alert(result.message || '导入失败');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('导入失败');
                });
        });
    }

    // 添加监控按钮事件
    const addCategoryBtn = document.getElementById('addCategoryBtn');
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener('click', function () {
            const areaId = document.getElementById('newCategoryId').value;
            const categoryNames = document.getElementById('newCategoryName').value;

            if (!areaId) {
                alert('请选择区域');
                return;
            }

            if (!categoryNames) {
                alert('请输入需要监控的商品名');
                return;
            }

            fetch('/api/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    area_id: areaId,
                    names: categoryNames.split(',').map(name => name.trim()).filter(name => name)
                })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        document.getElementById('newCategoryName').value = '';
                        loadCategories();
                    }
                    alert(result.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('添加监控失败');
                });
        });
    }

    // 启动监控按钮事件
    const startMonitorBtn = document.getElementById('startMonitorBtn');
    const stopMonitorBtn = document.getElementById('stopMonitorBtn');

    if (startMonitorBtn && stopMonitorBtn) {
        startMonitorBtn.addEventListener('click', function () {
            fetch('/api/monitor/start', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        startMonitorBtn.classList.add('hidden');
                        stopMonitorBtn.classList.remove('hidden');
                        isMonitoring = true;
                        startLogging();
                    }
                    alert(result.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('启动监控失败');
                });
        });

        stopMonitorBtn.addEventListener('click', function () {
            setTimeout(function() {alert('已经提交停止指令，稍等半分钟后自动停止...')}, 10)
            fetch('/api/monitor/stop', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        stopMonitorBtn.classList.add('hidden');
                        startMonitorBtn.classList.remove('hidden');
                        isMonitoring = false;
                        stopLogging();
                    }
                    alert(result.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('停止监控失败');
                });
        });
    }
});