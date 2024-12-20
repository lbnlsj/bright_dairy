import json
import os
from typing import List, Dict
from pathlib import Path


class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.accounts_file = self.data_dir / "accounts.json"
        self.categories_file = self.data_dir / "categories.json"
        self.config_file = self.data_dir / "config.json"  # 新增配置文件

        # Initialize files if they don't exist
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
