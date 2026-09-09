import streamlit as st
import datetime
import time
import pandas as pd
import os

# Set Page Config
st.set_page_config(
    page_title="FACE 圈 - NIV 罩護無痕 臨床照護助手 (v12 日期可調版)",
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

nurse_name = st.sidebar.text_input("填表人員/護理師簽名", placeholder="請輸入姓名")
st.sidebar.subheader("📅 填表日期與時間 (可自由調整補登)")
col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    entry_date = st.date_input("填表日期", value=datetime.date.today(), help="預設為今日，若為事後補單可選擇過去日期")
with col_d2:
    entry_time = st.time_input("填表時間", value=datetime.datetime.now().time(), help="預設為當前時間，可手動微調")

entry_datetime = datetime.datetime.combine(entry_date, entry_time)
st.sidebar.markdown(f"**選定紀錄時間：** `{entry_datetime.strftime('%Y-%m-%d %H:%M')}`")

# Navigation Tabs
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
    "📊 最佳壓力區間查檢表", 
    "⏰ 4小時定期減壓定時器", 
    "🛡️ 臉部皮膚完整度評估",
    "💾 查檢紀錄儲存與雲端同步匯出"
])

# Variables to share across tabs for saving data
if "temp_records" not in st.session_state:
    st.session_state.temp_records = []

# TAB 1: FLOWCHART
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
        # Standardize columns (just in case they are missing, though they shouldn't be)
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
        
        # Group by Chart No (病歷號) to find the latest state of each patient
        # We drop duplicates keep last to get the latest record
        latest_records = data_df_sorted.drop_duplicates(subset=["病歷號"], keep="last")
        
        # Filter active ones (病患狀態 != 結案/停用BIPAP (結案))
        active_records = latest_records[latest_records["病患狀態"] != "結案/停用BIPAP (結案)"]
        
        # Also calculate extra statistics for active cases:
        # - NIV Start Date (earliest record for this Chart No)
        # - Audit Count (total checks for this Chart No)
        start_dates = data_df_sorted.groupby("病歷號")["填表時間"].first().to_dict()
        check_counts = data_df_sorted.groupby("病歷號").size().to_dict()
        
        if not active_records.empty:
            # Build display dataframe
            display_records = active_records.copy()
            display_records["收案日期/首登時間"] = display_records["病歷號"].map(start_dates)
            display_records["累計查檢次數"] = display_records["病歷號"].map(check_counts)
            
            # Select columns to display beautifully
            cols_to_show = [
                "單位", "床號", "姓名", "病歷號", "BIPAP設定值", 
                "當班皮膚狀況", "漏氣量(Lpm)", "漏氣量判定", 
                "下一次減壓時間", "收案日期/首登時間", "累計查檢次數"
            ]
            
            # Keep only columns that exist
            cols_to_show = [c for c in cols_to_show if c in display_records.columns]
            
            active_list_table = display_records[cols_to_show].reset_index(drop=True)
            
            # Show summary stats
            st.subheader("📊 當前在案追蹤病人統計")
            st.success(f"📌 目前共有 **{len(active_list_table)}** 位病患正在進行 2-4 小時定期減壓防護模式。")
            
            # Show Table with color highlighting
            st.dataframe(active_list_table, use_container_width=True)
            
            # Tips for RTs
            st.markdown("""
            > 💡 **呼吸治療師 (RT) / 護理組長巡查指南：**
            > 1. **核對實體小時鐘**：請至上述床位探視，確認呼吸器旁的「減壓小時鐘」指針是否調到正確的下一次減壓時間。
            > 2. **雙指鬆緊度稽核**：現場抽測頭帶鬆緊度（兩指寬幅）與漏氣量（有管路 <= 60 Lpm / 無管路 <= 45 Lpm）。
            > 3. **一鍵結案機制**：當病人已離線、出院或停止 BIPAP 醫囑，請於左側輸入病歷號並將狀態選為**「結案/停用BIPAP (結案)」**儲存，系統會自動將其移出此追蹤名單。
            """)
        else:
            st.info("🎉 恭喜！目前無任何在案追蹤病患。所有收案病人都已順利結案。")
    else:
        st.info("💡 雲端資料庫目前尚無收案紀錄。當護理同仁填寫並儲存首筆病患查檢紀錄後，此處將會自動呈現即時的每日巡查追蹤名單！")


with tab2:
    st.header("📋 BIPAP 借機與照護完整流程圖")
    st.markdown("""
    本流程圖參考臨床 **「BIPAP 借機與照護流程圖 (護理單位適用)」**，協助快速掌握照護節點：
    """)
    
    st.graphviz_chart("""
    # ... graphviz definition ...
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

# TAB 2: MedRAS
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
            index=0,
            help="使用鼻胃管會增加管道壓迫風險，適合 F&P 面罩雙側 NG 槽。"
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
            index=0,
            help="RT 評估病患鼻胃管狀態。"
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
        
        # Risk flags
        nurse_risk = (medras_ng_select == "是") or (medras_skin_select == "是")
        rt_risk = (rt_medras_ng_select == "是") or (rt_medras_skin_select == "true" or rt_medras_skin_select == "是") or (rt_medras_suit_select == "否") or (rt_medras_device_select in ["紗布", "減壓墊"])
        
        has_risk = nurse_risk or rt_risk
        
        # Details of trigger
        triggers = []
        if medras_ng_select == "是": triggers.append("護理師評估：使用鼻胃管 (NG)")
        if medras_skin_select == "是": triggers.append("護理師評估：臉部皮膚脆弱或破皮")
        if rt_medras_ng_select == "強" or rt_medras_ng_select == "是": triggers.append("RT評估：使用鼻胃管 (NG)")
        if rt_medras_device_select in ["紗布", "減壓墊"]: triggers.append(f"RT評估：已使用減壓設備 ({rt_medras_device_select})")
        if rt_medras_skin_select == "是": triggers.append("RT評估：臉部配戴處已有破皮")
        if rt_medras_suit_select == "否": triggers.append("RT評估：面罩不適合病人 (臉凹或尺寸中間)")

        if has_risk:
            # Format reasons list
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

with tab4:
    st.header("📊 最佳壓力區間 & 查檢交班單")
    st.markdown("請每班護理師（白班、小夜、大夜）依時間點核對並落實以下查檢項目：")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. 漏氣量監測 (Leakage Check)")
        has_ng_input = st.selectbox("病患目前是否有插鼻胃管？", ["無鼻胃管", "有插鼻胃管"])
        leak_value = st.number_input("請輸入目前呼吸器面板顯示的漏氣量 (Lpm)", min_value=0, max_value=120, value=30, step=1)
        
        # Leak logic
        is_leak_ok = False
        if has_ng_input == "無鼻胃管":
            if leak_value <= 45:
                is_leak_ok = True
                st.success(f"✅ 合格 (無鼻胃管，理想值為 45 Lpm 以下，目前：{leak_value} Lpm)")
            else:
                st.error(f"❌ 異常 (無鼻胃管，理想值為 45 Lpm 以下，目前：{leak_value} Lpm)")
                st.warning("⚠️ 漏氣排除步驟：1. 檢查面罩是否戴正、有無歪斜；2. 若仍漏氣，微調綁帶；3. 面罩變形代表太緊，請重新調整，勿一味拉緊！")
        else:
            if leak_value <= 60:
                is_leak_ok = True
                st.success(f"✅ 合格 (有插鼻胃管，建議在 60 Lpm 以下，目前：{leak_value} Lpm)")
            else:
                st.error(f"❌ 異常 (有插鼻胃管，建議在 60 Lpm 以下，目前：{leak_value} Lpm)")
                st.warning("⚠️ 漏氣排除步驟：檢查面罩是否緊貼鼻翼，管路是否嵌入 NG 槽，調整後仍異常請聯絡 RT 協助。")

    with col2:
        st.subheader("2. 固定帶張力評估 (Tension Check)")
        tension_option = st.radio("檢查綁帶鬆緊度狀態：", [
            "符合標準：可伸入兩指寬 (併攏測試) 或符合 RT 畫線記號處",
            "異常：太緊（面罩變形、病患疼痛、無指幅空間）",
            "異常：太鬆（造成大洩漏、警報不斷）"
        ])
        
        if "符合標準" in tension_option:
            st.success("✅ 符合鼻樑安全受壓區間。請維持此鬆緊度！")
            tension_status = "符合"
        else:
            st.error("❌ 鬆緊度不合格！請依兩指幅寬度，重新微調扣環張力。")
            tension_status = "太緊 / 太鬆"

# TAB 4: TIMER
with tab5:
    st.header("⏰ 4小時定期減壓 15 分鐘計時器")
    st.markdown("""
    根據臨床標準：**連續使用 12 小時以上之病患，於 06:00 - 24:00 期間，每 2-4 小時應移除面罩讓皮膚休息 15 分鐘。**
    *(註：0:00 - 06:00 大夜班期間不執行 OFF，以利病患睡眠維持)*
    """)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("⏱️ 減壓休息定時器")
        st.info("當您協助病患移除面罩進行 15 分鐘皮膚休息時，請點擊下方按鈕開始計時：")
        
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
            
        if st.button("開始 15 分鐘減壓計時", key="start_timer"):
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
            
        if st.session_state.timer_running:
            elapsed = time.time() - st.session_state.start_time
            remaining = int(15 * 60 - elapsed)
            
            if remaining > 0:
                mins, secs = divmod(remaining, 60)
                st.metric(label="⏳ 減壓休息剩餘時間", value=f"{mins:02d}:{secs:02d}")
                time.sleep(1)
                st.rerun()
            else:
                st.balloons()
                st.success("🎉 15 分鐘休息結束！請協助病患重新正確配戴面罩並確認鬆緊度。")
                st.session_state.timer_running = False
                
    with col_t2:
        st.subheader("🕒 小時鐘設定指引")
        st.markdown("""
        為了跨班、跨職類有效交班，我們在呼吸器旁備有**「實體減壓小時鐘」**：
        1. **每次執行完減壓 15 分鐘後**，需將小時鐘的指針轉至**「下一次需要休息的時間」**。
        2. **範例：** 這次是 11:00 移除面罩休息，則 11:00 + 4 小時 = **15:00 (下午3點)**，請將時鐘指針轉到 **3 點鐘** 位置，交班給下一班同仁。
        """)
        
        curr_hour = st.slider("請選取「本次」開始休息時間 (時)：", min_value=6, max_value=20, value=11, step=1)
        interval = st.selectbox("設定減壓頻率：", ["Q4H (每4小時休息一次)", "Q3H (每3小時休息一次)", "Q2H (每2小時休息一次)"])
        
        gap = 4
        if "Q3H" in interval: gap = 3
        elif "Q2H" in interval: gap = 2
        
        next_hour = curr_hour + gap
        next_time_display = f"{(next_hour - 12 if next_hour > 12 else next_hour)} 點鐘"
        st.markdown(f"""
        <div class='success-box'>
            👉 <b>【小時鐘指針指引】</b><br>\n            本次休息：{curr_hour:02d}:00<br>\n            下一次減壓休息時間：<b>{next_hour:02d}:00</b><br>\n            <b>請將床邊實體小時鐘指針，調整轉至： <span style='font-size:20px; color:red;'>{next_time_display}</span></b>！\n        </div>
        """, unsafe_allow_html=True)

# TAB 5: SKIN
with tab6:
    st.header("🛡️ 臉部皮膚完整度評估 (NPIAP 標準)")
    st.markdown("請每班護理師（白班、小夜、大夜）細心評估病患鼻樑、臉頰、下巴皮膚狀態。")
    
    # High-visibility Day 1 Baseline Skin Assessment Toggle
    st.markdown("---")
    st.subheader("📌 臨床品質關鍵檢核：是否為初次配戴第一天？")
    is_first_day = st.checkbox(
        "⭐ 本班為該病患【初次配戴第一天】？ (品管圈核心項目！勾選後強制要求輸入 Baseline 膚況)",
        value=False,
        help="第一天上機新案的最容易遺漏初始膚況 (Baseline)。勾選後系統將強制引導您輸入初始膚況！"
    )
    
    baseline_status = "N/A (非第一天)"
    if is_first_day:
        st.markdown("""
        <div class='alert-box' style='border-left: 8px solid #F59E0B;'>
            <p class='info-tag'>🚨 臨床品管防護警告：第一天 Baseline 評估</p>
            <ul>
                <li>此病患符合<b>使用第一天</b>，請務必為其評估並記錄<b>上機前初始臉部皮膚狀況</b>。</li>
                <li>這對品管圈（QCC）計算「新發壓傷率」極為重要，可作為後續膚況變化的重要對照點！</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        baseline_status = st.selectbox("📌 請選取病患「第一天」上機時臉部 Baseline 膚況：", [
            "完好 (NL) - 皮膚完整無紅斑",
            "Stage 1 - 壓之不退色的指壓紅斑 (完整皮膚)",
            "Stage 2 - 部分皮層缺失 (有水泡或表淺潰瘍)",
            "Stage 3-4 - 全皮層缺失 (深層組織受損)",
            "DTI (深部組織損傷) - 持續壓之不退色",
            "X - 無法分級 (焦痂覆蓋)"
        ])
    else:
        st.markdown("""
        <div class='success-box' style='border-left: 5px solid #10B981;'>
            <p style='margin: 0;'>ℹ️ 目前非上機第一天，系統將自動套用日常當班追蹤。請於下方直接評估當班膚況。</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 當班常規皮膚完整度評估 (日常評估)")
    skin_status = st.selectbox("🔍 臉部皮膚目前狀態：", [
        "完好 (NL) - 皮膚完整無紅斑",
        "Stage 1 - 壓之不退色的指壓紅斑 (完整皮膚)",
        "Stage 2 - 部分皮層缺失 (有水泡或表淺潰瘍)",
        "Stage 3-4 - 全皮層缺失 (深層組織受損)",
        "DTI (深部組織損傷) - 持續壓之不退色的深紅色、紫色病變",
        "X - 無法分級 (焦痂覆蓋無法評估)"
    ])
    
    st.subheader("🚨 臨床照護指引")
    if "完好" in skin_status:
        st.markdown("""
        <div class='success-box'>
            🟢 <b>皮膚完整：</b><br>\n            1. 請持續落實每 2-4 小時定期移除面罩減壓 15 分鐘。<br>\n            2. 每次重新配戴時確認符合綁帶「兩指幅寬」或「RT 畫線記號」。<br>\n            3. 保持皮膚清潔，防範因油脂下滑。<br>\n            4. 這是預防照護的最佳狀態！做得好！\n        </div>
        """, unsafe_allow_html=True)
    elif "Stage 1" in skin_status:
        st.markdown("""
        <div class='alert-box' style='border-left: 5px solid red;'>\n            🔴 <b>警告：出現 I 級發紅壓傷！</b><br>\n            1. <b>請立即通報 RT！</b> 由 RT 評估是否需要更換低壓迫品牌面罩 (如 F&P) 或調整參數。<br>\n            2. 檢查頭帶是否拉得太緊，回歸兩指幅寬度。<br>\n            3. 若有水膠體敷料，請評估是否更換或黏貼預防防護。<br>\n            4. 縮短減壓時間間隔 (改為 2 小時減壓一次，每次 15 分鐘)。\n        </div>\n        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='danger-box'>\n            🛑 <b>緊急：出現 Stage 2 以上或 DTI 壓傷！</b><br>\n            1. <b>請立即聯絡 RT 到床邊共同評估！</b><br>\n            2. <b>執行通報流程：</b> 填寫醫療器材相關壓力性損傷 (MDRPI) 通報單。<br>\n            3. 執行皮膚照護 SOP，依醫囑給予合適之敷料 (如泡沫敷料、敷料減壓) 換藥照護。<br>\n            4. 密切監測，與醫師討論是否能有間歇呼吸器訓練或調降使用時間。\n        </div>\n        """, unsafe_allow_html=True)

# TAB 6: SAVE & EXPORT
with tab7:
    st.header("💾 本次查檢資料暫存與雲端同步匯出")
    st.markdown("""
    本分頁為本 App 的核心資料樞紐，支援**「本地暫存 CSV 下載」**與**「Streamlit Cloud + Google Sheets 雲端連線同步」**雙軌制。
    
    ### ☁️ 方案二：Google Sheets 雲端同步說明
    若您將此 App 部署於 Streamlit Cloud，您只要完成下方簡單配置，護理同仁填寫的每一筆紀錄都會**即時、自動地同步寫入您的 Google 試算表雲端硬碟**，跨單位（7A、7D、14C、14D）大數據一鍵彙整！
    """)

    # Instruction Expander
    with st.expander("🛠️ 雲端同步 (Google Sheets) 詳細設定指南"):
        st.markdown("""
        #### **第一步：建立 Google 試算表**
        1. 在您的 Google 雲端硬碟建立一個新的「Google 試算表」。
        2. 將工作表命名為 **`Sheet1`** (預設即是)。
        3. 在第一行手動輸入您要收集的欄位欄標（選做，系統若偵測空白會自動建立欄位）：
           `填表時間,單位,床號,病患狀態,姓名,病歷號,當日使用醫囑,BIPAP設定值,是否為初次上機第一天,第一天臉部Baseline皮膚狀況,鼻胃管狀態,漏氣量(Lpm),漏氣量判定,固定帶張力,當班皮膚狀況,下一次減壓時間,護理師簽名`
        4. 複製試算表的 **網址 URL**（例如 `https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit#gid=0`）。

        #### **第二步：共享您的 Google 試算表**
        * **方法 A（簡易版）：** 將試算表的共享權限設為「知道連結的人均可編輯」（適合醫院內部不記名快速測試）。
        * **方法 B（標準安全版）：** 建立一個 Google Service Account（服務帳戶）並取得 JSON 私鑰，再將服務帳戶的 Email (例：`xxxx@yyyy.iam.gserviceaccount.com`) 加入您試算表的「共用共用者」名單，賦予其「編輯者」權限。

        #### **第三步：在 Streamlit Cloud 設定 Secrets**
        1. 登入您的 **Streamlit Community Cloud** 主控台。
        2. 點擊您部署的這個 App 旁邊的 **"Settings" > "Secrets"**。
        3. 貼上您的配置金鑰（TOML 格式），範例如下：
        ```toml
        [connections.gsheets]
        spreadsheet = "https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit#gid=0"
        
        # 若是安全版(方法 B)需貼上 Service Account JSON 金鑰內容：
        # type = "service_account"
        # project_id = "your-gcp-project"
        # private_key_id = "xxxx"
        # private_key = "-----BEGIN PRIVATE KEY-----\\nxxxx\\n-----END PRIVATE KEY-----\\n"
        # client_email = "xxxx@yyyy.iam.gserviceaccount.com"
        ```
        4. 點選 **Save** 儲存。
        """)

    # Preview Current Entry
    st.subheader("📝 本次當班查檢資料預覽")
    
    current_entry = {
        "填表時間": entry_datetime.strftime('%Y-%m-%d %H:%M'),
        "單位": unit_select,
        "床號": bed_no if bed_no else "未填寫",
        "病患狀態": track_status,
        "姓名": patient_name if patient_name else "未填寫",
        "病歷號": chart_no if chart_no else "未填寫",
        "當日使用醫囑": bipap_order if bipap_order else "未填寫",
        "BIPAP設定值": bipap_settings,
        "是否為初次上機第一天": "是" if is_first_day else "否",
        "第一天臉部Baseline皮膚狀況": baseline_status.split(" - ")[0] if is_first_day else "N/A",
        "鼻胃管狀態": has_ng_input,
        "漏氣量(Lpm)": leak_value,
        "漏氣量判定": "合格" if is_leak_ok else "異常",
        "固定帶張力": tension_status,
        "當班皮膚狀況": skin_status.split(" - ")[0],
        "下一次減壓時間": f"{next_hour:02d}:00 (指針調整至 {next_time_display})",
        "護理師簽名": nurse_name if nurse_name else "未簽名"
    }
    
    preview_df = pd.DataFrame([current_entry]).T
    preview_df.columns = ["當前填寫數值"]
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
                # 1. Always save to local session state first
                st.session_state.temp_records.append(current_entry)
                local_success_msg = f"🎉 成功暫存於本機！目前累計暫存筆數：{len(st.session_state.temp_records)} 筆。"
                
                # 2. Try to sync with Google Sheets if configured
                if cloud_sync_enabled:
                    with st.spinner("☁️ 正在同步資料至 Google Sheets 雲端資料庫..."):
                        try:
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            
                            # Read current sheet
                            try:
                                existing_df = conn.read(worksheet="Sheet1", ttl="0")
                            except Exception:
                                existing_df = pd.DataFrame(columns=list(current_entry.keys()))
                                
                            # Convert entry to DataFrame
                            new_row_df = pd.DataFrame([current_entry])
                            
                            # Ensure column orders match or concatenate cleanly
                            combined_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                            
                            # Update sheet
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

# TAB 7: ACTIVE CASES TRACKER
# Footer
st.divider()
st.markdown("© 2026 國立臺灣大學醫學院附設醫院 - FACE 圈 | 罩護無痕品管專案 | 呼吸治療科、護理部、醫工部、品質管理中心聯合敬製")
