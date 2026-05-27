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
        font-size: 2.2rem !important;
    }
    h3 { 
        font-weight: 400 !important; 
        letter-spacing: 0.06em !important; 
        color: #333333 !important;
        font-size: 1.2rem !important;
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
        border-left: 3px solid #2C5E3B;
        letter-spacing: 0.05em;
        margin: 1rem 0;
    }
    .aesop-error {
        background-color: #F9F1F0 !important;
        color: #9E473A !important;
        padding: 1rem;
        border-left: 3px solid #9E473A;
        letter-spacing: 0.05em;
        margin: 1rem 0;
    }
    .aesop-info {
        background-color: #F1EFFB !important;
        color: #4A3E7D !important;
        padding: 1rem;
        letter-spacing: 0.05em;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Aesop — 零售對帳與審核單元")
st.markdown("<p style='letter-spacing:0.05em; color:#666666; font-size:0.9rem;'>ELEGANT REAL-TIME RECONCILIATION • PILOT VERSION</p>", unsafe_allow_html=True)
st.write(" ")

# 2. 全伺服器共享的臨時記憶置物櫃
@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()

# 圖片等比例縮放
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

# 建立左右 6:4 欄位
main_left, main_right = st.columns([6, 4])

# --- 右半邊：對帳主控台 (100% 鎖定，打字絕對不會重疊或被洗掉) ---
with main_right:
    st.markdown("### 🔍 填寫對帳範疇")
    
    col_shop, col_date = st.columns(2)
    with col_shop:
        shop_name = st.selectbox("選擇指定店鋪", ["請選擇", "台北信義店", "台中中友店", "高雄漢神店", "南西誠品店"], key="main_shop_select")
    with col_date:
        target_date = st.date_input("選擇對帳日期", key="main_date_select")

    room_id = f"{shop_name}_{target_date}"

    if shop_name != "請選擇":
        if room_id not in global_rooms:
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
        current_room = global_rooms[room_id]
        
        st.write(" ")
        st.markdown("### 💰 輸入系統金額")
        fee_col1, fee_col2 = st.columns(2)
        with fee_col1:
            mall_amount = st.number_input("百貨報表金額 (TWD)", min_value=0, step=1, value=0, key="amount_mall_input")
        with fee_col2:
            cegid_amount = st.number_input("Cegid 系統金額 (TWD)", min_value=0, step=1, value=0, key="amount_cegid_input")
            
        if mall_amount > 0 or cegid_amount > 0:
            diff = mall_amount - cegid_amount
            if diff == 0:
                st.markdown(f'<div class="aesop-success">✅ 金額完全相符。此案准予結案，請進行螢幕截圖。</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="aesop-error">❌ 偵測到帳面誤差。目前差額： {diff:,.0f} 元</div>', unsafe_allow_html=True)
                diff_reason = st.text_area("請闡述帳差原因 (必要填寫)", placeholder="例如：百貨刷卡手續費扣抵...", key="reason_text_input")
                if diff_reason:
                    st.markdown(f'<div class="aesop-success">⚠️ 帳差原因已載入。請直接截圖此畫面存檔。</div>', unsafe_allow_html=True)
        
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ 徹底清除此店鋪今日雲端暫存", key="clear_cache_btn"):
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
            st.rerun()

# --- 左半邊：單據比對區 (局部智慧監聽艙) ---
with main_left:
    st.markdown("### 📸 單據映像比對")
    
    if shop_name != "請選擇":
        
        # 建立隔離艙：只有這裡會背景重新整理
        @st.fragment
        def image_monitor_hub():
            current_room = global_rooms[room_id]
            
            # 💡 核心邏輯：如果兩張照片只要有任何一張「還是空的」，這個艙房每 4 秒就偷偷刷一次，直到照片進來為止
            if current_room["img_mall"] is None or current_room["img_cegid"] is None:
                from streamlit_autorefresh import st_autorefresh
                st_autorefresh(interval=4000, key="fragment_monitor_refresh")
            
            up_col1, up_col2 = st.columns(2)
            with up_col1:
                uploaded_mall = st.file_uploader("上傳百貨照片", type=["png", "jpg", "jpeg"], key="mall_file_key")
                if uploaded_mall:
                    current_room["img_mall"] = process_and_resize_image(uploaded_mall)
                    st.rerun()
            with up_col2:
                uploaded_cegid = st.file_uploader("上傳 Cegid 照片", type=["png", "jpg", "jpeg"], key="cegid_file_key")
                if uploaded_cegid:
                    current_room["img_cegid"] = process_and_resize_image(uploaded_cegid)
                    st.rerun()
                    
            st.write(" ")
            
            # 🔔 通知區：如果收到照片，立刻跳出優雅的 Aesop 綠色通知！
            if current_room["img_mall"] is not None and current_room["img_cegid"] is not None:
                st.markdown('<div class="aesop-success" style="margin-top:0px; margin-bottom:15px;">🔔 系統提示：手機端已成功同步上傳雙端單據，請開始比對金額。</div>', unsafe_allow_html=True)
            
            view_col1, view_col2 = st.columns(2)
            with view_col1:
                if current_room["img_mall"] is not None:
                    st.image(current_room["img_mall"], caption="MALL REPORT IMAGE", use_container_width=True)
                else:
                    st.markdown('<div class="aesop-info" style="font-size:0.85rem; text-align:center;">⏳ 靜待百貨單據上傳... (系統自動偵測中)</div>', unsafe_allow_html=True)
            with view_col2:
                if current_room["img_cegid"] is not None:
                    st.image(current_room["img_cegid"], caption="CEGID SYSTEM IMAGE", use_container_width=True)
                else:
                    st.markdown('<div class="aesop-info" style="font-size:0.85rem; text-align:center;">⏳ 靜待 Cegid 畫面截圖... (系統自動偵測中)</div>', unsafe_allow_html=True)

        # 啟動智慧艙
        image_monitor_hub()
        
    else:
        st.markdown('<div class="aesop-error">👈 請先於右側面板選擇【店鋪名稱】以開啟對帳作業。</div>', unsafe_allow_html=True)
