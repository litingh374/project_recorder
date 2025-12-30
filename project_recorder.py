import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- 設定頁面資訊 ---
st.set_page_config(
    page_title="營造專案詳細管理系統 v2.0", 
    layout="wide",
    page_icon="🏗️"
)

# 資料庫與圖片設定
DB_FILE = "construction_project_db_v2.csv"
IMG_DIR = "project_images"

# 確保圖片資料夾存在
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- 核心功能函式 ---

def load_data():
    """讀取資料庫"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # 定義所有欄位
        columns = [
            "登錄時間", "標案名稱", "文件編號版本", "業主", "建築事務所", 
            "人力配置", "拆除計畫簡述",
            "結構型式", "樓層規劃", "樓層高度",
            "開挖深度", "開挖工法", "支撐層數", "連續壁規格", "基樁規格", "取土口數量",
            "塔吊規格", "施工電梯(品牌/大小)", "施工大門(大小/數量)",
            "進度表圖檔", "備註"
        ]
        return pd.DataFrame(columns=columns)

def save_entry(data_dict, uploaded_file):
    """儲存資料與圖片"""
    # 處理圖片儲存
    img_filename = ""
    if uploaded_file is not None:
        # 為了避免檔名重複，加上時間戳記
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_filename = f"{timestamp}_{uploaded_file.name}"
        save_path = os.path.join(IMG_DIR, img_filename)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        data_dict["進度表圖檔"] = img_filename
    else:
        data_dict["進度表圖檔"] = "無"

    # 儲存 CSV
    df = load_data()
    new_entry = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)
    return updated_df

def convert_df_to_excel(df):
    """
    將 DataFrame 轉為設計過的 Excel (使用 XlsxWriter 引擎)
    """
    # 輸出到記憶體中的 BytesIO 物件，而非實體檔案，方便 Streamlit 下載
    from io import BytesIO
    output = BytesIO()
    
    # 使用 ExcelWriter 進行格式化
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='專案總表')
        
        workbook = writer.book
        worksheet = writer.sheets['專案總表']
        
        # 定義格式
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC', # 淺綠色背景
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # 套用格式到標題列
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # 設定欄寬 (根據內容長度稍微調整，或設固定寬度)
        worksheet.set_column('A:A', 20) # 時間
        worksheet.set_column('B:B', 30) # 標案名稱 (寬一點)
        worksheet.set_column('C:G', 15) # 一般欄位
        worksheet.set_column('H:Z', 20) # 後面技術欄位
        worksheet.set_column('U:U', 40) # 備註 (最寬)

    return output.getvalue()

# --- 介面設計 ---

st.title("🏗️ 營造專案詳細管理系統 v2.0")
st.caption("新增欄位：文件版次、人力、塔吊電梯、拆除計畫、進度表圖面")
st.markdown("---")

tab1, tab2 = st.tabs(["📝 新增詳細資料", "📂 檢視與匯出報表"])

with tab1:
    with st.form("full_spec_form", clear_on_submit=True):
        
        # 區塊 1: 專案管理基礎
        st.subheader("1. 專案管理基礎資訊")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input("標案名稱", placeholder="必填")
        with col2:
            doc_ver = st.text_input("文件編號/版本", placeholder="例：P-2023-001 v1.0")
        with col3:
            manpower = st.text_input("人力配置", placeholder="例：主任1/工務2/職安1")
        with col4:
            owner = st.text_input("業主", placeholder="建設公司/機關")

        # 區塊 2: 建築與拆除
        st.markdown("---")
        st.subheader("2. 建築結構與拆除計畫")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            struct_type = st.text_input("結構型式", placeholder="例：SRC造")
            demo_plan = st.text_area("拆除計畫相關", placeholder="例：舊有3層透天拆除，需鄰房保護", height=100)
        with col_b2:
            floors = st.text_input("樓層規劃", placeholder="例：B5 / 24F")
        with col_b3:
            floor_height = st.text_input("樓層高度", placeholder="例：1F 6m / 標準 3.4m")

        # 區塊 3: 大地工程 (開挖/支撐/取土)
        st.markdown("---")
        st.subheader("3. 大地工程細節")
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            excav_depth = st.text_input("開挖深度", placeholder="例：21.5 m")
            excav_method = st.text_input("開挖工法", placeholder="例：逆打 / 順打")
            soil_opening = st.text_input("取土口數量", placeholder="例：2處 (A區/B區)")
        with col_g2:
            wall_spec = st.text_input("連續壁規格", placeholder="例：100cm / 45m")
            strut_level = st.text_input("支撐層數", placeholder="例：5層 (H350x350)")
        with col_g3:
            pile_spec = st.text_input("基樁規格", placeholder="例：反循環 D200 L50m")

        # 區塊 4: 假設工程 (塔吊/電梯/大門)
        st.markdown("---")
        st.subheader("4. 假設工程配置")
        col_eq1, col_eq2, col_eq3 = st.columns(3)
        with col_eq1:
            tower_crane = st.text_input("塔吊規格", placeholder="例：Jaso J300 (45m臂長)")
        with col_eq2:
            elevator = st.text_input("施工電梯品牌/大小", placeholder="例：GEDA 載重2頓 雙籠")
        with col_eq3:
            gate = st.text_input("施工大門大小/數量", placeholder="例：8m寬 x 2處 (大安路/巷口)")

        # 區塊 5: 附件與備註
        st.markdown("---")
        col_final1, col_final2 = st.columns([1, 2])
        with col_final1:
            st.markdown("**上傳進度表圖面**")
            uploaded_img = st.file_uploader("選擇圖片 (jpg/png)", type=['png', 'jpg', 'jpeg'])
        with col_final2:
            note = st.text_area("備註", placeholder="其他補充事項...")

        submitted = st.form_submit_button("💾 儲存完整專案資料")

        if submitted:
            if name:
                entry_data = {
                    "登錄時間": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "標案名稱": name,
                    "文件編號版本": doc_ver,
                    "業主": owner,
                    "建築事務所": "", # 這裡可以視需求加回輸入框
                    "人力配置": manpower,
                    "拆除計畫簡述": demo_plan,
                    "結構型式": struct_type,
                    "樓層規劃": floors,
                    "樓層高度": floor_height,
                    "開挖深度": excav_depth,
                    "開挖工法": excav_method,
                    "支撐層數": strut_level,
                    "連續壁規格": wall_spec,
                    "基樁規格": pile_spec,
                    "取土口數量": soil_opening,
                    "塔吊規格": tower_crane,
                    "施工電梯(品牌/大小)": elevator,
                    "施工大門(大小/數量)": gate,
                    "備註": note
                }
                save_entry(entry_data, uploaded_img)
                st.success(f"已成功建立專案：{name}")
            else:
                st.error("請輸入標案名稱！")

with tab2:
    st.subheader("📊 專案資料列表")
    df = load_data()
    
    if not df.empty:
        # 1. 顯示 DataFrame
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 2. 圖片預覽功能
        st.markdown("### 🖼️ 進度表預覽")
        selected_project = st.selectbox("選擇要查看圖面的專案", df["標案名稱"].unique())
        
        if selected_project:
            # 找到該專案的圖片檔名
            project_row = df[df["標案名稱"] == selected_project].iloc[0]
            img_name = project_row["進度表圖檔"]
            
            if img_name != "無" and pd.notna(img_name):
                img_path = os.path.join(IMG_DIR, img_name)
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=f"{selected_project} - 進度表", width=600)
                else:
                    st.warning("⚠️ 找不到圖檔 (可能已被刪除)")
            else:
                st.info("此專案未上傳進度表圖片")

        st.markdown("---")
        
        # 3. 匯出 Excel
        excel_data = convert_df_to_excel(df)
        
        st.download_button(
            label="📥 下載 Excel 報表 (設計版)",
            data=excel_data,
            file_name='construction_projects_full.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        st.caption("說明：匯出的 Excel 已包含格式排版。圖片檔案較大，不直接嵌入 Excel，請對照上方的「進度表圖檔」檔名至 images 資料夾查看。")
        
    else:
        st.info("目前無資料，請至「新增詳細資料」分頁建立。")