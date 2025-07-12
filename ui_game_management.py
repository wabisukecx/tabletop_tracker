import streamlit as st
import time
from bgg_api import BGGApi

def render_game_management_page():
    """ゲーム管理ページ"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("game_management.title"))
    dm = st.session_state.data_manager

    tab1, tab2 = st.tabs([lang.get_text("game_management.search_tab"), lang.get_text("game_management.registered_tab")])

    with tab1:
        _render_game_search_tab(lang, dm)

    with tab2:
        _render_registered_games_tab(lang, dm)

def _render_game_search_tab(lang, dm):
    """ゲーム検索タブの表示"""
    st.markdown(f"### {lang.get_text('game_management.search_title')}")
    search_query = st.text_input(lang.get_text("game_management.game_name"), placeholder=lang.get_text("game_management.search_placeholder"))

    if st.button(lang.get_text("game_management.search_button")) and search_query:
        with st.spinner(lang.get_text("common.searching")):
            games = BGGApi.search_games(search_query)
        
        # セッション状態にゲームリストを保存
        st.session_state.search_results = games
    
    # 検索結果の表示（セッション状態から）
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        _render_search_results(lang, dm, st.session_state.search_results)
    
    elif hasattr(st.session_state, 'search_results') and not st.session_state.search_results:
        st.warning(lang.get_text("game_management.no_results"))

def _render_search_results(lang, dm, games):
    """検索結果の表示"""
    st.markdown(f"### {lang.get_text('game_management.search_results')} ({len(games)}{lang.get_text('game_management.search_results_count')})")
    
    # 検索結果が多い場合は警告表示
    if len(games) > 50:
        st.warning(lang.get_text("game_management.search_warning", count=len(games)))
    
    # ページネーション設定
    items_per_page = st.selectbox(lang.get_text("game_management.items_per_page"), [10, 25, 50, 100, lang.get_text("game_management.all_items")], index=0)
    
    if items_per_page == lang.get_text("game_management.all_items"):
        display_games = games
        start_idx = 0
        end_idx = len(games)
    else:
        items_per_page = int(items_per_page)
        
        # ページ番号の計算
        total_pages = (len(games) + items_per_page - 1) // items_per_page
        
        if total_pages > 1:
            page_num = st.selectbox("Page Selection", range(1, total_pages + 1), index=0, label_visibility="hidden")
            start_idx = (page_num - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(games))
            display_games = games[start_idx:end_idx]
            
            st.info(lang.get_text("game_management.page_info", 
                                 current=page_num, total=total_pages, 
                                 total_items=len(games), start=start_idx + 1, end=end_idx))
        else:
            display_games = games
            start_idx = 0
            end_idx = len(games)
    
    # ゲーム一覧の表示
    for i, game in enumerate(display_games):
        actual_index = start_idx + i  # 実際のインデックス
        
        # 各ゲームを横並びで表示
        col1, col2 = st.columns([4, 1])
        
        with col1:
            game_info = f"**{game['name']}**"
            if game['year']:
                game_info += f" ({game['year']})"
            st.write(game_info)
            st.write(f"{lang.get_text('game_management.bgg_id')}: {game['id']}")
        
        with col2:
            # 既に登録済みかチェック
            if game['id'] in dm.data["games"]:
                st.button(lang.get_text("game_management.added_button"), key=f"added_{game['id']}_{actual_index}", disabled=True)
            else:
                if st.button(lang.get_text("game_management.add_button"), key=f"add_{game['id']}_{actual_index}"):
                    with st.spinner(lang.get_text("game_management.adding_details", name=game['name'])):
                        details = BGGApi.get_game_details(game['id'])

                    if details and details.get("name"):
                        success = dm.add_game(details)
                        if success:
                            time.sleep(0.5)  # 短い待機時間でrerun
                            st.rerun()
                        else:
                            st.error(lang.get_text("game_management.add_failed"))
                    else:
                        st.error(lang.get_text("game_management.details_failed"))
        
        # 区切り線（最後の要素以外）
        if i < len(display_games) - 1:
            st.divider()
    
    # フッター情報
    if items_per_page != lang.get_text("game_management.all_items") and total_pages > 1:
        st.markdown(f"**{lang.get_text('game_management.displaying')}**: {start_idx + 1}-{end_idx} / **{lang.get_text('game_management.total_items')}**: {len(games)}")

def _render_registered_games_tab(lang, dm):
    """登録済みゲームタブの表示"""
    st.markdown(f"### {lang.get_text('game_management.registered_games_title')}")
    
    # 既存ゲームの多言語対応チェック
    if dm.update_game_multilingual_support():
        st.success("Games updated to support multiple languages!")
        st.rerun()
    
    games = dm.data.get("games", {})
    if games:
        # ソート選択
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{len(games)}** games registered")
        with col2:
            sort_options = [
                lang.get_text("game_management.sort_short_ranking"), 
                lang.get_text("game_management.sort_short_name"), 
                lang.get_text("game_management.sort_short_plays")
            ]
            sort_option = st.selectbox(
                "Sort:",
                sort_options,
                index=0,  # デフォルトはランキング順
                label_visibility="visible"
            )
        
        # ゲームリストをソート
        sorted_games = _sort_games_list(games, sort_option, dm)
        
        for game_id, game in sorted_games:
            # 現在の言語に応じたゲーム名を取得
            localized_name = dm.get_localized_game_name(game_id)
            
            # ランキング情報を表示用に追加
            ranking_info = ""
            if game.get('ranking', {}).get('overall'):
                ranking_info = f" (#{game['ranking']['overall']:,})"
            
            with st.expander(f"🎲 {localized_name}{ranking_info}"):
                _render_game_details(lang, dm, game_id, game)
    else:
        st.info(lang.get_text("game_management.no_games"))

def _sort_games_list(games, sort_option, dm):
    """ゲームリストをソート"""
    games_list = list(games.items())
    lang = st.session_state.lang_manager
    
    if sort_option == lang.get_text("game_management.sort_short_ranking"):
        # ランキング順（数字が小さい方が上位）
        def sort_key(item):
            game_id, game = item
            ranking = game.get('ranking', {}).get('overall')
            # ランキングがない場合は最下位に配置
            return ranking if ranking is not None else 999999
        
        games_list.sort(key=sort_key)
        
    elif sort_option == lang.get_text("game_management.sort_short_name"):
        # 名前順（現在の言語）
        def sort_key(item):
            game_id, game = item
            return dm.get_localized_game_name(game_id).lower()
        
        games_list.sort(key=sort_key)
        
    elif sort_option == lang.get_text("game_management.sort_short_plays"):
        # プレイ回数順
        def sort_key(item):
            game_id, game = item
            stats = dm.get_game_stats(game_id)
            return -stats.get('total_plays', 0)  # 降順
        
        games_list.sort(key=sort_key)
    
    return games_list

def _render_game_details(lang, dm, game_id, game):
    """ゲーム詳細情報の表示"""
    # レイアウト：画像と情報を横並び
    col_img, col_info, col_stats = st.columns([1, 2, 1])
    
    with col_img:
        # 箱絵表示
        if game.get('image_url'):
            try:
                st.image(game['image_url'], width=150, caption=lang.get_text("game_management.box_art"))
            except:
                st.write(lang.get_text("game_management.image_error"))
        else:
            st.write(lang.get_text("game_management.no_image"))
    
    with col_info:
        # 現在の言語に応じたゲーム名を表示
        localized_name = dm.get_localized_game_name(game_id)
        st.write(f"**{lang.get_text('game_management.game_name')}**: {localized_name}")
        
        # 多言語名の表示
        _render_multilingual_names(lang, game)
        
        st.write(f"**{lang.get_text('game_management.players_range')}**: {game.get('min_players', '?')}-{game.get('max_players', '?')}{lang.get_text('home.players_suffix')}")
        
        # 最適人数表示
        best_count = game.get('best_player_count', '')
        if best_count:
            st.write(f"**{lang.get_text('game_management.optimal_players')}**: {best_count}")
        
        st.write(f"**{lang.get_text('game_management.play_time')}**: {game.get('playing_time', '?')}{lang.get_text('game_management.minutes')}")
        
        rating = game.get('rating', 0)
        if rating > 0:
            st.write(f"**{lang.get_text('game_management.bgg_rating')}**: {rating:.1f}")
        else:
            st.write(f"**{lang.get_text('game_management.bgg_rating')}**: {lang.get_text('game_management.no_rating')}")
        
        # ランキング情報の表示
        _render_ranking_info(lang, game)
        
        st.write(f"**{lang.get_text('game_management.bgg_id')}**: {game_id}")
    
    with col_stats:
        stats = dm.get_game_stats(game_id)
        st.metric(lang.get_text("game_management.play_count"), f"{stats.get('total_plays', 0)}{lang.get_text('game_management.times')}")
        if stats.get('avg_duration', 0) > 0:
            st.metric(lang.get_text("game_management.avg_time"), f"{stats.get('avg_duration', 0):.0f}{lang.get_text('game_management.minutes')}")
    
    # 操作ボタン
    st.markdown("---")
    _render_game_action_buttons(lang, dm, game_id, game)

def _render_multilingual_names(lang, game):
    """多言語名の表示"""
    if "names" in game:
        names = game["names"]
        current_lang = st.session_state.lang_manager.get_current_language()
        
        if current_lang == "ja":
            # 日本語表示時
            if names.get("english") and names.get("english") != names.get("japanese"):
                st.write(f"**English**: {names['english']}")
            if names.get("alternates"):
                alt_names = [name for name in names["alternates"] if name not in [names.get("japanese"), names.get("english")]]
                if alt_names:
                    st.write(f"**Other names**: {', '.join(alt_names[:3])}")
        else:
            # 英語表示時
            if names.get("japanese") and names.get("japanese") != names.get("english"):
                st.write(f"**日本語**: {names['japanese']}")
            if names.get("alternates"):
                alt_names = [name for name in names["alternates"] if name not in [names.get("japanese"), names.get("english")]]
                if alt_names:
                    st.write(f"**Other names**: {', '.join(alt_names[:3])}")

def _render_ranking_info(lang, game):
    """ランキング情報の表示"""
    ranking = game.get('ranking', {})
    if ranking and any(ranking.values()):
        st.write(f"**BGG Rankings**:")
        
        # Overall ranking
        if ranking.get('overall'):
            st.write(f"  📊 Overall: #{ranking['overall']:,}")
        
        # Category rankings
        category_rankings = []
        if ranking.get('strategy'):
            category_rankings.append(f"Strategy: #{ranking['strategy']:,}")
        if ranking.get('family'):
            category_rankings.append(f"Family: #{ranking['family']:,}")
        if ranking.get('party'):
            category_rankings.append(f"Party: #{ranking['party']:,}")
        if ranking.get('thematic'):
            category_rankings.append(f"Thematic: #{ranking['thematic']:,}")
        if ranking.get('war'):
            category_rankings.append(f"War: #{ranking['war']:,}")
        if ranking.get('abstract'):
            category_rankings.append(f"Abstract: #{ranking['abstract']:,}")
        if ranking.get('customizable'):
            category_rankings.append(f"Customizable: #{ranking['customizable']:,}")
        
        if category_rankings:
            st.write(f"  🏆 Categories: {', '.join(category_rankings[:2])}")
            if len(category_rankings) > 2:
                with st.expander("Show more categories"):
                    for cat in category_rankings[2:]:
                        st.write(f"  • {cat}")

def _render_game_action_buttons(lang, dm, game_id, game):
    """ゲーム操作ボタンの表示"""
    col_refresh, col_del1, col_del2, col_del3 = st.columns([1, 1, 1, 1])
    
    # 情報再取得ボタン
    with col_refresh:
        if st.button(lang.get_text("game_management.refresh_info"), key=f"refresh_game_{game_id}"):
            with st.spinner(lang.get_text("game_management.updating_info", name=game['name'])):
                updated_data = BGGApi.get_game_details(game_id)
            
            if updated_data and updated_data.get("name"):
                # 既存データを更新（IDは保持）
                dm.data["games"][game_id].update(updated_data)
                dm.save_data("games")
                st.success(lang.get_text("game_management.info_updated", name=updated_data['name']))
                st.rerun()
            else:
                st.error(lang.get_text("game_management.update_failed"))
    
    # 削除ボタン
    with col_del1:
        if st.button(lang.get_text("game_management.delete_button"), key=f"delete_game_btn_{game_id}"):
            st.session_state[f"confirm_game_delete_{game_id}"] = True
    
    with col_del2:
        if st.session_state.get(f"confirm_game_delete_{game_id}", False):
            if st.button(lang.get_text("game_management.delete_confirm"), key=f"confirm_game_btn_{game_id}"):
                # プレイ記録をチェック
                plays = dm.data.get("plays", [])
                related_plays = [p for p in plays if p.get("game_id") == game_id]
                if related_plays:
                    st.error(lang.get_text("game_management.has_play_records", count=len(related_plays)))
                else:
                    success = dm.delete_game(game_id)
                    if success:
                        # 確認状態をリセット
                        if f"confirm_game_delete_{game_id}" in st.session_state:
                            del st.session_state[f"confirm_game_delete_{game_id}"]
                        st.rerun()
    
    with col_del3:
        if st.session_state.get(f"confirm_game_delete_{game_id}", False):
            if st.button(lang.get_text("game_management.cancel_button"), key=f"cancel_game_btn_{game_id}"):
                if f"confirm_game_delete_{game_id}" in st.session_state:
                    del st.session_state[f"confirm_game_delete_{game_id}"]
                st.rerun()