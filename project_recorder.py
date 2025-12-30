import streamlit as st
import io
from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.drawing.image import Image as XLImage

# --- 1. 頁面配置 ---
st.set_page_config(page_title="營造標案履歷系統 v9.2", layout="wide", page_icon="🏗️")

# --- 2. CSS 樣式 ---
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
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 Session State ---
default_values = {
    "project_name": "", "project_loc": "", "client_name": "", "architect_name": "",
    "bid_year": "", "contract_date": "", "contract_cost": "", "duration_days": "", # 新增 duration_days
    "floors_up": 0, "floors_down": 0,
    "site_area": 0.0, "total_floor_area": 0.0, "building_height": 0.0, "excavation_depth": 0.0,
    "const_method": "請選擇...", "struct_above": "請選擇...", "struct_below": "請選擇...", "transfer_slab": "", # 新增 transfer_slab
    "foundation_type": "請選擇...", "b_type": "請選擇...", "retain_sys": "請選擇...", 
    "wall_sys": "請選擇...", "gw_method": "請選擇..."
}

for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

def get_index(options, key):
    current_val = st.session_state[key]
    if current_val in options: return options.index(current_val)
    return 0

# --- 4. 介面設計 ---

st.title("🏗️ 營造標案履歷系統 v9.2")
st.caption("更新內容：新增「鋼構轉換層」、「日曆天工期」")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 基本資料與規格", "🖼️ 圖片與敘述", "📊 導出 Excel"])

with tab1:
    st.subheader("1. 專案基本資料")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("專案名稱", key="project_name", placeholder="例：信義區A1新建工程") 
        st.text_input("工程地點", key="project_loc", placeholder="例：台北市信義區")
    with c2:
        st.text_input("業主名稱", key="client_name", placeholder="例：XX建設股份有限公司")
        st.text_input("設計單位/建築師", key="architect_name", placeholder="例：OOO建築師事務所")
    with c3:
        st.text_input("投標年份", key="bid_year", placeholder="例：2023")
        c3_1, c3_2 = st.columns(2)
        with c3_1:
            st.text_input("完工年份", key="contract_date", placeholder="例：2025.12")
        with c3_2:
            # 新增工期欄位
            st.text_input("工期 (日曆天)", key="duration_days", placeholder="例：1200")
        
        st.text_input("工程造價 (億元)", key="contract_cost", placeholder="例：15.5")

    st.subheader("2. 建築規模")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        opts_type = ["請選擇...", "住宅大樓", "商辦大樓", "飯店", "百貨", "賣場", "廠房", "公共工程"]
        st.selectbox("建物類型", opts_type, index=get_index(opts_type, "b_type"), key="b_type")
    with col_b2:
        opts_struct = ["請選擇...", "SC (鋼骨)", "SRC (鋼骨鋼筋混凝土)", "RC (鋼筋混凝土)", "SS (純鋼構)"]
        st.selectbox("地上結構", opts_struct, index=get_index(opts_struct, "struct_above"), key="struct_above")
    with col_b3:
        opts_struct_down = ["請選擇...", "RC (鋼筋混凝土)", "SRC (鋼骨鋼筋混凝土)"]
        st.selectbox("地下結構", opts_struct_down, index=get_index(opts_struct_down, "struct_below"), key="struct_below")
    with col_b4:
        # 新增鋼構轉換層欄位
        st.text_input("鋼構轉換層", key="transfer_slab", placeholder="例：無 / 4F轉換桁架")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        opts_found = ["請選擇...", "筏式基礎", "筏式基礎+基樁", "獨立基腳"]
        st.selectbox("基礎型式", opts_found, index=get_index(opts_found, "foundation_type"), key="foundation_type")
        st.number_input("建築高度 (m)", key="building_height")
    with col_d2:
        st.number_input("地上層數 (F)", min_value=0, key="floors_up", help="輸入 0 表示未定")
        st.number_input("基地面積 (m²)", key="site_area")
        st.number_input("總樓地板面積 (m²)", key="total_floor_area")
    with col_d3:
        st.number_input("地下層數 (B)", min_value=0, key="floors_down")
        st.number_input("開挖深度 (m)", key="excavation_depth")

    st.subheader("3. 關鍵工法")
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        opts_method = ["請選擇...", "逆打工法 (Top-Down)", "順打工法 (Bottom-Up)", "雙順打工法"]
        st.selectbox("主體施工工法", opts_method, index=get_index(opts_method, "const_method"), key="const_method")
    with c_m2:
        opts_retain = ["請選擇...", "連續壁+鋼支柱(逆打)", "連續壁+內支撐", "地錨工法", "鋼板樁", "明挖工法"]
        st.selectbox("擋土支撐系統", opts_retain, index=get_index(opts_retain, "retain_sys"), key="retain_sys")
    with c_m3:
        opts_wall = ["請選擇...", "玻璃帷幕", "石材吊掛", "鋁板", "二丁掛"]
        st.selectbox("外牆工法", opts_wall, index=get_index(opts_wall, "wall_sys"), key="wall_sys")

    c_gw1, c_gw2, c_gw3 = st.columns(3)
    with c_gw1:
        opts_gw = ["請選擇...", "一般導溝", "全套管", "深導溝"]
        st.selectbox("導溝施作方式", opts_gw, index=get_index(opts_gw, "gw_method"), key="gw_method")

with tab2:
    st.header("工程特色與圖片")
    col_text1, col_text2 = st.columns(2)
    with col_text1:
        features = st.text_area("✨ 工程特色 (條列式)", placeholder="1. 採用特殊工法...\n2. 獲得綠建築標章...", height=200)
    with col_text2:
        challenges = st.text_area("🧗 施工挑戰 (條列式)", placeholder="1. 鄰近捷運監測...\n2. 基地狹小...", height=200)

    uploaded_img = st.file_uploader("上傳完工照 (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
    if uploaded_img:
        st.image(uploaded_img, width=400, caption="預覽圖片")

with tab3:
    st.header("導出 Excel 履歷")
    
    def generate_excel():
        wb = Workbook()
        ws = wb.active
        ws.title = "專案履歷表"
        p_name = st.session_state.project_name if st.session_state.project_name else "未命名專案"
        
        # 樣式
        border_style = Side(border_style="thin", color="000000")
        full_border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)
        fill_header = PatternFill(start_color="2D2926", end_color="2D2926", fill_type="solid")
        fill_sub_header = PatternFill(start_color="FFB81C", end_color="FFB81C", fill_type="solid")
        fill_light = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        font_title = Font(name='微軟正黑體', size=16, bold=True, color="FFFFFF")
        font_sub = Font(name='微軟正黑體', size=12, bold=True)
        font_label = Font(name='微軟正黑體', size=11, bold=True)
        font_val = Font(name='微軟正黑體', size=11)

        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 25

        ws.merge_cells('A1:D1')
        ws['A1'] = p_name
        ws['A1'].fill = fill_header
        ws['A1'].font = font_title
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 40

        def write_row(r, l1, v1, l2, v2):
            ws[f'A{r}'] = l1
            ws[f'B{r}'] = v1
            ws[f'C{r}'] = l2
            ws[f'D{r}'] = v2
            for c in ['A','C']: 
                ws[f'{c}{r}'].fill = fill_light
                ws[f'{c}{r}'].font = font_label
            for c in ['B','D']: ws[f'{c}{r}'].font = font_val
            for c in ['A','B','C','D']: 
                ws[f'{c}{r}'].border = full_border
                ws[f'{c}{r}'].alignment = Alignment(vertical='center', wrap_text=True)

        ss = st.session_state
        write_row(2, "工程地點", ss.project_loc, "投標年份", ss.bid_year)
        write_row(3, "業主單位", ss.client_name, "設計單位", ss.architect_name)
        
        # 整合完工年份與工期
        date_str = f"{ss.contract_date}"
        if ss.duration_days:
            date_str += f" ({ss.duration_days}日曆天)"
            
        write_row(4, "完工年份/工期", date_str, "建物用途", ss.b_type)
        cost_str = f"{ss.contract_cost} 億元" if ss.contract_cost else ""
        write_row(5, "工程造價", cost_str, "  ", "")

        start_row = 6
        ws.merge_cells(f'A{start_row}:D{start_row}')
        ws[f'A{start_row}'] = "建築規模與技術規格"
        ws[f'A{start_row}'].fill = fill_sub_header
        ws[f'A{start_row}'].font = font_sub
        ws[f'A{start_row}'].alignment = Alignment(horizontal='center')
        ws[f'A{start_row}'].border = full_border

        struct_str = f"地上:{ss.struct_above} / 地下:{ss.struct_below}"
        # 加入鋼構轉換層資訊
        if ss.transfer_slab:
            struct_str += f"\n(轉換層: {ss.transfer_slab})"
            
        floor_str = f"{ss.floors_up}F / {ss.floors_down}B (高 {ss.building_height}m)"
        area_str = f"基地:{ss.site_area:,.0f} / 總樓:{ss.total_floor_area:,.0f} m²"
        excav_str = f"{ss.const_method} / GL-{ss.excavation_depth}m"

        r = start_row + 1
        write_row(r, "樓層/高度", floor_str, "結構系統", struct_str)
        write_row(r+1, "面積資訊", area_str, "基礎型式", ss.foundation_type)
        
        retain_str = f"{ss.retain_sys}"
        if ss.gw_method != "請選擇...": retain_str += f" ({ss.gw_method})"
        write_row(r+2, "施工工法", excav_str, "擋土/導溝", retain_str)
        write_row(r+3, "外牆系統", ss.wall_sys, "其他", "")

        r_feat = r + 4
        ws.merge_cells(f'A{r_feat}:D{r_feat}'); ws[f'A{r_feat}'] = "工程特色"; ws[f'A{r_feat}'].fill = fill_sub_header; ws[f'A{r_feat}'].font = font_sub; ws[f'A{r_feat}'].border = full_border
        r_feat_content = r_feat + 1
        ws.merge_cells(f'A{r_feat_content}:D{r_feat_content}'); ws[f'A{r_feat_content}'] = features if features else "(無)"; ws[f'A{r_feat_content}'].alignment = Alignment(wrap_text=True, vertical='top'); ws[f'A{r_feat_content}'].border = full_border; ws.row_dimensions[r_feat_content].height = 60
        
        r_chal = r_feat_content + 1
        ws.merge_cells(f'A{r_chal}:D{r_chal}'); ws[f'A{r_chal}'] = "施工挑戰"; ws[f'A{r_chal}'].fill = fill_sub_header; ws[f'A{r_chal}'].font = font_sub; ws[f'A{r_chal}'].border = full_border
        r_chal_content = r_chal + 1
        ws.merge_cells(f'A{r_chal_content}:D{r_chal_content}'); ws[f'A{r_chal_content}'] = challenges if challenges else "(無)"; ws[f'A{r_chal_content}'].alignment = Alignment(wrap_text=True, vertical='top'); ws[f'A{r_chal_content}'].border = full_border; ws.row_dimensions[r_chal_content].height = 60
        
        r_img = r_chal_content + 1
        ws.merge_cells(f'A{r_img}:D{r_img}'); ws[f'A{r_img}'] = "專案照片"; ws[f'A{r_img}'].fill = fill_sub_header; ws[f'A{r_img}'].font = font_sub; ws[f'A{r_img}'].alignment = Alignment(horizontal='center'); ws[f'A{r_img}'].border = full_border

        r_img_content = r_img + 1
        if uploaded_img:
            img_io = io.BytesIO(uploaded_img.getvalue())
            img = XLImage(img_io)
            img.width = 400; img.height = 300
            ws.add_image(img, f'A{r_img_content}')
            ws.row_dimensions[r_img_content].height = 230
        else:
            ws.merge_cells(f'A{r_img_content}:D{r_img_content}')
            ws[f'A{r_img_content}'] = "(無照片)"
            ws[f'A{r_img_content}'].alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[r_img_content].height = 50

        out_buffer = io.BytesIO()
        wb.save(out_buffer)
        return out_buffer.getvalue()

    if st.button("生成並下載 Excel", type="primary"):
        xlsx_data = generate_excel()
        p_name = st.session_state.project_name if st.session_state.project_name else "Project"
        st.download_button(
            label="📥 點擊下載",
            data=xlsx_data,
            file_name=f"{p_name}_履歷表.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )