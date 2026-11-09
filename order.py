import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="野球オーダー作成", layout="wide")

# ---------------------------------------------------------
# CSVファイル管理関数
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

# ---------------------------------------------------------
# セッション状態の初期化
# ---------------------------------------------------------
if "roster" not in st.session_state:
    st.session_state.roster = load_roster()

if "swap_index" not in st.session_state:
    st.session_state.swap_index = None
if "swap_pos_index" not in st.session_state:
    st.session_state.swap_pos_index = None

saved_players, saved_positions, saved_def_type, saved_bat_count = load_game_data(LAST_GAME_FILE)
bat_count_init = saved_bat_count if saved_bat_count else 9

if "game_players" not in st.session_state:
    if saved_players:
        st.session_state.game_players = saved_players
    else:
        st.session_state.game_players = [f"#{p['背番号']} {p['名前']}" for p in st.session_state.roster]

if "lineup_positions" not in st.session_state:
    if saved_positions:
        st.session_state.lineup_positions = saved_positions
    else:
        default_pos = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手", "DH"]
        st.session_state.lineup_positions = [default_pos[i % len(default_pos)] for i in range(bat_count_init)]

# ---------------------------------------------------------
# 交代処理用コールバック関数
# ---------------------------------------------------------
def handle_pos_click(idx):
    current_sel = st.session_state.swap_pos_index
    if current_sel is None:
        st.session_state.swap_pos_index = idx
    elif current_sel == idx:
        st.session_state.swap_pos_index = None
    else:
        st.session_state.lineup_positions[current_sel], st.session_state.lineup_positions[idx] = \
            st.session_state.lineup_positions[idx], st.session_state.lineup_positions[current_sel]
        st.session_state.swap_pos_index = None
        def_t = saved_def_type or "9人制（投手・捕手・内野4・外野3）"
        save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, def_t, len(st.session_state.lineup_positions))

def handle_player_click(idx):
    current_sel = st.session_state.swap_index
    if current_sel is None:
        st.session_state.swap_index = idx
    elif current_sel == idx:
        st.session_state.swap_index = None
    else:
        st.session_state.game_players[current_sel], st.session_state.game_players[idx] = \
            st.session_state.game_players[idx], st.session_state.game_players[current_sel]
        st.session_state.swap_index = None
        def_t = saved_def_type or "9人制（投手・捕手・内野4・外野3）"
        save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, def_t, len(st.session_state.lineup_positions))

# ---------------------------------------------------------
# 【最終決定版CSS】完全左寄せ＆レイアウト安定化
# ---------------------------------------------------------
st.markdown("""
    <style>
    @media (max-width: 1200px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 3px !important;
            width: 100% !important;
            margin-left: 0 !important;
            margin-right: auto !important;
            padding: 1px 0 !important;
        }
        div[data-testid="column"] {
            flex: 0 0 auto !important;
            min-width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
            width: 25px !important;
            min-width: 25px !important;
            max-width: 25px !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
            width: 70px !important;
            min-width: 70px !important;
            max-width: 70px !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(3) {
            width: 150px !important;
            min-width: 150px !important;
            max-width: 150px !important;
        }
    }

    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        padding-left: 0.1rem !important;
        padding-right: 0.1rem !important;
        max-width: 100% !important;
    }
    .stButton {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    .stButton button {
        background-color: #f8f9fa !important;
        color: #31333f !important;
        border: 1px solid #d6d6d6 !important;
        border-radius: 4px !important;
        padding: 0.1rem 0.2rem !important;
        font-size: 0.72rem !important;
        min-height: 1.5rem !important;
        line-height: 1.1 !important;
        white-space: nowrap !important;
        width: 100% !important;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stButton button:hover {
        background-color: #e9ecef !important;
        border-color: #adb5bd !important;
    }
    /* 選択中の赤字スタイル */
    .stButton button[kind="primary"] {
        background-color: #fff0f0 !important;
        color: #ff4b4b !important;
        border-color: #ff4b4b !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

def format_position(pos):
    if not pos:
        return "  "
    if len(pos) == 2:
        return pos[0] + " " + pos[1]
    elif len(pos) == 1:
        return pos + "  "
    return pos[:3]

st.title("⚾ オーダー管理")

# ---------------------------------------------------------
# 【サイドバー】選手名簿の管理 ＆ 並び替え ＆ プラン管理
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

    # ---------------------------------------------------------
    # 【レイアウト改善】「▲」「▼」「選手名」の順に配置
    # ---------------------------------------------------------
    with st.expander("🔄 選手の並び替え", expanded=False):
        st.write("選手を上下に移動して並び順を変更できます。")
        for i, p in enumerate(st.session_state.roster):
            col_up, col_down, col_name = st.columns([0.8, 0.8, 2.4])
            with col_up:
                if i > 0:
                    if st.button("▲", key=f"roster_up_{i}"):
                        st.session_state.roster[i], st.session_state.roster[i-1] = st.session_state.roster[i-1], st.session_state.roster[i]
                        save_roster(st.session_state.roster)
                        st.rerun()
            with col_down:
                if i < len(st.session_state.roster) - 1:
                    if st.button("▼", key=f"roster_down_{i}"):
                        st.session_state.roster[i], st.session_state.roster[i+1] = st.session_state.roster[i+1], st.session_state.roster[i]
                        save_roster(st.session_state.roster)
                        st.rerun()
            with col_name:
                st.markdown(f"<div style='font-size:0.75rem; line-height:1.8rem; white-space:nowrap;'>#{p['背番号']} {p['名前']}</div>", unsafe_allow_html=True)

    with st.expander("✏️ 選手情報を編集", expanded=False):
        edit_target = st.selectbox("編集する選手", ["選択なし"] + [f"#{p['背番号']} {p['名前']}" for p in st.session_state.roster], key="edit_sel")
        if edit_target != "選択なし":
            target_num = edit_target.split()[0].replace("#", "")
            target_player = next((p for p in st.session_state.roster if p["背番号"] == target_num), None)
            
            if target_player:
                edit_num = st.text_input("背番号", value=target_player["背番号"], key="edit_num")
                edit_name = st.text_input("名前", value=target_player["名前"], key="edit_name")
                bats_list = ["右投右打", "右投左打", "左投左打", "右投右打", "右投両打"]
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
    st.dataframe(df_roster, width='stretch')

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
    with st.expander("📂 作戦プラン管理（プランA〜C）", expanded=False):
        st.write("現在のオーダー状態をプランとして保存したり、保存したプランを呼び出せます。")
        plan_choice = st.selectbox("対象プラン", ["プランA", "プランB", "プランC"])
        plan_filename = f"game_plan_{plan_choice[-1]}.csv"

        col_dummy, col_pl1, col_pl2 = st.columns([0.1, 0.9, 1.8])
        with col_pl1:
            if st.button(f"📥 呼出 ({plan_choice})"):
                p_p, p_pos, p_def, p_bat = load_game_data(plan_filename)
                if p_p:
                    st.session_state.game_players = p_p
                    st.session_state.lineup_positions = p_pos
                    st.session_state.swap_index = None
                    st.session_state.swap_pos_index = None
                    save_game_data(LAST_GAME_FILE, p_p, p_pos, p_def or "9人制（投手・捕手・内野4・外野3）", p_bat or 9)
                    st.success(f"{plan_choice} を呼び出しました！")
                    st.rerun()
                else:
                    st.warning(f"{plan_choice} の保存データなし")
        with col_pl2:
            if st.button(f"💾 保存 ({plan_choice})"):
                if "game_players" in st.session_state and "lineup_positions" in st.session_state:
                    save_game_data(plan_filename, st.session_state.game_players, st.session_state.lineup_positions, locals().get('defense_type', '9人制（投手・捕手・内野4・外野3）'), locals().get('batting_count', 9))
                    st.success(f"{plan_choice} に保存しました！")
                else:
                    st.warning("データなし")

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
        positions = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅左", "中堅右", "右翼手", "DH"]
    elif "投手なし" in defense_type:
        positions = ["捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "左中間", "中堅", "右中間", "右翼手", "DH"]
    else:
        positions = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "外野1", "外野2", "外野3", "外野4", "外野5", "DH"]

    # ---------------------------------------------------------
    # 参加メンバー選択（名簿順維持チェックボックス式）
    # ---------------------------------------------------------
    with st.expander("👥 本日の参加メンバー選択", expanded=True):
        st.write("登録名簿の順序通りにチェックが入ります。")
        all_players = [f"#{p['背番号']} {p['名前']}" for p in st.session_state.roster]
        
        if saved_players and all(p in all_players for p in saved_players):
            default_attended = saved_players
        else:
            default_attended = all_players[:min(len(all_players), max(10, batting_count))]

        attended_players = []
        for p_str in all_players:
            is_checked = st.checkbox(p_str, value=(p_str in default_attended), key=f"attend_check_{p_str}")
            if is_checked:
                attended_players.append(p_str)

    min_required = batting_count

    if len(attended_players) < min_required:
        st.warning(f"⚠️ 参加メンバーが不足しています（現在 {len(attended_players)}人 / 最低 {batting_count}人必要です）")
    else:
        if set(st.session_state.game_players) != set(attended_players):
            current_gp = [p for p in st.session_state.game_players if p in attended_players]
            added_p = [p for p in attended_players if p not in current_gp]
            st.session_state.game_players = current_gp + added_p

        st.session_state.last_defense_type = defense_type

        if len(st.session_state.lineup_positions) != batting_count:
            st.session_state.lineup_positions = [positions[i % len(positions)] if i < len(positions) else "DH" for i in range(batting_count)]

        save_game_data(LAST_GAME_FILE, st.session_state.game_players, st.session_state.lineup_positions, defense_type, batting_count)

        st.subheader("📝 スタメン（ワンタップ交代）")

        # ---------------------------------------------------------
        # スタメン一覧（比率: [0.1, 0.9, 1.8]）
        # ---------------------------------------------------------
        for i in range(batting_count):
            curr_pos = st.session_state.lineup_positions[i]
            p_name = st.session_state.game_players[i]
            
            is_p_sel = (st.session_state.swap_index == i)
            is_pos_sel = (st.session_state.swap_pos_index == i)
            
            formatted_pos = format_position(curr_pos)
            
            pos_btn_type = "primary" if is_pos_sel else "secondary"
            p_btn_type = "primary" if is_p_sel else "secondary"

            col_num, col_pos, col_player = st.columns([0.1, 0.9, 1.8])
            
            with col_num:
                st.markdown(f"<div style='text-align:right; font-weight:bold; font-size:0.75rem; line-height:1.8rem; padding-right:1px;'>{i+1}.</div>", unsafe_allow_html=True)
            with col_pos:
                st.button(formatted_pos, key=f"btn_pos_{i}", type=pos_btn_type, on_click=handle_pos_click, args=(i,))
            with col_player:
                st.button(p_name, key=f"btn_player_{i}", type=p_btn_type, on_click=handle_player_click, args=(i,))

        st.markdown("---")
        st.subheader("▼ 控え（ベンチ）")
        
        total_players = len(st.session_state.game_players)
        bench_count = total_players - batting_count
        
        if bench_count > 0:
            for b_idx in range(bench_count):
                real_idx = batting_count + b_idx
                p_name = st.session_state.game_players[real_idx]
                is_p_sel = (st.session_state.swap_index == real_idx)
                p_btn_type = "primary" if is_p_sel else "secondary"
                
                col_num, col_empty, col_player = st.columns([0.1, 0.9, 1.8])
                with col_num:
                    st.markdown(f"<div style='text-align:right; font-weight:bold; font-size:0.75rem; line-height:1.8rem; padding-right:1px;'>・</div>", unsafe_allow_html=True)
                with col_empty:
                    st.empty()
                with col_player:
                    st.button(p_name, key=f"btn_player_{real_idx}", type=p_btn_type, on_click=handle_player_click, args=(real_idx,))
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
