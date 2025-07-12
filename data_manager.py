import streamlit as st
import yaml
import os
from datetime import datetime
from typing import Dict, List

class DataManager:
    """データ管理クラス - 分離されたファイル管理"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # データディレクトリを作成
        os.makedirs(data_dir, exist_ok=True)
        
        # 各データファイルのパス
        self.files = {
            "games": os.path.join(data_dir, "games.yaml"),
            "players": os.path.join(data_dir, "players.yaml"),
            "plays": os.path.join(data_dir, "plays.yaml"),
            "score_sheets": os.path.join(data_dir, "score_sheets.yaml")
        }
        
        # データを読み込み
        self.data = self.load_all_data()
    
    def load_file(self, file_path: str, default_value) -> any:
        """個別ファイル読み込み"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    return data if data is not None else default_value
        except Exception as e:
            st.error(st.session_state.lang_manager.get_text("errors.file_load_error", path=file_path, error=str(e)))
        return default_value
    
    def save_file(self, file_path: str, data: any):
        """個別ファイル保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            st.error(st.session_state.lang_manager.get_text("errors.file_save_error", path=file_path, error=str(e)))
    
    def load_all_data(self) -> Dict:
        """全データ読み込み"""
        return {
            "games": self.load_file(self.files["games"], {}),
            "players": self.load_file(self.files["players"], {}),
            "plays": self.load_file(self.files["plays"], []),
            "score_sheets": self.load_file(self.files["score_sheets"], {})
        }
    
    def save_games(self):
        """ゲームデータ保存"""
        self.save_file(self.files["games"], self.data["games"])
    
    def save_players(self):
        """プレイヤーデータ保存"""
        self.save_file(self.files["players"], self.data["players"])
    
    def save_plays(self):
        """プレイ記録保存"""
        self.save_file(self.files["plays"], self.data["plays"])
    
    def save_score_sheets(self):
        """スコアシート保存"""
        self.save_file(self.files["score_sheets"], self.data["score_sheets"])
    
    def save_data(self, data_type: str = None):
        """データ保存（指定されたタイプのみ、または全て）"""
        if data_type:
            if data_type == "games":
                self.save_games()
            elif data_type == "players":
                self.save_players()
            elif data_type == "plays":
                self.save_plays()
            elif data_type == "score_sheets":
                self.save_score_sheets()
        else:
            # 全て保存
            self.save_games()
            self.save_players()
            self.save_plays()
            self.save_score_sheets()
    
    def add_game(self, game_data: Dict):
        """ゲーム追加"""
        # より厳密なデータ検証
        if not game_data:
            st.error(st.session_state.lang_manager.get_text("errors.game_data_empty"))
            return False
            
        if not game_data.get("id"):
            st.error(st.session_state.lang_manager.get_text("errors.game_id_not_found"))
            return False
            
        if not game_data.get("name") or game_data.get("name") == st.session_state.lang_manager.get_text("common.unknown_game"):
            st.error(st.session_state.lang_manager.get_text("errors.valid_game_name_not_found"))
            return False
        
        # gamesが存在しない場合は初期化
        if "games" not in self.data or self.data["games"] is None:
            self.data["games"] = {}
        
        # 既に登録済みかチェック
        if game_data["id"] in self.data["games"]:
            st.warning(st.session_state.lang_manager.get_text("errors.game_already_registered", name=game_data['name']))
            return False
        
        try:
            self.data["games"][game_data["id"]] = game_data
            self.save_data("games")  # ゲームデータのみ保存
            st.success(st.session_state.lang_manager.get_text("player_management.added_success", name=game_data['name']))
            return True
        except Exception as e:
            st.error(st.session_state.lang_manager.get_text("errors.game_add_error", error=str(e)))
            return False
    
    def delete_game(self, game_id: str):
        """ゲーム削除"""
        if game_id in self.data.get("games", {}):
            game_name = self.data["games"][game_id].get("name", st.session_state.lang_manager.get_text("common.unknown_game"))
            
            # 関連するプレイ記録もチェック
            plays = self.data.get("plays", [])
            related_plays = [p for p in plays if p.get("game_id") == game_id]
            if related_plays:
                st.warning(st.session_state.lang_manager.get_text("game_management.has_play_records", count=len(related_plays)))
                return False
            
            del self.data["games"][game_id]
            
            # スコアシートも削除
            if game_id in self.data.get("score_sheets", {}):
                del self.data["score_sheets"][game_id]
                self.save_data("score_sheets")  # スコアシートファイル更新
            
            self.save_data("games")  # ゲームデータのみ保存
            st.success(st.session_state.lang_manager.get_text("game_management.deleted", name=game_name))
            return True
        return False
    
    def add_player(self, player_name: str, player_data: Dict = None):
        """プレイヤー追加"""
        if not player_name or not player_name.strip():
            return False
            
        player_name = player_name.strip()
        
        # playersが存在しない場合は初期化
        if "players" not in self.data or self.data["players"] is None:
            self.data["players"] = {}
        
        if player_name not in self.data["players"]:
            if player_data:
                self.data["players"][player_name] = player_data
            else:
                self.data["players"][player_name] = {
                    "name": player_name,
                    "notes": "",
                    "created_at": datetime.now().isoformat()
                }
            self.save_data("players")  # プレイヤーデータのみ保存
            return True
        return False
    
    def add_play(self, play_data: Dict):
        """プレイ記録追加"""
        # playsが存在しない場合は初期化
        if "plays" not in self.data or self.data["plays"] is None:
            self.data["plays"] = []
        
        play_data["id"] = len(self.data["plays"])
        play_data["created_at"] = datetime.now().isoformat()
        self.data["plays"].append(play_data)
        self.save_data("plays")  # プレイ記録のみ保存
    
    def get_game_stats(self, game_id: str) -> Dict:
        """ゲーム統計取得"""
        plays = self.data.get("plays", [])
        plays = [p for p in plays if p.get("game_id") == game_id]
        if not plays:
            return {}
        
        total_plays = len(plays)
        total_players = sum(len(p.get("scores", {})) for p in plays)
        avg_duration = sum(p.get("duration", 0) for p in plays) / total_plays if total_plays > 0 else 0
        
        return {
            "total_plays": total_plays,
            "total_players": total_players,
            "avg_duration": round(avg_duration, 1),
            "plays": plays
        }
    
    def get_data_info(self) -> Dict:
        """データファイル情報取得"""
        info = {}
        for data_type, file_path in self.files.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                info[data_type] = {
                    "file_path": file_path,
                    "file_size": f"{file_size:,} bytes",
                    "modified_time": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "record_count": len(self.data.get(data_type, []))
                }
            else:
                info[data_type] = {
                    "file_path": file_path,
                    "file_size": st.session_state.lang_manager.get_text("common.none"),
                    "modified_time": st.session_state.lang_manager.get_text("common.none"),
                    "record_count": 0
                }
        return info
    
    def get_localized_game_name(self, game_id: str, language_code: str = None) -> str:
        """言語に応じたゲーム名を取得"""
        if language_code is None:
            language_code = st.session_state.lang_manager.get_current_language()
        
        game = self.data.get("games", {}).get(game_id, {})
        if not game:
            return st.session_state.lang_manager.get_text("common.unknown_game")
        
        # 新しい形式（names辞書）の場合
        if "names" in game:
            names = game["names"]
            
            # 現在の言語に応じた名前を選択
            if language_code == "ja" and names.get("japanese"):
                return names["japanese"]
            elif language_code == "en" and names.get("english"):
                return names["english"]
            elif names.get("english"):  # フォールバック：英語
                return names["english"]
            elif names.get("primary"):  # フォールバック：プライマリ
                return names["primary"]
            elif names.get("japanese"):  # フォールバック：日本語
                return names["japanese"]
        
        # 古い形式（name文字列）の場合（後方互換性）
        if "name" in game:
            return game["name"]
        
        return st.session_state.lang_manager.get_text("common.unknown_game")
    
    def update_game_multilingual_support(self):
        """既存ゲームデータを多言語対応形式に更新"""
        games = self.data.get("games", {})
        updated = False
        
        for game_id, game in games.items():
            # 古い形式の場合、新しい形式に変換
            if "name" in game and "names" not in game:
                old_name = game["name"]
                
                # 言語判定を改善
                is_japanese = self._is_japanese_name(old_name)
                is_english = self._is_english_name(old_name)
                
                # 新しい形式に変換
                if is_japanese:
                    game["names"] = {
                        "primary": old_name,
                        "japanese": old_name,
                        "english": "",
                        "alternates": []
                    }
                elif is_english:
                    game["names"] = {
                        "primary": old_name,
                        "japanese": "",
                        "english": old_name,
                        "alternates": []
                    }
                else:
                    # その他の言語（中国語など）
                    game["names"] = {
                        "primary": old_name,
                        "japanese": "",
                        "english": "",
                        "alternates": [old_name]
                    }
                
                updated = True
        
        if updated:
            self.save_data("games")
            return True
        return False
    
    def _is_japanese_name(self, text: str) -> bool:
        """日本語ゲーム名かどうかを判定"""
        if not text:
            return False
        
        # ひらがな、カタカナが含まれていれば確実に日本語
        for char in text:
            if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
                return True
        
        # 漢字のみの場合の判定を厳格化
        has_kanji = any('\u4E00' <= char <= '\u9FAF' for char in text)
        if has_kanji:
            # 英数字や日本語特有の記号が含まれている場合は日本語
            if any(char in text for char in '・〜～：'):
                return True
            
            # 漢字のみで3文字以下かつ、よくある日本語ゲーム名パターン
            kanji_only = all('\u4E00' <= char <= '\u9FAF' for char in text)
            if kanji_only and len(text) <= 3:
                return True
        
        return False
    
    def _is_english_name(self, text: str) -> bool:
        """英語ゲーム名かどうかを判定"""
        if not text:
            return False
        
        # ASCII文字のみで構成され、英字が含まれている
        return text.isascii() and any(char.isalpha() for char in text)