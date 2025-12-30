import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 設定頁面資訊 ---
st.set_page_config(
    page_title="營造專案詳細管理系統 v3.0", 
    layout="wide",
    page_icon="🏗️"
)

# 資料庫與圖片設定
DB_FILE = "construction_project_db_v3.csv"
IMG_DIR = "project_images"

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- 核心功能函式 ---

def load_data():
    """讀取資料庫"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # 定義所有詳細欄位
        columns = [
            "登錄時間", "標案名稱", "文件編號版本", "業主", "建築事務所", 
            "人力配置", "拆除計畫簡述",
            # 面積相關
            "基地面積(m2)", "建築面積(m2)", "總樓地板面積(m2)",
            # 樓層層數
            "地下室層數", "地上樓層數", "屋突層數",
            # 樓層高度
            "地下室高度總和(m)", "地上樓層高度總和(m)", "屋突高度總和(m)",
            # 結構與基礎
            "結構型式", "外牆型式", "筏基深度(m)", "筏基版厚(cm)",
            # 大地工程
            "開挖深度", "開挖工法", "支撐層數", "取土口數量",
            "連續壁規格(彙整)", "基樁規格",
            # 假設工程
            "塔吊規格", "施工電梯", "施工大門",
            "進度表圖檔", "備註"
        ]
        return pd.DataFrame(columns=columns)

def save_entry(data_dict, uploaded_file):
    """儲存資料與圖片"""
    img_filename = ""
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_filename = f"{timestamp}_{uploaded_file.name}"
        save_path = os.path.join(IMG_DIR, img_filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        data_dict["進度表圖檔"] = img_filename
    else:
        data_dict["進度表圖檔"] = "無"

    df = load_data()
    new_entry = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)
    return updated_df

def convert_df_to_excel(df):
    """將 DataFrame 轉為精美排版的 Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='專案總表')
        workbook = writer.book
        worksheet = writer.sheets['專案總表']
        
        # 格式設定
        header_format = workbook.add_format({
            'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center',
            'fg_color': '#4F81BD', 'font_color': 'white', 'border': 1
        })
        cell_format = workbook.add_format({
            'text_wrap': True, 'valign': 'top', 'border': 1
        })
        
        # 套用格式
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            # 設定預設欄寬
            worksheet.set_column(col_num, col_num, 15, cell_format)

        # 特別調整特定欄位寬度
        worksheet.set_column('B:B', 25) # 標案名稱
        worksheet.set_column('Y:Y', 35) # 連續壁規格 (因為內容多，設寬一點)
        worksheet.set_column('AE:AE', 40) # 備註

    return output.getvalue()

# --- 介面設計 ---

st.title("🏗️ 營造專案詳細管理系統 v3.0")
st.markdown("針對工期計算與詳細規格設計的進階版本")

tab1, tab2 = st.tabs(["📝 新增詳細資料", "📂 檢視與匯出報表"])

with tab1:
    with st.form("full_spec_form_v3", clear_on_submit=True):
        
        st.markdown("### 1. 專案基本與面積")
        c1, c2, c3, c4 = st.columns(4)
        with c1: name = st.text_input("標案名稱", placeholder="必填")
        with c2: doc_ver = st.text_input("文件編號/版本")
        with c3: owner = st.text_input("業主")
        with c4: architect = st.text_input("建築事務所")

        c_area1, c_area2, c_area3 = st.columns(3)
        with c_area1: area_base = st.text_input("基地面積 (m²)")
        with c_area2: area_build = st.text_input("建築面積 (m²)")
        with c_area3: area_total = st.text_input("總樓地板面積 (m²)")

        st.markdown("---")
        st.markdown("### 2. 樓層與高度規劃")
        st.caption("請分別輸入層數與高度數據")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1: 
            st.markdown("**地下室 (Basement)**")
            f_b_count = st.text_input("地下室層數", placeholder="例：B5")
            f_b_height = st.text_input("地下室高度總和 (m)")
        with col_f2:
            st.markdown("**地上層 (Floor)**")
            f_f_count = st.text_input("地上樓層數", placeholder="例：24F")
            f_f_height = st.text_input("地上高度總和 (m)")
        with col_f3:
            st.markdown("**屋突 (Roof)**")
            f_r_count = st.text_input("屋突層數", placeholder="例：R3")
            f_r_height = st.text_input("屋突高度總和 (m)")

        st.markdown("---")
        st.markdown("### 3. 結構與基礎")
        col_st1, col_st2, col_st3, col_st4 = st.columns(4)
        with col_st1: struct_type = st.text_input("結構型式", placeholder="SRC/RC/SC")
        with col_st2: wall_type = st.text_input("外牆型式", placeholder="石材/帷幕/二丁掛")
        with col_st3: raft_depth = st.text_input("筏基深度 (m)")
        with col_st4: raft_thick = st.text_input("筏基版厚 (cm)")

        st.markdown("---")
        st.markdown("### 4. 大地工程 (連續壁可多行輸入)")
        
        # 特別設計：連續壁多行輸入區
        dw_specs = st.text_area("連續壁規格 (請換行輸入不同單元)", 
                                height=100,
                                placeholder="例：\n第一單元厚100cm 深45m\n扶壁厚80cm 深30m")
        
        col_geo1, col_geo2, col_geo3, col_geo4 = st.columns(4)
        with col_geo1: excav_depth = st.text_input("開挖深度 (m)")
        with col_geo2: excav_method = st.text_input("開挖工法", placeholder="順打/逆打")
        with col_geo3: strut_level = st.text_input("支撐層數")
        with col_geo4: soil_opening = st.text_input("取土口數量")
        
        pile_spec = st.text_input("基樁規格", placeholder="說明樁徑與長度")

        st.markdown("---")
        st.markdown("### 5. 假設工程與其他")
        col_eq1, col_eq2, col_eq3 = st.columns(3)
        with col_eq1: tower_crane = st.text_input("塔吊規格")
        with col_eq2: elevator = st.text_input("施工電梯 (品牌/大小)")
        with col_eq3: gate = st.text_input("施工大門 (大小/數量)")
        
        c_ot1, c_ot2 = st.columns(2)
        with c_ot1: manpower = st.text_input("人力配置")
        with c_ot2: demo_plan = st.text_input("拆除計畫相關")

        st.markdown("---")
        col_img, col_note = st.columns([1, 2])
        with col_img: uploaded_img = st.file_uploader("上傳進度表/配置圖", type=['png', 'jpg', 'jpeg'])
        with col_note: note = st.text_area("備註事項")

        submitted = st.form_submit_button("💾 儲存專案資料 v3")

        if submitted:
            if name:
                entry = {
                    "登錄時間": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "標案名稱": name,
                    "文件編號版本": doc_ver,
                    "業主": owner,
                    "建築事務所": architect,
                    "基地面積(m2)": area_base,
                    "建築面積(m2)": area_build,
                    "總樓地板面積(m2)": area_total,
                    "地下室層數": f_b_count,
                    "地上樓層數": f_f_count,
                    "屋突層數": f_r_count,
                    "地下室高度總和(m)": f_b_height,
                    "地上樓層高度總和(m)": f_f_height,
                    "屋突高度總和(m)": f_r_height,
                    "結構型式": struct_type,
                    "外牆型式": wall_type,
                    "筏基深度(m)": raft_depth,
                    "筏基版厚(cm)": raft_thick,
                    "連續壁規格(彙整)": dw_specs, # 這裡存入多行文字
                    "開挖深度": excav_depth,
                    "開挖工法": excav_method,
                    "支撐層數": strut_level,
                    "取土口數量": soil_opening,
                    "基樁規格": pile_spec,
                    "塔吊規格": tower_crane,
                    "施工電梯": elevator,
                    "施工大門": gate,
                    "人力配置": manpower,
                    "拆除計畫相關": demo_plan,
                    "備註": note
                }
                save_entry(entry, uploaded_img)
                st.success(f"資料已儲存！專案：{name}")
            else:
                st.error("請輸入標案名稱")

with tab2:
    st.subheader("📊 專案總表")
    df = load_data()
    
    if not df.empty:
        # 顯示表格
        st.dataframe(df, use_container_width=True)
        
        # 產生 Excel 下載按鈕
        st.markdown("### 📥 報表輸出")
        excel_data = convert_df_to_excel(df)
        
        st.download_button(
            label="下載 Excel 報表 (包含所有欄位)",
            data=excel_data,
            file_name='Project_Report_v3.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        
        # 圖片檢視區 (保持不變)
        st.markdown("---")
        st.subheader("🖼️ 圖面檢視")
        sel_proj = st.selectbox("選擇專案", df["標案名稱"].unique())
        if sel_proj:
            row = df[df["標案名稱"] == sel_proj].iloc[0]
            if row["進度表圖檔"] != "無":
                img_p = os.path.join(IMG_DIR, row["進度表圖檔"])
                if os.path.exists(img_p):
                    from PIL import Image
                    st.image(Image.open(img_p), caption=f"{sel_proj} 圖面", width=700)
    else:
        st.info("目前無資料，請先新增一筆資料後，Excel 下載按鈕才會出現。")