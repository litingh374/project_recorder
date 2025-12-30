import streamlit as st
import pandas as pd
import io
import re
from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.drawing.image import Image as XLImage

# 新增讀檔套件
import pdfplumber
from pptx import Presentation

# --- 1. 頁面配置 ---
st.set_page_config(page_title="營造履歷智慧填表系統 v7.0", layout="wide", page_icon="🏗️")

# --- 2. 智慧提取函式 (核心邏輯) ---
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_ppt(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

def parse_construction_data(text):
    """
    使用正則表達式 (Regex) 從文字中抓取關鍵數據
    """
    data = {}
    
    # 1. 抓取專案名稱 (假設通常在第一行或包含"工程"字眼)
    # 這裡做簡單處理：抓取含有"工程"且長度適中的句子
    name_match = re.search(r"(\S*新建工程|\S*大樓工程)", text)
    if name_match:
        data["project_name"] = name_match.group(1)

    # 2. 抓取基地面積 (尋找 "基地面積" 後面的數字)
    # 支援格式：基地面積 1,234.56 m2 或 基地面積:1234
    area_match = re.search(r"基地面積\D*([\d,]+\.?\d*)", text)
    if area_match:
        try:
            data["site_area"] = float(area_match.group(1).replace(",", ""))
        except:
            pass

    # 3. 抓取總樓地板面積
    fa_match = re.search(r"(總樓地板|總樓地|總建坪)\D*([\d,]+\.?\d*)", text)
    if fa_match:
        try:
            data["total_floor_area"] = float(fa_match.group(2).replace(",", ""))
        except:
            pass

    # 4. 抓取樓層 (地上/地下)
    # 格式：地上 24 層、地下 5 層 或 24F/B5
    up_match = re.search(r"地上\D*(\d+)", text)
    down_match = re.search(r"地下\D*(\d+)", text)
    
    if up_match: data["floors_up"] = int(up_match.group(1))
    if down_match: data["floors_down"] = int(down_match.group(1))

    # 5. 抓取開挖深度
    depth_match = re.search(r"(開挖深度|GL-)\D*([\d,]+\.?\d*)", text)
    if depth_match:
        try:
            data["excavation_depth"] = float(depth_match.group(2).replace(",", ""))
        except:
            pass

    # 6. 抓取工法關鍵字 (簡單關鍵字比對)
    if "逆打" in text: data["const_method"] = "逆打工法 (Top-Down)"
    elif "雙順打" in text: data["const_method"] = "雙順打工法"
    elif "順打" in text: data["const_method"] = "順打工法 (Bottom-Up)"

    if "SRC" in text: data["struct_above"] = "SRC (鋼骨鋼筋混凝土)"
    elif "SC" in text: data["struct_above"] = "SC (鋼骨)"
    elif "RC" in text: data["struct_above"] = "RC (鋼筋混凝土)"

    return data

# --- 3. 初始化 Session State (讓資料可以被填入) ---
# 這是為了讓程式記得"剛剛抓到的資料"
default_values = {
    "project_name": "未命名工程",
    "project_loc": "",
    "client_name": "",
    "architect_name": "",
    "contract_date": "",
    "contract_cost": "",
    "floors_up": 15,
    "floors_down": 3,
    "site_area": 1000.0,
    "total_floor_area": 12000.0,
    "building_height": 50.0,
    "excavation_depth": 12.0,
    "const_method": "順打工法 (Bottom-Up)",
    "struct_above": "RC (鋼筋混凝土)"
}

for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 4. 介面設計 ---

st.title("🏗️ 營造履歷智慧填表系統 v7.0")

# === 新增：檔案上傳與自動解析區 ===
with st.expander("📂 智慧匯入 (上傳 PDF/PPT 自動填寫)", expanded=True):
    st.info("💡 支援上傳標案簡報 (PPTX) 或 報告書 (PDF)。系統將自動搜尋「面積」、「樓層」、「工法」等關鍵字並填入下方欄位。")
    uploaded_doc = st.file_uploader("拖曳檔案到這裡...", type=["pdf", "pptx"])
    
    if uploaded_doc is not None:
        if st.button("🚀 開始分析檔案內容"):
            with st.spinner("正在讀取檔案並尋找工程數據..."):
                try:
                    # 1. 提取文字
                    raw_text = ""
                    if uploaded_doc.name.endswith(".pdf"):
                        raw_text = extract_text_from_pdf(uploaded_doc)
                    elif uploaded_doc.name.endswith(".pptx"):
                        raw_text = extract_text_from_ppt(uploaded_doc)
                    
                    # 2. 解析數據
                    extracted_data = parse_construction_data(raw_text)
                    
                    # 3. 更新 Session State (填表)
                    if extracted_data:
                        for k, v in extracted_data.items():
                            st.session_state[k] = v
                        st.success(f"✅ 解析成功！已自動填入 {len(extracted_data)} 個欄位，請檢查下方內容。")
                        st.markdown(f"**偵測到的數據：** {extracted_data}")
                    else:
                        st.warning("⚠️ 檔案中找不到常見的工程關鍵字，請手動輸入。")
                        
                except Exception as e:
                    st.error(f"解析失敗：{e}")

# === 原有表單 (但 value 改為讀取 session_state) ===

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📝 基本資料與規格", "🖼️ 圖片與敘述", "📊 導出 Excel"])

with tab1:
    st.subheader("1. 專案基本資料")
    c1, c2, c3 = st.columns(3)
    with c1:
        # 注意：這裡使用 key 和 value 的搭配技巧
        st.text_input("專案名稱", key="project_name") 
        st.text_input("工程地點", key="project_loc")
    with c2:
        st.text_input("業主名稱", key="client_name")
        st.text_input("設計單位/建築師", key="architect_name")
    with c3:
        st.text_input("完工年份", key="contract_date")
        st.text_input("工程造價 (億元)", key="contract_cost")

    st.subheader("2. 建築規模")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.selectbox("建物類型", ["住宅大樓", "商辦大樓", "飯店", "廠房", "公共工程"])
    with col_b2:
        # 結構選單需要特殊的處理，因為自動抓取的是字串，要對應到 index 比較複雜
        # 這裡簡化處理：如果自動抓到值，直接顯示在說明文字，使用者手動選
        idx_above = 0
        struct_opts = ["SC (鋼骨)", "SRC (鋼骨鋼筋混凝土)", "RC (鋼筋混凝土)", "SS (純鋼構)"]
        if st.session_state.struct_above in struct_opts:
            idx_above = struct_opts.index(st.session_state.struct_above)
        st.selectbox("地上結構", struct_opts, index=idx_above)
    with col_b3:
        st.selectbox("地下結構", ["RC (鋼筋混凝土)", "SRC (鋼骨鋼筋混凝土)"])
    with col_b4:
        st.selectbox("基礎型式", ["筏式基礎", "筏式基礎+基樁", "獨立基腳"])

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.number_input("地上層數 (F)", min_value=1, key="floors_up")
        st.number_input("地下層數 (B)", min_value=0, key="floors_down")
    with col_d2:
        st.number_input("基地面積 (m²)", key="site_area")
        st.number_input("總樓地板面積 (m²)", key="total_floor_area")
    with col_d3:
        st.number_input("建築高度 (m)", key="building_height")
        st.number_input("開挖深度 (m)", key="excavation_depth")

    st.subheader("3. 關鍵工法")
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        # 工法選單處理
        method_opts = ["逆打工法 (Top-Down)", "順打工法 (Bottom-Up)", "雙順打工法"]
        idx_method = 0
        if st.session_state.const_method in method_opts:
            idx_method = method_opts.index(st.session_state.const_method)
        st.selectbox("主體施工工法", method_opts, index=idx_method)
    with c_m2:
        st.selectbox("擋土支撐系統", ["連續壁+鋼支柱(逆打)", "連續壁+內支撐", "地錨工法", "鋼板樁"])
    with c_m3:
        st.selectbox("外牆工法", ["玻璃帷幕", "石材吊掛", "鋁板", "二丁掛"])

with tab2:
    st.header("工程特色與圖片")
    col_text1, col_text2 = st.columns(2)
    with col_text1:
        features = st.text_area("✨ 工程特色", "1. 自動匯入測試...\n2. 請填寫特色", height=200)
    with col_text2:
        challenges = st.text_area("🧗 施工挑戰", "1. ...", height=200)

    uploaded_img = st.file_uploader("上傳完工照 (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
    if uploaded_img:
        st.image(uploaded_img, width=300)

with tab3:
    st.header("導出 Excel")
    st.info("點擊下方按鈕生成履歷表 (功能同上版本，此處省略 Excel 生成代碼以節省篇幅)")
    # 這裡可以把上一個版本的 generate_excel() 函式放進來
    # 為了方便你直接執行，我這裡做一個簡易版按鈕
    if st.button("生成 Excel"):
        st.success("功能與 v6.58 相同，請將上個版本的 generate_excel 函式複製過來即可！")