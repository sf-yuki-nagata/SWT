import streamlit as st
import time
import pandas as pd

# ------------------------------------------------
# 初期設定とステート管理
# ------------------------------------------------
st.set_page_config(page_title="Snowvillage Quiz", page_icon="❄️", initial_sidebar_state="collapsed")

# セッション状態の初期化
if "phase" not in st.session_state:
    st.session_state.phase = "login" # login, quiz, result の3フェーズ
if "username" not in st.session_state:
    st.session_state.username = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 1
if "retry" not in st.session_state:
    st.session_state.retry = False
if "rankings" not in st.session_state:
    st.session_state.rankings = []

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
# ページ1: ログイン画面（TOP）
# ------------------------------------------------
def page_login():
    st.markdown("<h1 style='text-align: center; color: #29b5e8;'>❄️ クイズチャレンジ</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    # フォームを中央に配置するためのカラム構成
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h4 style='text-align: center;'>プレイヤー名を入力してください</h4>", unsafe_allow_html=True)
        username = st.text_input("ユーザー名", label_visibility="collapsed", placeholder="例：スノウ太郎")
        
        st.write("")
        # 名前が入力されていないとボタンを押せないように制御
        start_btn = st.button("🚀 クイズスタート！", type="primary", use_container_width=True, disabled=not username)
        
        if start_btn:
            st.session_state.username = username
            st.session_state.start_time = time.time()
            st.session_state.phase = "quiz"
            st.session_state.current_q = 1
            st.rerun()

# ------------------------------------------------
# ページ2: クイズ画面（1〜5問目共通）
# ------------------------------------------------
def page_quiz():
    q_idx = st.session_state.current_q - 1
    q_data = QUIZ_DATA[q_idx]

    # ヘッダーと設問（中央揃え）
    st.markdown(f"<h2 style='text-align: center;'>第 {st.session_state.current_q} 問</h2>", unsafe_allow_html=True)
    
    # 間違えた場合の「再挑戦」メッセージ
    if st.session_state.retry:
        st.markdown("<h4 style='text-align: center; color: #ff4b4b;'>❌ 再挑戦！</h4>", unsafe_allow_html=True)
        
    st.markdown(f"<h4 style='text-align: center;'>{q_data['q']}</h4>", unsafe_allow_html=True)
    st.divider()

    # ヒント（エクスパンダー）
    with st.expander("💡 ヒントを見る"):
        st.write(q_data["hint"])

    st.write("")

    # 4択の回答（ラジオボタン、デフォルト選択なし）
    user_choice = st.radio(
        "回答を選択してください", 
        q_data["opts"], 
        index=None, 
        label_visibility="collapsed"
    )

    st.write("")
    
    # 回答ボタン（選択されていないと押せない）
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("解答する", type="primary", use_container_width=True, disabled=not user_choice):
            if user_choice == q_data["ans"]:
                # 正解の場合
                st.session_state.retry = False
                if st.session_state.current_q < 5:
                    st.session_state.current_q += 1
                else:
                    # 5問目正解でクリア処理
                    st.session_state.elapsed_time = time.time() - st.session_state.start_time
                    # ランキングに登録
                    st.session_state.rankings.append({
                        "プレイヤー名": st.session_state.username,
                        "クリアタイム": round(st.session_state.elapsed_time, 2)
                    })
                    st.session_state.phase = "result"
            else:
                # 不正解の場合
                st.session_state.retry = True
            
            st.rerun()

    # 画面下部のステータスバーと応援メッセージ
    st.write("")
    st.write("")
    st.divider()
    
    # 進行度バー
    progress_val = st.session_state.current_q / 5
    st.progress(progress_val)
    
    # メッセージの設定
    messages = {
        1: "さあ、始まりました！どんどん答えていこう！",
        2: "いいペースです！その調子！",
        3: "折り返し地点！落ち着いていこう！",
        4: "あと1問！",
        5: "泣いても笑っても最後の問題！"
    }
    st.markdown(f"<p style='text-align: center; color: gray;'>({st.session_state.current_q}/5) {messages[st.session_state.current_q]}</p>", unsafe_allow_html=True)

# ------------------------------------------------
# ページ3: 結果・ランキング画面
# ------------------------------------------------
def page_result():
    st.balloons()
    st.markdown("<h2 style='text-align: center; color: #29b5e8;'>🎉 NICE CHALLENGE！！</h2>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{st.session_state.username}さん、参加してくれてありがとうございます！</h4>", unsafe_allow_html=True)
    
    # タイムの表示
    st.markdown(f"<h3 style='text-align: center;'>あなたのタイム: <span style='color: #ff4b4b;'>{round(st.session_state.elapsed_time, 2)}秒</span></h3>", unsafe_allow_html=True)
    
    st.divider()
    
    # コミュニティへの誘導
    st.markdown("<h4 style='text-align: center;'>もっとコミュニティを楽しもう！</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # リンクボタン
        st.link_button("❄️ snowvillage はこちら！", "https://snowvillage.cloud/", use_container_width=True)
    
    st.divider()

    # ランキングの表示
    st.subheader("🏆 リーダーボード（タイムアタック）")
    
    # タイムが短い順にソート
    sorted_ranking = sorted(st.session_state.rankings, key=lambda x: x["クリアタイム"])
    df = pd.DataFrame(sorted_ranking)
    df.index = [f"{i+1}位" for i in range(len(df))]
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "クリアタイム": st.column_config.NumberColumn("クリアタイム (秒)", format="%.2f 秒")
        }
    )
    
    st.write("")
    if st.button("もう一度挑戦する（別名でプレイ）", icon="🔄"):
        st.session_state.phase = "login"
        st.session_state.username = ""
        st.session_state.retry = False
        st.rerun()

# ------------------------------------------------
# ナビゲーション制御
# ------------------------------------------------
# 状態に応じて表示するページを動的に定義する
if st.session_state.phase == "login":
    pages = {"ログイン": [st.Page(page_login, title="スタート画面", icon="🏠")]}
elif st.session_state.phase == "quiz":
    pages = {"クイズ": [st.Page(page_quiz, title="クイズ挑戦中...", icon="🎮")]}
else:
    pages = {"結果": [st.Page(page_result, title="結果発表・ランキング", icon="🏆")]}

# メニューを生成して実行
# position="hidden" にすることで、サイドバーを隠して完全にアプリ風の画面遷移にしています
pg = st.navigation(pages, position="hidden")
pg.run()
