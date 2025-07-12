import streamlit as st
import pandas as pd
from datetime import date

def render_play_recording_page():
    """プレイ記録ページ表示"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("play_recording.title"))
    
    dm = st.session_state.data_manager
    
    tab1, tab2 = st.tabs([lang.get_text("play_recording.new_record_tab"), lang.get_text("play_recording.history_tab")])
    
    with tab1:
        _render_new_play_tab(lang, dm)
    
    with tab2:
        _render_play_history_tab(lang, dm)

def _render_new_play_tab(lang, dm):
    """新規プレイ記録タブの表示"""
    st.markdown(f"### {lang.get_text('play_recording.new_play_title')}")
    
    if not dm.data.get("games"):
        st.warning(lang.get_text("play_recording.need_games"))
        return
    
    # 登録済みプレイヤーをチェック
    existing_players = list(dm.data.get("players", {}).keys())
    if not existing_players:
        st.warning(lang.get_text("play_recording.need_players"))
        st.info(lang.get_text("play_recording.need_players_info"))
        st.stop()
    
    # プレイヤー数選択
    max_players = min(len(existing_players), 8)
    num_players = st.number_input(lang.get_text("play_recording.player_count"), min_value=1, max_value=max_players, value=min(2, max_players))
    
    # ゲーム選択
    game_options = {game["name"]: game_id for game_id, game in dm.data.get("games", {}).items()}
    selected_game_name = st.selectbox(lang.get_text("play_recording.game_selection"), options=list(game_options.keys()))
    selected_game_id = game_options[selected_game_name]
    
    # 基本情報入力
    basic_info = _render_basic_info_form(lang)
    
    # スコア入力
    score_data = _render_score_input_section(lang, dm, selected_game_id, existing_players, num_players)
    
    # 保存ボタン
    _render_save_button(lang, dm, selected_game_id, basic_info, score_data)

def _render_basic_info_form(lang):
    """基本情報フォームの表示"""
    st.markdown(f"#### {lang.get_text('play_recording.players_and_scores')}")
    
    col1, col2 = st.columns(2)
    with col1:
        play_date = st.date_input(lang.get_text("play_recording.play_date"), value=date.today())
        duration = st.number_input(lang.get_text("play_recording.play_time_minutes"), min_value=1, value=60)
    with col2:
        location = st.text_input(lang.get_text("play_recording.location"), placeholder=lang.get_text("play_recording.location_placeholder"))
        notes = st.text_area(lang.get_text("play_recording.memo"), placeholder=lang.get_text("play_recording.memo_placeholder"))
    
    return {
        "date": play_date,
        "duration": duration,
        "location": location,
        "notes": notes
    }

def _render_score_input_section(lang, dm, selected_game_id, existing_players, num_players):
    """スコア入力セクションの表示"""
    # 選択されたゲームのスコアシートをチェック
    score_sheet = dm.data.get("score_sheets", {}).get(selected_game_id, None)
    
    if score_sheet:
        return _render_scoresheet_input(lang, score_sheet, existing_players, num_players)
    else:
        return _render_simple_score_input(lang, existing_players, num_players)

def _render_scoresheet_input(lang, score_sheet, existing_players, num_players):
    """スコアシート使用時の入力"""
    game_type = score_sheet.get("game_type", lang.get_text("game_types.competitive"))
    st.info(lang.get_text("play_recording.scoresheet_using", name=score_sheet['name'], type=game_type))
    
    if game_type == lang.get_text("game_types.cooperative"):
        return _render_cooperative_game_input(lang, score_sheet, existing_players, num_players)
    else:
        return _render_competitive_game_input(lang, score_sheet, existing_players, num_players)

def _render_cooperative_game_input(lang, score_sheet, existing_players, num_players):
    """協力ゲーム用の入力"""
    st.markdown(f"##### {lang.get_text('play_recording.overall_result')}")
    
    # 全体共通項目の入力
    global_data = {}
    for field in score_sheet["fields"]:
        if field.get("global", False):
            if field["type"] == "choice":
                global_data[field["name"]] = st.selectbox(
                    field["name"], 
                    options=field.get("options", [lang.get_text("common.select")]),
                    key=f"global_{field['name']}"
                )
            elif field["type"] == "number":
                global_data[field["name"]] = st.number_input(
                    field["name"], 
                    value=field.get("default", 0),
                    key=f"global_{field['name']}"
                )
            elif field["type"] == "checkbox":
                global_data[field["name"]] = st.checkbox(
                    field["name"], 
                    value=field.get("default", False),
                    key=f"global_{field['name']}"
                )
    
    st.markdown(f"##### {lang.get_text('play_recording.player_individual_info')}")
    
    # プレイヤー個別項目の入力
    players_detailed_scores = {}
    for i in range(num_players):
        st.markdown(f"**{lang.get_text('play_recording.player_label', num=i+1)}**")
        
        # プレイヤー選択
        selected_player = st.selectbox(lang.get_text("play_recording.player_selection"), options=existing_players, key=f"coop_player_select_{i}")
        
        # 個別項目入力
        player_scores = {}
        for field in score_sheet["fields"]:
            if not field.get("global", False):
                if field["type"] == "choice":
                    player_scores[field["name"]] = st.selectbox(
                        field["name"], 
                        options=field.get("options", [lang.get_text("common.select")]),
                        key=f"player_{i}_{field['name']}"
                    )
                elif field["type"] == "number":
                    player_scores[field["name"]] = st.number_input(
                        field["name"], 
                        value=field.get("default", 0),
                        key=f"player_{i}_{field['name']}"
                    )
                elif field["type"] == "checkbox":
                    player_scores[field["name"]] = st.checkbox(
                        field["name"], 
                        value=field.get("default", False),
                        key=f"player_{i}_{field['name']}"
                    )
        
        if selected_player:
            players_detailed_scores[selected_player] = player_scores
    
    # 協力ゲームでは全員同じ結果（勝利/敗北）
    game_result = global_data.get(lang.get_text("play_recording.game_result"), "勝利")
    if game_result == "勝利":
        players_scores = {player: 1 for player in players_detailed_scores.keys()}
    else:
        players_scores = {player: 0 for player in players_detailed_scores.keys()}
    
    return {
        "players_scores": players_scores,
        "detailed_scores": {
            "global": global_data,
            "players": players_detailed_scores
        },
        "score_sheet": score_sheet
    }

def _render_competitive_game_input(lang, score_sheet, existing_players, num_players):
    """対戦ゲーム用の入力"""
    players_detailed_scores = {}
    players_total_scores = {}
    
    for i in range(num_players):
        st.markdown(f"##### {lang.get_text('play_recording.player_label', num=i+1)}")
        
        # プレイヤー選択
        selected_player = st.selectbox(lang.get_text("play_recording.player_selection"), options=existing_players, key=f"sheet_player_select_{i}")
        
        # スコア項目入力
        player_scores = {}
        total_score = 0
        
        # 各スコア項目を表示
        score_cols = st.columns(len(score_sheet["fields"]))
        for field_idx, field in enumerate(score_sheet["fields"]):
            with score_cols[field_idx]:
                if field["type"] == "number":
                    score_value = st.number_input(
                        field["name"], 
                        value=field.get("default", 0), 
                        key=f"sheet_score_{i}_{field_idx}_{field['name']}"
                    )
                    player_scores[field["name"]] = score_value
                    total_score += score_value
                elif field["type"] == "checkbox":
                    checkbox_value = st.checkbox(
                        field["name"], 
                        value=field.get("default", False),
                        key=f"sheet_score_{i}_{field_idx}_{field['name']}"
                    )
                    player_scores[field["name"]] = checkbox_value
                    # チェックされた場合は設定された点数を加算
                    if checkbox_value:
                        points = field.get("points", 0)
                        total_score += points
                        st.caption(f"+ {points}{lang.get_text('play_recording.points')}")
        
        # 合計スコア表示
        st.write(f"**{score_sheet.get('total_field', lang.get_text('play_recording.total_label'))}**: {total_score}")
        
        if selected_player:
            players_detailed_scores[selected_player] = player_scores
            players_total_scores[selected_player] = total_score
    
    return {
        "players_scores": players_total_scores,
        "detailed_scores": players_detailed_scores,
        "score_sheet": score_sheet
    }

def _render_simple_score_input(lang, existing_players, num_players):
    """従来の単純スコア入力"""
    st.info(lang.get_text("play_recording.no_scoresheet"))
    st.markdown(f"*{lang.get_text('play_recording.scoresheet_info')}*")
    
    players_scores = {}
    for i in range(num_players):
        col1, col2 = st.columns(2)
        with col1:
            # 既存プレイヤーから選択
            selected_player = st.selectbox(lang.get_text("play_recording.player_label", num=i+1), options=existing_players, key=f"simple_player_select_{i}")
            
        with col2:
            score = st.number_input(lang.get_text("play_recording.score_label"), value=0, key=f"simple_score_{i}")
        
        if selected_player:
            players_scores[selected_player] = score
    
    return {
        "players_scores": players_scores,
        "detailed_scores": None,
        "score_sheet": None
    }

def _render_save_button(lang, dm, selected_game_id, basic_info, score_data):
    """保存ボタンの表示と処理"""
    st.markdown("---")
    if st.button(lang.get_text("play_recording.save_play"), type="primary", use_container_width=True):
        if score_data["players_scores"]:
            # 同じプレイヤーが重複選択されていないかチェック
            if len(score_data["players_scores"]) != len(set(score_data["players_scores"].keys())):
                st.error(lang.get_text("play_recording.duplicate_players"))
            else:
                # プレイ記録を保存
                play_data = {
                    "game_id": selected_game_id,
                    "date": basic_info["date"].isoformat(),
                    "duration": basic_info["duration"],
                    "location": basic_info["location"],
                    "notes": basic_info["notes"],
                    "scores": score_data["players_scores"],
                    "detailed_scores": score_data["detailed_scores"],
                    "score_sheet_used": score_data["score_sheet"]["name"] if score_data["score_sheet"] else None,
                    "game_type": score_data["score_sheet"].get("game_type", lang.get_text("game_types.competitive")) if score_data["score_sheet"] else lang.get_text("game_types.competitive")
                }
                dm.add_play(play_data)
                st.success(lang.get_text("play_recording.saved_success"))
                st.rerun()
        else:
            st.error(lang.get_text("play_recording.select_players"))

def _render_play_history_tab(lang, dm):
    """プレイ履歴タブの表示"""
    st.markdown(f"### {lang.get_text('play_recording.history_title')}")
    plays = dm.data.get("plays", [])
    if plays:
        for idx, play in enumerate(reversed(plays)):  # 新しい順
            _render_play_history_item(lang, dm, play)
    else:
        st.info(lang.get_text("play_recording.no_plays"))

def _render_play_history_item(lang, dm, play):
    """プレイ履歴アイテムの表示"""
    game_name = dm.get_localized_game_name(play.get("game_id", ""))
    
    # 協力ゲームかどうかをチェック
    game_id = play.get("game_id", "")
    score_sheet = dm.data.get("score_sheets", {}).get(game_id, {})
    is_coop_game = score_sheet.get("game_type") == lang.get_text("game_types.cooperative")
    
    if is_coop_game and play.get("detailed_scores", {}).get("global"):
        _render_cooperative_play_history(lang, play, game_name)
    else:
        _render_competitive_play_history(lang, play, game_name)

def _render_cooperative_play_history(lang, play, game_name):
    """協力ゲームプレイ履歴の表示"""
    global_data = play["detailed_scores"]["global"]
    game_result = global_data.get(lang.get_text("play_recording.game_result"), lang.get_text("play_recording.unknown"))
    result_icon = "🏆" if "勝利" in game_result or "Victory" in game_result else "💔" if "敗北" in game_result or "Defeat" in game_result else "🤝"
    
    with st.expander(f"{result_icon} {game_name} ({play.get('date', '')}) - {game_result}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{lang.get_text('play_recording.game_label')}**: {game_name}")
            st.write(f"**{lang.get_text('play_recording.date_label')}**: {play.get('date', '')}")
            st.write(f"**{lang.get_text('play_recording.duration_label')}**: {play.get('duration', 0)}{lang.get_text('game_management.minutes')}")
            st.write(f"**{lang.get_text('play_recording.location_label')}**: {play.get('location', '')}")
            if play.get('notes'):
                st.write(f"**{lang.get_text('play_recording.memo_label')}**: {play['notes']}")
        
        with col2:
            st.write(f"**{lang.get_text('play_recording.game_result')}**:")
            for key, value in global_data.items():
                st.write(f"**{key}**: {value}")
        
        # プレイヤー情報表示
        if play.get("detailed_scores", {}).get("players"):
            st.markdown("---")
            st.markdown(f"**{lang.get_text('play_recording.participants')}**")
            
            players_data = play["detailed_scores"]["players"]
            if players_data:
                player_info = []
                for player, data in players_data.items():
                    row = {lang.get_text("play_recording.player_selection"): player}
                    for key, value in data.items():
                        row[key] = value
                    player_info.append(row)
                
                df_players = pd.DataFrame(player_info)
                st.dataframe(df_players, use_container_width=True)

def _render_competitive_play_history(lang, play, game_name):
    """対戦ゲームプレイ履歴の表示"""
    winner = max(play.get("scores", {}).items(), key=lambda x: x[1])[0] if play.get("scores") else lang.get_text("play_recording.unknown")
    
    with st.expander(f"🎲 {game_name} ({play.get('date', '')}) - {lang.get_text('play_recording.winner')}: {winner}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{lang.get_text('play_recording.game_label')}**: {game_name}")
            st.write(f"**{lang.get_text('play_recording.date_label')}**: {play.get('date', '')}")
            st.write(f"**{lang.get_text('play_recording.duration_label')}**: {play.get('duration', 0)}{lang.get_text('game_management.minutes')}")
            st.write(f"**{lang.get_text('play_recording.location_label')}**: {play.get('location', '')}")
            if play.get('notes'):
                st.write(f"**{lang.get_text('play_recording.memo_label')}**: {play['notes']}")
        
        with col2:
            st.write(f"**{lang.get_text('play_recording.score_results')}**:")
            scores = play.get("scores", {})
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # 正しい順位計算（同点の場合は同順位）
            current_rank = 1
            prev_score = None
            
            for i, (player, score) in enumerate(sorted_scores):
                # 前のスコアと違う場合は順位を更新
                if prev_score is not None and score != prev_score:
                    current_rank = i + 1
                
                # 順位に応じたアイコン表示（同順位は全員同じメダル）
                if current_rank == 1:
                    st.write(f"🥇 {lang.get_text('play_recording.position_1st')} {player}: {score}{lang.get_text('play_recording.points')}")
                elif current_rank == 2:
                    st.write(f"🥈 {lang.get_text('play_recording.position_2nd')} {player}: {score}{lang.get_text('play_recording.points')}")
                elif current_rank == 3:
                    st.write(f"🥉 {lang.get_text('play_recording.position_3rd')} {player}: {score}{lang.get_text('play_recording.points')}")
                else:
                    st.write(f"{lang.get_text('play_recording.position_nth', n=current_rank)} {player}: {score}{lang.get_text('play_recording.points')}")
                
                prev_score = score
        
        # 詳細スコアがある場合は表示（対戦ゲーム）
        if play.get("detailed_scores") and isinstance(play["detailed_scores"], dict):
            st.markdown("---")
            st.markdown(f"**{lang.get_text('play_recording.detailed_scores')}**")
            if play.get("score_sheet_used"):
                st.markdown(f"*{lang.get_text('play_recording.used_scoresheet')}: {play['score_sheet_used']}*")
            
            detailed_scores = play["detailed_scores"]
            if detailed_scores:
                # 詳細スコアをテーブル形式で表示
                detail_data = []
                players = list(detailed_scores.keys())
                
                if players:
                    # スコア項目の取得
                    score_fields = list(detailed_scores[players[0]].keys())
                    
                    for player in players:
                        row = {lang.get_text("play_recording.player_selection"): player}
                        for field in score_fields:
                            value = detailed_scores[player].get(field, 0)
                            if isinstance(value, bool):
                                row[field] = "✓" if value else "-"
                            else:
                                row[field] = value
                        row[lang.get_text("play_recording.total_label")] = scores.get(player, 0)
                        detail_data.append(row)
                    
                    df_details = pd.DataFrame(detail_data)
                    st.dataframe(df_details, use_container_width=True)