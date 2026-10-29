import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="野球オーダー作成", layout="wide")

# ---------------------------------------------------------
# モバイル（iPhone 16e向け）カスタムCSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .sticky-header {
        position: -webkit-sticky;
        position: sticky;
        top: 2.5rem;
        z-index: 999;
        background-color: #ffffff;
        border: 2px solid #ff4b4b;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    /* スマホ専用：オーダー行を絶対に崩さないためのテーブルスタイル */
    .order-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 8px;
    }
    .order-table td {
        padding: 6px 4px;
        vertical-align: middle;
        border-bottom: 1px solid #eee;
    }
    .col-num {
        width: 8%;
        text-align: center;
        font-weight: bold;
        font-size: 1rem;
    }
    .col-pos {
        width: 38%;
        white-space: nowrap;
    }
    .col-player {
        width: 54%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CSVファイル管理
# ---------------------------------------------------------
ROSTER_FILE = "roster.csv"
LAST_GAME_FILE = "last_game.csv"

def load_roster():
    if os.path.exists(ROSTER_FILE):
        try:
            df = pd.read_csv(ROSTER_FILE, dtype=str)
            return df.to_dict(orient="records")
        except Exception:
            pass
    return [
        {"背番号": "1", "名前": "山田太郎", "投打": "右投右打", "メイン守備": "投手"},
        {"背番号": "2", "名前": "佐藤次郎", "投打": "右投右打", "メイン守備": "捕手"},
        {"背番号": "3", "名前": "鈴木三郎", "投打": "右投左打", "メイン守備": "一塁手"},
        {"背番号": "4", "名前": "高橋四郎", "投打": "右投右打", "メイン守備": "二塁手"},
        {"背番号": "5", "名前": "田中五郎", "投打": "右投右打", "メイン守備": "三塁手"},
        {"背番号": "6", "名前": "伊藤六郎", "投打": "右投左打", "メイン守備": "遊撃手"},
        {"背番号": "7", "名前": "渡辺七郎", "投打": "左投左打", "メイン守備": "左翼手"},
        {"背番号": "8", "名前": "山本八郎", "投打": "右投両打", "メイン守備": "中堅手"},
        {"背番号": "9", "名前": "中村九郎", "投打": "右投右打", "メイン守備": "右翼手"},
        {"背番号": "10", "名前": "小林十郎", "投打": "右投右打", "メイン守備": "控"},
        {"背番号": "11", "名前": "加藤一郎", "投打": "左投左打", "メイン守備": "控"},
        {"背番号": "12", "名前": "吉田二郎", "投打": "右投右打", "メイン守備": "控"},
    ]

def save_roster(roster_data):
    df = pd.DataFrame(roster_data)
    df.to_csv(ROSTER_FILE, index=False, encoding="utf-8-sig")

def load_game_data(filename):
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename, dtype=str)
            if "game_players" in df.columns and "lineup_positions" in df.columns:
                players = df["game_players"].dropna().tolist()
                positions = df["lineup_positions"].dropna().tolist()
                defense_type = df["defense_type"].iloc[0] if "defense_type" in df.columns and not pd.isna(df["defense_type"].iloc[0]) else None
                batting_count = int(df["batting_count"].iloc[0]) if "batting_count" in df.columns and not pd.isna(df["batting_count"].iloc[0]) else None
                return players, positions, defense_type, batting_count
        except Exception:
            pass
    return None, None, None, None

def save_game_data(filename, players, positions, defense_type, batting_count):
    max_len = max(len(players), len(positions), 1)
    df_dict = {
        "game_players": players + [None] * (max_len - len(players)),
        "lineup_positions": positions + [None] * (max_len - len(positions)),
        "defense_type": [defense_type] + [None] * (max_len - 1),
        "batting_count": [str(batting_count)] + [None] * (max_len - 1)
    }
    df = pd.DataFrame(df_dict)
    df.to_csv(filename, index=False, encoding="utf-8-sig")

if "roster" not in st.session_state:
    st.session_state.roster = load_roster()

if "swap_index" not in st.session_state:
    st.session_state.swap_index = None
if "swap_pos_index" not in st.session_state:
    st.session_state.swap_pos_index = None

st.title("⚾ オーダー管理")

# ---------------------------------------------------------
# 【サイドバー】選手名簿の管理 ＆ プラン管理
# ---------------------------------------------------------
with st.sidebar:
    st.header("📋 チーム名簿管理")
    
    with st.expander("＋ 新規選手登録", expanded=False):
        new_num = st.text_input("背番号", key="new_num")
        new_name = st.text_input("名前", key="new_name")
        new_bats = st.selectbox("投打", ["右投右打", "右投左打", "左投左打", "左投右打", "右投両打"], key="new_bats")
        new_pos = st.selectbox("メイン守備", ["投手", "捕手", "内野手", "外野手", "DH", "控"], key="new_pos")
        if st.button("追加する"):
            if new_num and new_name:
                if any(p["背番号"] == new_num for p in st.session_state.roster):
                    st.error(f"背番号 {new_num} は登録済みです")
                else:
                    st.session_state.roster.append({
                        "背番号": new_num, "名前": new_name, "投打": new_bats, "メイン守備": new_pos
                    })
                    save_roster(st.session_state.roster)
                    st.success(f"{new_name} 選手を追加しました")
                    st.rerun()
            else:
                st.error("背番号と名前を入力してください")

    with st.expander("✏️ 選手情報を編集", expanded=False):
        edit_target = st.selectbox("編集する選手", ["選択なし"] + [f"#{p['背番号']} {p['名前']}" for p in st.session_state.roster], key="edit_sel")
        if edit_target != "選択なし":
            target_num = edit_target.split()[0].replace("#", "")
            target_player = next((p for p in st.session_state.roster if p["背番号"] == target_num), None)
            
            if target_player:
                edit_num = st.text_input("背番号", value=target_player["背番号"], key="edit_num")
                edit_name = st.text_input("名前", value=target_player["名前"], key="edit_name")
                bats_list = ["右投右打", "右投左打", "左投左打", "左投右打", "右投両打"]
                edit_bats = st.selectbox("投打", bats_list, index=bats_list.index(target_player["投打"]) if target_player["投打"] in bats_list else 0, key="edit_bats")
                pos_list = ["投手", "捕手", "内野手", "外野手", "DH", "控"]
                edit_pos = st.selectbox("メイン守備", pos_list, index=pos_list.index(target_player["メイン守備"]) if target_player["メイン守備"] in pos_list else 0, key="edit_pos")
                
                if st.button("変更を保存"):
                    target_player["背番号"] = edit_num
                    target_player["名前"] = edit_name
                    target_player["投打"] = edit_bats
                    target_player["メイン守備"] = edit_pos
                    save_roster(st.session_state.roster)
                    st.success("更新しました")
                    st.rerun()

    with st.expander("🗑️ 選手を削除", expanded=False):
        delete_target = st.selectbox("削除する選手", ["選択なし"] + [f"#{p['背番号']} {p['名前']}" for p in st.session_state.roster], key="del_sel")
        if st.button("削除実行"):
            if delete_target != "選択なし":
                target_num = delete_target.split()[0].replace("#", "")
                st.session_state.roster = [p for p in st.session_state.roster if p["背番号"] != target_num]
                save_roster(st.session_state.roster)
                st.warning("削除しました")
                st.rerun()

    st.markdown("---")
    df_roster = pd.DataFrame(st.session_state.roster)
    st.dataframe(df_roster, use_container_width=True)

    st.markdown("---")
    csv_data = df_roster.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(label="CSVダウンロード", data=csv_data, file_name="roster.csv", mime="text/csv")
    uploaded_file = st.file_uploader("CSVアップロード", type=["csv"])
    if uploaded_file is not None:
        try:
            up_df = pd.read_csv(uploaded_file, dtype=str)
            st.session_state.roster = up_df.to_dict(orient="records")
            save_roster(st.session_state.roster)
            st.success("CSVから読み込みました")
            st.rerun()
        except Exception as e:
            st.error(f"失敗: {e}")

# ---------------------------------------------------------
# メイン画面（プラン管理 ＆ オーダー作成）
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📱 オーダー作成", "📲 LINE送信"])

with tab1:
    saved_players, saved_positions, saved_def_type, saved_bat_count = load_game_data(LAST_GAME_FILE)

    with st.expander("📂 作戦プラン管理（プランA〜C）", expanded=False):
        st.write("現在のオーダー状態をプランとして保存したり、保存したプランを呼び出せます。")
        plan_choice = st.selectbox("対象プラン", ["プランA", "プランB", "プランC"])
        plan_filename = f"game_plan_{plan_choice[-1]}.csv"

        col_pl1, col_pl2 = st.columns(2)
        with col_pl1:
            if st.button(f"📥 {plan_choice}を読み込む"):
                p_p, p_pos, p_def, p_bat = load_game_data(plan_filename)
                if p_p:
                    st.session_state.game_players = p_p
                    st.session_state.lineup_positions = p_pos
                    st.session_state.swap_index = None
                    st.session_state.swap_pos_index = None
                    save_game_data(LAST_GAME_FILE, p_p, p_pos, p_def or "9人制（投手・捕手・内野4・外野3）", p_bat or 9)
                    st.success(f"{plan_choice} を読み込みました！")
                    st.rerun()
                else:
                    st.warning(f"{plan_choice} の保存データがまだありません。")
        with col_pl2:
            if st.button(f"💾 現在の状態を{plan_choice}に保存"):
                if "game_players" in st.session_state and "lineup_positions" in st.session_state:
                    save_game_data(plan_filename, st.session_state.game_players, st.session_state.lineup_positions, locals().get('defense_type', '9人制（投手・捕手・内野4・外野3）'), locals().get('batting_count', 9))
                    st.success(f"現在のオーダーを {plan_choice} に保存しました！")
                else:
                    st.warning("保存するオーダーデータがありません。")

    with st.expander("⚙️ 試合ルール設定", expanded=False):
        def_options = [
            "9人制（投手・捕手・内野4・外野3）",
            "10人制（投手あり・外野4）",
            "10人制（投手なし・外野5）",
            "カスタム守備"
        ]
        default_def_idx = def_options.index(saved_def_type) if saved_def_type in def_options else 0
        defense_type = st.selectbox("守備スタイル", def_options, index=default_def_idx)
        
        default_bat_val = saved_bat_count if saved_bat_count is not None else 9
        batting_count = st.number_input("打撃人数", min_value=9, max_value=15, value=default_bat_val, step=1)

    if "9人制" in defense_type:
        positions = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手", "DH"]
    elif "外野4" in defense_type:
        positions = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手(左)", "中堅手(右)", "右翼手", "DH"]
    elif "投手なし" in defense_type:
        positions = ["捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "左中間", "中堅", "右中間", "右翼手", "DH"]
    else:
        positions = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "外野1", "外野2", "外野3", "外野4", "外野5", "DH"]

    all_players = [f"#{p['背番号']} {p['名前']}" for p in st.session_state.roster]
    min_required = batting_count

    if saved_players and all(p in all_players for p in saved_players):
        default_attended = saved_players
    else:
        default_attended = all_players[:min(len(all_players), max(10, batting_count))]
    
    attended_players = st.multiselect(
        f"参加メンバー（最低{min_required}人）", 
        all_players, 
        default=default_attended
    )

    if len(attended_players) < min_required:
        st.warning(f"⚠️ 参加メンバーが不足しています（{len(attended_players)}/{batting_count}人）")
    else:
        if "game_players" not in st.session_state:
            if saved_players and set(saved_players) == set(attended_players):
                st.session_state.game_players = list(saved_players)
            else:
                st.session_state.game_players = list(attended_players)
            st.session_state.swap_index = None
            st.session_state.swap_pos_index = None
        elif set(st.session_state.game_players) != set(attended_players):
            current_gp = [p for p in st.session_state.game_players if p in attended_players]
            added_p = [p for p in attended_players if p not in current_gp]
            st.session_state.game_players = current_gp + added_p

        if "last_defense_type" not in st.session_state:
            st.session_state.last_defense_type = defense_type

        if "lineup_positions" not in st.session_state or st.session_state.last_defense_type != defense_type or len(st.session_state.lineup_positions) != batting_count:
            if not ("lineup_positions" in st.session_state and saved_positions and len(saved_positions) == batting_count and st.session_state.last_defense_type == defense_type):
                st.session_state.lineup_positions = [positions[i % len(positions)] if i < len(positions) else "DH" for i in range(batting_count)]
            st.session_state.last_defense_type = defense_type

        save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, defense_type, batting_count)

        if st.session_state.swap_index is not None or st.session_state.swap_pos_index is not None:
            st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                if st.session_state.swap_index is not None:
                    sel_name = st.session_state.game_players[st.session_state.swap_index]
                    st.markdown(f"🔴 <b style='color:red;'>【選手】{sel_name}</b> 選択中", unsafe_allow_html=True)
                if st.session_state.swap_pos_index is not None:
                    sel_pos_name = st.session_state.lineup_positions[st.session_state.swap_pos_index]
                    st.markdown(f"🔵 <b style='color:blue;'>【守備】{sel_pos_name}</b> 選択中", unsafe_allow_html=True)
            with head_col2:
                if st.button("解除", key="clear_all"):
                    st.session_state.swap_index = None
                    st.session_state.swap_pos_index = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("📝 スタメン（ワンタップ交代）")

        # スマホでも絶対に崩れないHTMLテーブル構造で描画
        for i in range(batting_count):
            curr_pos = st.session_state.lineup_positions[i]
            p_name = st.session_state.game_players[i]
            
            is_p_sel = (st.session_state.swap_index == i)
            is_pos_sel = (st.session_state.swap_pos_index == i)

            pos_style = "color:blue; font-weight:bold;" if is_pos_sel else "color:#333;"
            p_style = "color:red; font-weight:bold;" if is_p_sel else "color:#111;"
            
            btn_pos_lbl = "📍" if is_pos_sel else "🔄"
            btn_pos_type = "primary" if is_pos_sel else "secondary"

            btn_p_lbl = "📍" if is_p_sel else "🔄"
            btn_p_type = "primary" if is_p_sel else "secondary"

            # 1行をテーブルとしてHTMLで構築し、内部のボタンだけStreamlitの仕組みを割り当てる
            st.markdown(f"""
            <table class="order-table">
                <tr>
                    <td class="col-num">{i+1}</td>
                    <td class="col-pos"><span style="{pos_style}">{curr_pos}</span></td>
                    <td class="col-player"><span style="{p_style}">{p_name}</span></td>
                </tr>
            </table>
            """, unsafe_allow_html=True)

            # ボタン操作用の行をその直下にコンパクトに配置
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button(f"{btn_pos_lbl} 守備変更 ({i+1})", key=f"btn_pos_{i}", type=btn_pos_type):
                    if st.session_state.swap_pos_index is None:
                        st.session_state.swap_pos_index = i
                        st.rerun()
                    elif st.session_state.swap_pos_index == i:
                        st.session_state.swap_pos_index = None
                        st.rerun()
                    else:
                        target_p_idx = st.session_state.swap_pos_index
                        st.session_state.lineup_positions[i], st.session_state.lineup_positions[target_p_idx] = \
                            st.session_state.lineup_positions[target_p_idx], st.session_state.lineup_positions[i]
                        st.session_state.swap_pos_index = None
                        save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, defense_type, batting_count)
                        st.rerun()
            with bc2:
                if st.button(f"{btn_p_lbl} 選手交代 ({i+1})", key=f"btn_p_{i}", type=btn_p_type):
                    if st.session_state.swap_index is None:
                        st.session_state.swap_index = i
                        st.rerun()
                    elif st.session_state.swap_index == i:
                        st.session_state.swap_index = None
                        st.rerun()
                    else:
                        target_idx = st.session_state.swap_index
                        st.session_state.game_players[i], st.session_state.game_players[target_idx] = \
                            st.session_state.game_players[target_idx], st.session_state.game_players[i]
                        st.session_state.swap_index = None
                        save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, defense_type, batting_count)
                        st.rerun()
            st.markdown("<hr style='margin: 2px 0 8px 0; border: none; border-top: 1px dashed #ddd;'>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("▼ 控え（ベンチ）")
        
        total_players = len(st.session_state.game_players)
        bench_count = total_players - batting_count
        
        if bench_count > 0:
            for b_idx in range(bench_count):
                real_idx = batting_count + b_idx
                p_name = st.session_state.game_players[real_idx]
                is_p_sel = (st.session_state.swap_index == real_idx)
                p_style = "color:red; font-weight:bold;" if is_p_sel else "color:#111;"
                btn_lbl = "📍" if is_p_sel else "🔄"
                btn_type = "primary" if is_p_sel else "secondary"
                
                bc1, bc2 = st.columns([3, 1])
                with bc1:
                    st.markdown(f"<div style='{p_style} padding-top:6px; white-space:nowrap;'>・{p_name}</div>", unsafe_allow_html=True)
                with bc2:
                    if st.button(btn_lbl, key=f"btn_p_{real_idx}", type=btn_type):
                        if st.session_state.swap_index is None:
                            st.session_state.swap_index = real_idx
                            st.rerun()
                        elif st.session_state.swap_index == real_idx:
                            st.session_state.swap_index = None
                            st.rerun()
                        else:
                            target_idx = st.session_state.swap_index
                            st.session_state.game_players[real_idx], st.session_state.game_players[target_idx] = \
                                st.session_state.game_players[target_idx], st.session_state.game_players[real_idx]
                            st.session_state.swap_index = None
                            save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, defense_type, batting_count)
                            st.rerun()
        else:
            st.info("控え選手なし")

        final_lineup = []
        for i in range(batting_count):
            final_lineup.append({
                "打順": i + 1,
                "選手情報": st.session_state.game_players[i],
                "守備位置": st.session_state.lineup_positions[i]
            })
        st.session_state.current_lineup = final_lineup
        st.session_state.bench_players = st.session_state.game_players[batting_count:]
        st.session_state.batting_count = batting_count

with tab2:
    st.subheader("📲 LINE送信用 メンバー表")
    if "current_lineup" in st.session_state:
        line_text = "【本日のスターティングメンバー】\n"
        line_text += f"(打撃: {st.session_state.get('batting_count', 9)}人打ち)\n\n"
        
        for item in st.session_state.current_lineup:
            line_text += f"{item['打順']}番 [{item['守備位置']}] {item['選手情報']}\n"
        
        line_text += "\n【控え選手（ベンチ）】\n"
        if "bench_players" in st.session_state and st.session_state.bench_players:
            for b in st.session_state.bench_players:
                line_text += f"・{b}\n"
        else:
            line_text += "なし\n"
        
        line_text += "\n本日も応援よろしくお願いします！⚾"

        st.code(line_text, language="text")
        st.caption("※右上のボタンでそのままLINEに貼り付けられます。")
