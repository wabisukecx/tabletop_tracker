import streamlit as st
import traceback

# 分割されたモジュールをインポート
from language_manager import LanguageManager
from data_manager import DataManager
from ui_common import render_sidebar, render_home_page
from ui_game_management import render_game_management_page
from ui_player_management import render_player_management_page
from ui_play_recording import render_play_recording_page
from ui_score_sheet import render_score_sheet_page
from ui_statistics import render_statistics_page
from ui_settings import render_settings_page

# ページ設定
st.set_page_config(
    page_title="TabletopTracker",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """セッション状態初期化"""
    if "lang_manager" not in st.session_state:
        st.session_state.lang_manager = LanguageManager()
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = DataManager()
    if "current_page" not in st.session_state:
        st.session_state.current_page = st.session_state.lang_manager.get_text("pages.home")

def main():
    """メイン実行関数"""
    try:
        # セッション状態を初期化
        init_session_state()
        
        # サイドバーを表示
        render_sidebar()

        # 現在のページと言語管理を取得
        lang = st.session_state.lang_manager
        current_page = st.session_state.current_page

        # 現在のページに応じてコンテンツを表示
        if current_page == lang.get_text("pages.home"):
            render_home_page()
        elif current_page == lang.get_text("pages.game_management"):
            render_game_management_page()
        elif current_page == lang.get_text("pages.player_management"):
            render_player_management_page()
        elif current_page == lang.get_text("pages.play_recording"):
            render_play_recording_page()
        elif current_page == lang.get_text("pages.score_sheet_management"):
            render_score_sheet_page()
        elif current_page == lang.get_text("pages.statistics"):
            render_statistics_page()
        elif current_page == lang.get_text("pages.settings"):
            render_settings_page()
        
    except Exception as e:
        # エラーハンドリング
        lang = st.session_state.get('lang_manager')
        if lang:
            st.error(lang.get_text("errors.unexpected_error", error=str(e)))
        else:
            st.error(f"An unexpected error occurred: {str(e)}")
        
        # デバッグ用にトレースバックを表示
        with st.expander("Technical Details (for debugging)"):
            st.code(traceback.format_exc())

# アプリケーションの実行
if __name__ == "__main__":
    main()