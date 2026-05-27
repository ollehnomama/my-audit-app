import streamlit as st
from PIL import Image, ImageOps

# 1. 網頁基本設定 (設定為寬螢幕模式)
st.set_page_config(
    page_title="即時對帳審核工具", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 限制上傳檔案大小為 10MB
st.config.set_option("server.maxUploadSize", 10)

# Aesop 極簡風格 CSS
st.markdown("""
    <style>
    .main { background-color: #FAF9F6; } /* 象牙白背景 */
    h1, h3 { color: #333333; font-family: sans-serif; }
    /* 讓上傳小工具的排版稍微緊湊一點 */
    .stFileUploader { padding-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ 即時對帳與審核系統")
st.caption("隨用隨清 • 左右並排完美截圖版")
st.write("---")

# 2. 全伺服器共享的臨時記憶置物櫃
@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()

# 智慧圖片等比例縮放函式 (限制長邊 2000 像素)
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

# 🛠️ 核心改版：建立網頁的「左、右」兩大區塊
# 左邊佔 60% 空間放照片，右邊佔 40% 空間放控制台與金額
main_left, main_right = st.columns([6, 4])

# --- 右半邊：控制台與金額輸入 (永遠在最上方) ---
with main_right:
    st.write("### ⚙️ 對帳資訊輸入")
    
    # 讓店鋪與日期並排在右側上方
    col_shop, col_date = st.columns(2)
    with col_shop:
        shop_name = st.selectbox("選擇店鋪", ["請選擇", "台北信義店", "台中中友店", "高雄漢神店", "南西誠品店"])
    with col_date:
        target_date = st.date_input("對帳日期")

    room_id = f"{shop_name}_{target_date}"

    # 只有在選了店鋪後，才顯示金額輸入與判定
    if shop_name != "請選擇":
        if room_id not in global_rooms:
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
        current_room = global_rooms[room_id]
        
        st.write(" ")
        st.write("### 💰 金額判定")
        fee_col1, fee_col2 = st.columns(2)
        with fee_col1:
            mall_amount = st.number_input("百貨金額 (TWD)", min_value=0, step=1, value=0)
        with fee_col2:
            cegid_amount = st.number_input("Cegid 金額 (TWD)", min_value=0, step=1, value=0)
            
        # 核心防呆判定邏輯
        if mall_amount > 0 or cegid_amount > 0:
            diff = mall_amount - cegid_amount
            
            if diff == 0:
                st.success("✅ 金額完全相符！准予結案。")
            else:
                st.error(f"❌ 帳差金額： {diff:,.0f} 元")
                diff_reason = st.text_area("⚠️ 請填寫帳差原因：", placeholder="例如：百貨刷卡手續費扣抵...")
        
        # 徹底銷毀按鈕
        st.write(" ")
        if st.button("🗑️ 徹底清除此店鋪今日雲端暫存"):
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
            st.rerun()

# --- 左半邊：上傳區與雙圖並排顯示 ---
with main_left:
    st.write("### 📸 單據比對區")
    
    if shop_name != "請選擇":
        # 上傳按鈕並排
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            uploaded_mall = st.file_uploader("百貨照片 (最大 10MB)", type=["png", "jpg", "jpeg"], key="mall_upload")
            if uploaded_mall:
                current_room["img_mall"] = process_and_resize_image(uploaded_mall)
                st.rerun()
        with up_col2:
            uploaded_cegid = st.file_uploader("Cegid 照片 (最大 10MB)", type=["png", "jpg", "jpeg"], key="cegid_upload")
            if uploaded_cegid:
                current_room["img_cegid"] = process_and_resize_image(uploaded_cegid)
                st.rerun()
                
        st.write("---")
        
        # 顯示圖片並排
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            if current_room["img_mall"] is not None:
                st.image(current_room["img_mall"], caption="百貨單據", use_container_width=True)
            else:
                st.info("⏳ 等待百貨照片...")
        with view_col2:
            if current_room["img_cegid"] is not None:
                st.image(current_room["img_cegid"], caption="Cegid 畫面", use_container_width=True)
            else:
                st.info("⏳ 等待 Cegid 照片...")
    else:
        st.warning("👈 請先在右側選擇【店鋪名稱】以開啟對帳房間。")
