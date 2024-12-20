from flask import Flask, render_template, jsonify, request
import random
import time
from datetime import datetime
import threading
import queue
import json
import os
from pathlib import Path
from data_manager import DataManager
from loguru import logger

# 设置日志配置
logger.remove()  # 移除默认的处理器
logger.add(
    "logs/auto_order_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    encoding="utf-8"
)
logger.add(
    "logs/errors_{time}.log",
    rotation="100 MB",
    retention="10 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    encoding="utf-8"
)

app = Flask(__name__)

# 全局变量
monitoring = False
log_queue = queue.Queue()
monitor_thread = None
data_manager = DataManager()  # 创建数据管理器实例

# 初始化全局数据
accounts = data_manager.load_accounts()
categories = data_manager.load_categories()
running_categories = set()


class MonitoringState:
    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.error_count = 0
        self.success_count = 0


state = MonitoringState()


def generate_mock_log():
    """生成模拟日志"""
    log_types = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'SUCCESS']
    log_templates = [
        ("正在检查商品 {0}", lambda: random.choice(["牛奶", "酸奶", "奶粉"])),
        ("发现 {0} 个匹配商品", lambda: str(random.randint(0, 5))),
        ("尝试为账号 {0} 下单商品 {1}", lambda: (
            f"138****{random.randint(1000, 9999)}",
            random.choice(["牛奶", "酸奶", "奶粉"])
        )),
        ("账号 {0} 登录失败", lambda: f"138****{random.randint(1000, 9999)}"),
        ("等待 {0} 秒后进行下一次检查", lambda: str(random.randint(1, 30)))
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
    logger.info("开始监控任务")
    state.start_time = datetime.now()
    while state.is_running:
        try:
            log_message = generate_mock_log()
            log_queue.put(log_message)
            # 记录到文件日志
            logger.info(log_message)
            time.sleep(random.uniform(0.5, 2.0))
        except Exception as e:
            logger.exception("监控任务出错")
            state.error_count += 1
            time.sleep(1)
        finally:
            if state.error_count > 50:  # 如果错误次数过多，自动停止监控
                logger.error("错误次数过多，自动停止监控")
                state.is_running = False
                break


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有类目"""
    try:
        return jsonify(categories)
    except Exception as e:
        logger.exception("获取类目失败")
        return jsonify({'message': '获取类目失败'}), 500


@app.route('/api/categories', methods=['POST'])
def add_category():
    """添加新类目"""
    try:
        data = request.json
        category_id = data.get('id')
        name = data.get('name')

        if not category_id or not name:
            return jsonify({'message': '类目ID和名称不能为空'}), 400

        # 检查ID是否已存在
        if any(c['id'] == category_id for c in categories):
            return jsonify({'message': '类目ID已存在'}), 400

        new_category = {
            'id': category_id,
            'name': name
        }
        categories.append(new_category)
        # 保存更新后的类目数据
        if data_manager.save_categories(categories):
            logger.info(f"添加类目成功: {new_category}")
            return jsonify({'message': '类目添加成功'})
        else:
            raise Exception("保存类目数据失败")

    except Exception as e:
        logger.exception("添加类目失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """更新类目"""
    try:
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

                old_category = category.copy()
                category['id'] = new_id
                category['name'] = new_name

                # 保存更新后的类目数据
                if data_manager.save_categories(categories):
                    logger.info(f"更新类目成功: {old_category} -> {category}")
                    return jsonify({'message': '类目更新成功'})
                else:
                    raise Exception("保存类目数据失败")

        return jsonify({'message': '类目不存在'}), 404
    except Exception as e:
        logger.exception("更新类目失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除类目"""
    try:
        if category_id in running_categories:
            return jsonify({'message': '无法删除正在监控的类目'}), 400

        for i, category in enumerate(categories):
            if category['id'] == category_id:
                deleted_category = categories.pop(i)
                # 保存更新后的类目数据
                if data_manager.save_categories(categories):
                    logger.info(f"删除类目成功: {deleted_category}")
                    return jsonify({'message': '类目删除成功'})
                else:
                    raise Exception("保存类目数据失败")

        return jsonify({'message': '类目不存在'}), 404
    except Exception as e:
        logger.exception("删除类目失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """启动监控"""
    global monitor_thread

    try:
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
        state.error_count = 0
        state.success_count = 0

        if not monitor_thread or not monitor_thread.is_alive():
            monitor_thread = threading.Thread(target=monitoring_task)
            monitor_thread.daemon = True
            monitor_thread.start()
            logger.info("监控线程已启动")

        return jsonify({
            'success': True,
            'message': '监控已启动'
        })
    except Exception as e:
        logger.exception("启动监控失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """停止监控"""
    global monitor_thread

    try:
        if not state.is_running:
            return jsonify({
                'success': False,
                'message': '监控未在运行'
            })

        state.is_running = False
        if monitor_thread and monitor_thread.is_alive():
            monitor_thread = None
            logger.info("监控线程已停止")

        return jsonify({
            'success': True,
            'message': '监控已停止'
        })
    except Exception as e:
        logger.exception("停止监控失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/status')
def get_status():
    """获取当前状态"""
    try:
        status = {
            'is_running': state.is_running,
            'account_count': len(accounts),
            'category_count': len(categories),
            'error_count': state.error_count,
            'success_count': state.success_count
        }

        if state.start_time:
            status['running_time'] = str(datetime.now() - state.start_time)

        return jsonify(status)
    except Exception as e:
        logger.exception("获取状态失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/logs/activity')
def get_activity_logs():
    """获取活动商品日志"""
    try:
        logs = []
        while not log_queue.empty():
            try:
                logs.append(log_queue.get_nowait())
            except queue.Empty:
                break
        return jsonify(logs)
    except Exception as e:
        logger.exception("获取活动日志失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/logs/points')
def get_point_logs():
    """获取积分商品日志"""
    try:
        # 此处可以添加积分商品的专门日志
        return jsonify([])
    except Exception as e:
        logger.exception("获取积分日志失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """获取所有账号"""
    try:
        return jsonify(accounts)
    except Exception as e:
        logger.exception("获取账号列表失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/accounts', methods=['POST'])
def import_accounts():
    """导入账号"""
    try:
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

        # 添加新账号并保存
        accounts.extend(new_accounts)
        if data_manager.save_accounts(accounts):
            logger.info(f"成功导入 {len(new_accounts)} 个账号")
            return jsonify({
                'success': True,
                'message': f'成功导入 {len(new_accounts)} 个账号'
            })
        else:
            raise Exception("保存账号数据失败")

    except Exception as e:
        logger.exception("导入账号失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/config/areas', methods=['GET'])
def get_area_config():
    """获取区域配置"""
    try:
        config = data_manager.load_config()
        return jsonify(config.get('area_config', {}))
    except Exception as e:
        logger.exception("获取区域配置失败")
        return jsonify({'message': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': '未找到请求的资源'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)

    # 启动应用
    app.run(host='0.0.0.0', port=1848, debug=True)
