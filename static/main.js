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
        .catch(error => console.error('Error loading area config:', error));
}

// 修改loadCategories函数，使用区域配置显示区域名
function loadCategories() {
    Promise.all([
        fetch('/api/categories').then(res => res.json()),
        fetch('/api/config/areas').then(res => res.json())
    ])
        .then(([categories, areaConfig]) => {
            const categoryList = document.getElementById('categoryList');
            categoryList.innerHTML = categories.map(category => {
                // 从区域配置中查找区域名
                const areaName = Object.entries(areaConfig).find(([name, id]) => id === category.id)?.[0] || category.id;
                return `
                    <tr>
                        <td class="px-4 py-2">${areaName}</td>
                        <td class="px-4 py-2">${category.name}</td>
                        <td class="px-4 py-2 text-right">
                            <button onclick="deleteCategory('${category.id}')" 
                                    class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm">
                                删除
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        })
        .catch(error => console.error('Error loading data:', error));
}


// 确保页面加载时初始化区域选择框
document.addEventListener('DOMContentLoaded', function () {
    loadAreaConfig();
    loadCategories();
});


// 全局变量存储监控状态
let isMonitoring = false;


// 删除类目
function deleteCategory(categoryId) {
    if (!confirm('确定要删除此监控项吗？')) {
        return;
    }

    fetch(`/api/categories/${categoryId}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
            if (result.message === '类目删除成功') {
                loadCategories();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('删除失败');
        });
}

// 导入账号
document.addEventListener('DOMContentLoaded', function () {
    const importAccountBtn = document.getElementById('importAccountBtn');
    if (importAccountBtn) {
        importAccountBtn.addEventListener('click', function () {
            const accountInput = document.getElementById('accountInput');
            const accounts = accountInput.value;

            fetch('/api/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({accounts})
            })
                .then(response => response.json())
                .then(result => {
                    alert(result.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('导入失败');
                });
        });
    }
});

// 添加监控
// 删除原来的静态AREA_CONFIG定义

// 修改添加监控的事件处理
document.addEventListener('DOMContentLoaded', function () {
    const addCategoryBtn = document.getElementById('addCategoryBtn');
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener('click', function () {
            const categoryId = document.getElementById('newCategoryId').value;
            const categoryName = document.getElementById('newCategoryName').value;

            if (!categoryId) {
                alert('请选择区域');
                return;
            }

            if (!categoryName) {
                alert('请输入需要监控的商品名');
                return;
            }

            fetch('/api/categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: categoryId,
                    name: categoryName
                })
            })
                .then(response => response.json())
                .then(result => {
                    alert(result.message);
                    if (result.message === '类目添加成功') {
                        document.getElementById('newCategoryName').value = '';
                        // 重新加载类目列表
                        loadCategories();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('添加监控失败');
                });
        });
    }
});

// 确保页面加载时初始化所有必要的数据
document.addEventListener('DOMContentLoaded', function () {
    // 加载区域配置
    loadAreaConfig();
    // 加载类目列表
    loadCategories();

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
});

// 启动/停止监控
document.addEventListener('DOMContentLoaded', function () {
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
                        isMonitoring = true;
                        startMonitorBtn.classList.add('hidden');
                        stopMonitorBtn.classList.remove('hidden');
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
            fetch('/api/monitor/stop', {
                method: 'POST'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        isMonitoring = false;
                        stopMonitorBtn.classList.add('hidden');
                        startMonitorBtn.classList.remove('hidden');
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

// 日志轮询
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

function stopLogging() {
    clearInterval(activityLogInterval);
    clearInterval(pointLogInterval);
}

function clearLogs() {
    document.getElementById('activityLogContent').innerHTML = '';
    document.getElementById('pointLogContent').innerHTML = '';
}

// 页面加载时获取区域配置和类目列表
document.addEventListener('DOMContentLoaded', function () {
    loadAreaConfig();
    loadCategories();

    // 加载已保存的账号
    fetch('/api/accounts')
        .then(response => response.json())
        .then(accounts => {
            const accountInput = document.getElementById('accountInput');
            // 将账号列表转换为文本格式
            accountInput.value = accounts.map(account =>
                `${account.phone},${account.password}`
            ).join('\n');
        })
        .catch(error => console.error('Error fetching accounts:', error));
});