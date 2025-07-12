import streamlit as st
import os
import shutil
from datetime import datetime

def render_settings_page():
    """設定ページ表示"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("settings.title"))
    
    dm = st.session_state.data_manager
    
    tab1, tab2 = st.tabs([lang.get_text("settings.file_info_tab"), lang.get_text("settings.data_management_tab")])
    
    with tab1:
        _render_file_info_tab(lang, dm)
    
    with tab2:
        _render_data_management_tab(lang, dm)

def _render_file_info_tab(lang, dm):
    """ファイル情報タブの表示"""
    st.markdown(f"### {lang.get_text('settings.file_info_title')}")
    st.info(lang.get_text("settings.file_info_desc"))
    
    data_info = dm.get_data_info()
    
    # データタイプ名のマッピング
    type_names = {
        "games": lang.get_text("settings.games_label"),
        "players": lang.get_text("settings.players_label"), 
        "plays": lang.get_text("settings.plays_label"),
        "score_sheets": lang.get_text("settings.scoresheets_label")
    }
    
    for data_type, info in data_info.items():
        _render_data_type_info(lang, data_type, info, type_names)

def _render_data_type_info(lang, data_type, info, type_names):
    """データタイプ情報の表示"""
    type_display_name = type_names.get(data_type, data_type)
    record_count_text = lang.get_text('settings.records_count', count=info['record_count'])
    
    with st.expander(f"{type_display_name} ({record_count_text})", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{lang.get_text('settings.file_path')}**: `{info['file_path']}`")
            st.write(f"**{lang.get_text('settings.file_size')}**: {info['file_size']}")
        
        with col2:
            st.write(f"**{lang.get_text('settings.last_modified')}**: {info['modified_time']}")
            records_suffix = lang.get_text('settings.records_count', count='').strip()
            st.write(f"**{lang.get_text('settings.record_count')}**: {info['record_count']:,}{records_suffix}")

def _render_data_management_tab(lang, dm):
    """データ管理タブの表示"""
    st.markdown(f"### {lang.get_text('settings.data_management_title')}")
    
    # バックアップセクション
    _render_backup_section(lang, dm)
    
    # データ統計セクション
    _render_data_stats_section(lang, dm)
    
    # データディレクトリ情報セクション
    _render_data_directory_section(lang, dm)

def _render_backup_section(lang, dm):
    """バックアップセクションの表示"""
    st.markdown(f"#### {lang.get_text('settings.backup_create')}")
    
    if st.button(lang.get_text("settings.backup_all")):
        _create_backup(lang, dm)

def _create_backup(lang, dm):
    """バックアップの作成"""
    try:
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # 各データファイルをバックアップ
        backup_count = 0
        for data_type, file_path in dm.files.items():
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, f"{data_type}.yaml")
                shutil.copy2(file_path, backup_path)
                backup_count += 1
        
        if backup_count > 0:
            st.success(lang.get_text("settings.backup_created", dir=backup_dir))
        else:
            st.warning("No files were found to backup.")
            
    except Exception as e:
        st.error(f"Backup failed: {str(e)}")

def _render_data_stats_section(lang, dm):
    """データ統計セクションの表示"""
    st.markdown(f"#### {lang.get_text('settings.data_stats')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        games_label = lang.get_text("settings.games_label").replace("🎲 ", "")
        st.metric(games_label, len(dm.data.get("games", {})))
    
    with col2:
        players_label = lang.get_text("settings.players_label").replace("👥 ", "")
        st.metric(players_label, len(dm.data.get("players", {})))
    
    with col3:
        plays_label = lang.get_text("settings.plays_label").replace("🎮 ", "")
        st.metric(plays_label, len(dm.data.get("plays", [])))
    
    with col4:
        scoresheets_label = lang.get_text("settings.scoresheets_label").replace("📊 ", "")
        st.metric(scoresheets_label, len(dm.data.get("score_sheets", {})))

def _render_data_directory_section(lang, dm):
    """データディレクトリセクションの表示"""
    st.markdown(f"#### {lang.get_text('settings.data_directory')}")
    st.write(f"**{lang.get_text('settings.data_location')}**: `{dm.data_dir}/`")
    st.write(lang.get_text("settings.independent_files"))
    
    # データディレクトリの詳細情報
    _render_directory_details(dm)

def _render_directory_details(dm):
    """データディレクトリの詳細情報表示"""
    if os.path.exists(dm.data_dir):
        st.write("**Directory Contents:**")
        try:
            files = os.listdir(dm.data_dir)
            for file in files:
                file_path = os.path.join(dm.data_dir, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    st.write(f"- `{file}` ({file_size:,} bytes, modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')})")
        except Exception as e:
            st.write(f"Could not read directory contents: {str(e)}")
    else:
        st.write("Data directory does not exist yet.")