import streamlit as st
from PIL import Image, ImageOps

# 1. 網頁基本設定 (寬螢幕模式、隱藏側邊欄)
st.set_page_config(
    page_title="Aesop Style Audit Tool", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 限制上傳檔案大小為 10MB
st.config.set_option("server.maxUploadSize", 10)

# Aesop 極簡美學高級 CSS
st.markdown("""
    <style>
    .main { 
        background-color: #FAF9F6 !important; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Microsoft JhengHei", sans-serif !important;
        color: #252525 !important;
    }
    h1 { 
        font-weight: 300 !important; 
        letter-spacing: 0.08em !important; 
        color: #252525 !important;
        font-size: 2rem !important;
    }
    h3 { 
        font-weight: 400 !important; 
        letter-spacing: 0.06em !important; 
        color: #333333 !important;
        font-size: 1.1rem !important;
        border-bottom: 1px solid #EAE6DF;
        padding-bottom: 0.5rem;
    }
    .stSelectbox div[data-baseweb="select"], .stDateInput div[data-baseweb="input"], .stNumberInput div[data-baseweb="input"], .stTextArea textarea {
        border-radius: 0px !important;
        border: 1px solid #333333 !important;
        background-color: #FAF9F6 !important;
        color: #252525 !important;
    }
    .stFileUploader section {
        border-radius: 0px !important;
        border: 1px dashed #8E765D !important;
        background-color: #F5F4F0 !important;
    }
    div.stButton > button {
        border-radius: 0px !important;
        background-color: #252525 !important;
        color: #FAF9F6 !important;
        border: 1px solid #252525 !important;
        padding: 0.6rem 2rem !important;
        letter-spacing: 0.1em !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FAF9F6 !important;
        color: #252525 !important;
        border: 1px solid #252525 !important;
    }
    .aesop-success {
        background-color: #EBF2EE !important;
        color: #2C5E3B !important;
        padding: 1rem;
        border-left: 2px solid #2C5E3B;
        letter-spacing: 0.05em;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .aesop-error {
        background-color: #F9F1F0 !important;
        color: #9E473A !important;
        padding: 1rem;
        border-left: 2px solid #9E473A;
        letter-spacing: 0.05em;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .aesop-info {
        background-color: #F5F4F0 !important;
        color: #8E765D !important;
        padding: 1rem;
        border-left: 2px solid #8E765D;
        letter-spacing: 0.05em;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .diff-display {
        border: 1px solid #EAE6DF;
        background-color: #F5F4F0;
        padding: 10px 14px;
        font-size: 1.1rem;
        font-weight: 500;
        color: #252525;
        letter-spacing: 0.05em;
        height: 42px;
        line-height: 22px;
    }
    
    /* 💡 核心優化：徹底隱藏數字輸入框右側的加減（調整）按鈕 */
    div[data-testid="stNumberInputStepDown"], div[data-testid="stNumberInputStepUp"] {
        display: none !important;
    }
    /* 讓輸入文字區域填滿，避免右側留白過多 */
    .stNumberInput div[data-baseweb="input"] {
        padding-right: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Aesop 零售店鋪對帳單元")
st.markdown("<p style='letter-spacing:0.08em; color:#666666; font-size:0.85rem;'>RECONCILIATION AND RETAIL AUDIT PURSUIT</p>", unsafe_allow_html=True)
st.write(" ")

# 2. 全伺服器共享的臨時記憶置物櫃
@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()

# 圖片等比例優化縮放
def process_and_resize_image(uploaded_file):
    img = Image.open(uploaded_file)
    try:
        img = ImageOps.exif_transpose(img)
    except:
        pass
    max_size = 2000
    width, height = img.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img

# 左右分流佈局
main_left, main_right = st.columns([6, 4])

# --- 右半邊：對帳主控台 ---
with main_right:
    st.markdown("### 審核範疇")
    
    col_shop, col_date = st.columns(2)
    with col_shop:
        shop_name = st.selectbox("指定店鋪", ["請選擇", "台北信義店", "台中中友店", "高雄漢神店", "南西誠品店"], key="main_shop_select")
    with col_date:
        target_date = st.date_input("對帳日期", key="main_date_select")

    room_id = f"{shop_name}_{target_date}"

    if shop_name != "請選擇":
        if room_id not in global_rooms:
            global_rooms[room_id] = {"img_single": None}
        current_room = global_rooms[room_id]
        
        st.write(" ")
        if st.button("同步雲端單據狀態", key="refresh_images_btn"):
            st.rerun()
            
        st.write("---")
        st.markdown("### 數值登錄")
        
        input_col, output_col = st.columns(2)
        
        with input_col:
            mall_amount = st.number_input("百貨報表金額 (TWD)", min_value=0, step=1, value=0, key="amount_mall_input")
            cegid_amount = st.number_input("Cegid 系統金額 (TWD)", min_value=0, step=1, value=0, key="amount_cegid_input")
            
        with output_col:
            diff = mall_amount - cegid_amount
            st.markdown("<label style='font-size:0.85rem; color:#FAF9F6;'>Placeholder</label>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.85rem; margin-bottom:8px; color:#252525;'>今日帳差</p>", unsafe_allow_html=True)
            st.markdown(f'<div class="diff-display">{diff:,.0f}</div>', unsafe_allow_html=True)
            
        if mall_amount > 0 or cegid_amount > 0:
            if diff == 0:
                st.markdown(f'<div class="aesop-success">雙端數值一致，務請截圖留存以茲核備。</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="aesop-error">帳面未盡相符。</div>', unsafe_allow_html=True)
                diff_reason = st.text_area("請闡述帳差原因", placeholder="請以此處紀錄異常緣由...", key="reason_text_input")
                if diff_reason:
                    st.markdown(f'<div class="aesop-success">原因已載入。請直接將此畫面截圖存檔。</div>', unsafe_allow_html=True)
        
        st.write(" ")
        st.write(" ")
        if st.button("即時銷毀雲端暫存資料", key="clear_cache_btn"):
            global_rooms[room_id] = {"img_single": None}
            st.rerun()

# --- 左半邊：單據比對區 ---
with main_left:
    st.markdown("### 單據映像")
    
    if shop_name != "請選擇":
        current_room = global_rooms[room_id]
        
        uploaded_file = st.file_uploader("檔案上傳 (最大限制 10MB)", type=["png", "jpg", "jpeg"], key="single_file_key")
        if uploaded_file:
            current_room["img_single"] = process_and_resize_image(uploaded_file)
            st.rerun()
                
        st.write(" ")
        
        if current_room.get("img_single") is not None:
            st.markdown('<div class="aesop-success" style="margin-top:0px;">對帳單據已於雲端就位。</div>', unsafe_allow_html=True)
            st.image(current_room["img_single"], caption="AUDIT REPORT IMAGE", use_container_width=True)
        else:
            st.markdown('<div class="aesop-info" style="margin-top:0px;">靜待單據上傳。完成後請點擊右側「同步雲端單據狀態」。</div>', unsafe_allow_html=True)
            
    else:
        st.markdown('<div class="aesop-error">請先於右側面板指定店鋪，以開啟對帳作業。</div>', unsafe_allow_html=True)
