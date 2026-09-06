import streamlit as st
import time
import pandas as pd

# ------------------------------------------------
# 初期設定とステート管理
# ------------------------------------------------
st.set_page_config(page_title="Snowvillage Quiz", page_icon="❄️")

# セッション状態の初期化
if "phase" not in st.session_state:
    st.session_state.phase = "login" # login, quiz, result
if "username" not in st.session_state:
    st.session_state.username = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "rankings" not in st.session_state:
    st.session_state.rankings = []
# 【新機能】間違えた選択肢を記録するリスト
if "wrong_choices" not in st.session_state:
    st.session_state.wrong_choices = []

# クイズデータ（5問・4択）
QUIZ_DATA = [
    {
        "q": "Snowflakeはどのクラウドプロバイダー上で実行できますか？",
        "opts": ["AWSのみ", "AWS, GCP", "AWS, Azure, GCP", "オンプレミスのみ"],
        "ans": "AWS, Azure, GCP",
        "hint": "Snowflakeはマルチクラウドに対応しているのが強みです！"
    },
    {
        "q": "Snowflakeのアーキテクチャの最大の特徴は何を分離していること？",
        "opts": ["ユーザーとパスワード", "コンピュートとストレージ", "ネットワークとセキュリティ", "テーブルとビュー"],
        "ans": "コンピュートとストレージ",
        "hint": "処理能力とデータ保存場所を別々にスケーリングできます。"
    },
    {
        "q": "Snowflakeの仮想ウェアハウスのサイズ変更はいつ行えますか？",
        "opts": ["サーバー再起動時のみ", "月に1回だけ", "無停止でいつでも", "データロード前のみ"],
        "ans": "無停止でいつでも",
        "hint": "ダウンタイムなしで瞬時にスケールアップ・ダウンが可能です。"
    },
    {
        "q": "Snowflakeでデータを共有する際、データをコピーする必要はありますか？",
        "opts": ["常に必要", "外部クラウドへの共有時のみ必要", "不要（同じデータを参照）", "週に1回同期が必要"],
        "ans": "不要（同じデータを参照）",
        "hint": "「データシェアリング」という機能を使うと、コピーなしで安全に共有できます。"
    },
    {
        "q": "Snowflakeの日本コミュニティの名称は？",
        "opts": ["SnowMountain", "Snowvillage", "SnowCity", "SnowTown"],
        "ans": "Snowvillage",
        "hint": "村（village）のように温かく、みんなで助け合うコミュニティです！"
    }
]

# ------------------------------------------------
# ページ1: クイズ画面（ログイン・クイズ・結果を内包）
# ------------------------------------------------
def page_main_quiz():
    # --- ログインフェーズ ---
    if st.session_state.phase == "login":
        st.markdown("<h1 style='text-align: center; color: #29b5e8;'>❄️ クイズチャレンジ</h1>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h4 style='text-align: center;'>プレイヤー名を入力してください</h4>", unsafe_allow_html=True)
            username = st.text_input("ユーザー名", label_visibility="collapsed", placeholder="例：スノウ太郎")
            
            st.write("")
            start_btn = st.button("🚀 クイズスタート！", type="primary", use_container_width=True, disabled=not username)
            
            if start_btn:
                st.session_state.username = username
                st.session_state.start_time = time.time()
                st.session_state.phase = "quiz"
                st.session_state.current_q = 1
                st.session_state.wrong_choices = [] # 履歴リセット
                st.rerun()

    # --- クイズ実行フェーズ ---
    elif st.session_state.phase == "quiz":
        q_idx = st.session_state.current_q - 1
        q_data = QUIZ_DATA[q_idx]

        st.markdown(f"<h2 style='text-align: center;'>第 {st.session_state.current_q} 問</h2>", unsafe_allow_html=True)
        
        # 【新機能】間違えた回数に応じて再挑戦メッセージを変化させる
        mistake_count = len(st.session_state.wrong_choices)
        if mistake_count > 0:
            st.markdown("<h4 style='text-align: center; color: #ff4b4b;'>❌ 再挑戦！</h4>", unsafe_allow_html=True)
            if mistake_count == 1:
                st.markdown("<p style='text-align: center; font-weight: bold; color: #e67e22;'>惜しい！もう一度よく考えてみよう！</p>", unsafe_allow_html=True)
            elif mistake_count == 2:
                st.markdown("<p style='text-align: center; font-weight: bold; color: #e67e22;'>あと少し！選択肢が絞られてきたぞ！</p>", unsafe_allow_html=True)
            elif mistake_count >= 3:
                st.markdown("<p style='text-align: center; font-weight: bold; color: #e67e22;'>もう正解は目の前！自信を持って！</p>", unsafe_allow_html=True)
            
        st.markdown(f"<h4 style='text-align: center;'>{q_data['q']}</h4>", unsafe_allow_html=True)
        st.divider()

        with st.expander("💡 ヒントを見る"):
            st.write(q_data["hint"])

        st.write("")

        # 【新機能】間違えた選択肢を除外して表示
        available_opts = [opt for opt in q_data["opts"] if opt not in st.session_state.wrong_choices]
        
        user_choice = st.radio(
            "回答を選択してください", 
            available_opts, 
            index=None, 
            label_visibility="collapsed"
        )

        st.write("")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("解答する", type="primary", use_container_width=True, disabled=not user_choice):
                if user_choice == q_data["ans"]:
                    # 正解：次の問題へ進む準備
                    st.session_state.wrong_choices = [] # 不正解履歴をクリア
                    if st.session_state.current_q < 5:
                        st.session_state.current_q += 1
                    else:
                        st.session_state.elapsed_time = time.time() - st.session_state.start_time
                        st.session_state.rankings.append({
                            "プレイヤー名": st.session_state.username,
                            "クリアタイム": round(st.session_state.elapsed_time, 2)
                        })
                        st.session_state.phase = "result"
                else:
                    # 不正解：間違えた選択肢をリストに追加して再描画
                    st.session_state.wrong_choices.append(user_choice)
                
                st.rerun()

        st.write("")
        st.write("")
        st.divider()
        
        progress_val = st.session_state.current_q / 5
        st.progress(progress_val)
        
        messages = {
            1: "さあ、始まりました！どんどん答えていこう！",
            2: "いいペースです！その調子！",
            3: "折り返し地点！落ち着いていこう！",
            4: "あと1問！",
            5: "泣いても笑っても最後の問題！"
        }
        st.markdown(f"<p style='text-align: center; color: gray;'>({st.session_state.current_q}/5) {messages[st.session_state.current_q]}</p>", unsafe_allow_html=True)

    # --- 結果発表フェーズ ---
    elif st.session_state.phase == "result":
        st.balloons()
        st.markdown("<h2 style='text-align: center; color: #29b5e8;'>🎉 NICE CHALLENGE！！</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>{st.session_state.username}さん、参加してくれてありがとうございます！</h4>", unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='text-align: center;'>あなたのタイム: <span style='color: #ff4b4b;'>{round(st.session_state.elapsed_time, 2)}秒</span></h3>", unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("<h4 style='text-align: center;'>もっとコミュニティを楽しもう！</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.link_button("❄️ snowvillage はこちら！", "https://snowvillage.cloud/", use_container_width=True)
        
        st.write("")
        st.write("")
        
        # もう一度遊ぶボタン
        if st.button("もう一度挑戦する（別名でプレイ）", icon="🔄"):
            st.session_state.phase = "login"
            st.session_state.username = ""
            st.session_state.wrong_choices = []
            st.rerun()

# ------------------------------------------------
# ページ2: いつでも見れるランキング画面
# ------------------------------------------------
def page_ranking():
    st.title("🏆 リーダーボード")
    st.write("現在のタイムアタックランキングです！")
    
    # プレイ中にランキングを見た場合のアナウンス
    if st.session_state.phase == "quiz":
        st.info("💡 現在クイズに挑戦中です！左のメニューから「クイズ」に戻ると、続きから再開できます。")
    
    if not st.session_state.rankings:
        st.write("まだ参加者がいません。あなたが最初のチャレンジャーになりましょう！")
        return

    sorted_ranking = sorted(st.session_state.rankings, key=lambda x: x["クリアタイム"])
    df = pd.DataFrame(sorted_ranking)
    df.index = [f"{i+1}位" for i in range(len(df))]
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "プレイヤー名": st.column_config.TextColumn("プレイヤー名", max_chars=50),
            "クリアタイム": st.column_config.NumberColumn("クリアタイム (秒)", format="%.2f 秒")
        }
    )

# ------------------------------------------------
# ナビゲーションの構築（常時表示）
# ------------------------------------------------
quiz_page = st.Page(page_main_quiz, title="クイズ", icon="🎮", default=True)
ranking_page = st.Page(page_ranking, title="ランキング", icon="🏆")

# 辞書型で渡すことでサイドバーに美しいメニューを構築
pg = st.navigation(
    {
        "メインメニュー": [quiz_page, ranking_page]
    }
)
pg.run()
