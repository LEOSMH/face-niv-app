import streamlit as st
import datetime
import time
import pandas as pd
import os

# Set Page Config
st.set_page_config(
    page_title="FACE 圈 - NIV 罩護無痕 臨床照護助手 (v14 精準單張KEY單版)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
    }
    .section-box {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 15px;
    }
    .alert-box {
        background-color: #FEF3C7;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #F59E0B;
        color: #111827 !important;
        margin-bottom: 15px;
    }
    .alert-box p, .alert-box li, .alert-box span {
        color: #111827 !important;
    }
    .danger-box {
        background-color: #FEE2E2;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #EF4444;
        color: #111827 !important;
        margin-bottom: 15px;
    }
    .danger-box p, .danger-box li, .danger-box span {
        color: #111827 !important;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #10B981;
        color: #111827 !important;
        margin-bottom: 15px;
    }
    .success-box p, .success-box li, .success-box span {
        color: #111827 !important;
    }
    .info-tag {
        font-size: 14px;
        font-weight: bold;
        color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# App Headers
st.markdown("<div class='main-title'>NIV 罩護無痕 臨床護理照護 App</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>台大醫院 FACE 圈 跨科部跨團隊智慧結晶 (護理、RT、醫工)</div>", unsafe_allow_html=True)

# Sidebar - Patient Demographics & QCC Logo
logo_loaded = False
try:
    if os.path.exists("face_logo.png"):
        st.sidebar.image("face_logo.png", width=150)
        logo_loaded = True
except Exception:
    pass

if not logo_loaded:
    st.sidebar.markdown("""
    <div style="background-color: #1E3A8A; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
        <span style="font-size: 40px;">🏥</span>
        <h3 style="color: white; margin: 5px 0 0 0;">台大醫院 FACE 圈</h3>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### 🏥 FACE 圈 臨床照護精神")
st.sidebar.markdown("""
**F**usion (跨界融合)
**A**ssessment (精準評估)
**C**omfort (舒適防護)
**E**limination (消除壓傷)
""")
st.sidebar.divider()

st.sidebar.subheader("👤 病患基本資料登記")
unit_select = st.sidebar.selectbox("單位 (Unit)", ["7A", "7D", "14C", "14D"])
bed_no = st.sidebar.text_input("床號 (Bed No.)", placeholder="例：12")
patient_name = st.sidebar.text_input("姓名 (Patient Name)", placeholder="例：王小明")
chart_no = st.sidebar.text_input("病歷號 (Chart No.)", placeholder="例：1234567")

track_status = st.sidebar.selectbox(
    "🔄 本次填表病患狀態 (Status)", 
    ["收案/日常查檢 (追蹤中)", "結案/停用BIPAP (結案)"],
    help="若病人停用BIPAP或出院，請選擇『結案』以移出每日巡查名單。"
)

st.sidebar.subheader("📋 醫囑與呼吸器設定")
bipap_order = st.sidebar.text_input(
    "當日 BIPAP 使用醫囑 (Order)", 
    value="BIPAP持續使用12hr, off 15 mins Q4H between 06:00-24:00"
)

col_set1, col_set2, col_set3 = st.sidebar.columns(3)
with col_set1:
    ipap_val = st.number_input("IPAP", min_value=4, max_value=30, value=16, step=1, help="cmH2O")
with col_set2:
    epap_val = st.number_input("EPAP", min_value=4, max_value=20, value=8, step=1, help="cmH2O")
with col_set3:
    fio2_options = [21, 25] + list(range(30, 101, 5))
    default_index = fio2_options.index(40)
    fio2_val = st.selectbox("FiO2 (%)", options=fio2_options, index=default_index, help="氧氣濃度")

bipap_settings = f"{ipap_val}/{epap_val}/{fio2_val}%"

nurse_name = st.sidebar.text_input("KEY單人員 / 護理師簽名", placeholder="請輸入姓名")

st.sidebar.subheader("📅 單張日期 (支援事後補KEY)")
entry_date = st.sidebar.date_input("單張日期", value=datetime.date.today(), help="請選擇紙本單張上記錄的日期")
entry_date_str = entry_date.strftime('%Y-%m-%d')
st.sidebar.markdown(f"**選定紀錄日期：** `{entry_date_str}`")


# Session State & Callbacks for NG (Nasogastric Tube) Synchronization
if "medras_ng_nurse_key" not in st.session_state:
    st.session_state["medras_ng_nurse_key"] = "否"
if "medras_ng_rt_key" not in st.session_state:
    st.session_state["medras_ng_rt_key"] = "否"
if "checklist_ng_key" not in st.session_state:
    st.session_state["checklist_ng_key"] = "無鼻胃管 (標準 leakage <= 45 Lpm)"

def update_ng_from_nurse():
    val = st.session_state["medras_ng_nurse_key"]
    st.session_state["medras_ng_rt_key"] = val
    st.session_state["checklist_ng_key"] = "有插鼻胃管 (標準 leakage <= 60 Lpm)" if val == "是" else "無鼻胃管 (標準 leakage <= 45 Lpm)"

def update_ng_from_rt():
    val = st.session_state["medras_ng_rt_key"]
    st.session_state["medras_ng_nurse_key"] = val
    st.session_state["checklist_ng_key"] = "有插鼻胃管 (標準 leakage <= 60 Lpm)" if val == "是" else "無鼻胃管 (標準 leakage <= 45 Lpm)"

def update_ng_from_checklist():
    is_yes = "有插鼻胃管" in st.session_state["checklist_ng_key"]
    val = "是" if is_yes else "否"
    st.session_state["medras_ng_nurse_key"] = val
    st.session_state["medras_ng_rt_key"] = val

# Check if streamlit-gsheets-connection is available in the runtime environment

has_gsheets_library = False
try:
    from streamlit_gsheets import GSheetsConnection
    has_gsheets_library = True
except ImportError:
    pass

cloud_sync_enabled = False
# If secrets are configured and library is loaded, enable cloud sync option
if has_gsheets_library and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    cloud_sync_enabled = True

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "👥 今日巡查在案名單",
    "📋 照護流程主軸", 
    "🔍 MedRAS 智能評估小卡", 
    "📊 最佳壓力區間查檢單 (三班KEY單)", 
    "⏰ 定期減壓時間點勾稽與備註", 
    "🛡️ 臉部皮膚完整度評估 (三班KEY單)",
    "💾 查檢紀錄儲存與雲端同步匯出"
])

# Variables to share across tabs for saving data
if "temp_records" not in st.session_state:
    st.session_state.temp_records = []

# TAB 1: ACTIVE CASES TRACKER
with tab1:
    st.header("👥 今日巡查在案名單 (Active Cases)")
    st.markdown("""
    本看板會自動分析雲端或本地儲存的歷史紀錄，透過 **「病歷號」** 進行追蹤與聚合，
    篩選出**「目前仍在使用 BIPAP 且尚未結案」**的病患。這能協助呼吸治療師（RT）與病房品管同仁快速掌握**「每天有哪些病人需要去探視與查檢」**！
    """)

    # Get data source: Cloud Sheets (if enabled) or Local session state
    data_df = None
    if cloud_sync_enabled:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            data_df = conn.read(worksheet="Sheet1", ttl="0")
        except Exception:
            pass
            
    if data_df is None or data_df.empty:
        # Fallback to local session records
        if len(st.session_state.temp_records) > 0:
            data_df = pd.DataFrame(st.session_state.temp_records)
            
    if data_df is not None and not data_df.empty:
        # Ensure all required columns are there
        required_cols = ["填表時間", "單位", "床號", "姓名", "病歷號", "病患狀態"]
        for col in required_cols:
            if col not in data_df.columns:
                data_df[col] = "N/A"
                
        # Parse fill time for correct chronological sorting
        try:
            data_df["填表時間_dt"] = pd.to_datetime(data_df["填表時間"])
        except Exception:
            data_df["填表時間_dt"] = data_df["填表時間"]
            
        # Chronological sort
        data_df_sorted = data_df.sort_values(by="填表時間_dt", ascending=True)
        
        # Calculate global Case Number (收案號碼) for each patient based on earliest chronological appearance
        first_records = data_df_sorted.drop_duplicates(subset=["病歷號"], keep="first")
        case_id_map = {chart_no: idx + 1 for idx, chart_no in enumerate(first_records["病歷號"])}

        # Group by Chart No (病歷號) to find the latest state of each patient
        latest_records = data_df_sorted.drop_duplicates(subset=["病歷號"], keep="last")
        
        # Filter active ones (病患狀態 != 結案/停用BIPAP (結案))
        active_records = latest_records[latest_records["病患狀態"] != "結案/停用BIPAP (結案)"]
        
        # Calculate statistics
        start_dates = data_df_sorted.groupby("病歷號")["填表時間"].first().to_dict()
        check_counts = data_df_sorted.groupby("病歷號").size().to_dict()
        
        if not active_records.empty:
            display_records = active_records.copy()
            display_records["收案號碼"] = display_records["病歷號"].map(case_id_map)
            display_records["收案日期/首登時間"] = display_records["病歷號"].map(start_dates)
            display_records["累計查檢單張數"] = display_records["病歷號"].map(check_counts)
            
            cols_to_show = [
                "收案號碼", "單位", "床號", "姓名", "病歷號", "BIPAP設定值", 
                "白班皮膚狀況", "小夜皮膚狀況", "大夜皮膚狀況",
                "減壓執行次數", "收案日期/首登時間", "累計查檢單張數"
            ]
            
            cols_to_show = [c for c in cols_to_show if c in display_records.columns]
            active_list_table = display_records[cols_to_show].reset_index(drop=True)
            active_list_table.insert(0, "項次", range(1, len(active_list_table) + 1))
            active_list_table.set_index("項次", inplace=True)
            
            st.subheader("📊 當前在案追蹤病人統計")
            st.success(f"📌 目前共有 **{len(active_list_table)}** 位病患正在進行 2-4 小時定期減壓防護模式。")
            st.dataframe(active_list_table, use_container_width=True)
            
            st.markdown("""
            > 💡 **呼吸治療師 (RT) / 護理組長巡查指南：**
            > 1. **核對實體小時鐘**：請至上述床位探視，確認呼吸器旁的「減壓小時鐘」指針是否調到正確的下一次減壓時間。
            > 2. **雙指鬆緊度稽核**：現場抽測頭帶鬆緊度（兩指寬幅）與漏氣量（有管路 <= 60 Lpm / 無管路 <= 45 Lpm）。
            > 3. **一鍵結案機制**：當病人已離線、出院或停止 BIPAP 醫囑，請於左側輸入病歷號並將狀態選為**「結案/停用BIPAP (結案)」**儲存，系統會自動將其移出此追蹤名單。
            """)
        else:
            st.info("🎉 恭喜！目前無任何在案追蹤病患。所有收案病人都已順利結案。")
    else:
        st.info("💡 雲端資料庫目前尚無收案紀錄。當同仁KEY入首筆單張紀錄後，此處將會自動呈現即時的每日巡查追蹤名單！")

# TAB 2: FLOWCHART
with tab2:
    st.header("📋 BIPAP 借機與照護完整流程圖")
    st.markdown("""
    本流程圖參考臨床 **「BIPAP 借機與照護流程圖 (護理單位適用)」**，協助快速掌握照護節點：
    """)
    
    st.graphviz_chart("""
    digraph G {
        node [shape=box, style=filled, fontname="Arial", fontsize=10];
        
        start [label="病房 BIPAP 借機需求\\n(7A / 7D / 14C / 14D)", fillcolor="#E0F2FE", color="#0284C7"];
        check_time [label="預計使用時間是否大於 12 小時？\\n或新借出的新病人？", fillcolor="#FEF3C7", color="#D97706", shape=diamond];
        borrow_trilogy [label="至管路櫃借用已綁好\\n文件與物品的 Trilogy 機器", fillcolor="#E0F2FE", color="#0284C7"];
        medras_eval [label="探視病人並勾選 MedRAS 小卡\\n(2個護理師題目 / 4個RT題目)", fillcolor="#F3E8FF", color="#7C3AED"];
        fp_recommend [label="符合任意 1 項？\\n建議自費購買 F&P 面罩 (可免減壓墊)", fillcolor="#D1FAE5", color="#059669", shape=diamond];
        buy_fp [label="引導家屬購買 F&P 面罩\\n(免減壓墊，內建NG槽)", fillcolor="#D1FAE5", color="#059669"];
        use_public [label="使用公費面罩\\n(需加強減壓防護)", fillcolor="#FEE2E2", color="#DC2626"];
        adjust_mask [label="確認面罩鬆緊度適當 (兩指寬/RT畫線標記)\\n漏氣監測合格 (<45 / <60 Lpm)", fillcolor="#E0F2FE", color="#0284C7"];
        audit_n [label="白班病房同仁 / 品管圈員協助稽核：\\n1. 減壓動態查檢交班表\\n2. 小時鐘指針設定", fillcolor="#F3E8FF", color="#7C3AED"];
        done [label="落實每 2-4 小時移除面罩 15 分鐘\\n持續追蹤皮膚狀況！", fillcolor="#D1FAE5", color="#059669"];

        start -> check_time;
        check_time -> borrow_trilogy [label="是"];
        check_time -> adjust_mask [label="否 (小於 12 小時)"];
        borrow_trilogy -> medras_eval;
        medras_eval -> fp_recommend;
        fp_recommend -> buy_fp [label="是 (符合任意 1 點)"];
        fp_recommend -> use_public [label="否 (皆不符合)"];
        buy_fp -> adjust_mask;
        use_public -> adjust_mask;
        adjust_mask -> audit_n;
        audit_n -> done;
    }
    """)

# TAB 3: MedRAS
with tab3:
    st.header("🔍 MedRAS 智能評估小卡 (護理師 & RT 聯合版)")
    st.markdown("""
    根據 **FACE 圈 MedRAS 護備小卡** 指引，評估病患特質。
    不論是護理師評估或是呼吸治療師 (RT) 評估，<b>只要其中任意一個項目符合</b>，即可建議家屬自費購買 **F&P 面罩** (臨床實證受壓極低，且兩側有設計 NG 槽，<b>可以不需減壓墊</b>)。
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👩‍⚕️ 護理師 MedRAS 評估")
        medras_ng_select = st.selectbox(
            "1. 臨床上是否有使用鼻胃管 (NG)？", 
            ["否", "是"], 
            key="medras_ng_nurse_key",
            on_change=update_ng_from_nurse,
            help="使用鼻胃管會增加管道壓迫風險，適合 F&P 面罩雙側 NG 槽。(已跨頁面智慧連動)"
        )
        medras_skin_select = st.selectbox(
            "2. 臉部配戴面罩處是否有破皮，或屬於易破皮之高風險膚質？", 
            ["否", "是"], 
            index=0,
            help="高風險脆弱膚質或已有壓傷者，建議更換低壓面罩。"
        )
        
        st.write("") # Spacer
        st.subheader("🩺 呼吸治療師 (RT) MedRAS 評估")
        rt_medras_ng_select = st.selectbox(
            "1. 臨床上是否有使用鼻胃管 (NG)？ (RT版)", 
            ["否", "是"], 
            key="medras_ng_rt_key",
            on_change=update_ng_from_rt,
            help="RT 評估病患鼻胃管狀態。(已跨頁面智慧連動)"
        )
        rt_medras_device_select = st.selectbox(
            "2. 目前使用的減壓設備：", 
            ["無", "紗布", "減壓墊"], 
            index=0,
            help="若已需使用紗布或減壓墊，顯示患者臉部有受壓痕跡或不適。"
        )
        rt_medras_skin_select = st.selectbox(
            "3. 臉部配戴面罩處是否有破皮？ (RT版)", 
            ["否", "是"], 
            index=0,
            help="RT 評估臉部配戴處是否有破皮。"
        )
        rt_medras_suit_select = st.selectbox(
            "4. 面罩是否適合病人？ (Ex: 臉凹、介於現有 S/M/L 尺寸中間)", 
            ["是", "否"], 
            index=0,
            help="若選擇『否』，代表現有面罩與病患臉型不適配，極易造成大漏氣或局部壓迫。"
        )
        
    with col2:
        st.subheader("💡 系統評估與決策建議")
        
        nurse_risk = (medras_ng_select == "是") or (medras_skin_select == "是")
        rt_risk = (rt_medras_ng_select == "是") or (rt_medras_skin_select == "是") or (rt_medras_suit_select == "否") or (rt_medras_device_select in ["紗布", "減壓墊"])
        
        has_risk = nurse_risk or rt_risk
        
        triggers = []
        if medras_ng_select == "是": triggers.append("護理師評估：使用鼻胃管 (NG)")
        if medras_skin_select == "是": triggers.append("護理師評估：臉部皮膚脆弱或破皮")
        if rt_medras_ng_select == "是": triggers.append("RT評估：使用鼻胃管 (NG)")
        if rt_medras_device_select in ["紗布", "減壓墊"]: triggers.append(f"RT評估：已使用減壓設備 ({rt_medras_device_select})")
        if rt_medras_skin_select == "是": triggers.append("RT評估：臉部配戴處已有破皮")
        if rt_medras_suit_select == "否": triggers.append("RT評估：面罩不適合病人 (臉凹或尺寸中間)")

        if has_risk:
            reasons_html = "".join([f"<li>{t}</li>" for t in triggers])
            st.markdown(f"""
            <div class='success-box'>
                <p class='info-tag'>🌟 決策：強烈建議使用自費 F&P 面罩！</p>
                <ul>
                    <li><b>觸發原因：</b> 病患符合以下 MedRAS 指標：
                        <ul>{reasons_html}</ul>
                    </li>
                    <li><b>優勢：</b> F&P 面罩具有雙側 NG 槽，可防管路壓迫；且假人實驗顯示 F&P 臉頰/下巴受壓極低。</li>
                    <li><b>好消息：可以不需另外使用減壓墊！</b> 減壓墊容易造成額外漏氣，不加減壓墊更安全。</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-box'>
                <p class='info-tag'>⚖️ 決策：可先使用公費面罩</p>
                <ul>
                    <li><b>評估結果：</b> 目前護理與 RT 評估皆未達高風險指標（無鼻胃管、皮膚完整、面罩合適、無使用減壓敷料）。</li>
                    <li><b>照護重點：</b> 仍須嚴格遵循面罩配戴標準 SOP，並在 RT 初次定位後<b>於頭綁帶處做畫線記號</b>，避免家屬或同仁過度拉緊。</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# TAB 4: THREE SHIFTS CHECKLIST (BATCH KEYING)
with tab4:
    st.header("📊 最佳壓力區間 & 三班查檢交班單 (紙本單張批次KEY單)")
    st.markdown("請對照紙本查檢交班單，**一次輸入 yesterday/當日 白班 (N)、小夜 (HN)、大夜 (ON) 的完整數據**：")
    
    st.subheader("1. 鼻胃管管路條件")
    has_ng_input = st.selectbox(
        "病患目前是否有插鼻胃管？", 
        ["無鼻胃管 (標準 leakage <= 45 Lpm)", "有插鼻胃管 (標準 leakage <= 60 Lpm)"],
        key="checklist_ng_key",
        on_change=update_ng_from_checklist,
        help="連動 MedRAS 評估結果，不論在何處切換皆自動同步全單。"
    )
    st.caption("🔗 **智慧連動提醒：** 鼻胃管 (NG) 狀態已與 MedRAS 小卡 (護理/RT版) 自動同步。更改任意一處，全單自動更新！")
    
    st.divider()
    st.subheader("2. 三班漏氣量與固定帶張力對照輸入 (含「未填寫」遺漏選項)")
    
    col_shift_N, col_shift_HN, col_shift_ON = st.columns(3)
    
    with col_shift_N:
        st.markdown("### ☀️ 白班 (N)")
        leak_val_N = st.number_input("白班 漏氣量 (Lpm)", min_value=0, max_value=120, value=30, step=1, key="leak_val_N")
        leak_status_N = st.selectbox("白班 漏氣量判定", ["合格", "不合格", "未填寫"], index=0, key="leak_status_N")
        tension_N = st.selectbox("白班 固定帶張力 (2指寬/畫線記號)", ["符合", "太緊", "太鬆", "未填寫"], index=0, key="tension_N")
        
    with col_shift_HN:
        st.markdown("### 🌆 小夜 (HN)")
        leak_val_HN = st.number_input("小夜 漏氣量 (Lpm)", min_value=0, max_value=120, value=30, step=1, key="leak_val_HN")
        leak_status_HN = st.selectbox("小夜 漏氣量判定", ["合格", "不合格", "未填寫"], index=0, key="leak_status_HN")
        tension_HN = st.selectbox("小夜 固定帶張力 (2指寬/畫線記號)", ["符合", "太緊", "太鬆", "未填寫"], index=0, key="tension_HN")

    with col_shift_ON:
        st.markdown("### 🌙 大夜 (ON)")
        leak_val_ON = st.number_input("大夜 漏氣量 (Lpm)", min_value=0, max_value=120, value=30, step=1, key="leak_val_ON")
        leak_status_ON = st.selectbox("大夜 漏氣量判定", ["合格", "不合格", "未填寫"], index=0, key="leak_status_ON")
        tension_ON = st.selectbox("大夜 固定帶張力 (2指寬/畫線記號)", ["符合", "太緊", "太鬆", "未填寫"], index=0, key="tension_ON")

# TAB 5: DECOMPRESSION MULTI-SELECT CHECKLIST
with tab5:
    st.header("⏰ 定期減壓時間點勾稽與備註 (06:00 - 24:00)")
    st.markdown("""
    根據臨床照護指引：**連續使用 12 小時以上之病患，於 06:00 - 24:00 期間，每 2-4 小時應移除面罩讓皮膚休息 15 分鐘。**
    *(註：00:00 - 06:00 大夜班期間不執行 OFF，以利病患睡眠維持)*
    """)
    
    st.subheader("1. 請勾選昨日本日單張上記錄有執行「移除面罩休息 15 分鐘」的時間點：")
    decomp_hours_options = [
        "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", 
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", 
        "20:00", "21:00", "22:00", "23:00", "24:00"
    ]
    
    decomp_selected = st.multiselect(
        "點擊下拉勾選已執行減壓的時間點 (可複選)：",
        options=decomp_hours_options,
        default=["09:00", "13:00", "17:00", "21:00"],
        help="請根據紙本單張上記錄打勾的時間點進行批次輸入。"
    )
    
    st.info(f"📌 目前已勾選執行減壓次數： **{len(decomp_selected)}** 次 ({', '.join(decomp_selected) if decomp_selected else '無勾選'})")
    
    st.divider()
    st.subheader("2. 定期減壓未執行原因 / 備註紀錄：")
    decomp_reasons = st.multiselect(
        "未執行常見原因（可複選）：",
        ["病人不配合", "血氧不穩定", "呼吸型態不佳", "其他"],
        default=[]
    )
    decomp_note_text = st.text_input("其他詳細備註說明", placeholder="例：20:00 因病人躁動不配合未執行；或 14:00 執行噴霧治療併同減壓...")
    
    full_decomp_note = ""
    if decomp_reasons:
        full_decomp_note += f"【原因】{', '.join(decomp_reasons)} "
    if decomp_note_text:
        full_decomp_note += f"{decomp_note_text}"
    if not full_decomp_note:
        full_decomp_note = "無特殊備註"

# TAB 6: THREE SHIFTS SKIN ASSESSMENT
with tab6:
    st.header("🛡️ 臉部皮膚完整度評估 (NPIAP 標準 - 三班KEY單)")
    st.markdown("請對照紙本查檢單，記錄該病患初次 Baseline 及三班臉部皮膚狀態：")
    
    st.markdown("---")
    st.subheader("📌 1. 臨床品質關鍵檢核：是否為初次配戴第一天？")
    is_first_day = st.checkbox(
        "⭐ 本日紀錄包含該病患【初次配戴第一天】？ (品管圈核心項目！勾選後請輸入 Baseline 膚況)",
        value=False,
        help="第一天上機新案最容易遺漏初始膚況 (Baseline)。勾選後系統將引導您輸入初始膚況！"
    )
    
    baseline_status = "N/A (非第一天)"
    if is_first_day:
        st.markdown("""
        <div class='alert-box' style='border-left: 8px solid #F59E0B;'>
            <p class='info-tag'>🚨 臨床品管防護警告：第一天 Baseline 評估</p>
            <ul>
                <li>此病患符合<b>使用第一天</b>，請務必輸入其<b>上機前初始臉部皮膚狀況</b>。</li>
                <li>這對品管圈（QCC）計算「新發壓傷率」極為重要！</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        baseline_status = st.selectbox("📌 請選取病患「第一天」上機時臉部 Baseline 膚況：", [
            "完好 (NL)",
            "Stage 1",
            "Stage 2",
            "Stage 3-4",
            "DTI",
            "X (無法分級)",
            "未填寫"
        ], index=0)
    else:
        st.markdown("""
        <div class='success-box' style='border-left: 5px solid #10B981;'>
            <p style='margin: 0;'>ℹ️ 目前非上機第一天，系統將紀錄三班常規追蹤。請於下方直接選擇三班膚況。</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 2. 當日三班臉部皮膚完整度評估 (含「未填寫」遺漏選項)")
    
    skin_options = ["完好 (NL)", "Stage 1", "Stage 2", "Stage 3-4", "DTI", "X (無法分級)", "未填寫"]
    
    col_skin_N, col_skin_HN, col_skin_ON = st.columns(3)
    
    with col_skin_N:
        st.markdown("### ☀️ 白班 (N)")
        skin_N = st.selectbox("白班 皮膚狀況", skin_options, index=0, key="skin_N")

    with col_skin_HN:
        st.markdown("### 🌆 小夜 (HN)")
        skin_HN = st.selectbox("小夜 皮膚狀況", skin_options, index=0, key="skin_HN")

    with col_skin_ON:
        st.markdown("### 🌙 大夜 (ON)")
        skin_ON = st.selectbox("大夜 皮膚狀況", skin_options, index=0, key="skin_ON")

    st.divider()
    st.subheader("🚨 臨床照護警示與處理指引")
    
    all_skins = [skin_N, skin_HN, skin_ON]
    if any("Stage 2" in s or "Stage 3" in s or "DTI" in s or "X" in s for s in all_skins):
        st.markdown("""
        <div class='danger-box'>
            🛑 <b>緊急：出現 Stage 2 以上、DTI 或無法分級之壓傷！</b><br>
            1. <b>請立即通報 RT 共同評估！</b><br>
            2. <b>填寫醫療器材相關壓力性損傷 (MDRPI) 通報單。</b><br>
            3. 執行皮膚照護 SOP，依醫囑給予合適之敷料換藥照護。<br>
        </div>
        """, unsafe_allow_html=True)
    elif any("Stage 1" in s for s in all_skins):
        st.markdown("""
        <div class='alert-box' style='border-left: 5px solid red;'>
            🔴 <b>警告：出現 I 級發紅壓傷！</b><br>
            1. <b>請通報 RT！</b> 評估是否更換低壓迫品牌面罩 (如 F&P) 或微調參數。<br>
            2. 回歸頭帶兩指幅寬度。<br>
            3. 縮短減壓間隔 (改為每 2 小時減壓一次)。
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='success-box'>
            🟢 <b>皮膚狀況良好或常規維持中：</b><br>
            請持續落實每 2-4 小時定期移除面罩減壓 15 分鐘，維持最佳照護品質！
        </div>
        """, unsafe_allow_html=True)

# TAB 7: SAVE & EXPORT
with tab7:
    st.header("💾 本次查檢資料暫存與雲端同步匯出")
    st.markdown("""
    本分頁支援**「本地暫存 CSV 下載」**與**「Streamlit Cloud + Google Sheets 雲端連線同步」**雙軌制。
    """)

    # Instruction Expander
    with st.expander("🛠️ 雲端同步 (Google Sheets) 設定指南"):
        st.markdown("""
        #### **第一步：建立 Google 試算表**
        1. 在您的 Google 雲端硬碟建立一個新的「Google 試算表」，命名標籤頁為 **`Sheet1`**。
        2. 第一列欄標建議包含：
           `填表時間,單位,床號,病患狀態,姓名,病歷號,當日使用醫囑,BIPAP設定值,是否為初次上機第一天,第一天臉部Baseline皮膚狀況,鼻胃管狀態,白班漏氣量(Lpm),白班漏氣判定,白班固定帶張力,小夜漏氣量(Lpm),小夜漏氣判定,小夜固定帶張力,大夜漏氣量(Lpm),大夜漏氣判定,大夜固定帶張力,已執行減壓時間點,減壓執行次數,減壓備註與未執行原因,白班皮膚狀況,小夜皮膚狀況,大夜皮膚狀況,KEY單人員簽名`
        """)

    # Construct complete structured current entry for 3 shifts
    current_entry = {
        "填表時間": entry_date_str,
        "單位": unit_select,
        "床號": bed_no if bed_no else "未填寫",
        "病患狀態": track_status,
        "姓名": patient_name if patient_name else "未填寫",
        "病歷號": chart_no if chart_no else "未填寫",
        "當日使用醫囑": bipap_order if bipap_order else "未填寫",
        "BIPAP設定值": bipap_settings,
        "是否為初次上機第一天": "是" if is_first_day else "否",
        "第一天臉部Baseline皮膚狀況": baseline_status.split(" - ")[0] if is_first_day else "N/A",
        "鼻胃管狀態": has_ng_input.split(" ")[0],
        "白班漏氣量(Lpm)": leak_val_N,
        "白班漏氣判定": leak_status_N,
        "白班固定帶張力": tension_N,
        "小夜漏氣量(Lpm)": leak_val_HN,
        "小夜漏氣判定": leak_status_HN,
        "小夜固定帶張力": tension_HN,
        "大夜漏氣量(Lpm)": leak_val_ON,
        "大夜漏氣判定": leak_status_ON,
        "大夜固定帶張力": tension_ON,
        "已執行減壓時間點": ", ".join(decomp_selected) if decomp_selected else "未勾選",
        "減壓執行次數": len(decomp_selected),
        "減壓備註與未執行原因": full_decomp_note,
        "白班皮膚狀況": skin_N.split(" - ")[0],
        "小夜皮膚狀況": skin_HN.split(" - ")[0],
        "大夜皮膚狀況": skin_ON.split(" - ")[0],
        "KEY單人員簽名": nurse_name if nurse_name else "未簽名"
    }
    
    st.subheader("📝 本次 KEY 單資料預覽 (三班綜合數據)")
    preview_df = pd.DataFrame([current_entry]).T
    preview_df.columns = ["當前輸入數值"]
    st.table(preview_df)

    if cloud_sync_enabled:
        st.markdown("""
        <div class='success-box' style='border-left: 8px solid #10B981;'>
            ✨ <b>雲端資料庫狀態：已連線！</b><br>
            系統偵測到 Google Sheets 連線設定已就緒。點擊下方儲存按鈕將同步寫入雲端與本機！
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='alert-box' style='border-left: 5px solid #F59E0B;'>
            ℹ️ <b>目前運行模式：本地離線暫存模式</b><br>
            未檢測到 Google Sheets 雲端配置或處於本機開發環境。點擊下方按鈕將資料<b>儲存於此瀏覽器暫存清單中</b>，您依然可以正常一鍵匯出下載 CSV 報表！
        </div>
        """, unsafe_allow_html=True)

    col_btn1, col_col2 = st.columns(2)
    with col_btn1:
        if st.button("📥 儲存此筆資料並執行同步", use_container_width=True):
            if not bed_no or not patient_name or not chart_no:
                st.warning("⚠️ 請確認左側【病患基本資料】(床號、姓名、病歷號) 是否填寫完整再儲存！")
            else:
                # 1. Always save to local session state
                st.session_state.temp_records.append(current_entry)
                local_success_msg = f"🎉 成功暫存於本機！目前累計暫存筆數：{len(st.session_state.temp_records)} 筆。"
                
                # 2. Try to sync with Google Sheets if configured
                if cloud_sync_enabled:
                    with st.spinner("☁️ 正在同步資料至 Google Sheets 雲端資料庫..."):
                        try:
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            try:
                                existing_df = conn.read(worksheet="Sheet1", ttl="0")
                            except Exception:
                                existing_df = pd.DataFrame(columns=list(current_entry.keys()))
                                
                            new_row_df = pd.DataFrame([current_entry])
                            combined_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                            
                            conn.update(worksheet="Sheet1", data=combined_df)
                            st.success(f"{local_success_msg} \n\n ☁️ 雲端同步成功！數據已安全寫入 Google Sheets。")
                        except Exception as cloud_err:
                            st.error(f"⚠️ 本地暫存成功，但雲端同步失敗：{str(cloud_err)}")
                            st.info("請檢查您的 Streamlit Cloud Secrets 設定與 Google 試算表共用權限。")
                else:
                    st.success(local_success_msg)
                
    with col_col2:
        if st.button("🗑️ 清空本地暫存清單", use_container_width=True):
            st.session_state.temp_records = []
            st.info("已清空本地瀏覽器暫存數據。")

    # Display Accumulated Table
    st.subheader("📋 目前累計查檢清單 (交班與收案總表)")
    if len(st.session_state.temp_records) > 0:
        history_df = pd.DataFrame(st.session_state.temp_records)
        st.dataframe(history_df, use_container_width=True)
        
        csv_data = history_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 匯出並下載為交班 CSV 報表 (可用 Excel 直接打開)",
            data=csv_data,
            file_name=f"NIV_Care_Report_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("💡 目前暫無已儲存的紀錄。在上方填寫完畢並點選「儲存此筆資料並執行同步」後，數據就會顯示在這裡，並可以匯出下載成 Excel 檔案喔！")

# Footer
st.divider()
st.markdown("© 2026 國立臺灣大學醫學院附設醫院 - FACE 圈 | 罩護無痕品管專案 | 呼吸治療科、護理部、醫工部、品質管理中心聯合敬製")
