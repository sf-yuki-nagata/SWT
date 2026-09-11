import streamlit as st
import time
import pandas as pd
import base64
import os
import random

# --- カスタムデザインを適用するCSS ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* 全体のベースフォントを少し小さく見せるための調整 */
    .stApp {
        font-size: 14px !important;
    }
    
    /* 画面全体を上に引き上げる（メインコンテンツの上部余白を削る） */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 1. ラジオボタンをSnowflakeブルーの角丸ボタン化 */
    .stRadio [role="radiogroup"] {
        gap: 10px;
    }
    .stRadio [role="radiogroup"] label {
        background-color: #29b5e8 !important; 
        border-radius: 10px !important;        
        padding: 6px 12px !important; /* 上下のパディングを減らして高さを細く調整 */
        border: 2px solid #29b5e8 !important; /* 枠線も少し細くスッキリさせる */
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .stRadio [role="radiogroup"] label:hover {
        transform: translateY(-2px); 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stRadio [role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    .stRadio [role="radiogroup"] label p {
        color: black !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important; 
        text-align: center !important;
        margin: 0 !important;
        width: 100%;
    }
    .stRadio [role="radiogroup"] label:has(input:checked) {
        background-color: #ffffff !important;
        border: 2px solid #29b5e8 !important;
    }

    /* 🌟追加：ランキング表（st.table）の文字サイズを約4ポイント大きくする */
    [data-testid="stTable"] {
        font-size: 30px !important; /* 14px + 4px */
    }
    [data-testid="stTable"] th {
        font-size: 16px !important;
        color: #555 !important;
    }
    [data-testid="stTable"] td {
        font-size: 18px !important;
        font-weight: bold !important;
        vertical-align: middle !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画像をHTMLで表示するためのBase64エンコード関数 ---
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 全ユーザーの進行状況を共有するためのグローバル辞書 ---
@st.cache_resource
def get_active_users():
    return {}

# --- 全ユーザーでランキングを共有するためのグローバルリスト ---
@st.cache_resource
def get_global_rankings():
    return []

# ------------------------------------------------
# リアルタイム更新（フラグメント）
# ------------------------------------------------
@st.fragment(run_every=3)
def show_active_users_fragment(current_q):
    active_users = get_active_users()
    same_q_users = sum(1 for q in active_users.values() if q == current_q)
    st.markdown(f"<p style='text-align: center; color: #ff4b4b; font-weight: bold; font-size: 0.9rem; margin-bottom: 0px;'>🔥 現在 {same_q_users} 人がこの問題に挑戦中！</p>", unsafe_allow_html=True)

# 管理者ダッシュボード用のリアルタイム更新フラグメント
@st.fragment(run_every=3)
def admin_dashboard_content():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h2 style='text-align: center; color: #555;'>📱 クイズに参加する</h2>", unsafe_allow_html=True)
        if os.path.exists("QR.png"):
            st.image("QR.png", use_container_width=True)
        else:
            st.warning("⚠️ `QR.png` が見つかりません。")
            
    with col2:
        st.markdown("<h2 style='text-align: center; color: #555;'>🏆 リアルタイムランキング</h2>", unsafe_allow_html=True)
        global_rankings = get_global_rankings()
        
        if not global_rankings:
            st.info("まだ参加者がいません。")
        else:
            sorted_ranking = sorted(global_rankings, key=lambda x: x["クリアタイム"])
            # 🌟変更：st.dataframe から st.table に変更し、フォーマットを自前で行う
            formatted_ranking = [
                {"プレイヤー名": r["プレイヤー名"], "クリアタイム": f"{r['クリアタイム']:.2f} 秒"}
                for r in sorted_ranking
            ]
            df = pd.DataFrame(formatted_ranking)
            df.index = [f"{i+1}位" for i in range(len(df))]
            
            st.table(df)

# ------------------------------------------------
# 初期設定とステート管理
# ------------------------------------------------
st.set_page_config(page_title="Snowvillage Quiz", page_icon="❄️", layout="wide")

# --- カスタムCSSの呼び出し ---
inject_custom_css()

if "phase" not in st.session_state:
    st.session_state.phase = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "wrong_choices" not in st.session_state:
    st.session_state.wrong_choices = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# --- Excelから抽出・整理したクイズデータ ---
QUIZ_DATA = [
    {
        "q": "日本のコミュニティは？",
        "opts": ["SnowVillage", "SnowCircle", "SnowSaber", "SnowNeighbors"],
        "ans": "SnowVillage",
        "hint": "コミュニティブースの「POWERED BY」の後ろに注目！"
    },
    {
        "q": "日本のコミュニティは2026年9月現在、何人を突破した？\n（Slackワークスペースの参加人数）",
        "opts": ["5000人", "2500人", "1000人", "500人"],
        "ans": "2500人",
        "hint": "コミュニティブースでもらえるシールに正解の数字が隠れてるよ"
    },
    {
        "q": "下のマーク（アイコン）が意味するSnowflakeの機能はどれですか？",
        "opts": ["Dynamic Table", "Snowflake Horizon", "Snowpark", "Iceberg Table"],
        "ans": "Iceberg Table",
        "hint": "アイコンの右下のマーク、これが意味するものは"
    },
    {
        "q": "企業がAIをビジネスに適用し、使いこなすためのプラットフォームとしてのSnowflakeのポジションを表すキーワードは？",
        "opts": ["AI Data Cloud", "Enterprise Lakehouse", "Data Cloud", "Cloud DWH"],
        "ans": "AI Data Cloud",
        "hint": "組織が重要なデータとアプリケーションに接続し、コラボレーションを行ってイノベーションを推進するための『グローバルなネットワーク』として定義されています"
    },
    {
        "q": "自然言語の指示からSQLやPythonコードを生成し、データエンジニアリングやアプリ開発のワークフローを支援するデータネイティブなAIコーディングエージェントの名称はどれですか？",
        "opts": ["Snowflake CoCo", "Snowflake CoWork", "Cortex AI", "Cortex ANALYST"],
        "ans": "Snowflake CoCo",
        "hint": "頭文字から命名されていて、2026年のSummitで発表されたよ！"
    },
    {
        "q": "社内の数値データとテキストデータを横断して自然言語で分析し、グラフ作成からメール送信といった業務まで対話形式で自動化できる、ビジネスユーザー向けのAIワークアシスタント機能は？",
        "opts": ["Snowflake Cortex", "Snowflake Horizon", "Snowflake Snowpark", "Snowflake CoWork"],
        "ans": "Snowflake CoWork",
        "hint": "売上などの「数値データ」と問い合わせ履歴などの「テキストデータ」の両方を掛け合わせた分析を「チャット形式」で行える機能といえば"
    },
    {
        "q": "2025年9月にリリースされた、コードの管理やモデルの開発もできGitの統合もできる開発環境は？",
        "opts": ["snowsight", "Snowflake Notebooks", "Workspace", "Worksheet"],
        "ans": "Workspace",
        "hint": "これまで別々だったNotebookやSQLワークシートなどの開発ツールを、一つの「プロジェクト専用の空間」にまとめたような機能であることから名付けられています。"
    },
    {
        "q": "Snowflakeにおいて、AIエージェントやBIツールが共通のビジネスロジックを理解できるように、データ資産のメタデータを収集・強化し、一貫した意味（セマンティクス）やリネージを提供するガバナンス機能はどれですか？",
        "opts": ["Universal Search", "Trust Center", "Horizon Context", "Snowflake Cortex"],
        "ans": "Horizon Context",
        "hint": "メタデータから「ビジネスの文脈」を構築し、AIに正しい意味を理解させるためのレイヤー"
    },
    {
        "q": "Streamlitでのアプリ開発を学べるクリスマス企画「○○days of Streamlit」は何日で完結するコンテンツでしょうか？",
        "opts": ["30 days", "25 days", "24 days", "365 days"],
        "ans": "25 days",
        "hint": "クリスマスまでにstreamlitを覚えられるってことはクリスマスは12月何日？"
    }
]

# ------------------------------------------------
# ページ1: クイズ画面（ログイン・クイズ・結果を内包）
# ------------------------------------------------
def page_main_quiz():
    active_users = get_active_users() 
    global_rankings = get_global_rankings()

    # --- ログインフェーズ ---
    if st.session_state.phase == "login":
        st.markdown("<h3 style='text-align: center; color: #29b5e8;'>❄️ Streamlitで<br>クイズチャレンジ</h3>", unsafe_allow_html=True)
        st.write("")
        
        col1, col2, col3 = st.columns([1, 5, 1])
        with col2:
            st.markdown("<p style='text-align: center; font-weight: bold;'>プレイヤー名を入力してください</p>", unsafe_allow_html=True)
            username = st.text_input("ユーザー名", label_visibility="collapsed", placeholder="例：スノウ太郎")
            
            st.write("")
            start_btn = st.button("🚀 クイズスタート！", type="primary", use_container_width=True, disabled=not username)
            
            if start_btn:
                st.session_state.username = username
                st.session_state.start_time = time.time()
                st.session_state.phase = "quiz"
                st.session_state.current_q = 1
                st.session_state.wrong_choices = []
                
                shuffled_quiz = []
                last_q_data = None
                
                for q in QUIZ_DATA:
                    q_copy = q.copy()
                    opts_copy = q_copy["opts"].copy()
                    random.shuffle(opts_copy)
                    q_copy["opts"] = opts_copy
                    
                    if q_copy["q"] == "日本のコミュニティは？":
                        last_q_data = q_copy
                    else:
                        shuffled_quiz.append(q_copy)
                
                random.shuffle(shuffled_quiz)
                shuffled_quiz = shuffled_quiz[:4]
                
                if last_q_data:
                    shuffled_quiz.append(last_q_data)
                    
                st.session_state.quiz_data = shuffled_quiz

                active_users[username] = 1
                st.rerun()

    # --- クイズ実行フェーズ ---
    elif st.session_state.phase == "quiz":
        q_idx = st.session_state.current_q - 1
        q_data = st.session_state.quiz_data[q_idx]
        TOTAL_Q = len(st.session_state.quiz_data) 

        timer_html = f"""
        <div style="text-align: right; font-size: 1.0rem; font-weight: bold; color: #29b5e8; margin-bottom: -40px;" id="live-timer">⏱️ 0.00秒</div>
        <script>
            const startTime = {st.session_state.start_time * 1000};
            setInterval(function() {{
                const now = Date.now();
                const diff = (now - startTime) / 1000;
                document.getElementById('live-timer').innerText = "⏱️ " + diff.toFixed(2) + "秒";
            }}, 100);
        </script>
        """
        st.components.v1.html(timer_html, height=40)

        st.markdown(f"<h3 style='text-align: center;'>第 {st.session_state.current_q} 問</h3>", unsafe_allow_html=True)
        
        mistake_count = len(st.session_state.wrong_choices)
        if mistake_count > 0:
            st.markdown("<h5 style='text-align: center; color: #ff4b4b;'>❌ 再挑戦！</h5>", unsafe_allow_html=True)
            if mistake_count == 1:
                st.markdown("<p style='text-align: center; font-weight: bold; color: #e67e22; font-size: 0.9rem;'>惜しい！もう一度よく考えてみよう！</p>", unsafe_allow_html=True)
            elif mistake_count == 2:
                st.markdown("<p style='text-align: center; font-weight: bold; color: #e67e22; font-size: 0.9rem;'>あと少し！選択肢が絞られてきたぞ！</p>", unsafe_allow_html=True)
            elif mistake_count >= 3:
                st.markdown("<p style='text-align: center; font-weight: bold; color: #e67e22; font-size: 0.9rem;'>もう正解は目の前！自信を持って！</p>", unsafe_allow_html=True)
            
        st.markdown(f"<h5 style='text-align: center; white-space: pre-wrap; line-height: 1.5;'>{q_data['q']}</h5>", unsafe_allow_html=True)
        
        if "下のマーク（アイコン）が意味するSnowflakeの機能はどれですか？" in q_data['q']:
            img_b64 = get_image_base64("image_c64ebb.png")
            if img_b64:
                st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{img_b64}" width="70"></div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ `image_c64ebb.png` が見つかりません。")
        
        show_active_users_fragment(st.session_state.current_q)
        
        st.markdown("<hr style='margin: 10px 0px 15px 0px; border-top: 1px solid #e6e6e6;'>", unsafe_allow_html=True)

        with st.expander("💡 ヒントを見る" + "\u200b" * st.session_state.current_q):
            st.write(q_data["hint"])

        available_opts = [opt for opt in q_data["opts"] if opt not in st.session_state.wrong_choices]
        
        user_choice = st.radio(
            "回答を選択してください", 
            available_opts, 
            index=None, 
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("解答する", type="primary", use_container_width=True, disabled=not user_choice):
                if user_choice == q_data["ans"]:
                    st.session_state.wrong_choices = [] 
                    if st.session_state.current_q < TOTAL_Q:
                        st.session_state.current_q += 1
                        active_users[st.session_state.username] = st.session_state.current_q
                    else:
                        st.session_state.elapsed_time = time.time() - st.session_state.start_time
                        
                        global_rankings.append({
                            "プレイヤー名": st.session_state.username,
                            "クリアタイム": round(st.session_state.elapsed_time, 2)
                        })
                        
                        st.session_state.phase = "result"
                        if st.session_state.username in active_users:
                            del active_users[st.session_state.username]
                else:
                    st.session_state.wrong_choices.append(user_choice)
                
                st.rerun()

        st.markdown("<hr style='margin: 15px 0px 10px 0px; border-top: 1px solid #e6e6e6;'>", unsafe_allow_html=True)
        
        progress_val = st.session_state.current_q / TOTAL_Q
        st.progress(progress_val)
        
        if st.session_state.current_q == 1:
            msg = "さあ、始まりました！どんどん答えていこう！"
        elif st.session_state.current_q == TOTAL_Q:
            msg = "泣いても笑っても最後の問題！"
        elif st.session_state.current_q == TOTAL_Q // 2:
            msg = "折り返し地点！落ち着いていこう！"
        elif st.session_state.current_q == TOTAL_Q - 1:
            msg = "あと1問！"
        else:
            msg = "いいペースです！その調子！"

        st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.85rem;'>({st.session_state.current_q}/{TOTAL_Q}) {msg}</p>", unsafe_allow_html=True)

    # --- 結果発表フェーズ ---
    elif st.session_state.phase == "result":
        st.snow()
        st.markdown("<h3 style='text-align: center; color: #29b5e8;'>🎉 NICE CHALLENGE！！</h3>", unsafe_allow_html=True)
        
        st.markdown(f"<h5 style='text-align: center; line-height: 1.6;'>{st.session_state.username}さん、<br>参加してくれてありがとうございます！</h5>", unsafe_allow_html=True)
        
        st.markdown(f"<h4 style='text-align: center;'>あなたのタイム: <span style='color: #ff4b4b;'>{round(st.session_state.elapsed_time, 2)}秒</span></h4>", unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("<p style='text-align: center; font-size: 1.0rem; font-weight: bold; margin-bottom: 5px;'>もっとコミュニティを楽しもう！</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.1rem; font-weight: bold; color: #29b5e8;'>Let's go see SnowVillage!!!</p>", unsafe_allow_html=True)
        
        img_base64 = get_image_base64("image_f9229b.png")
        if img_base64:
            html_img_link = f"""
            <div style="display: flex; justify-content: center;">
                <a href="https://snowvillage.cloud/contents/" target="_blank">
                    <img src="data:image/png;base64,{img_base64}" style="width: 140px; cursor: pointer; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                </a>
            </div>
            """
            st.markdown(html_img_link, unsafe_allow_html=True)
        else:
            st.warning("⚠️ `image_f9229b.png` が見つかりません。app.pyと同じフォルダに配置してください。")
            st.link_button("❄️ snowvillage はこちら！", "https://snowvillage.cloud/", use_container_width=True)
        
        st.write("")
        st.write("")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("もう一度挑戦する（別名でプレイ）", icon="🔄", use_container_width=True):
                st.session_state.phase = "login"
                st.session_state.username = ""
                st.session_state.wrong_choices = []
                st.rerun()
            
            st.write("")
            if st.button("ランキングを見よう！", icon="🏆", use_container_width=True):
                st.switch_page(ranking_page)

# ------------------------------------------------
# ページ2: いつでも見れるランキング画面
# ------------------------------------------------
def page_ranking():
    st.markdown("<h3 style='text-align: center;'>🏆 回答最速王</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>現在の回答王番付はこちら🥇</p>", unsafe_allow_html=True)
    
    if st.session_state.phase == "quiz":
        st.info("💡 現在クイズに挑戦中です！左のメニューから「クイズ」に戻ると、続きから再開できます。")
    
    global_rankings = get_global_rankings()
    
    if not global_rankings:
        st.write("まだ参加者がいません。あなたが最初のチャレンジャーになりましょう！")
    else:
        sorted_ranking = sorted(global_rankings, key=lambda x: x["クリアタイム"])
        # 🌟変更：st.dataframe から st.table に変更し、フォーマットを自前で行う
        formatted_ranking = [
            {"プレイヤー名": r["プレイヤー名"], "クリアタイム": f"{r['クリアタイム']:.2f} 秒"}
            for r in sorted_ranking
        ]
        df = pd.DataFrame(formatted_ranking)
        df.index = [f"{i+1}位" for i in range(len(df))]
        
        st.table(df)

# ------------------------------------------------
# ページ3: 管理者画面（ダッシュボード＆リセット）
# ------------------------------------------------
def page_admin():
    # ログインしていない場合の表示
    if not st.session_state.admin_logged_in:
        st.markdown("<h3 style='text-align: center;'>🔒 管理者ログイン</h3>", unsafe_allow_html=True)
        st.write("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            admin_pw = st.text_input("パスワードを入力してください", type="password")
            if st.button("ログイン", use_container_width=True):
                if admin_pw == "streamlit":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("パスワードが違います。")
    
    # ログイン済みの表示（ダッシュボード）
    else:
        st.markdown("<h2 style='text-align: center; color: #29b5e8;'>streamlitでクイズに挑戦しよう！！</h2>", unsafe_allow_html=True)
        st.write("")
        
        # QRコードとランキングをリアルタイムで表示
        admin_dashboard_content()
        
        st.divider()
        
        # 管理者用のアクションボタン
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🗑️ ランキングをリセットする", use_container_width=True, type="primary"):
                get_global_rankings().clear()
                st.success("ランキングをリセットしました！")
                time.sleep(1)
                st.rerun()
                
            st.write("")
            if st.button("🚪 ログアウト", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()

# ------------------------------------------------
# ナビゲーションの構築（常時表示）
# ------------------------------------------------
quiz_page = st.Page(page_main_quiz, title="クイズ", icon="🎮", default=True)
ranking_page = st.Page(page_ranking, title="ランキング", icon="🏆")
admin_page = st.Page(page_admin, title="管理者画面", icon="⚙️")

pg = st.navigation(
    {
        "メインメニュー": [quiz_page, ranking_page, admin_page]
    }
)
pg.run()
