import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="RCA - Root Cause Analysis", layout="wide", page_icon="🔍")

st.markdown("""
<style>
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    border: 1px dashed #6B7280 !important;
    border-radius: 12px !important;
    background: #111827 !important;
    padding: 20px !important;
}
[data-testid="stFileUploader"] section {
    border: none !important;
    background: transparent !important;
}
[data-testid="stFileUploader"] div div div {
    border: none !important;
    background: transparent !important;
}
[data-testid="stFileUploader"] small {
    display: none !important;
}
[data-testid="stDataFrame"] table, th, td {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>🔍 RCA - Root Cause Analysis with Risk Priority</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>RCA = <b>Root Cause Analysis</b> | Detect → Evidence → Timeline → Causes → Why → Preventive → AI</p>", unsafe_allow_html=True)
st.divider()

uploaded = st.file_uploader("Drop CSV file here or click to browse", type=['csv'])

def get_real_answer(user_q, df, filename, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details):
    q = user_q.lower().strip()
    words = set(re.findall(r'\b\w+\b', q))
    rows = len(df)
    def has_any(keys): return any(k in q for k in keys)
    def has_word(w): return w in words
    if q in ["hi","hello","hey"] or (has_word("hello") and len(words)<4):
        return f"Hello! 👋 {filename} - {rows} rows, Missing {missing}, Outlier {total_out} in {max_col}"
    if has_any(["which should i solve first", "which to solve first", "solve first", "first cause", "priority"]):
        top = risk_df.iloc[0]
        return f"🚨 **SOLVE FIRST = {top['Cause']} - {top['Risk %']}%**\n\nWhy? Highest Risk % ({top['Risk %']}%), Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}. Fix this first, crashes will reduce by 80%."
    if has_any(["how many times", "frequency"]):
        return f"📊 Frequency: Missing {missing}, Duplicate {duplicates}, Outlier {total_out}"
    if has_any(["what is rca", "rca full form"]):
        return f"**RCA = Root Cause Analysis** - Finding WHY crashed. Root cause {max_col} Max {max_val}"
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
    
    # --- SOLVE FIRST LOGIC ---
    solve_first_cause = risk_df.iloc[0]['Cause']
    solve_first_risk = risk_df.iloc[0]['Risk %']
    solve_first_reason = f"Highest Risk {solve_first_risk}%, Missing {missing}, Outlier {total_out} in {max_col}"

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📦 Evidence & Timeline", "🔍 Causes & Why", "🛡️ Preventive (10)", "🤖 AI Assistant"])

    with tab1:
        # SOLVE FIRST BANNER ADDED HERE
        st.error(f"🚨 WHICH TO SOLVE FIRST? → **{solve_first_cause} ({solve_first_risk}%)** | Reason: {solve_first_reason}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{len(df):,}"); m2.metric("Factor", max_col); m3.metric("Missing", missing); m4.metric("Duplicate", duplicates)
        st.dataframe(df.head(8), use_container_width=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**Risk Priority %**")
            fig1, ax1 = plt.subplots(figsize=(2.0,1.4))
            ax1.bar(risk_df["Cause"], risk_df["Risk %"], color=['#ff4444','#ffaa00','#ffe600'], width=0.35)
            ax1.set_ylim(0,120)
            ax1.tick_params(labelsize=6, rotation=15)
            for i,v in enumerate(risk_df["Risk %"]): ax1.text(i, v+3, f"{v}%", ha='center', va='bottom', fontsize=7, fontweight='bold')
            plt.tight_layout(); st.pyplot(fig1)
        with c2:
            st.write("**Incident Frequency**")
            freq_df = pd.DataFrame({"Type":["Missing","Duplicate","Outlier"], "Count":[missing, duplicates, total_out]})
            max_freq = max(missing, duplicates, total_out, 1)
            fig2, ax2 = plt.subplots(figsize=(2.0,1.4))
            ax2.bar(freq_df["Type"], freq_df["Count"], color=['#e74c3c','#f39c12','#3498db'], width=0.35)
            ax2.set_ylim(0, max_freq*1.4)
            ax2.tick_params(labelsize=7)
            for i,v in enumerate(freq_df["Count"]):
                if v>0: ax2.text(i, v+ max_freq*0.06, str(v), ha='center', va='bottom', fontsize=7, fontweight='bold')
            plt.tight_layout(); st.pyplot(fig2)
        with c3:
            st.write("**Factor % Pie**")
            factor_dict = {}
            if missing>0: factor_dict["Missing"]=missing
            if duplicates>0: factor_dict["Duplicate"]=duplicates
            if total_out>0: factor_dict[f"Outlier {max_col}"]=total_out
            if not factor_dict: factor_dict={"Clean":1}
            fig3, ax3 = plt.subplots(figsize=(2.0,1.4))
            ax3.pie(factor_dict.values(), labels=[k[:10] for k in factor_dict.keys()], autopct='%1.1f%%', textprops={'fontsize':6}, wedgeprops={'linewidth':0.5, 'edgecolor':'white'})
            plt.tight_layout(); st.pyplot(fig3)

    with tab2:
        st.subheader("1) Collect Evidence")
        c1, c2, c3 = st.columns(3)
        c1.metric("Missing", missing); c2.metric("Duplicate", duplicates); c3.metric(f"Outlier {max_col}", total_out)
        if outlier_details:
            out_df = pd.DataFrame.from_dict(outlier_details, orient='index', columns=['Count','Max Value'])
            st.dataframe(out_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center')]}]), use_container_width=True)
        st.divider()
        st.subheader("2) Timeline: Before / During / After")
        timeline_df = pd.DataFrame({"Stage": ["Before", "During", "After"], "What Happened": [f"File had {len(df)} rows, {max_col} normal", f"{total_out} outliers, Max {max_val}", f"Crashed - Missing {missing}, Dup {duplicates}"], "Evidence": [f"{len(df.columns)} cols", f"Max {max_col}={max_val}", f"Total {missing+duplicates+total_out}"]})
        st.dataframe(timeline_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center')]}]), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("3) Causes with 3 Evidence - Middle Aligned")
        # SOLVE FIRST HIGHLIGHT IN CAUSES TAB
        st.success(f"✅ **SOLVE FIRST PRIORITY:** {solve_first_cause} - {solve_first_risk}% - Fix this first to prevent 80% crashes!")
        
        cause_df = pd.DataFrame({"Cause": ["Data Quality Failure", "System Migration", "App Logic Error"], "Risk %": [f"{risk_df.iloc[0]['Risk %']}%", "65%", "45%"], "Evidence 1": [f"Missing {missing}", f"Duplicate {duplicates}", f"{max_col} no validation"], "Evidence 2": [f"Outlier {total_out}", f"{len(df.columns)} cols", f"{total_out} fails"], "Evidence 3": [f"Max {max_val}", f"{uploaded.size/1024:.1f} KB", f"No try-except"], "Action": [f"🚨 SOLVE FIRST" if i==0 else "Solve 2nd" if i==1 else "Solve 3rd" for i in range(3)]})
        st.dataframe(cause_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center')]}]), use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("4) Why Data Crashed?")
        st.error(f"Because {max_col} has extreme {max_val} - {total_out} outliers! Solve {solve_first_cause} first!")

    with tab4:
        st.subheader("5) Preventive Actions - 10 - Middle Aligned")
        prevent_df = pd.DataFrame({"No": list(range(1,11)), "Preventive Action": [f"Check missing → {missing}", f"Remove dup → {duplicates}", f"IQR filter {max_col} → {total_out}", f"Validation max > {max_val*0.8}", f"Try-except {max_col}", f"Size alert > {int(len(df)*1.5)}", f"Daily auto-clean", f"Backup before migration", f"Log extreme > {max_val*0.5}", f"Real-time alert"], "Fixes": [f"{missing}", f"{duplicates}", f"{total_out}", f"Max {max_val}", "Crash", "Size", "Daily", "Safe", "Audit", "Real-time"], "Priority": ["P0 - FIRST" if i<3 else f"P{i-2}" for i in range(1,11)]})
        st.dataframe(prevent_df.style.set_table_styles([{'selector': 'th, td', 'props': [('text-align', 'center'), ('vertical-align', 'middle')]}]), use_container_width=True, hide_index=True)
        st.success(f"Apply 10 steps → Start with P0 actions for {solve_first_cause} → 0 crashes!")

    with tab5:
        st.markdown("### 🤖 AI Assistant - With Clear Chat")
        col_chat1, col_chat2 = st.columns([3,1])
        with col_chat2:
            if st.button("🗑️ Clear Chat", use_container_width=True, type="primary"):
                st.session_state.messages = [{"role":"assistant","content":f"Chat cleared! 👋 {uploaded.name} - {len(df)} rows"}]
                st.rerun()
        with col_chat1:
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role":"assistant","content":f"Hello! 👋 RCA = Root Cause Analysis AI! {uploaded.name}: {len(df)} rows, Missing {missing}, Outlier {total_out} in {max_col}. 🚨 SOLVE FIRST: {solve_first_cause} ({solve_first_risk}%)"}]
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            if prompt := st.chat_input("Ask like ChatGPT..."):
                st.session_state.messages.append({"role":"user","content":prompt})
                with st.chat_message("user"): st.markdown(prompt)
                ans = get_real_answer(prompt, df, uploaded.name, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details)
                with st.chat_message("assistant"): st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})
else:
    st.info("Upload CSV to see Evidence, Timeline, Causes, Why, Preventive, AI Chatbot - With Solve First Priority")
