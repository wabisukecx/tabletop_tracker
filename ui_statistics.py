import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def render_statistics_page():
    """統計ページ表示"""
    lang = st.session_state.lang_manager
    st.title(lang.get_text("statistics.title"))
    
    dm = st.session_state.data_manager
    
    plays = dm.data.get("plays", [])
    if not plays:
        st.info(lang.get_text("statistics.need_plays"))
        return
    
    tab1, tab2, tab3 = st.tabs([
        lang.get_text("statistics.overall_tab"), 
        lang.get_text("statistics.by_game_tab"), 
        lang.get_text("statistics.by_player_tab")
    ])
    
    with tab1:
        _render_overall_statistics(lang, dm, plays)
    
    with tab2:
        _render_game_statistics(lang, dm, plays)
    
    with tab3:
        _render_player_statistics(lang, dm, plays)

def _render_overall_statistics(lang, dm, plays):
    """全体統計の表示"""
    st.markdown(f"### {lang.get_text('statistics.overall_stats')}")
    
    # 基本統計メトリクス
    _render_overall_metrics(lang, plays)
    
    # 月別プレイ回数グラフ
    _render_monthly_plays_chart(lang, plays)

def _render_overall_metrics(lang, plays):
    """全体統計メトリクスの表示"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(lang.get_text("statistics.total_plays"), len(plays))
    
    with col2:
        total_time = sum(play.get("duration", 0) for play in plays)
        st.metric(lang.get_text("statistics.total_time"), f"{total_time}{lang.get_text('game_management.minutes')}")
    
    with col3:
        avg_time = total_time / len(plays) if plays else 0
        st.metric(lang.get_text("statistics.avg_time"), f"{avg_time:.1f}{lang.get_text('game_management.minutes')}")
    
    with col4:
        unique_games = len(set(play.get("game_id") for play in plays))
        st.metric(lang.get_text("statistics.unique_games"), unique_games)

def _render_monthly_plays_chart(lang, plays):
    """月別プレイ回数グラフの表示"""
    st.markdown(f"### {lang.get_text('statistics.monthly_plays')}")
    
    # 日付データの処理
    play_dates = []
    for play in plays:
        try:
            play_date = datetime.fromisoformat(play.get("date", "2024-01-01"))
            play_dates.append(play_date)
        except ValueError:
            # 無効な日付の場合はデフォルト値を使用
            play_dates.append(datetime(2024, 1, 1))
    
    df_plays = pd.DataFrame({"date": play_dates})
    df_plays["month"] = df_plays["date"].dt.to_period("M")
    monthly_counts = df_plays.groupby("month").size()
    
    fig = px.bar(
        x=monthly_counts.index.astype(str), 
        y=monthly_counts.values,
        labels={"x": lang.get_text("statistics.month_label"), "y": lang.get_text("statistics.play_count_label")}
    )
    st.plotly_chart(fig, use_container_width=True)

def _render_game_statistics(lang, dm, plays):
    """ゲーム別統計の表示"""
    st.markdown(f"### {lang.get_text('statistics.game_stats')}")
    
    # ゲーム別プレイ回数の集計
    game_counts = _calculate_game_counts(lang, dm, plays)
    
    if game_counts:
        # 円グラフの表示
        _render_game_play_ratio_chart(lang, game_counts)
        
        # 詳細テーブルの表示
        _render_game_details_table(lang, dm)
    else:
        st.info(lang.get_text("play_recording.no_plays"))

def _calculate_game_counts(lang, dm, plays):
    """ゲーム別プレイ回数の計算"""
    game_counts = {}
    for play in plays:
        game_id = play.get("game_id")
        game_name = dm.get_localized_game_name(game_id)
        game_counts[game_name] = game_counts.get(game_name, 0) + 1
    return game_counts

def _render_game_play_ratio_chart(lang, game_counts):
    """ゲーム別プレイ割合の円グラフ表示"""
    fig = px.pie(
        values=list(game_counts.values()), 
        names=list(game_counts.keys()),
        title=lang.get_text("statistics.play_ratio")
    )
    st.plotly_chart(fig, use_container_width=True)

def _render_game_details_table(lang, dm):
    """ゲーム詳細テーブルの表示"""
    st.markdown(f"#### {lang.get_text('statistics.game_details')}")
    
    game_stats = []
    for game_id, game in dm.data.get("games", {}).items():
        stats = dm.get_game_stats(game_id)
        localized_name = dm.get_localized_game_name(game_id)
        
        # ランキング情報も含める
        ranking = game.get('ranking', {}).get('overall')
        ranking_text = f"#{ranking:,}" if ranking else lang.get_text("game_management.unranked")
        
        game_stats.append({
            lang.get_text("game_management.game_name"): localized_name,
            "BGG Ranking": ranking_text,
            lang.get_text("statistics.play_count_label"): stats.get("total_plays", 0),
            lang.get_text("statistics.avg_time_label"): f"{stats.get('avg_duration', 0):.1f}{lang.get_text('game_management.minutes')}"
        })
    
    df_game_stats = pd.DataFrame(game_stats)
    
    # ソート選択
    sort_options = [
        lang.get_text("game_management.sort_short_plays"), 
        lang.get_text("game_management.sort_short_ranking"), 
        lang.get_text("game_management.sort_short_name")
    ]
    sort_option = st.selectbox(
        "Sort:",
        sort_options,
        index=0,  # デフォルトはプレイ回数順
        label_visibility="visible"
    )
    
    if sort_option == lang.get_text("game_management.sort_short_plays"):
        df_game_stats = df_game_stats.sort_values(lang.get_text("statistics.play_count_label"), ascending=False)
    elif sort_option == lang.get_text("game_management.sort_short_ranking"):
        # ランキングでソート（数字が小さい方が上位）
        unranked_text = lang.get_text("game_management.unranked")
        df_game_stats['ranking_sort'] = df_game_stats["BGG Ranking"].apply(
            lambda x: int(x.replace('#', '').replace(',', '')) if x != unranked_text else 999999
        )
        df_game_stats = df_game_stats.sort_values('ranking_sort').drop('ranking_sort', axis=1)
    else:
        df_game_stats = df_game_stats.sort_values(lang.get_text("game_management.game_name"))
    
    st.dataframe(df_game_stats, use_container_width=True)

def _render_player_statistics(lang, dm, plays):
    """プレイヤー別統計の表示"""
    st.markdown(f"### {lang.get_text('statistics.player_stats')}")
    
    # プレイヤー別勝利数の計算
    player_stats_data = _calculate_player_stats(plays)
    
    if player_stats_data["player_wins"]:
        # 統計テーブルの表示
        _render_player_stats_table(lang, player_stats_data)
    else:
        st.info(lang.get_text("play_recording.no_plays"))

def _calculate_player_stats(plays):
    """プレイヤー統計の計算（協力ゲーム対応版）"""
    player_wins = {}
    player_games = {}
    
    for play in plays:
        scores = play.get("scores", {})
        if scores:
            # 協力ゲームかどうかをチェック
            game_type = play.get("game_type", "")
            is_cooperative = (game_type == "協力ゲーム" or game_type == "Cooperative Game")
            
            # 各プレイヤーの参加ゲーム数をカウント
            for player in scores.keys():
                player_games[player] = player_games.get(player, 0) + 1
            
            if is_cooperative:
                # 協力ゲームの場合は全体結果で勝敗判定
                detailed_scores = play.get("detailed_scores", {})
                global_data = detailed_scores.get("global", {}) if detailed_scores else {}
                
                # ゲーム結果をチェック
                game_result = ""
                for key, value in global_data.items():
                    if "結果" in key or "Result" in key or key == "ゲーム結果":
                        game_result = str(value)
                        break
                
                # 勝利判定 - 協力ゲームでは全員が同じ結果
                if "勝利" in game_result or "Victory" in game_result or "Win" in game_result:
                    # 全員に勝利を加算
                    for player in scores.keys():
                        player_wins[player] = player_wins.get(player, 0) + 1
                # 敗北の場合は誰にも勝利を加算しない
                
            else:
                # 対戦ゲームの場合は最高スコアで勝敗判定（従来通り）
                winner = max(scores.items(), key=lambda x: x[1])[0]
                player_wins[winner] = player_wins.get(winner, 0) + 1
    
    return {
        "player_wins": player_wins,
        "player_games": player_games
    }

def _render_player_stats_table(lang, player_stats_data):
    """プレイヤー統計テーブルの表示"""
    player_wins = player_stats_data["player_wins"]
    player_games = player_stats_data["player_games"]
    
    # 統計データの構築
    player_stats = []
    for player in player_games.keys():
        wins = player_wins.get(player, 0)
        total = player_games[player]
        win_rate = (wins / total * 100) if total > 0 else 0
        player_stats.append({
            lang.get_text("player_management.name_label"): player,
            lang.get_text("statistics.win_count_label"): wins,
            lang.get_text("statistics.play_count_label"): total,
            lang.get_text("statistics.win_rate_label"): f"{win_rate:.1f}%"
        })
    
    # テーブルの表示
    df_player_stats = pd.DataFrame(player_stats)
    df_player_stats = df_player_stats.sort_values(lang.get_text("statistics.win_count_label"), ascending=False)
    st.dataframe(df_player_stats, use_container_width=True)