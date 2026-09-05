import streamlit as st
import pandas as pd

# ------------------------------------------------
# 1. セッション状態の初期化（全ページで共有するデータ）
# ------------------------------------------------
if "ranking_data" not in st.session_state:
    # 初期ランキングデータ
    st.session_state.ranking_data = [
        {"名前": "Streamlitマスター", "スコア": 100},
        {"名前": "Pythonビギナー", "スコア": 50},
    ]

# ------------------------------------------------
# 2. 各ページの中身を「関数」として定義する
# ------------------------------------------------

def page_quiz():
    """クイズ画面のコンテンツ"""
    st.title("🎮 クイズに挑戦！")
    st.write("前回のクイズ機能をここに組み込みます。今回はテスト用のボタンを用意しました。")
    
    # 擬似的なスコア獲得ボタン
    if st.button("クイズに全問正解した！（スコア150点獲得）", type="primary"):
        st.session_state.latest_score = 150
        st.success("おめでとう！150点を獲得しました。")
        
    # スコアがある場合、ランキング登録UIを表示
    if "latest_score" in st.session_state:
        with st.container(border=True):
            st.subheader("ランキングに登録する")
            name = st.text_input("プレイヤー名を入力してください")
            
            if st.button("登録"):
                if name:
                    # セッション状態のランキングリストに追加
                    st.session_state.ranking_data.append(
                        {"名前": name, "スコア": st.session_state.latest_score}
                    )
                    # 二重登録を防ぐため最新スコアをリセット
                    del st.session_state["latest_score"]
                    st.info("登録完了！サイドバーからランキング画面を見てみましょう。")
                    st.rerun()
                else:
                    st.warning("名前を入力してください。")


def page_ranking():
    """ランキング画面のコンテンツ"""
    st.title("👑 ランキング")
    st.write("現在のトッププレイヤーたちです！")
    
    # スコアの降順（高い順）でデータをソート
    sorted_ranking = sorted(
        st.session_state.ranking_data, 
        key=lambda x: x["スコア"], 
        reverse=True
    )
    
    # DataFrameに変換して見た目を整える
    df = pd.DataFrame(sorted_ranking)
    df.index = [f"{i+1}位" for i in range(len(df))] # インデックスを順位に変更
    
    # st.dataframeでリッチに表示（st.tableでも可）
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "名前": st.column_config.TextColumn("プレイヤー名", max_chars=50),
            "スコア": st.column_config.NumberColumn("スコア", format="%d 点")
        }
    )

# ------------------------------------------------
# 3. st.Page でページオブジェクトを作成
# ------------------------------------------------
# 関数、タイトル、アイコンを指定します
quiz = st.Page(page_quiz, title="クイズをプレイ", icon="❓")
ranking = st.Page(page_ranking, title="リーダーボード", icon="🏆")

# ------------------------------------------------
# 4. st.navigation でメニューを構築して実行
# ------------------------------------------------
# 辞書型で渡すと、サイドバーにセクション名を付けられます
pg = st.navigation(
    {
        "メインメニュー": [quiz, ranking]
    }
)

# アプリの実行
pg.run()
