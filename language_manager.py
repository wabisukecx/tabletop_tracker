import streamlit as st
import yaml
import os
from typing import Dict

class LanguageManager:
    """多言語管理クラス"""
    
    def __init__(self, language_dir="language"):
        self.language_dir = language_dir
        self.current_language = "ja"  # デフォルト言語
        self.translations = {}
        self.available_languages = {}
        
        # 言語ディレクトリを作成
        os.makedirs(language_dir, exist_ok=True)
        
        # 設定ファイルパス
        self.settings_file = os.path.join(language_dir, "settings.yaml")
        
        # 利用可能な言語を検出
        self._discover_languages()
        
        # 設定を読み込み
        self._load_settings()
        
        # 翻訳を読み込み
        self._load_translations()
    
    def _discover_languages(self):
        """利用可能な言語を検出"""
        self.available_languages = {
            "ja": "日本語 (Japanese)",
            "en": "English"
        }
        
        # 言語ディレクトリ内のyamlファイルを検索
        if os.path.exists(self.language_dir):
            for file in os.listdir(self.language_dir):
                if file.endswith('.yaml') and file != 'settings.yaml':
                    lang_code = file[:-5]  # .yamlを除去
                    if lang_code not in self.available_languages:
                        self.available_languages[lang_code] = lang_code.upper()
    
    def _load_settings(self):
        """設定を読み込み"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = yaml.safe_load(f)
                    if settings and 'language' in settings:
                        self.current_language = settings['language']
        except Exception as e:
            st.error(f"Language settings load error: {str(e)}")
    
    def _save_settings(self):
        """設定を保存"""
        try:
            settings = {'language': self.current_language}
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(settings, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            st.error(f"Language settings save error: {str(e)}")
    
    def _load_translations(self):
        """翻訳ファイルを読み込み"""
        file_path = os.path.join(self.language_dir, f"{self.current_language}.yaml")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = yaml.safe_load(f) or {}
            else:
                st.warning(f"Language file not found: {file_path}")
                self.translations = {}
        except Exception as e:
            st.error(f"Translation file load error: {str(e)}")
            self.translations = {}
    
    def set_language(self, language_code: str):
        """言語を設定"""
        if language_code in self.available_languages:
            self.current_language = language_code
            self._save_settings()
            self._load_translations()
            return True
        return False
    
    def get_text(self, key: str, **kwargs) -> str:
        """翻訳テキストを取得"""
        try:
            # ネストしたキーを処理 (例: "app.title")
            keys = key.split('.')
            value = self.translations
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return key  # キーが見つからない場合はキーをそのまま返す
            
            # 文字列フォーマットを適用
            if isinstance(value, str) and kwargs:
                try:
                    return value.format(**kwargs)
                except (KeyError, ValueError):
                    return value
            
            return str(value) if value is not None else key
            
        except Exception:
            return key
    
    def get_current_language(self) -> str:
        """現在の言語コードを取得"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """利用可能な言語一覧を取得"""
        return self.available_languages