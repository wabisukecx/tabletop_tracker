import streamlit as st
from typing import Dict, List

class ScoreSheetManager:
    """スコアシート管理クラス"""
    
    @staticmethod
    def create_generic_sheet() -> Dict:
        """汎用スコアシート作成"""
        return {
            "name": st.session_state.lang_manager.get_text("scoresheet.create_custom"),
            "fields": [
                {"name": st.session_state.lang_manager.get_text("scoresheet.score_items"), "type": "number", "default": 0},
            ],
            "total_field": st.session_state.lang_manager.get_text("play_recording.total_label")
        }
    
    @staticmethod
    def create_custom_sheet(game_name: str, fields: List[Dict]) -> Dict:
        """カスタムスコアシート作成"""
        return {
            "name": f"{game_name} " + st.session_state.lang_manager.get_text("scoresheet.title"),
            "fields": fields,
            "total_field": st.session_state.lang_manager.get_text("play_recording.total_label")
        }