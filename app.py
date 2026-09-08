# --- カスタムデザインを適用するCSS ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* 1. ラジオボタンをSnowflakeブルーの角丸ボタン化 */
    .stRadio [role="radiogroup"] {
        gap: 12px;
    }
    .stRadio [role="radiogroup"] label {
        background-color: #29b5e8 !important; /* Snowflakeブルー */
        border-radius: 12px !important;       /* 角丸 */
        padding: 15px !important;
        border: 3px solid #29b5e8 !important;
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
        font-size: 1.1rem !important;
        text-align: center !important;
        margin: 0 !important;
        width: 100%;
    }
    .stRadio [role="radiogroup"] label:has(input:checked) {
        background-color: #ffffff !important;
        border: 3px solid #29b5e8 !important;
    }

    /* 2. サイドバーの開閉アイコンを完全に「📺🔄」に変更する強力なハック */
    /* 閉じているときの左上のアイコン (>>) を上書き */
    [data-testid="collapsedControl"] svg {
        visibility: hidden !important; /* 元のアイコンを見えなくする */
    }
    [data-testid="collapsedControl"] {
        position: relative !important;
    }
    [data-testid="collapsedControl"]::before {
        content: "📺🔄" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-size: 1.4rem !important;
        visibility: visible !important;
    }

    /* 開いているときのサイドバー内の閉じるアイコン (<) も揃える */
    [data-testid="stSidebarCollapseButton"] svg {
        visibility: hidden !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        position: relative !important;
    }
    [data-testid="stSidebarCollapseButton"]::before {
        content: "📺🔄" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        font-size: 1.4rem !important;
        visibility: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)
