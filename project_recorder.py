import streamlit as st
import pandas as pd
import io
from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

# --- 1. 頁面配置 ---
st.set_page_config(page_title="營造標案履歷系統", layout="wide", page_icon="🏗️")

# --- 2. CSS 樣式 (延續原版風格) ---
st.markdown("""
    <style>
    :root { --main-yellow: #FFB81C; --accent-orange: #FF4438; --dark-grey: #2D2926; }
    .stApp { background-color: #f4f6f9; }
    h1, h2, h3, label { color: var(--dark-grey) !important; font-weight: bold !important; font-family: '微軟正黑體', sans-serif; }
    .stButton>button { 
        background-color: var(--main-yellow); color: var(--dark-grey); 
        border: none; width: 100%; border-radius: 8px; font-size: 18px; font-weight: bold; padding: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 20px; font-weight: bold; color: #2D2926; 
        border-left: 6px solid #FFB81C; padding-left: 10px; margin-bottom: 20px; margin-top: 30px; background-color: #fff; padding-top:10px; padding-bottom:10px; border-radius: 0 5px 5px 0;
    }
    .card {
        background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 標題與側邊欄 ---
st.title("🏗️ 營造標案履歷資料庫系統")
st.markdown("此系統協助您將工程實績標準化，生成專業的 Excel 履歷卡。")

# --- 4. 輸入介面 (Tab 分頁設計) ---
tab1, tab2, tab3 = st.tabs(["📝 基本資料與規格", "🖼️ 圖片與敘述", "📊 預覽與導出"])

with tab1:
    st.markdown("<div class='section-header'>1. 專案基本資料</div>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            project_name = st.text_input("專案名稱", "信義區 A1 商辦大樓新建工程")
            project_loc = st.text_input("工程地點", "台北市信義區")
        with c2:
            client_name = st.text_input("業主名稱", "XX 建設股份有限公司")
            architect_name = st.text_input("設計單位/建築師", "OOO 建築師事務所")
        with c3:
            contract_date = st.text_input("完工年份 (或工程期間)", "2023.05 - 2025.12")
            contract_cost = st.text_input("工程造價 (億元)", "15.5")

    st.markdown("<div class='section-header'>2. 建築規模與構造</div>", unsafe_allow_html=True)
    with st.container():
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1:
            b_type = st.selectbox("建物類型", ["住宅大樓", "商辦大樓", "飯店/酒店", "百貨商場", "高科技廠房", "醫療機構", "公共工程"])
        with col_b2:
            struct_above = st.selectbox("地上結構", ["SC (鋼骨)", "SRC (鋼骨鋼筋混凝土)", "RC (鋼筋混凝土)", "SS (純鋼構)"])
        with col_b3:
            struct_below = st.selectbox("地下結構", ["RC (鋼筋混凝土)", "SRC (鋼骨鋼筋混凝土)"])
        with col_b4:
            foundation_type = st.selectbox("基礎型式", ["筏式基礎", "筏式基礎+基樁", "獨立基腳"])

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            floors_up = st.number_input("地上層數 (F)", min_value=1, value=24)
            floors_down = st.number_input("地下層數 (B)", min_value=0, value=5)
        with col_d2:
            site_area = st.number_input("基地面積 (m²)", value=2500.0)
            total_floor_area = st.number_input("總樓地板面積 (m²)", value=32000.0)
        with col_d3:
            building_height = st.number_input("建築高度 (m)", value=89.5)
            excavation_depth = st.number_input("開挖深度 (m)", value=18.5)

    st.markdown("<div class='section-header'>3. 關鍵工法</div>", unsafe_allow_html=True)
    with st.container():
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            const_method = st.selectbox("主體施工工法", ["逆打工法 (Top-Down)", "順打工法 (Bottom-Up)", "雙順打工法"])
        with c_m2:
            retain_sys = st.selectbox("擋土支撐系統", ["連續壁+鋼支柱(逆打)", "連續壁+內支撐", "地錨工法", "鋼板樁"])
        with c_m3:
            wall_sys = st.selectbox("外牆工法", ["玻璃帷幕單元", "石材乾式吊掛", "鋁包板/金屬板", "二丁掛磁磚"])

with tab2:
    st.markdown("<div class='section-header'>4. 專案特色與挑戰 (履歷重點)</div>", unsafe_allow_html=True)
    
    col_text1, col_text2 = st.columns(2)
    with col_text1:
        features = st.text_area("✨ 工程特色 (條列式)", 
            "1. 採用逆打工法縮短工期 3 個月。\n2. 綠建築黃金級標章認證。\n3. 使用高強度混凝土 (8000psi)。", height=200)
    with col_text2:
        challenges = st.text_area("🧗 施工挑戰與克服", 
            "1. 鄰近捷運線，開挖監測要求嚴格。\n2. 市中心交通動線狹窄，物流計畫複雜。\n3. 深開挖達 20m，地下水位控制不易。", height=200)

    st.markdown("<div class='section-header'>5. 專案照片</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("上傳完工照或透視圖 (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='專案封面圖預覽', width=400)
    else:
        st.info("尚未上傳照片，Excel 報表將留空。")

with tab3:
    st.markdown("<div class='section-header'>6. 履歷預覽與導出</div>", unsafe_allow_html=True)
    
    # --- 預覽卡片 ---
    st.markdown(f"""
    <div style="background-color:white; padding:30px; border-radius:10px; border-left: 10px solid #FFB81C; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        <h2 style="margin-top:0;">{project_name}</h2>
        <p style="color:#666; font-size:16px;">{contract_date} | {project_loc}</p>
        <hr>
        <div style="display:flex; flex-wrap:wrap;">
            <div style="flex:1; min-width:300px;">
                <p><b>業主：</b>{client_name}</p>
                <p><b>建築師：</b>{architect_name}</p>
                <p><b>規模：</b>地上 {floors_up}F / 地下 {floors_down}B</p>
                <p><b>結構：</b>{struct_above} / {struct_below}</p>
            </div>
            <div style="flex:1; min-width:300px;">
                <p><b>總樓地板：</b>{total_floor_area:,.0f} m²</p>
                <p><b>造價：</b>{contract_cost} 億元</p>
                <p><b>工法：</b>{const_method}</p>
                <p><b>開挖：</b>GL -{excavation_depth}m</p>
            </div>
        </div>
        <hr>
        <p><b>工程特色：</b><br>{features.replace(chr(10), '<br>')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # --- Excel 生成邏輯 ---
    def generate_excel():
        wb = Workbook()
        ws = wb.active
        ws.title = "專案履歷表"
        
        # 樣式定義
        border_style = Side(border_style="thin", color="000000")
        thick_border = Side(border_style="medium", color="000000")
        full_border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)
        
        fill_header = PatternFill(start_color="2D2926", end_color="2D2926", fill_type="solid") # 深灰
        fill_sub_header = PatternFill(start_color="FFB81C", end_color="FFB81C", fill_type="solid") # 黃色
        fill_light = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid") # 淺灰

        font_title = Font(name='微軟正黑體', size=16, bold=True, color="FFFFFF")
        font_sub = Font(name='微軟正黑體', size=12, bold=True, color="2D2926")
        font_label = Font(name='微軟正黑體', size=11, bold=True)
        font_val = Font(name='微軟正黑體', size=11)

        # 設定欄寬
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 25
        
        # 標題區
        ws.merge_cells('A1:D1')
        cell = ws['A1']
        cell.value = project_name
        cell.fill = fill_header
        cell.font = font_title
        cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 40

        # 資料填寫函數
        def write_row(row_idx, label1, val1, label2, val2):
            ws[f'A{row_idx}'] = label1
            ws[f'B{row_idx}'] = val1
            ws[f'C{row_idx}'] = label2
            ws[f'D{row_idx}'] = val2
            
            for col in ['A', 'C']:
                ws[f'{col}{row_idx}'].fill = fill_light
                ws[f'{col}{row_idx}'].font = font_label
            for col in ['B', 'D']:
                ws[f'{col}{row_idx}'].font = font_val
                
            for col in ['A', 'B', 'C', 'D']:
                ws[f'{col}{row_idx}'].border = full_border
                ws[f'{col}{row_idx}'].alignment = Alignment(vertical='center', wrap_text=True)

        # 基本資料
        write_row(2, "工程地點", project_loc, "完工年份", contract_date)
        write_row(3, "業主單位", client_name, "設計單位", architect_name)
        write_row(4, "工程造價", f"{contract_cost} 億元", "建物用途", b_type)
        
        # 分隔標題
        ws.merge_cells('A5:D5')
        ws['A5'] = "建築規模與技術規格"
        ws['A5'].fill = fill_sub_header
        ws['A5'].font = font_sub
        ws['A5'].alignment = Alignment(horizontal='center')
        ws['A5'].border = full_border

        # 技術規格
        struct_str = f"地上:{struct_above} / 地下:{struct_below}"
        floor_str = f"{floors_up}F / {floors_down}B (高 {building_height}m)"
        area_str = f"基地:{site_area:,.0f} / 總樓:{total_floor_area:,.0f} m²"
        excav_str = f"{const_method} / GL-{excavation_depth}m"
        
        write_row(6, "樓層/高度", floor_str, "結構系統", struct_str)
        write_row(7, "面積資訊", area_str, "基礎型式", foundation_type)
        write_row(8, "施工工法", excav_str, "擋土系統", retain_sys)
        write_row(9, "外牆系統", wall_sys, "其他", "")

        # 質化描述
        ws.merge_cells('A10:D10')
        ws['A10'] = "工程特色"
        ws['A10'].fill = fill_sub_header
        ws['A10'].font = font_sub
        ws['A10'].border = full_border
        
        ws.merge_cells('A11:D11')
        ws['A11'] = features
        ws['A11'].font = font_val
        ws['A11'].alignment = Alignment(wrap_text=True, vertical='top')
        ws['A11'].border = full_border
        ws.row_dimensions[11].height = 80

        ws.merge_cells('A12:D12')
        ws['A12'] = "施工挑戰"
        ws['A12'].fill = fill_sub_header
        ws['A12'].font = font_sub
        ws['A12'].border = full_border
        
        ws.merge_cells('A13:D13')
        ws['A13'] = challenges
        ws['A13'].font = font_val
        ws['A13'].alignment = Alignment(wrap_text=True, vertical='top')
        ws['A13'].border = full_border
        ws.row_dimensions[13].height = 80

        # 圖片區
        ws.merge_cells('A14:D14')
        ws['A14'] = "專案照片"
        ws['A14'].fill = fill_sub_header
        ws['A14'].font = font_sub
        ws['A14'].alignment = Alignment(horizontal='center')
        ws['A14'].border = full_border

        if uploaded_file:
            img_io = io.BytesIO(uploaded_file.getvalue())
            img = XLImage(img_io)
            # 簡單調整圖片大小以適應儲存格
            img.width = 400
            img.height = 300
            ws.add_image(img, 'A15')
            ws.row_dimensions[15].height = 230
        else:
            ws.merge_cells('A15:D15')
            ws['A15'] = "(無照片)"
            ws['A15'].alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[15].height = 50

        buffer = io.BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    excel_data = generate_excel()
    
    st.download_button(
        label="📥 下載 Excel 標案履歷表",
        data=excel_data,
        file_name=f"{project_name}_履歷表.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )