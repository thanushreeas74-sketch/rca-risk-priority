import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="RCA - Root Cause Analysis", layout="wide", page_icon="🔍")

st.markdown("""
<style>
/* FIX 1: Remove white box - make upload blend with dark theme */
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="stFileUploader"] div {
    background: linear-gradient(135deg, #2C3E50 0%, #4CA1AF 100%) !important;
    border: 2px dashed #4CAF50 !important;
    border-radius: 15px !important;
    padding: 10px !important;
}
[data-testid="stFileUploader"] section {
    background: transparent !important;
    border: none !important;
}
/* FIX 3: Table middle align */
[data-testid="stDataFrame"] table, th, td {
    text-align: center !important;
    justify-content: center !important;
}
div[data-testid="stDataFrame"] {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Correct RCA Full Form
st.markdown("<h2 style='text-align:center; margin-bottom:0px;'>🔍 RCA - Root Cause Analysis with Risk Priority</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>RCA = <b>Root Cause Analysis</b> | Workflow: Detect → Collect Evidence → Timeline → Causes with 3 Evidence → Why Crashed → Preventive Actions → AI Assistant</p>", unsafe_allow_html=True)
st.divider()

st.markdown("### 📤 Upload Your Dataset")
uploaded = st.file_uploader("Upload ANY CSV - CIDDS, Bank, College, Hospital", type=['csv'], label_visibility="collapsed")
st.caption("✨ Supports: CIDDS, Bank Transactions, College Data, Hospital, ANY CSV - Auto Detects Issues")

def get_real_answer(user_q, df, filename, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details):
    q = user_q.lower().strip()
    words = set(re.findall(r'\b\w+\b', q))
    rows = len(df)
    def has_any(keys): return any(k in q for k in keys)
    def has_word(w): return w in words
    if q in ["hi","hello","hey"] or (has_word("hello") and len(words)<4):
        return f"Hello! 👋 I analyzed **{filename}** - {rows} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}."
    if has_any(["which should i solve first", "which to solve first", "solve first"]):
        return f"🚨 **Solve FIRST = {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%** - {filename}: Missing {missing}, Outlier {total_out} in {max_col} Max {max_val} - P0 TODAY"
    if has_any(["how many times", "frequency"]):
        return f"📊 Frequency {filename}: Missing {missing}, Duplicate {duplicates}, Outlier {total_out} in {max_col}"
    if has_any(["collect evidence", "evidence"]):
        return f"📦 Real Evidence {filename}: Missing {missing}, Dup {duplicates}, Outlier {total_out} in {max_col} Max {max_val}"
    if has_any(["timeline"]):
        return f"⏰ Timeline {filename}: Before {rows} rows normal, During {total_out} outliers Max {max_val}, After crashed"
    if has_any(["causes", "3 evidence"]):
        return f"🔍 Causes: Data Quality - Missing {missing}, Outlier {total_out}, Max {max_val} | System - Dup {duplicates} | App - {max_col} fail"
    if has_any(["why data crashed", "why crashed"]):
        return f"💥 Why Crashed: {max_col} extreme {max_val} - {total_out} times, system can't handle"
    if "missing" in q and "detail" in q:
        miss = df.isnull().sum(); miss = miss[miss>0].to_dict()
        return f"📭 Missing: {missing}, {miss}" if missing>0 else "✅ No Missing"
    if "outlier" in q and "detail" in q:
        return f"⚠️ Outlier: {max_col} {total_out} Max {max_val} {outlier_details}"
    if has_any(["file size", "file info"]):
        kb = uploaded.size/1024 if hasattr(uploaded, 'size') else 0
        return f"📁 {filename}: {rows} rows, {len(df.columns)} cols, {kb:.1f} KB"
    if has_any(["preventive", "prevent"]):
        return f"🛡️ 10 Preventive: check missing {missing}, dup {duplicates}, IQR {max_col} {total_out}, alert max {max_val*0.8}, try-except, size check, daily clean, backup, log, real-time alert"
    if has_any(["what is rca", "rca full form"]):
        return f"**RCA = Root Cause Analysis** - Finding WHY crashed. For {filename}, root cause {max_col} Max {max_val} {total_out} outliers"
    return f"🤖 For {filename} '{user_q}': {rows} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}, Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%"

if uploaded:
    df = pd.read_csv(uploaded, low_memory=False)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    outlier_details = {}
    max_col = numeric_cols[0] if numeric_cols else df.columns[0]
    max_val = 0
    total_out = 0
    if numeric_cols:
        for col in numeric_cols[:5]:
            try:
                col_data = df[col].dropna()
                if len(col_data)>10:
                    q1, q3 = np.percentile(col_data, [25,75])
                    iqr = q3-q1
                    outs = col_data[col_data > q3 + 1.5*iqr]
                    if len(outs)>0:
                        outlier_details[col] = [len(outs), float(col_data.max())]
                        if float(col_data.max()) > max_val:
                            max_val = float(col_data.max())
                            max_col = col
                            total_out = len(outs)
            except: pass
    risk_df = pd.DataFrame({"Cause":["Data Quality Failure","System Migration","App Logic Error"],"Risk %":[80 if (missing or total_out or duplicates) else 25,65,45]}).sort_values("Risk %", ascending=False).reset_index(drop=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📦 Evidence & Timeline", "🔍 Causes & Why", "🛡️ Preventive (10)", "🤖 AI Assistant"])

    with tab1:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📄 Rows", f"{len(df):,}")
        m2.metric("⚠️ Factor", max_col)
        m3.metric("📭 Missing", missing)
        m4.metric("📑 Duplicate", duplicates)
        st.dataframe(df.head(8), use_container_width=True)
        
        st.markdown("#### 📊 Charts - Thin & No Line Cross")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**Risk Priority %**")
            # FIX 2: Make charts little thin + fix 10687 line cross
            fig1, ax1 = plt.subplots(figsize=(2.2,1.5))
            bars1 = ax1.bar(risk_df["Cause"], risk_df["Risk %"], color=['#ff4444','#ffaa00','#ffe600'], width=0.4) # thin width 0.4
            ax1.set_ylim(0,115) # more space for label not cross line
            ax1.tick_params(labelsize=6, rotation=15)
            for i,v in enumerate(risk_df["Risk %"]):
                ax1.text(i, v+4, f"{v}%", ha='center', va='bottom', fontsize=7, fontweight='bold') # va bottom, higher
            plt.tight_layout()
            st.pyplot(fig1)
        with c2:
            st.write("**Incident Frequency**")
            freq_df = pd.DataFrame({"Type":["Missing","Duplicate","Outlier"], "Count":[missing, duplicates, total_out]})
            max_freq = max(missing, duplicates, total_out, 1)
            fig2, ax2 = plt.subplots(figsize=(2.2,1.5))
            bars2 = ax2.bar(freq_df["Type"], freq_df["Count"], color=['#e74c3c','#f39c12','#3498db'], width=0.4) # thin
            ax2.set_ylim(0, max_freq*1.3) # 30% extra space so 10687 not cross line
            ax2.tick_params(labelsize=7)
            for i,v in enumerate(freq_df["Count"]):
                if v>0:
                    ax2.text(i, v+ max_freq*0.05, str(v), ha='center', va='bottom', fontsize=7, fontweight='bold') # not crossing
            plt.tight_layout()
            st.pyplot(fig2)
        with c3:
            st.write("**Factor % Pie - With %**")
            factor_dict = {}
            if missing>0: factor_dict["Missing"]=missing
            if duplicates>0: factor_dict["Duplicate"]=duplicates
            if total_out>0: factor_dict[f"Outlier {max_col}"]=total_out
            if not factor_dict: factor_dict={"Clean":1}
            total_f = sum(factor_dict.values())
            fig3, ax3 = plt.subplots(figsize=(2.2,1.5))
            wedges, texts, autotexts = ax3.pie(factor_dict.values(), labels=[k[:12] for k in factor_dict.keys()], autopct='%1.1f%%', textprops={'fontsize':6}, wedgeprops={'linewidth':0.5, 'edgecolor':'white'})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(7)
            plt.tight_layout()
            st.pyplot(fig3)
            for k,v in factor_dict.items():
                st.caption(f"{k}: {v} ({v/total_f*100:.1f}%)")

    with tab2:
        st.subheader("1) Collect Evidence - Real Evidence")
        c1, c2, c3 = st.columns(3)
        c1.metric("Missing", missing)
        c2.metric("Duplicate", duplicates)
        c3.metric(f"Outlier {max_col}", total_out)
        if outlier_details:
            out_df = pd.DataFrame.from_dict(outlier_details, orient='index', columns=['Count','Max Value'])
            # FIX 3: Middle align
            st.dataframe(out_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center')]}]), use_container_width=True)
        
        st.divider()
        st.subheader("2) Timeline: Before / During / After")
        timeline_df = pd.DataFrame({
            "Stage": ["Before", "During", "After"],
            "What Happened": [f"File had {len(df)} rows, {max_col} normal", f"{total_out} outliers, Max {max_val} in {max_col}", f"Crashed - Missing {missing}, Dup {duplicates}, Outlier {total_out}"],
            "Evidence": [f"{len(df.columns)} cols", f"Max {max_col}={max_val}", f"Total {missing+duplicates+total_out}"]
        })
        st.dataframe(timeline_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center')]}]), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("3) Causes with 3 Evidence Each")
        cause_df = pd.DataFrame({
            "Cause": ["Data Quality Failure", "System Migration", "App Logic Error"],
            "Risk %": [f"{risk_df.iloc[0]['Risk %']}%", "65%", "45%"],
            "Evidence 1": [f"Missing {missing}", f"Duplicate {duplicates}", f"{max_col} no validation"],
            "Evidence 2": [f"Outlier {total_out} in {max_col}", f"{len(df.columns)} cols", f"{total_out} fails"],
            "Evidence 3": [f"Max {max_val} extreme", f"{uploaded.size/1024:.1f} KB", f"No try-except"]
        })
        st.dataframe(cause_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center')]}]), use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("4) Why Data Crashed?")
        st.error(f"Because {max_col} has extreme {max_val} - {total_out} outliers! System can't handle {max_val}")

    with tab4:
        st.subheader("5) Preventive Actions - 10 Actions - Middle Aligned")
        prevent_df = pd.DataFrame({
            "No": list(range(1,11)),
            "Preventive Action": [f"Check missing df.isnull().sum() → {missing}", f"Remove dup df.drop_duplicates() → {duplicates}", f"IQR filter {max_col} → {total_out}", f"Validation if max > {max_val*0.8}: Alert", f"Try-except for {max_col}", f"Size alert > {int(len(df)*1.5)} rows", f"Daily auto-clean pipeline", f"Backup before migration", f"Log extreme > {max_val*0.5}", f"Real-time dashboard alert"],
            "Fixes": [f"{missing}", f"{duplicates}", f"{total_out}", f"Max {max_val}", "Crash", "Size", "Daily", "Safe", "Audit", "Real-time"]
        })
        # FIX 3: Middle align 4th sheet also
        st.dataframe(prevent_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center'), ('vertical-align', 'middle')]}]), use_container_width=True, hide_index=True)
        st.success(f"Apply 10 steps → 0 crashes for {uploaded.name}!")

    with tab5:
        st.markdown("### 🤖 AI Assistant - With Clear Chat")
        col_chat1, col_chat2 = st.columns([3,1])
        with col_chat2:
            if st.button("🗑️ Clear Chat", use_container_width=True, type="primary"):
                st.session_state.messages = [{"role":"assistant","content":f"Chat cleared! 👋 {uploaded.name} - {len(df)} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}"}]
                st.rerun()
        with col_chat1:
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role":"assistant","content":f"Hello! 👋 RCA = Root Cause Analysis AI!\n{uploaded.name}: {len(df)} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}\nAsk: collect evidence? timeline? causes? why crashed? preventive?"}]
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            if prompt := st.chat_input("Ask like ChatGPT..."):
                st.session_state.messages.append({"role":"user","content":prompt})
                with st.chat_message("user"): st.markdown(prompt)
                ans = get_real_answer(prompt, df, uploaded.name, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details)
                with st.chat_message("assistant"): st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})

else:
    st.info("Upload CSV to see Evidence, Timeline, Causes, Why, Preventive, AI Chatbot")
