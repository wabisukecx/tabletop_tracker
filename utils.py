def get_player_statistics(dm, player_name):
    """プレイヤーの統計情報を取得"""
    total_plays = 0
    wins = 0
    
    plays = dm.data.get("plays", [])
    for play in plays:
        scores = play.get("scores", {})
        if player_name in scores:
            total_plays += 1
            
            # 協力ゲームかどうかをチェック
            game_type = play.get("game_type", "")
            is_cooperative = (game_type == "協力ゲーム" or game_type == "Cooperative Game")
            
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
                
                # 勝利判定
                if "勝利" in game_result or "Victory" in game_result or "Win" in game_result:
                    wins += 1
                # 敗北の場合は勝利数に加算しない
                
            else:
                # 対戦ゲームの場合は最高スコアで勝敗判定（従来通り）
                if scores:
                    winner = max(scores.items(), key=lambda x: x[1])[0]
                    if winner == player_name:
                        wins += 1
    
    return {
        "total_plays": total_plays,
        "wins": wins
    }