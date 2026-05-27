import streamlit as st
from PIL import Image, ImageOps
from streamlit_autorefresh import st_autorefresh

# 1. 網頁基本設定
st.set_page_config(
    page_title="Aesop Style Audit Tool", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.config.set_option("server.maxUploadSize", 10)
st_autorefresh(interval=3000, key="reconciliation_refresh")

# Aesop 視覺風格 CSS
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
    .upload-tip {
        font-size: 0.8rem;
        color: #8E765D;
        letter-spacing: 0.03em;
        margin-top: 4px;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Aesop — 零售對帳與審核單元")
st.markdown("<p style='letter-spacing:0.05em; color:#666666; font-size:0.9rem;'>ELEGANT REAL-TIME RECONCILIATION • PILOT VERSION</p>", unsafe_allow_html=True)
st.write(" ")

@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()

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

# 左右並排排版
main_left, main_right = st.columns([6, 4])

# --- 右半邊：對帳主控台 ---
with main_right:
    st.markdown("### 🔍 填寫對帳範疇")
    
    col_shop, col_date = st.columns(2)
    with col_shop:
        shop_name = st.selectbox("選擇指定店鋪", ["請選擇", "台北信義店", "台中中友店", "高雄漢神店", "南西誠品店"])
    with col_date:
        target_date = st.date_input("選擇對帳日期")

    room_id = f"{shop_name}_{target_date}"

    if shop_name != "請選擇":
        if room_id not in global_rooms:
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
        current_room = global_rooms[room_id]
        
        st.write(" ")
        st.markdown("### 💰 輸入系統金額")
        fee_col1, fee_col2 = st.columns(2)
        with fee_col1:
            mall_amount = st.number_input("百貨報表金額 (TWD)", min_value=0, step=1, value=0)
        with fee_col2:
            cegid_amount = st.number_input("Cegid 系統金額 (TWD)", min_value=0, step=1, value=0)
            
        if mall_amount > 0 or cegid_amount > 0:
            diff = mall_amount - cegid_amount
            if diff == 0:
                st.markdown(f'<div class="aesop-success">✅ 金額完全相符。此案准予結案，請進行螢幕截圖。</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="aesop-error">❌ 偵測到帳面誤差。目前差額： {diff:,.0f} 元</div>', unsafe_allow_html=True)
                diff_reason = st.text_area("請闡述帳差原因 (必要填寫)", placeholder="例如：百貨刷卡手續費扣抵...")
                if diff_reason:
                    st.markdown(f'<div class="aesop-success">⚠️ 帳差原因已載入。請直接截圖此畫面存檔。</div>', unsafe_allow_html=True)
        
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ 徹底清除此店鋪今日雲端暫存"):
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
            st.rerun()

# --- 左半邊：單據比對區 ---
with main_left:
    st.markdown("### 📸 單據映像比對")
    
    if shop_name != "請選擇":
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            uploaded_mall = st.file_uploader("上傳百貨照片 (最大 10MB)", type=["png", "jpg", "jpeg"], key="mall_upload")
            # 💡 貼心優化：加上手機端壓縮上傳的提示文字
            st.markdown('<p class="upload-tip">💡 貼心提示：若手機拍照上傳較慢，可改用「手機螢幕截圖」上傳，傳輸速度可提升 10 倍且依然清晰。</p>', unsafe_allow_html=True)
            if uploaded_mall:
                current_room["img_mall"] = process_and_resize_image(uploaded_mall)
                st.rerun()
        with up_col2:
            uploaded_cegid = st.file_uploader("上傳 Cegid 照片 (最大 10MB)", type=["png", "jpg", "jpeg"], key="cegid_upload")
            st.markdown('<p class="upload-tip">💡 貼心提示：系統畫面建議直接使用電腦或手機截圖上傳，檔案小且對齊效果最佳。</p>', unsafe_allow_html=True)
            if uploaded_cegid:
                current_room["img_cegid"] = process_and_resize_image(uploaded_cegid)
                st.rerun()
                
        st.write(" ")
        
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            if current_room["img_mall"] is not None:
                st.image(current_room["img_mall"], caption="MALL REPORT IMAGE", use_container_width=True)
            else:
                st.markdown('<div class="aesop-info" style="font-size:0.85rem; text-align:center;">⏳ 靜待百貨單據上傳</div>', unsafe_allow_html=True)
        with view_col2:
            if current_room["img_cegid"] is not None:
                st.image(current_room["img_cegid"], caption="CEGID SYSTEM IMAGE", use_container_width=True)
            else:
                st.markdown('<div class="aesop-info" style="font-size:0.85rem; text-align:center;">⏳ 靜待 Cegid 畫面截圖</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="aesop-error">👈 請先於右側面板選擇【店鋪名稱】以開啟對帳作業。</div>', unsafe_allow_html=True)
