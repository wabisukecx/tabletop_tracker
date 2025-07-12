import streamlit as st

def render_sidebar():
    """サイドバー表示"""
    lang = st.session_state.lang_manager
    st.sidebar.title(lang.get_text("sidebar.title"))
    
    # 言語選択
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {lang.get_text('sidebar.language')}")
    
    available_languages = lang.get_available_languages()
    current_lang = lang.get_current_language()
    
    # 言語選択ボックス
    selected_lang = st.sidebar.selectbox(
        "Language Selection",
        options=list(available_languages.keys()),
        format_func=lambda x: available_languages[x],
        index=list(available_languages.keys()).index(current_lang),
        label_visibility="hidden"
    )
    
    # 言語が変更された場合
    if selected_lang != current_lang:
        lang.set_language(selected_lang)
        st.rerun()
    
    st.sidebar.markdown("---")
    
    pages = [
        lang.get_text("pages.home"),
        lang.get_text("pages.game_management"),
        lang.get_text("pages.player_management"),
        lang.get_text("pages.score_sheet_management"),
        lang.get_text("pages.play_recording"),
        lang.get_text("pages.statistics"),
        lang.get_text("pages.settings")
    ]
    st.session_state.current_page = st.sidebar.selectbox("Page Navigation", pages, label_visibility="hidden")
    
    st.sidebar.markdown("---")
    
    # 簡易統計表示
    dm = st.session_state.data_manager
    st.sidebar.markdown(f"### {lang.get_text('sidebar.simple_stats')}")
    st.sidebar.metric(lang.get_text("sidebar.registered_games"), len(dm.data.get("games", {})))
    st.sidebar.metric(lang.get_text("sidebar.play_records"), len(dm.data.get("plays", [])))
    st.sidebar.metric(lang.get_text("sidebar.players"), len(dm.data.get("players", {})))

def render_home_page():
    """ホームページ表示"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("app.title"))
    st.markdown(lang.get_text("app.subtitle"))
    
    dm = st.session_state.data_manager
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"📚 {lang.get_text('sidebar.registered_games')}",
            value=len(dm.data.get("games", {})),
            delta=None
        )
    
    with col2:
        st.metric(
            label=f"🎮 {lang.get_text('sidebar.play_records')}",
            value=len(dm.data.get("plays", [])),
            delta=None
        )
    
    with col3:
        st.metric(
            label=f"👥 {lang.get_text('sidebar.players')}",
            value=len(dm.data.get("players", {})),
            delta=None
        )
    
    # 最近のプレイ記録
    st.markdown(f"### {lang.get_text('home.recent_plays')}")
    plays = dm.data.get("plays", [])
    if plays:
        recent_plays = sorted(plays, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        for play in recent_plays:
            game_name = dm.get_localized_game_name(play.get("game_id", ""))
            play_date = play.get("date", "")
            player_count = len(play.get("scores", {}))
            
            st.write(f"🎲 **{game_name}** ({play_date}) - {player_count}{lang.get_text('home.players_suffix')}")
    else:
        st.info(lang.get_text("home.no_plays"))