import streamlit as st
from score_sheet_manager import ScoreSheetManager

def render_score_sheet_page():
    """スコアシート管理ページ表示"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("scoresheet.title"))
    st.markdown(lang.get_text("scoresheet.subtitle"))
    
    dm = st.session_state.data_manager
    
    tab1, tab2 = st.tabs([lang.get_text("scoresheet.create_tab"), lang.get_text("scoresheet.manage_tab")])
    
    with tab1:
        _render_create_scoresheet_tab(lang, dm)
    
    with tab2:
        _render_manage_scoresheet_tab(lang, dm)

def _render_create_scoresheet_tab(lang, dm):
    """スコアシート作成タブの表示"""
    st.markdown(f"### {lang.get_text('scoresheet.create_custom')}")
    
    if not dm.data.get("games"):
        st.warning(lang.get_text("scoresheet.need_games"))
        return
    
    # ゲーム選択
    game_options = {}
    for game_id, game in dm.data.get("games", {}).items():
        localized_name = dm.get_localized_game_name(game_id)
        game_options[localized_name] = game_id
    
    selected_game_name = st.selectbox(lang.get_text("scoresheet.target_game"), options=list(game_options.keys()))
    selected_game_id = game_options[selected_game_name]
    
    # ゲームタイプ選択
    game_type = st.selectbox(lang.get_text("scoresheet.game_type"), [lang.get_text("scoresheet.competitive_game"), lang.get_text("scoresheet.cooperative_game")])
    
    st.markdown(f"#### {lang.get_text('scoresheet.score_items')}")
    
    # ゲームタイプに応じて初期フィールドを設定
    _initialize_score_fields(lang, game_type)
    
    # フィールド編集セクション
    _render_field_editor(lang, game_type)
    
    # フィールド追加ボタン
    _render_add_field_button(lang, game_type)
    
    # スコアシート保存
    _render_save_scoresheet_button(lang, dm, selected_game_id, selected_game_name, game_type)

def _initialize_score_fields(lang, game_type):
    """スコアフィールドの初期化"""
    if game_type == lang.get_text("scoresheet.cooperative_game"):
        st.info(lang.get_text("scoresheet.coop_info"))
        
        # 協力ゲーム用の基本項目を初期設定
        if "score_fields" not in st.session_state or st.session_state.get("last_game_type") != lang.get_text("scoresheet.cooperative_game"):
            st.session_state.score_fields = [
                {"name": lang.get_text("play_recording.game_result"), "type": "choice", "options": ["勝利", "敗北", "引き分け"], "global": True},
                {"name": "難易度", "type": "choice", "options": ["初級", "中級", "上級"], "global": True},
                {"name": "達成スコア", "type": "number", "default": 0, "global": True},
                {"name": "プレイヤー役割", "type": "choice", "options": ["役割1", "役割2", "役割3"], "global": False}
            ]
            st.session_state.last_game_type = lang.get_text("scoresheet.cooperative_game")
    else:
        # 対戦ゲーム用の基本項目
        if "score_fields" not in st.session_state or st.session_state.get("last_game_type") != lang.get_text("scoresheet.competitive_game"):
            st.session_state.score_fields = [{"name": "基本スコア", "type": "number", "default": 0}]
            st.session_state.last_game_type = lang.get_text("scoresheet.competitive_game")

def _render_field_editor(lang, game_type):
    """フィールドエディターの表示"""
    # 既存フィールド表示・編集
    for i, field in enumerate(st.session_state.score_fields):
        st.markdown(f"**{lang.get_text('scoresheet.item_label', num=i+1)}**")
        
        # フィールド基本情報
        _render_field_basic_info(lang, game_type, field, i)
        
        # フィールド設定値
        _render_field_settings(lang, game_type, field, i)
        
        st.divider()

def _render_field_basic_info(lang, game_type, field, i):
    """フィールド基本情報の表示"""
    # 項目名を全幅で配置
    field["name"] = st.text_input(lang.get_text("scoresheet.item_name"), value=field["name"], key=f"field_name_{i}")
    
    # 種類選択を全幅で配置
    if game_type == lang.get_text("scoresheet.cooperative_game"):
        field_types = ["choice", "number", "checkbox"]
        type_labels = [lang.get_text("scoresheet.choice_type"), lang.get_text("scoresheet.number_type"), lang.get_text("scoresheet.checkbox_type")]
    else:
        field_types = ["number", "checkbox"]
        type_labels = [lang.get_text("scoresheet.number_type"), lang.get_text("scoresheet.checkbox_type")]
    
    current_index = field_types.index(field["type"]) if field["type"] in field_types else 0
    selected_type = st.selectbox(lang.get_text("scoresheet.item_type"), type_labels, index=current_index, key=f"field_type_{i}")
    field["type"] = field_types[type_labels.index(selected_type)]

def _render_field_settings(lang, game_type, field, i):
    """フィールド設定値の表示"""
    if field["type"] == "number":
        field["default"] = st.number_input(lang.get_text("scoresheet.initial_value"), value=field.get("default", 0), key=f"field_default_{i}")
        if game_type == lang.get_text("scoresheet.cooperative_game"):
            field["global"] = st.checkbox(lang.get_text("scoresheet.global_item"), value=field.get("global", False), key=f"field_global_{i}")
    elif field["type"] == "checkbox":
        col_points, col_check = st.columns(2)
        with col_points:
            field["points"] = st.number_input(lang.get_text("scoresheet.checkbox_points"), value=field.get("points", 0), key=f"field_points_{i}")
        with col_check:
            field["default"] = st.checkbox(lang.get_text("scoresheet.initial_checked"), value=field.get("default", False), key=f"field_default_{i}")
    elif field["type"] == "choice":
        # 選択肢を設定
        options_text = st.text_input(
            lang.get_text("scoresheet.choice_options"), 
            value=",".join(field.get("options", [])), 
            key=f"field_options_{i}",
            placeholder=lang.get_text("scoresheet.choice_placeholder")
        )
        field["options"] = [opt.strip() for opt in options_text.split(",") if opt.strip()]
        
        if game_type == lang.get_text("scoresheet.cooperative_game"):
            field["global"] = st.checkbox(lang.get_text("scoresheet.global_item"), value=field.get("global", False), key=f"field_global_{i}")
            if field["global"]:
                st.caption(lang.get_text("scoresheet.global_common"))
            else:
                st.caption(lang.get_text("scoresheet.individual_item"))
    
    # 削除ボタンを設定値の最後に配置
    if st.button(lang.get_text("scoresheet.delete_field"), key=f"delete_field_{i}", use_container_width=True, type="secondary"):
        st.session_state.score_fields.pop(i)
        st.rerun()
def _render_add_field_button(lang, game_type):
    """フィールド追加ボタンの表示"""
    # ボタンを入力フィールドと同じ全幅で配置
    if st.button(lang.get_text("scoresheet.add_item"), use_container_width=True, type="secondary"):
        if game_type == lang.get_text("scoresheet.cooperative_game"):
            new_field = {
                "name": f"項目{len(st.session_state.score_fields)+1}", 
                "type": "choice", 
                "options": ["選択肢1", "選択肢2"],
                "global": False
            }
        else:
            new_field = {
                "name": f"項目{len(st.session_state.score_fields)+1}", 
                "type": "number", 
                "default": 0
            }
        st.session_state.score_fields.append(new_field)
        st.rerun()

def _render_save_scoresheet_button(lang, dm, selected_game_id, selected_game_name, game_type):
    """スコアシート保存ボタンの表示"""
    # ボタンを入力フィールドと同じ全幅で配置し、primary styleを適用
    if st.button(lang.get_text("scoresheet.save_scoresheet"), use_container_width=True, type="primary"):
        sheet_data = ScoreSheetManager.create_custom_sheet(selected_game_name, st.session_state.score_fields)
        sheet_data["game_type"] = game_type  # ゲームタイプを追加
        
        # score_sheetsが存在しない場合は初期化
        if "score_sheets" not in dm.data or dm.data["score_sheets"] is None:
            dm.data["score_sheets"] = {}
        
        dm.data["score_sheets"][selected_game_id] = sheet_data
        dm.save_data("score_sheets")  # スコアシートデータのみ保存
        st.success(lang.get_text("scoresheet.saved_success"))

def _render_manage_scoresheet_tab(lang, dm):
    """スコアシート管理タブの表示"""
    st.markdown(f"### {lang.get_text('scoresheet.existing_sheets')}")
    if dm.data.get("score_sheets"):
        for game_id, sheet in dm.data["score_sheets"].items():
            _render_scoresheet_item(lang, dm, game_id, sheet)
    else:
        st.info(lang.get_text("scoresheet.no_scoresheets"))

def _render_scoresheet_item(lang, dm, game_id, sheet):
    """個別スコアシートアイテムの表示"""
    game_name = dm.get_localized_game_name(game_id)
    game_type = sheet.get("game_type", lang.get_text("scoresheet.competitive_game"))
    type_icon = "🤝" if game_type == lang.get_text("scoresheet.cooperative_game") else "⚔️"
    
    with st.expander(f"📊 {game_name} のスコアシート ({type_icon} {game_type})"):
        st.write(f"**{lang.get_text('scoresheet.sheet_name')}**: {sheet['name']}")
        st.write(f"**{lang.get_text('scoresheet.game_type')}**: {game_type}")
        st.write(f"**{lang.get_text('scoresheet.score_items_label')}**:")
        
        for field in sheet["fields"]:
            field_info = _format_field_info(lang, field)
            st.write(field_info)

def _format_field_info(lang, field):
    """フィールド情報のフォーマット"""
    field_info = f"- **{field['name']}**"
    
    if field['type'] == 'number':
        field_info += f" ({lang.get_text('scoresheet.number_type')}) - {lang.get_text('scoresheet.initial_value_label')}: {field.get('default', 0)}"
        if field.get('global', False):
            field_info += f" {lang.get_text('scoresheet.global_common_label')}"
    elif field['type'] == 'checkbox':
        field_info += f" ({lang.get_text('scoresheet.checkbox_type')}) - {lang.get_text('scoresheet.points_label')}: {field.get('points', 0)}{lang.get_text('play_recording.points')}"
        if field.get('default', False):
            field_info += f" {lang.get_text('scoresheet.initial_check_label')}"
    elif field['type'] == 'choice':
        field_info += f" ({lang.get_text('scoresheet.choice_type')}) - {lang.get_text('scoresheet.options_label')}: {', '.join(field.get('options', []))}"
        if field.get('global', False):
            field_info += f" {lang.get_text('scoresheet.global_common_label')}"
        else:
            field_info += f" {lang.get_text('scoresheet.individual_label')}"
    
    return field_info