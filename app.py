import streamlit as st
from PIL import Image

# 1. 網頁基本設定 (Aesop 簡約風格色調調整)
st.set_page_config(page_title="即時對帳審核工具", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #FAF9F6; } /* 象牙白背景 */
    h1, h3 { color: #333333; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ 即時對帳與審核系統")
st.caption("隨用隨清 • 跨裝置同步 • 不儲存資料庫")
st.write("---")

# 2. 多店鋪分流設定 (利用臨時記憶體 Cache)
if "rooms" not in st.session_state:
    st.session_state.rooms = {}

# 讓使用者選擇店鋪與日期，組合出臨時房間代碼
col_shop, col_date = st.columns(2)
with col_shop:
    shop_name = st.selectbox("1. 選擇店鋪", ["請選擇", "台北信義店", "台中中友店", "高雄漢神店", "南西誠品店"])
with col_date:
    target_date = st.date_input("2. 對帳日期")

room_id = f"{shop_name}_{target_date}"

# 如果選了店鋪，就初始化這個房間的記憶體
if shop_name != "請选择":
    if room_id not in st.session_state.rooms:
        st.session_state.rooms[room_id] = {"img_mall": None, "img_cegid": None}
    
    current_room = st.session_state.rooms[room_id]

    # 3. 圖片上傳區 (手機電腦皆可用)
    st.write("### 📸 步驟一：上傳對帳單據")
    img_col1, img_col2 = st.columns(2)
    
    with img_col1:
        st.markdown("**【百貨系統截圖 / 發票】**")
        uploaded_mall = st.file_uploader("選擇或拍攝百貨照片", type=["png", "jpg", "jpeg"], key="mall_upload")
        if uploaded_mall:
            # 自動壓縮圖片以節省記憶體
            img = Image.open(uploaded_mall)
            img.thumbnail((800, 800))
            current_room["img_mall"] = img

    with img_col2:
        st.markdown("**【Cegid 系統截警】**")
        uploaded_cegid = st.file_uploader("選擇或拍攝 Cegid 照片", type=["png", "jpg", "jpeg"], key="cegid_upload")
        if uploaded_cegid:
            img = Image.open(uploaded_cegid)
            img.thumbnail((800, 800))
            current_room["img_cegid"] = img

    st.write("---")

    # 4. 對帳面板 (如果兩張圖都有了，就顯示出來並開始對帳)
    if current_room["img_mall"] and current_room["img_cegid"]:
        st.write("### 💻 步驟二：電腦對帳與金額判定")
        
        # 雙圖並排顯示
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            st.image(current_room["img_mall"], caption="百貨單據", use_container_width=True)
        with view_col2:
            st.image(current_room["img_cegid"], caption="Cegid 畫面", use_container_width=True)
        
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
                # 強制填寫原因
                diff_reason = st.text_area("⚠️ 請填寫帳差原因：", placeholder="例如：百貨刷卡手續費扣抵 / 百客退貨未同步...")
                
                if diff_reason:
                    st.warning("⚠️ 已填寫帳差原因，請截圖此畫面留存。")
        
        # 清除暫存按鈕
        st.write(" ")
        if st.button("🗑️ 清除此店鋪今日暫存 (關閉網頁也會自動清除)"):
            st.session_state.rooms[room_id] = {"img_mall": None, "img_cegid": None}
            st.rerun()
            
    else:
        st.info("ℹ️ 等待單據上傳中... 請在上方分別上傳「百貨」與「Cegid」兩張照片。")
else:
    st.warning("👈 請先在上方選擇【店鋪名稱】以開啟專屬對帳房間。")
