import streamlit as st
from PIL import Image

# 1. 網頁基本設定 (設定上傳檔案上限為 10MB)
st.set_page_config(
    page_title="即時對帳審核工具", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 透過 Streamlit 內建參數限制上傳檔案大小為 10MB (預設是 200MB)
# 注意：這行必須緊跟在 set_page_config 後面
st.config.set_option("server.maxUploadSize", 10)

st.markdown("""
    <style>
    .main { background-color: #FAF9F6; } /* 象牙白背景 */
    h1, h3 { color: #333333; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ 即時對帳與審核系統 (高畫質縮圖版)")
st.caption("隨用隨清 • 跨裝置同步 • 限制上傳最大 10MB • 自動等比例優化畫質")
st.write("---")

# 2. 建立全伺服器共享的臨時記憶置物櫃
@st.cache_resource
def get_global_rooms():
    return {}

global_rooms = get_global_rooms()

# 讓使用者選擇店鋪與日期，組合出臨時房間代碼
col_shop, col_date = st.columns(2)
with col_shop:
    shop_name = st.selectbox("1. 選擇店鋪", ["請選擇", "台北信義店", "台中中友店", "高雄漢神店", "南西誠品店"])
with col_date:
    target_date = st.date_input("2. 對帳日期")

room_id = f"{shop_name}_{target_date}"

# 智慧圖片等比例縮放函式
def process_and_resize_image(uploaded_file):
    img = Image.open(uploaded_file)
    # 如果圖片包含旋轉資訊，自動轉正
    try:
        img = ImageOps.exif_transpose(img)
    except:
        pass
    
    # 限制長邊最大 2000 像素，另一邊會等比例縮放，不會變形
    max_size = 2000
    width, height = img.size
    
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        # 使用高畫質濾鏡進行縮放
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img

# 如果選了店鋪，就初始化這個房間的共享記憶體
if shop_name != "請選擇":
    if room_id not in global_rooms:
        global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
    
    current_room = global_rooms[room_id]

    # 3. 圖片上傳區
    st.write("### 📸 步驟一：上傳對帳單據 (上限 10MB，自動調整尺寸)")
    img_col1, img_col2 = st.columns(2)
    
    with img_col1:
        st.markdown("**【百貨系統截圖 / 發票】**")
        if current_room["img_mall"] is not None:
            st.success("🟢 雲端已有百貨照片")
        
        uploaded_mall = st.file_uploader("選擇或拍攝百貨照片 (最大 10MB)", type=["png", "jpg", "jpeg"], key="mall_upload")
        if uploaded_mall:
            with st.spinner("正在優化圖片畫質..."):
                current_room["img_mall"] = process_and_resize_image(uploaded_mall)
            st.rerun()

    with img_col2:
        st.markdown("**【Cegid 系統截圖】**")
        if current_room["img_cegid"] is not None:
            st.success("🟢 雲端已有 Cegid 照片")
            
        uploaded_cegid = st.file_uploader("選擇或拍攝 Cegid 照片 (最大 10MB)", type=["png", "jpg", "jpeg"], key="cegid_upload")
        if uploaded_cegid:
            with st.spinner("正在優化圖片畫質..."):
                current_room["img_cegid"] = process_and_resize_image(uploaded_cegid)
            st.rerun()

    st.write("---")

    # 4. 對帳面板
    if current_room["img_mall"] or current_room["img_cegid"]:
        st.write("### 💻 步驟二：電腦對帳與金額判定")
        
        # 雙圖並排顯示
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            if current_room["img_mall"] is not None:
                st.image(current_room["img_mall"], caption="百貨單據 (智慧等比例優化)", use_container_width=True)
            else:
                st.info("⏳ 等待百貨照片上傳...")
        with view_col2:
            if current_room["img_cegid"] is not None:
                st.image(current_room["img_cegid"], caption="Cegid 畫面 (智慧等比例優化)", use_container_width=True)
            else:
                st.info("⏳ 等待 Cegid 照片上傳...")
        
        st.write(" ")
        
        # 金額輸入
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
                st.info("💡 提示：現在您可以直接對螢幕進行截圖歸檔。")
            else:
                st.error(f"❌ 金額不一致！帳差金額： {diff:,.0f} 元")
                diff_reason = st.text_area("⚠️ 請填寫帳差原因：", placeholder="例如：百貨刷卡手續費扣抵...")
                
                if diff_reason:
                    st.warning("⚠️ 已填寫帳差原因，請截圖此畫面留存。")
        
        # 徹底銷毀按鈕
        st.write(" ")
        if st.button("🗑️ 徹底清除此店鋪今日雲端暫存 (對帳完請點此銷毀資料)"):
            global_rooms[room_id] = {"img_mall": None, "img_cegid": None}
            st.rerun()
            
    else:
        st.info("ℹ️ 等待單據上傳中... 請在上方分別上傳「百貨」與「Cegid」兩張照片。")
else:
    st.warning("👈 請先在上方選擇【店鋪名稱】以開啟專屬對帳房間。")
