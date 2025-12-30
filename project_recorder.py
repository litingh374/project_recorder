import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 設定頁面資訊 ---
st.set_page_config(
    page_title="營造專案智慧管理系統 v4.0", 
    layout="wide",
    page_icon="🏗️"
)

# 資料庫與圖片設定
DB_FILE = "construction_project_db_v4.csv"
IMG_DIR = "project_images"

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- 核心功能函式 ---

def load_data():
    """讀取資料庫"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # 定義欄位 (包含動態欄位)
        columns = [
            "登錄時間", "標案名稱", "文件編號版本", "業主", "建築事務所", 
            "建物類型", "基地現況", "前置作業時間(月)", "有無地改",
            # 面積
            "基地面積(m2)", "建築面積(m2)", "總樓地板面積(m2)",
            # 樓層與高度 (數值)
            "地下室層數", "地上樓層數", "屋突層數",
            "地下室高度總和(m)", "地上樓層高度總和(m)", "屋突高度總和(m)",
            # 結構與基礎
            "上部結構型式", "下部結構型式", "外牆型式",
            "基礎型式", "筏基深度(m)", "筏基版厚(cm)",
            # 大地與擋土
            "擋土型式(連續壁等)", 
            "開挖深度(m)", "開挖工法", 
            # 動態工法欄位 (順打/逆打共用或專用)
            "支撐/鋼支柱規格", "中間柱/基樁規格", "取土口/構台",
            # 假設與其他
            "塔吊規格", "施工電梯", "施工大門",
            "人力配置", "拆除計畫簡述", "備註", "進度表圖檔"
        ]
        return pd.DataFrame(columns=columns)

def save_entry(data_dict, uploaded_file):
    """儲存資料"""
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
    # 確保新舊欄位一致，使用 concat
    new_entry = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)
    return updated_df

def convert_df_to_excel(df):
    """轉出 Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='專案總表')
        workbook = writer.book
        worksheet = writer.sheets['專案總表']
        
        header_fmt = workbook.add_format({
            'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center',
            'fg_color': '#4F81BD', 'font_color': 'white', 'border': 1
        })
        cell_fmt = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        
        for col, val in enumerate(df.columns):
            worksheet.write(0, col, val, header_fmt)
            worksheet.set_column(col, col, 15, cell_fmt)
        
        worksheet.set_column('B:B', 25) # 標案
        worksheet.set_column('X:X', 30) # 擋土
        worksheet.set_column('AJ:AJ', 40) # 備註

    return output.getvalue()

# --- 介面設計 ---

st.title("🏗️ 營造專案智慧管理系統 v4.0")
st.markdown("新增功能：樓層增減按鈕、工法動態欄位切換、詳細基地條件設定")

tab1, tab2 = st.tabs(["📝 新增智慧表單", "📂 報表與圖面"])

with tab1:
    with st.form("smart_form_v4", clear_on_submit=True):
        
        # --- 1. 基本資料與基地現況 ---
        st.subheader("1. 專案背景與基地現況")
        c1, c2, c3, c4 = st.columns(4)
        with c1: name = st.text_input("標案名稱", placeholder="必填")
        with c2: doc_ver = st.text_input("文件編號/版本")
        with c3: owner = st.text_input("業主")
        with c4: architect = st.text_input("建築事務所")

        c_type1, c_type2, c_type3, c_type4 = st.columns(4)
        with c_type1:
            bldg_type = st.selectbox("建物類型", 
                ["住宅", "集合住宅", "辦公", "飯店", "百貨", "廠房", "醫院", "其他"])
        with c_type2:
            site_cond = st.selectbox("基地現況", 
                ["純空地", "有上部舊建物", "有上部舊建物及地下室", "舊建物已拆除(僅回填地下室)"])
        with c_type3:
            soil_imp = st.radio("有無地質改良", ["無", "有"], horizontal=True)
        with c_type4:
            pre_work_time = st.number_input("前置作業時間 (月)", min_value=0.0, step=0.5)

        # --- 2. 樓層與高度 (使用 +/- 按鈕) ---
        st.markdown("---")
        st.subheader("2. 樓層與高度規劃 (點擊 +/- 調整)")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            st.info("🔽 地下室 (Basement)")
            f_b_count = st.number_input("地下室層數 (B)", min_value=0, step=1, format="%d")
            f_b_height = st.number_input("地下高度總和 (m)", min_value=0.0, step=0.1, format="%.2f")
            
        with col_f2:
            st.warning("🔼 地上層 (Floor)")
            f_f_count = st.number_input("地上樓層數 (F)", min_value=1, step=1, format="%d")
            f_f_height = st.number_input("地上高度總和 (m)", min_value=0.0, step=0.5, format="%.2f")
            
        with col_f3:
            st.success("🏠 屋突 (Roof)")
            f_r_count = st.number_input("屋突層數 (R)", min_value=0, step=1, format="%d")
            f_r_height = st.number_input("屋突高度總和 (m)", min_value=0.0, step=0.1, format="%.2f")

        # 自動計算總樓高預覽
        total_h = f_b_height + f_f_height + f_r_height
        st.caption(f"📊 目前設定總建築高度約為：{total_h:.2f} m")

        # --- 3. 結構與基礎 ---
        st.markdown("---")
        st.subheader("3. 結構與基礎型式")
        
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1: 
            st_upper = st.text_input("上部結構型式", placeholder="例：SRC / SC")
            st_lower = st.text_input("下部結構型式", placeholder="例：RC")
        with col_st2: 
            wall_type = st.text_input("外牆型式", placeholder="例：帷幕牆")
            found_type = st.text_input("基礎型式", placeholder="例：筏式基礎 / 獨立基腳")
        with col_st3: 
            raft_depth = st.text_input("筏基深度 (m)")
            raft_thick = st.text_input("筏基版厚 (cm)")

        # --- 4. 大地工程 (動態邏輯區) ---
        st.markdown("---")
        st.subheader("4. 大地工程與開挖邏輯")
        
        # 4.1 擋土系統
        rw_specs = st.text_area("擋土型式規格 (連續壁/預壘樁等)", height=80, 
                               placeholder="可多行輸入，例：\n連續壁 厚100cm 深45m\n扶壁 厚80cm")
        
        # 4.2 開挖工法選擇與動態欄位
        col_met1, col_met2 = st.columns([1, 3])
        with col_met1:
            method = st.selectbox("開挖工法", ["順打", "逆打", "雙順打"])
            excav_depth = st.text_input("開挖深度 (m)")
        
        with col_met2:
            # 根據選擇顯示不同欄位
            if method == "順打":
                st.markdown("##### 🟢 順打工法配置")
                # 順打關注水平支撐與中間柱
                dyn_strut = st.text_input("水平支撐規格", placeholder="例：H350x350 @5層")
                dyn_pile = st.text_input("中間柱規格", placeholder="例：H300x300 / 構台柱")
                dyn_soil = st.text_input("取土口數量/位置", placeholder="例：2處 (A區/B區)")
                
            elif method == "逆打":
                st.markdown("##### 🔴 逆打工法配置")
                # 逆打關注鋼支柱與基樁
                dyn_strut = st.text_input("鋼支柱(構台柱)規格", placeholder="例：鋼箱型柱 600x600")
                dyn_pile = st.text_input("基樁規格 (逆打承重)", placeholder="例：全套管 D200 L50m")
                dyn_soil = st.text_input("取土口/開孔配置", placeholder="例：1F預留開孔 3處")
                
            else: # 雙順打
                st.markdown("##### 🔵 雙順打工法配置")
                dyn_strut = st.text_input("支撐/樓板複合配置", placeholder="例：B1/B3樓板，B2/B4支撐")
                dyn_pile = st.text_input("中間柱/基樁規格", placeholder="例：共用型式")
                dyn_soil = st.text_input("取土動線", placeholder="說明垂直運輸方式")

        # --- 5. 假設工程與其他 ---
        st.markdown("---")
        st.subheader("5. 面積與假設工程")
        
        c_area1, c_area2, c_area3 = st.columns(3)
        with c_area1: area_base = st.text_input("基地面積 (m²)")
        with c_area2: area_build = st.text_input("建築面積 (m²)")
        with c_area3: area_total = st.text_input("總樓地板面積 (m²)")
        
        col_eq1, col_eq2, col_eq3 = st.columns(3)
        with col_eq1: tower_crane = st.text_input("塔吊規格")
        with col_eq2: elevator = st.text_input("施工電梯 (品牌/大小)")
        with col_eq3: gate = st.text_input("施工大門 (大小/數量)")
        
        c_final1, c_final2 = st.columns(2)
        with c_final1: manpower = st.text_input("人力配置")
        with c_final2: demo_plan = st.text_input("拆除計畫簡述")

        st.markdown("---")
        col_img, col_note = st.columns([1, 2])
        with col_img: uploaded_img = st.file_uploader("上傳進度表/配置圖", type=['png', 'jpg', 'jpeg'])
        with col_note: note = st.text_area("備註事項")

        submitted = st.form_submit_button("💾 儲存智慧表單 v4")

        if submitted:
            if name:
                entry = {
                    "登錄時間": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "標案名稱": name,
                    "文件編號版本": doc_ver,
                    "業主": owner,
                    "建築事務所": architect,
                    "建物類型": bldg_type,
                    "基地現況": site_cond,
                    "有無地改": soil_imp,
                    "前置作業時間(月)": pre_work_time,
                    "基地面積(m2)": area_base,
                    "建築面積(m2)": area_build,
                    "總樓地板面積(m2)": area_total,
                    "地下室層數": f_b_count,
                    "地上樓層數": f_f_count,
                    "屋突層數": f_r_count,
                    "地下室高度總和(m)": f_b_height,
                    "地上樓層高度總和(m)": f_f_height,
                    "屋突高度總和(m)": f_r_height,
                    "上部結構型式": st_upper,
                    "下部結構型式": st_lower,
                    "外牆型式": wall_type,
                    "基礎型式": found_type,
                    "筏基深度(m)": raft_depth,
                    "筏基版厚(cm)": raft_thick,
                    "擋土型式(連續壁等)": rw_specs,
                    "開挖深度(m)": excav_depth,
                    "開挖工法": method,
                    "支撐/鋼支柱規格": dyn_strut, # 存入動態欄位的值
                    "中間柱/基樁規格": dyn_pile,   # 存入動態欄位的值
                    "取土口/構台": dyn_soil,       # 存入動態欄位的值
                    "塔吊規格": tower_crane,
                    "施工電梯": elevator,
                    "施工大門": gate,
                    "人力配置": manpower,
                    "拆除計畫簡述": demo_plan,
                    "備註": note
                }
                save_entry(entry, uploaded_img)
                st.success(f"✅ 資料已建檔：{name} ({method}案)")
            else:
                st.error("❌ 請輸入標案名稱")

with tab2:
    st.subheader("📊 專案資料庫檢視")
    df = load_data()
    
    if not df.empty:
        # 顯示可互動表格
        st.dataframe(df, use_container_width=True)
        
        # 下載 Excel
        st.markdown("### 📥 報表輸出")
        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="下載 Excel 報表 (包含動態工法欄位)",
            data=excel_data,
            file_name='Smart_Project_Report_v4.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        
        # 圖片檢視
        st.markdown("---")
        st.subheader("🖼️ 圖面檢視")
        sel_proj = st.selectbox("選擇專案", df["標案名稱"].unique())
        if sel_proj:
            row = df[df["標案名稱"] == sel_proj].iloc[0]
            if row["進度表圖檔"] != "無":
                img_p = os.path.join(IMG_DIR, row["進度表圖檔"])
                if os.path.exists(img_p):
                    from PIL import Image
                    st.image(Image.open(img_p), caption=f"{sel_proj} 進度/配置圖", width=700)
                else:
                    st.warning("圖檔遺失")
            else:
                st.info("無上傳圖檔")
    else:
        st.info("尚無資料，請至左側新增。")