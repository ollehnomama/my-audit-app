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
