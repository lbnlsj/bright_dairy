from flask import Flask, render_template, jsonify, request
from datetime import datetime
import threading
import json
import requests
import queue
from pathlib import Path
from loguru import logger
from data_manager import DataManager
from monitor_core import MonitorTask, send_dingding_msg

# Configure logging
logger.remove()
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

# Global variables
data_manager = DataManager()
monitor_task = None
log_queue = queue.Queue()


class MonitoringState:
    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.error_count = 0
        self.success_count = 0


state = MonitoringState()

# Load initial data
accounts = data_manager.load_accounts()
categories = data_manager.load_categories()


def update_config():
    try:
        url = 'https://m.4008117117.com/api/item/shop-category/tree?frontCategoryId=4403&longitude=120.2126&latitude=30.290851&isFinish=true'
        response = requests.get(url)

        if not response.ok:
            logger.error(f"Failed to fetch config: HTTP {response.status_code}")
            return False

        data = response.json()
        if not data.get('success'):
            logger.error("API response indicates failure")
            return False

        # Get the childrenList from first item in data
        child_list = data.get('data', [])[0].get('childrenList', [])

        # Initialize new area config
        new_area_config = {}

        # Extract required categories
        for child in child_list:
            name = child['name']
            area_id = child['id']

            # Only add specific areas we're interested in
            new_area_config[name] = area_id

        # Add fixed entry for 积分商城
        new_area_config['积分商城'] = '3586'

        # Load existing config
        config_path = Path('data/config.json')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                current_config = json.load(f)
        else:
            current_config = {}

        # Update area_config section
        current_config['area_config'] = new_area_config

        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, ensure_ascii=False, indent=2)

        logger.info("Successfully updated config with new area mappings")
        return True

    except Exception as e:
        logger.exception("Failed to update config")
        return False


@app.route('/')
def index():
    update_config()
    return render_template('index.html')


# 在 app.py 全局变量部分添加
activity_log_queue = queue.Queue()
point_log_queue = queue.Queue()


# 修改 start_monitoring 函数
@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    global monitor_task
    global categories
    categories = data_manager.load_categories()
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

        # Initialize monitor task with both log queues
        monitor_task = MonitorTask(accounts, categories, activity_log_queue, point_log_queue)
        monitor_task.start()

        state.is_running = True
        state.start_time = datetime.now()
        state.error_count = 0
        state.success_count = 0

        logger.info("Monitor started")

        return jsonify({
            'success': True,
            'message': '监控已启动'
        })
    except Exception as e:
        logger.exception("Failed to start monitor")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 修改日志获取函数
@app.route('/api/logs/activity')
def get_activity_logs():
    """获取活动商品日志"""
    try:
        logs = []
        while not activity_log_queue.empty():
            try:
                logs.append(activity_log_queue.get_nowait())
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
        logs = []
        while not point_log_queue.empty():
            try:
                logs.append(point_log_queue.get_nowait())
            except queue.Empty:
                break
        return jsonify(logs)
    except Exception as e:
        logger.exception("获取积分日志失败")
        return jsonify({'message': str(e)}), 500


@app.route('/api/config/areas', methods=['GET'])
def get_area_config():
    """获取区域配置"""
    try:
        config = data_manager.load_config()
        return jsonify(config.get('area_config', {}))
    except Exception as e:
        logger.exception("获取区域配置失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有类目"""
    try:
        categories = data_manager.load_categories()
        return jsonify(categories)
    except Exception as e:
        logger.exception("获取类目失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/categories', methods=['POST'])
def add_category():
    global categories
    categories = data_manager.load_categories()

    """添加新类目"""
    try:
        data = request.json
        area_id = data.get('area_id')
        names = data.get('names', [])

        if not area_id or not names:
            return jsonify({
                'success': False,
                'message': '区域ID和商品名不能为空'
            }), 400

        added_categories = []
        for name in names:
            name = name.strip()
            if name:  # 忽略空白名称
                new_category = data_manager.add_category(area_id, name)
                added_categories.append(new_category)

        logger.info(f"添加类目成功: {added_categories}")
        return jsonify({
            'success': True,
            'message': '类目添加成功',
            'data': added_categories
        })

    except Exception as e:
        logger.exception("添加类目失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/categories/<monitor_id>', methods=['DELETE'])
def delete_category(monitor_id):
    global categories
    categories = data_manager.load_categories()

    """删除类目"""
    try:
        # 检查是否正在监控中
        if monitor_task and monitor_task.is_running():
            return jsonify({
                'success': False,
                'message': '监控运行中，无法删除类目'
            }), 400

        if data_manager.delete_category(monitor_id):
            logger.info(f"删除类目成功: {monitor_id}")
            return jsonify({
                'success': True,
                'message': '类目删除成功'
            })

        return jsonify({
            'success': False,
            'message': '类目不存在'
        }), 404
    except Exception as e:
        logger.exception("删除类目失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """获取所有账号"""
    try:
        accounts = data_manager.load_accounts()
        return jsonify(accounts)
    except Exception as e:
        logger.exception("获取账号列表失败")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/accounts', methods=['POST'])
def import_accounts():
    """导入账号"""
    try:
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

        if not new_accounts:
            return jsonify({
                'success': False,
                'message': '没有有效的账号数据'
            }), 400

        merged_accounts = new_accounts

        # 保存更新后的账号列表
        if data_manager.save_accounts(merged_accounts):
            global accounts
            accounts = merged_accounts
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


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """停止监控"""
    global monitor_task

    try:
        if not state.is_running:
            return jsonify({
                'success': False,
                'message': '监控未在运行'
            })

        if monitor_task:
            monitor_task.stop()
            monitor_task = None

        state.is_running = False
        logger.info("Monitor stopped")

        return jsonify({
            'success': True,
            'message': '监控已停止'
        })
    except Exception as e:
        logger.exception("Failed to stop monitor")
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
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '未找到请求的资源'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


def start_monitor_on_startup():
    """Start monitoring when application starts"""
    global monitor_task, categories, accounts

    try:
        # 重新加载最新数据
        categories = data_manager.load_categories()
        accounts = data_manager.load_accounts()

        if not categories:
            logger.warning("没有可监控的类目，跳过自动启动")
            return

        if not accounts:
            logger.warning("没有可用的账号，跳过自动启动")
            return

        # 初始化监控任务
        monitor_task = MonitorTask(accounts, categories)
        monitor_task.start()

        state.is_running = True
        state.start_time = datetime.now()
        state.error_count = 0
        state.success_count = 0

        logger.info("监控已自动启动")
        import time

        while 1:
            time.sleep(1)

    except Exception as e:

        logger.exception("自动启动监控失败")


if __name__ == '__main__':
    # Ensure log directory exists
    send_dingding_msg('开始运行')
    Path("logs").mkdir(exist_ok=True)

    # 自动启动监控
    # start_monitor_on_startup()

    # Start application
    app.run(host='0.0.0.0', port=7485, debug=True)
