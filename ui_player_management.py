import streamlit as st
from datetime import datetime
from utils import get_player_statistics

def render_player_management_page():
    """プレイヤー管理ページ"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("player_management.title"))
    
    dm = st.session_state.data_manager
    
    tab1, tab2 = st.tabs([lang.get_text("player_management.add_tab"), lang.get_text("player_management.registered_tab")])
    
    with tab1:
        _render_add_player_tab(lang, dm)
    
    with tab2:
        _render_registered_players_tab(lang, dm)

def _render_add_player_tab(lang, dm):
    """プレイヤー追加タブの表示"""
    st.markdown(f"### {lang.get_text('player_management.add_new_player')}")
    
    with st.form("add_player_form"):
        player_name = st.text_input(lang.get_text("player_management.player_name"), placeholder=lang.get_text("player_management.player_name_placeholder"))
        player_notes = st.text_area(lang.get_text("player_management.notes"), placeholder=lang.get_text("player_management.notes_placeholder"))
        
        if st.form_submit_button(lang.get_text("player_management.add_button")):
            _handle_add_player(lang, dm, player_name, player_notes)

def _handle_add_player(lang, dm, player_name, player_notes):
    """プレイヤー追加の処理"""
    if player_name.strip():
        players_dict = dm.data.get("players", {})
        if player_name not in players_dict:
            # プレイヤーデータの作成
            player_data = {
                "name": player_name.strip(),
                "notes": player_notes.strip() if player_notes.strip() else "",
                "created_at": datetime.now().isoformat()
            }
            
            # playersが存在しない場合は初期化
            if "players" not in dm.data or dm.data["players"] is None:
                dm.data["players"] = {}
            
            # プレイヤーを追加
            dm.data["players"][player_name.strip()] = player_data
            dm.save_data("players")  # プレイヤーデータのみ保存
            
            st.success(lang.get_text("player_management.added_success", name=player_name))
            st.rerun()
        else:
            st.error(lang.get_text("player_management.already_exists", name=player_name))
    else:
        st.error(lang.get_text("player_management.name_required"))

def _render_registered_players_tab(lang, dm):
    """登録済みプレイヤータブの表示"""
    st.markdown(f"### {lang.get_text('player_management.registered_players')}")
    
    if dm.data.get("players"):
        # プレイヤーリストの表示
        for player_name, player_data in dm.data["players"].items():
            with st.expander(f"👤 {player_name}"):
                _render_player_details(lang, dm, player_name, player_data)
    else:
        st.info(lang.get_text("player_management.no_players"))

def _render_player_details(lang, dm, player_name, player_data):
    """プレイヤー詳細情報の表示"""
    # プレイヤーの統計情報
    player_stats = get_player_statistics(dm, player_name)
    
    # 基本情報を1列で表示
    st.write(f"**{lang.get_text('player_management.name_label')}**: {player_data.get('name', player_name)}")
    
    # 統計情報を横並びで表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(lang.get_text('player_management.play_count_label'), f"{player_stats['total_plays']}")
    with col2:
        st.metric(lang.get_text('player_management.win_count'), f"{player_stats['wins']}")
    with col3:
        if player_stats['total_plays'] > 0:
            win_rate = (player_stats['wins'] / player_stats['total_plays']) * 100
            st.metric(lang.get_text('player_management.win_rate'), f"{win_rate:.1f}%")
        else:
            st.metric(lang.get_text('player_management.win_rate'), "0.0%")
    
    # メモがある場合のみ表示
    if player_data.get('notes'):
        st.write(f"**{lang.get_text('player_management.memo_label')}**: {player_data['notes']}")
    
    # 登録日
    registration_date = player_data.get('created_at', lang.get_text('play_recording.unknown'))
    if registration_date != lang.get_text('play_recording.unknown'):
        registration_date = registration_date[:10]
    st.write(f"**{lang.get_text('player_management.registration_date')}**: {registration_date}")
    
    # プレイヤー削除ボタン
    _render_player_delete_buttons(lang, dm, player_name)

def _render_player_delete_buttons(lang, dm, player_name):
    """プレイヤー削除ボタンの表示"""
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        if st.button(lang.get_text("player_management.delete_player", name=player_name), key=f"delete_btn_{player_name}"):
            st.session_state[f"confirm_state_{player_name}"] = True
    
    with col_del2:
        if st.session_state.get(f"confirm_state_{player_name}", False):
            if st.button(lang.get_text("player_management.delete_player_confirm"), key=f"confirm_btn_{player_name}"):
                del dm.data["players"][player_name]
                dm.save_data("players")  # プレイヤーデータのみ保存
                st.success(lang.get_text("player_management.deleted_success", name=player_name))
                # 確認状態をリセット
                if f"confirm_state_{player_name}" in st.session_state:
                    del st.session_state[f"confirm_state_{player_name}"]
                st.rerun()