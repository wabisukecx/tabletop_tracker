import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
from typing import Dict, List

class BGGApi:
    """BoardGameGeek API クライアント"""
    BASE_URL = "https://boardgamegeek.com/xmlapi2"
    
    @staticmethod
    def search_games(query: str) -> List[Dict]:
        """ゲーム検索"""
        try:
            url = f"{BGGApi.BASE_URL}/search"
            params = {"query": query, "type": "boardgame"}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                games = []
                for item in root.findall(".//item"):
                    # 名前の取得を改善
                    name_elem = item.find("name")
                    if name_elem is not None:
                        name = name_elem.get("value", "")
                    else:
                        name = st.session_state.lang_manager.get_text("common.unknown_game")
                    
                    # 年の取得
                    year_elem = item.find("yearpublished")
                    year = year_elem.get("value", "") if year_elem is not None else ""
                    
                    game = {
                        "id": item.get("id"),
                        "name": name,
                        "year": year
                    }
                    games.append(game)
                
                return games
            else:
                st.error(st.session_state.lang_manager.get_text("errors.bgg_search_error", code=response.status_code))
                
        except Exception as e:
            st.error(st.session_state.lang_manager.get_text("errors.search_error", error=str(e)))
        return []
    
    @staticmethod
    def get_game_details(game_id: str) -> Dict:
        """ゲーム詳細情報取得"""
        try:
            url = f"{BGGApi.BASE_URL}/thing"
            params = {"id": game_id, "stats": "1"}
            
            # 最大3回まで試行
            for attempt in range(3):
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 202:
                    # 202レスポンスの場合は少し待機して再試行
                    time.sleep(3)
                    continue
                elif response.status_code == 200:
                    break
                else:
                    st.error(st.session_state.lang_manager.get_text("errors.bgg_api_error", code=response.status_code))
                    return {}
            
            if response.status_code != 200:
                st.error(st.session_state.lang_manager.get_text("errors.bgg_no_response"))
                return {}

            # XML解析
            root = ET.fromstring(response.content)
            
            item = root.find(".//item")
            if item is None:
                st.error(st.session_state.lang_manager.get_text("errors.game_info_not_found"))
                return {}
            
            # 全ての言語名を取得
            names = BGGApi._extract_all_names(item)
            
            if not names.get("primary"):
                st.error(st.session_state.lang_manager.get_text("errors.game_name_not_found"))
                return {}
            
            # 画像URLの取得
            image_url = BGGApi._extract_image_url(item)
            
            # その他の情報取得
            minplayers_elem = item.find(".//minplayers")
            min_players = minplayers_elem.get("value", "1") if minplayers_elem is not None else "1"
            
            maxplayers_elem = item.find(".//maxplayers")
            max_players = maxplayers_elem.get("value", "4") if maxplayers_elem is not None else "4"
            
            playingtime_elem = item.find(".//playingtime")
            playing_time = playingtime_elem.get("value", "60") if playingtime_elem is not None else "60"
            
            # 最適人数の取得
            best_player_count = BGGApi.get_best_player_count(item)
            
            # 評価情報とランキング情報の取得
            rating_info = BGGApi._extract_rating_and_ranking(item)

            game_data = {
                "id": game_id,
                "names": names,  # 全言語名を保存
                "name": names.get("primary", ""),  # 後方互換性のため
                "image_url": image_url,
                "min_players": str(min_players),
                "max_players": str(max_players),
                "playing_time": str(playing_time),
                "best_player_count": best_player_count,
                "rating": rating_info["rating"],
                "ranking": rating_info["ranking"]  # ランキング情報を追加
            }
            
            return game_data
                
        except requests.exceptions.Timeout:
            st.error(st.session_state.lang_manager.get_text("errors.bgg_timeout"))
        except ET.ParseError as e:
            st.error(st.session_state.lang_manager.get_text("errors.bgg_parse_error"))
        except Exception as e:
            st.error(st.session_state.lang_manager.get_text("errors.game_detail_error", error=str(e)))
        return {}
    
    @staticmethod
    def _extract_all_names(item) -> Dict:
        """全ての言語名を抽出"""
        names = {
            "primary": "",
            "japanese": "",
            "english": "",
            "alternates": []
        }
        
        # 全ての名前要素を取得
        name_candidates = []
        primary_name = ""
        
        for name_elem in item.findall(".//name"):
            name_value = name_elem.get("value", "")
            name_type = name_elem.get("type", "")
            
            if not name_value:
                continue
            
            name_candidates.append({
                "value": name_value,
                "type": name_type,
                "is_japanese": BGGApi._is_japanese_text(name_value),
                "is_english": BGGApi._is_english_text(name_value)
            })
            
            # プライマリ名を記録
            if name_type == "primary":
                primary_name = name_value
        
        # 名前の分類と設定
        for candidate in name_candidates:
            name_value = candidate["value"]
            
            # プライマリ名の設定
            if candidate["type"] == "primary":
                names["primary"] = name_value
            
            # 日本語名の設定（ひらがな・カタカナを含む）
            if candidate["is_japanese"] and not names["japanese"]:
                names["japanese"] = name_value
            
            # 英語名の設定（ASCII文字のみ）
            elif candidate["is_english"] and not names["english"]:
                names["english"] = name_value
            
            # その他の名前は代替名として保存
            else:
                if name_value not in [names.get("primary"), names.get("japanese"), names.get("english")]:
                    names["alternates"].append(name_value)
        
        # プライマリ名が設定されていない場合の優先順位
        if not names["primary"]:
            if names["japanese"]:
                names["primary"] = names["japanese"]
            elif names["english"]:
                names["primary"] = names["english"]
            elif name_candidates:
                names["primary"] = name_candidates[0]["value"]
        
        # 重複を除去
        names["alternates"] = list(dict.fromkeys(names["alternates"]))  # 順序を保持しつつ重複除去
        
        return names
    
    @staticmethod
    def _is_japanese_text(text: str) -> bool:
        """日本語テキストかどうかを判定"""
        if not text:
            return False
        
        # ひらがな、カタカナが含まれていれば確実に日本語
        for char in text:
            if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
                return True
        
        # 漢字のみの場合は、よくある日本語ゲーム名のパターンをチェック
        has_kanji = any('\u4E00' <= char <= '\u9FAF' for char in text)
        if has_kanji:
            # 英数字や記号が含まれている場合は日本語の可能性が高い
            has_ascii = any(char.isascii() for char in text)
            if has_ascii:
                return True
            
            # 漢字のみで短い場合（1-6文字）は日本語の可能性が高い
            kanji_only = all('\u4E00' <= char <= '\u9FAF' or char in '・' for char in text)
            if kanji_only and 1 <= len(text) <= 6:
                return True
        
        return False
    
    @staticmethod
    def _is_english_text(text: str) -> bool:
        """英語テキストかどうかを判定"""
        if not text:
            return False
        
        # ASCII文字のみで構成されているかチェック
        if not text.isascii():
            return False
        
        # 英字が含まれているかチェック
        has_alpha = any(char.isalpha() for char in text)
        return has_alpha
    
    @staticmethod
    def _extract_image_url(item) -> str:
        """画像URLの抽出"""
        image_url = ""
        image_elem = item.find(".//image")
        if image_elem is not None and image_elem.text:
            image_url = image_elem.text.strip()
        
        # サムネイルURLの取得（画像がない場合のフォールバック）
        if not image_url:
            thumbnail_elem = item.find(".//thumbnail")
            if thumbnail_elem is not None and thumbnail_elem.text:
                image_url = thumbnail_elem.text.strip()
        
        return image_url
    
    @staticmethod
    def _extract_rating_and_ranking(item) -> Dict:
        """評価とランキング情報の抽出"""
        rating_info = {
            "rating": 0.0,
            "ranking": {
                "overall": None,
                "strategy": None,
                "family": None,
                "party": None,
                "abstract": None,
                "thematic": None,
                "war": None,
                "customizable": None
            }
        }
        
        try:
            stats_elem = item.find(".//statistics")
            if stats_elem is not None:
                ratings_elem = stats_elem.find(".//ratings")
                if ratings_elem is not None:
                    # 評価の取得
                    rating_elem = ratings_elem.find(".//average")
                    if rating_elem is not None and rating_elem.get("value"):
                        rating_info["rating"] = float(rating_elem.get("value"))
                    
                    # ランキングの取得
                    ranks_elem = ratings_elem.find(".//ranks")
                    if ranks_elem is not None:
                        for rank_elem in ranks_elem.findall(".//rank"):
                            rank_type = rank_elem.get("type", "")
                            rank_name = rank_elem.get("name", "")
                            rank_value = rank_elem.get("value", "")
                            
                            # 数値でない場合（"Not Ranked"など）はNoneのまま
                            try:
                                rank_value = int(rank_value) if rank_value.isdigit() else None
                            except (ValueError, AttributeError):
                                rank_value = None
                            
                            # ランキングカテゴリーの判定
                            if rank_type == "subtype" and rank_name == "boardgame":
                                rating_info["ranking"]["overall"] = rank_value
                            elif rank_type == "family":
                                if "strategy" in rank_name.lower():
                                    rating_info["ranking"]["strategy"] = rank_value
                                elif "family" in rank_name.lower():
                                    rating_info["ranking"]["family"] = rank_value
                                elif "party" in rank_name.lower():
                                    rating_info["ranking"]["party"] = rank_value
                                elif "abstract" in rank_name.lower():
                                    rating_info["ranking"]["abstract"] = rank_value
                                elif "thematic" in rank_name.lower():
                                    rating_info["ranking"]["thematic"] = rank_value
                                elif "war" in rank_name.lower():
                                    rating_info["ranking"]["war"] = rank_value
                                elif "customizable" in rank_name.lower():
                                    rating_info["ranking"]["customizable"] = rank_value
        
        except (ValueError, TypeError, AttributeError):
            pass
        
        return rating_info
    
    @staticmethod
    def get_best_player_count(item) -> str:
        """最適人数を取得"""
        try:
            # プレイヤー数投票の取得
            poll_elem = item.find(".//poll[@name='suggested_numplayers']")
            if poll_elem is None:
                return ""
            
            best_counts = []
            recommended_counts = []
            
            for results in poll_elem.findall(".//results"):
                numplayers = results.get("numplayers", "")
                if not numplayers or numplayers == "":
                    continue
                
                # 各投票結果を取得
                best_votes = 0
                recommended_votes = 0
                not_recommended_votes = 0
                
                for result in results.findall(".//result"):
                    value = result.get("value", "")
                    numvotes = int(result.get("numvotes", "0"))
                    
                    if value == "Best":
                        best_votes = numvotes
                    elif value == "Recommended":
                        recommended_votes = numvotes
                    elif value == "Not Recommended":
                        not_recommended_votes = numvotes
                
                # 投票数が十分にある場合のみ判定
                total_votes = best_votes + recommended_votes + not_recommended_votes
                if total_votes < 5:  # 投票数が少ない場合はスキップ
                    continue
                
                # Bestの割合が50%以上の場合
                if best_votes > (total_votes * 0.5):
                    best_counts.append(numplayers)
                # Best + Recommendedの割合が70%以上の場合
                elif (best_votes + recommended_votes) > (total_votes * 0.7):
                    recommended_counts.append(numplayers)
            
            # 結果の整理
            if best_counts:
                if len(best_counts) == 1:
                    return f"{best_counts[0]}{st.session_state.lang_manager.get_text('home.players_suffix')}"
                else:
                    return f"{min(best_counts)}-{max(best_counts)}{st.session_state.lang_manager.get_text('home.players_suffix')}"
            elif recommended_counts:
                if len(recommended_counts) == 1:
                    return f"{recommended_counts[0]}{st.session_state.lang_manager.get_text('home.players_suffix')}"
                else:
                    return f"{min(recommended_counts)}-{max(recommended_counts)}{st.session_state.lang_manager.get_text('home.players_suffix')}"
            
            return ""
            
        except Exception as e:
            return ""