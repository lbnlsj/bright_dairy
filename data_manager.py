import json
import os
from typing import List, Dict
from pathlib import Path
import uuid


class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.accounts_file = self.data_dir / "accounts.json"
        self.categories_file = self.data_dir / "categories.json"
        self.config_file = self.data_dir / "config.json"

        self._init_files()

    def _init_files(self):
        """Initialize data files if they don't exist"""
        if not self.accounts_file.exists():
            self.save_accounts([])
        if not self.categories_file.exists():
            self.save_categories([])
        if not self.config_file.exists():
            self._init_config()

    def _init_config(self):
        """Initialize config file with default values"""
        default_config = {
            "area_config": {
                "光明文创": "8346",
                "“梅奔”星光夜": "8329",
                "星耀东体夜": "8338",
                "积分商城": "3586"
            }
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

    def load_config(self) -> dict:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def load_accounts(self) -> List[Dict]:
        """Load accounts from file"""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading accounts: {e}")
            return []

    def save_accounts(self, accounts: List[Dict]) -> bool:
        """Save accounts to file"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving accounts: {e}")
            return False

    def load_categories(self) -> List[Dict]:
        """Load categories from file"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading categories: {e}")
            return []

    def save_categories(self, categories: List[Dict]) -> bool:
        """Save categories to file"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(categories, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving categories: {e}")
            return False

    def add_category(self, area_id: str, name: str) -> Dict:
        """Add a new category with a unique monitor_id"""
        categories = self.load_categories()

        # 生成唯一的monitor_id
        monitor_id = str(uuid.uuid4())

        new_category = {
            "monitor_id": monitor_id,  # 唯一监控ID
            "area_id": area_id,  # 区域ID
            "name": name.strip()  # 商品名称
        }

        categories.append(new_category)
        self.save_categories(categories)
        return new_category

    def delete_category(self, monitor_id: str) -> bool:
        """Delete a category by monitor_id"""
        categories = self.load_categories()
        original_length = len(categories)

        categories = [cat for cat in categories if cat.get('monitor_id') != monitor_id]

        if len(categories) < original_length:
            self.save_categories(categories)
            return True
        return False

    def get_categories_by_area(self, area_id: str) -> List[Dict]:
        """Get all categories for a specific area"""
        categories = self.load_categories()
        return [cat for cat in categories if cat.get('area_id') == area_id]