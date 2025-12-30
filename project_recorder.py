import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 設定頁面資訊 ---
st.set_page_config(
    page_title="營造標案詳細資料庫", 
    layout="wide",
    page_icon="🏗️"
)

# 資料庫檔案名稱
DB_FILE = "construction_specs_db.csv"

# --- 核心功能函式 ---

def load_data():
    """讀取資料庫，如果不存在則建立新的"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # 定義所有需要的欄位
        columns = [
            "登錄時間", "標案名稱", "地號", "業主", "建築事務所", "基地面積",
            "結構型式", "樓層規劃", "樓層高度", 
            "開挖深度(GL-)", "開挖工法", "連續壁規格", "基樁規格",
            "備註"
        ]
        return pd.DataFrame(columns=columns)

def save_entry(data_dict):
    """將單筆資料存入 CSV"""
    df = load_data()
    # 將字典轉換為 DataFrame 並合併
    new_entry = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)
    return updated_df

# --- 介面設計 ---

st.title("🏗️ 營造標案詳細規格資料庫")
st.markdown("此系統用於詳細記錄標案的結構形式、開挖工法與基礎規格。")
st.markdown("---")

# 建立分頁 (Tabs) 來區分「輸入資料」與「查詢資料」
tab1, tab2 = st.tabs(["📝 新增標案資料", "📂 檢視歷史檔案"])

with tab1:
    with st.form("spec_form", clear_on_submit=True):
        st.subheader("1. 專案基本資料")
        col_base1, col_base2, col_base3 = st.columns(3)
        with col_base1:
            name = st.text_input("標案名稱", placeholder="例如：信義區商業大樓新建工程")
            owner = st.text_input("業主", placeholder="建設公司或機關名稱")
        with col_base2:
            lot = st.text_input("地號", placeholder="例如：信義段一小段...")
            architect = st.text_input("建築事務所")
        with col_base3:
            area = st.text_input("基地面積", placeholder="例如：1500 m² (453坪)")
        
        st.markdown("---")
        st.subheader("2. 建築結構與樓層")
        col_struc1, col_struc2, col_struc3 = st.columns(3)
        with col_struc1:
            # 結構型式
            struct_type = st.text_input("結構工法型式", placeholder="例如：SRC造、RC造、SC造")
        with col_struc2:
            # 地下幾層/地上幾層
            floors = st.text_input("樓層規劃", placeholder="例如：B5 / 24F")
        with col_struc3:
            # 樓層高度
            floor_height = st.text_input("樓層高度", placeholder="例如：標準層 3.6m / 1F 6m")

        st.markdown("---")
        st.subheader("3. 大地工程 (開挖/擋土/基礎)")
        col_geo1, col_geo2 = st.columns(2)
        
        with col_geo1:
            excav_depth = st.text_input("開挖深度 (GL-)", placeholder="例如：21.5 m")
            excav_method = st.text_input("開挖工法", placeholder="例如：逆打工法、順打(島區)")
        
        with col_geo2:
            wall_spec = st.text_input("連續壁規格 (厚度/深度)", placeholder="例如：厚100cm / 深45m")
            pile_spec = st.text_input("基樁規格", placeholder="例如：反循環基樁 D=2m L=50m，共12支")

        st.markdown("---")
        note = st.text_area("其他備註", placeholder="例如：特殊地質改良、鄰房保護措施...")

        # 送出按鈕
        submitted = st.form_submit_button("💾 儲存專案資料")

        if submitted:
            if name:
                # 收集資料
                entry_data = {
                    "登錄時間": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "標案名稱": name,
                    "地號": lot,
                    "業主": owner,
                    "建築事務所": architect,
                    "基地面積": area,
                    "結構型式": struct_type,
                    "樓層規劃": floors,
                    "樓層高度": floor_height,
                    "開挖深度(GL-)": excav_depth,
                    "開挖工法": excav_method,
                    "連續壁規格": wall_spec,
                    "基樁規格": pile_spec,
                    "備註": note
                }
                save_entry(entry_data)
                st.success(f"已成功新增標案：{name}")
            else:
                st.error("❌ 請至少輸入「標案名稱」才能存檔。")

with tab2:
    st.subheader("📊 所有標案列表")
    df = load_data()
    
    if not df.empty:
        # 顯示資料表 (設為可互動，方便閱讀寬表格)
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("💡 **提示**：如果欄位太多被切掉，可以在表格上**按住 Shift + 滾輪**左右滑動，或點擊表格右上角的放大鏡圖示全螢幕查看。")
        
        # 下載按鈕
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 Excel/CSV 報表",
            data=csv_data,
            file_name='construction_projects_db.csv',
            mime='text/csv'
        )
    else:
        st.info("目前資料庫是空的，請切換到「新增標案資料」分頁進行輸入。")