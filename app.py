from flask import Flask, render_template, jsonify, request
import random
import time
from datetime import datetime
import threading
import queue
import json

app = Flask(__name__)

# 全局变量
monitoring = False
log_queue = queue.Queue()
monitor_thread = None  # 确保在全局作用域定义
accounts = []
proxies = []
categories = []  # 存储类目列表
running_categories = set()  # 存储正在监控的类目ID


class MonitoringState:
    def __init__(self):
        self.is_running = False


state = MonitoringState()


def generate_mock_log():
    """生成模拟日志"""
    log_types = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'SUCCESS']
    log_templates = [
        ("Checking products with account {0}", lambda: f"138{random.randint(10000000, 99999999)}"),
        ("Found {0} matching products", lambda: str(random.randint(0, 10))),
        ("Successfully ordered product: {0} with account {1}", lambda: (
            random.choice(["星座挂件A", "星座挂件B", "星座挂件C", "星座挂件D"]),
            f"138{random.randint(10000000, 99999999)}"
        )),
        ("No available proxies for account {0}", lambda: f"138{random.randint(10000000, 99999999)}"),
        ("Login successful for account {0}", lambda: f"138{random.randint(10000000, 99999999)}"),
        ("Waiting {0} seconds before next check", lambda: str(random.randint(1, 30)))
    ]

    log_type = random.choice(log_types)
    template, value_generator = random.choice(log_templates)

    values = value_generator()
    if isinstance(values, tuple):
        message = template.format(*values)
    else:
        message = template.format(values)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} | {log_type:<8} | {message}"


def monitoring_task():
    """模拟监控任务"""
    while state.is_running:
        try:
            log_message = generate_mock_log()
            log_queue.put(log_message)
            time.sleep(random.uniform(0.5, 2.0))
        except Exception as e:
            print(f"Error in monitoring task: {e}")
            time.sleep(1)


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有类目"""
    return jsonify(categories)


@app.route('/api/categories', methods=['POST'])
def add_category():
    """添加新类目"""
    data = request.json
    category_id = data.get('id')
    name = data.get('name')

    if not category_id or not name:
        return jsonify({'message': '类目ID和名称不能为空'}), 400

    # 检查ID是否已存在
    if any(c['id'] == category_id for c in categories):
        return jsonify({'message': '类目ID已存在'}), 400

    categories.append({
        'id': category_id,
        'name': name
    })
    return jsonify({'message': '类目添加成功'})


@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """更新类目"""
    data = request.json
    new_id = data.get('id')
    new_name = data.get('name')

    if not new_id or not new_name:
        return jsonify({'message': '类目ID和名称不能为空'}), 400

    # 找到要更新的类目
    for category in categories:
        if category['id'] == category_id:
            # 如果ID发生变化，检查新ID是否已存在
            if new_id != category_id and any(c['id'] == new_id for c in categories):
                return jsonify({'message': '新类目ID已存在'}), 400

            category['id'] = new_id
            category['name'] = new_name
            return jsonify({'message': '类目更新成功'})

    return jsonify({'message': '类目不存在'}), 404


@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除类目"""
    if category_id in running_categories:
        return jsonify({'message': '无法删除正在监控的类目'}), 400

    for i, category in enumerate(categories):
        if category['id'] == category_id:
            categories.pop(i)
            return jsonify({'message': '类目删除成功'})

    return jsonify({'message': '类目不存在'}), 404


@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """启动所有类目的监控"""
    global monitor_thread  # 声明全局变量

    if not categories:
        return jsonify({
            'success': False,
            'message': '没有可监控的类目'
        })

    if state.is_running:
        return jsonify({
            'success': False,
            'message': '监控已经在运行中'
        })

    state.is_running = True
    if not monitor_thread or not monitor_thread.is_alive():
        monitor_thread = threading.Thread(target=monitoring_task)
        monitor_thread.daemon = True
        monitor_thread.start()

    return jsonify({
        'success': True,
        'message': '监控已启动'
    })


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """停止所有监控"""
    global monitor_thread  # 声明全局变量

    if not state.is_running:
        return jsonify({
            'success': False,
            'message': '监控未在运行'
        })

    state.is_running = False
    if monitor_thread and monitor_thread.is_alive():
        # 等待线程完成
        monitor_thread = None

    return jsonify({
        'success': True,
        'message': '监控已停止'
    })


@app.route('/api/status')
def get_status():
    """获取当前状态"""
    return jsonify({
        'is_running': state.is_running,
        'account_count': len(accounts),
        'proxy_count': len(proxies)
    })


@app.route('/api/logs/activity')
def get_activity_logs():
    """获取活动商品日志"""
    logs = []
    try:
        while not log_queue.empty():
            logs.append(log_queue.get_nowait())
    except queue.Empty:
        pass
    return jsonify(logs)


@app.route('/api/logs/points')
def get_point_logs():
    """获取积分商品日志"""
    return jsonify([])  # 暂时返回空列表


@app.route('/api/accounts', methods=['POST'])
def import_accounts():
    """导入账号"""
    global accounts
    data = request.json
    account_text = data.get('accounts', '')

    new_accounts = []
    for line in account_text.split('\n'):
        line = line.strip()
        if line and ',' in line:
            phone, password = line.split(',', 1)
            new_accounts.append({
                'phone': phone.strip(),
                'password': password.strip()
            })

    accounts.extend(new_accounts)
    return jsonify({
        'success': True,
        'message': f'成功导入 {len(new_accounts)} 个账号'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1848, debug=True)