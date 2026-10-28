import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="RCA - Root Cause Analysis", layout="wide", page_icon="🔍")

# CSS for attractive design
st.markdown("""
<style>
.upload-box {
    border: 2px dashed #4CAF50;
    border-radius: 15px;
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    text-align: center;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 15px;
    border-radius: 12px;
    color: white;
}
.chat-bubble-user {
    background: #DCF8C6;
    padding: 10px;
    border-radius: 15px 15px 0px 15px;
    margin: 5px;
}
.chat-bubble-ai {
    background: #E3F2FD;
    padding: 10px;
    border-radius: 15px 15px 15px 0px;
    margin: 5px;
}
</style>
""", unsafe_allow_html=True)

# FIX 1: RCA Full Form CORRECT - Root Cause Analysis (not Risk Priority)
st.markdown("<h1 style='text-align:center; margin-bottom:0px;'>🔍 RCA - Root Cause Analysis with Risk Priority</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; font-size:13px;'>RCA Full Form = <b>Root Cause Analysis</b> | Workflow: Detect → Collect Evidence → Timeline → Causes with 3 Evidence → Why Crashed → Preventive Actions → AI Assistant</p>", unsafe_allow_html=True)
st.divider()

# FIX 2: Upload box attractive, not boring
st.markdown("### 📤 Upload Your Dataset - Attractive Upload Box")
with st.container():
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded = st.file_uploader("Drag & Drop or Click to Upload - Works for ANY CSV (Bank, College, Hospital, CIDDS, etc.)", type=['csv'], label_visibility="collapsed")
    st.markdown("**✨ Supports: CIDDS, Bank Transactions, College Data, Hospital, ANY CSV - Auto Detects Issues**")
    st.markdown('</div>', unsafe_allow_html=True)

def get_real_answer(user_q, df, filename, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details):
    q = user_q.lower().strip()
    words = set(re.findall(r'\b\w+\b', q))
    rows = len(df)
    def has_any(keys): return any(k in q for k in keys)
    def has_word(w): return w in words
    if q in ["hi","hello","hey"] or (has_word("hello") and len(words)<4):
        return f"Hello! 👋 I analyzed **{filename}** - {rows} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}. Ask me anything like ChatGPT!"
    if has_any(["which should i solve first", "which to solve first", "solve first", "first priority"]):
        return f"🚨 **Solve FIRST = {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%**\n\nFor {filename}: Missing {missing}, Duplicate {duplicates}, Outlier {total_out} in {max_col} Max {max_val} - Highest risk, P0 TODAY"
    if has_any(["how many times", "frequency", "times crashed"]):
        return f"📊 **Frequency for {filename}:** Missing {missing} times, Duplicate {duplicates} times, Outlier {total_out} times in {max_col}. Total {missing+duplicates+total_out}"
    if has_any(["collect evidence", "evidence"]):
        return f"📦 **Real Evidence from {filename}:**\n1. Missing {missing}\n2. Duplicate {duplicates}\n3. Outlier {total_out} in {max_col} Max {max_val}"
    if has_any(["timeline", "before", "during", "after"]):
        return f"⏰ **Timeline for {filename}:**\n• Before: {rows} rows normal\n• During: {total_out} outliers, Max {max_val}\n• After: Crashed - Missing {missing}, Duplicate {duplicates}"
    if has_any(["causes", "cause with", "3 evidence"]):
        return f"🔍 **Causes with 3 Evidence:**\n1. Data Quality - Missing {missing}, Outlier {total_out}, Max {max_val}\n2. System Migration - Dup {duplicates}, {len(df.columns)} cols, size {uploaded.size/1024:.1f}KB\n3. App Logic - {max_col} fail, {total_out} times break, no validation"
    if has_any(["why data crashed", "why crashed", "why crash"]):
        return f"💥 **Why Crashed {filename}:** {max_col} extreme {max_val} - {total_out} times. System can't handle {max_val}, so crash!"
    if "missing" in q and "detail" in q:
        miss = df.isnull().sum(); miss = miss[miss>0].to_dict()
        return f"📭 Missing Details: Total {missing}, Per col {miss}" if missing>0 else f"✅ No Missing in {filename}"
    if "outlier" in q and "detail" in q:
        return f"⚠️ Outlier Details: {max_col} Count {total_out} Max {max_val} All: {outlier_details}"
    if has_any(["file size", "file info"]):
        kb = uploaded.size/1024 if hasattr(uploaded, 'size') else 0
        return f"📁 {filename}: {rows} rows, {len(df.columns)} cols, {kb:.1f} KB"
    if has_any(["preventive", "prevent", "actions"]):
        return f"🛡️ **10 Preventive Actions for {filename}:**\n1. df.isnull().sum() → {missing}\n2. drop_duplicates → {duplicates}\n3. IQR filter {max_col} → {total_out}\n4. Alert if max > {max_val*0.8}\n5. Try-except\n6. Validation before insert\n7. Size check > {int(rows*1.5)}\n8. Log extreme\n9. Daily auto-clean\n10. Real-time dashboard alert"
    if has_any(["summary", "overview"]):
        return f"📋 Summary {filename}: {rows} rows, Missing {missing}, Dup {duplicates}, Outlier {total_out} in {max_col} Max {max_val}, Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%"
    if has_any(["what is rca", "rca full form"]):
        return f"**RCA Full Form = Root Cause Analysis.** Not Risk Priority! Risk Priority is part of RCA. RCA means finding WHY data crashed. For {filename}, RCA found {max_col} Max {max_val} with {total_out} outliers is Root Cause."
    return f"🤖 For {filename} - '{user_q}': {rows} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}, Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%. Ask: timeline? causes? why crashed? preventive?"

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
        # FIX 2: Dashboard attractive - colored metrics
        st.markdown("### 🎨 Attractive Dashboard - Overview of THIS File")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📄 Total Rows", f"{len(df):,}", delta="From File")
        m2.metric("⚠️ Main Factor", max_col, delta=f"{total_out} outliers")
        m3.metric("📭 Missing", missing, delta="Evidence", delta_color="inverse")
        m4.metric("📑 Duplicate", duplicates, delta="Evidence", delta_color="inverse")
        
        st.divider()
        st.dataframe(df.head(8), use_container_width=True)
        
        # FIX 3: Charts little bit smaller + percentage for pie
        st.markdown("#### 📊 Charts - Small Size + Pie %")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**Risk Priority %**")
            fig1, ax1 = plt.subplots(figsize=(2.5,1.6))  # MORE SMALL
            ax1.bar(risk_df["Cause"], risk_df["Risk %"], color=['#ff4444','#ffaa00','#ffe600'])
            ax1.set_ylim(0,100)
            ax1.tick_params(labelsize=6, rotation=15)
            for i,v in enumerate(risk_df["Risk %"]): ax1.text(i, v+2, f"{v}%", ha='center', fontsize=8, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig1)
        with c2:
            st.write("**Incident Frequency**")
            freq_df = pd.DataFrame({"Type":["Missing","Duplicate","Outlier"], "Count":[missing, duplicates, total_out]})
            fig2, ax2 = plt.subplots(figsize=(2.5,1.6))  # MORE SMALL
            ax2.bar(freq_df["Type"], freq_df["Count"], color=['#e74c3c','#f39c12','#3498db'])
            ax2.tick_params(labelsize=7)
            for i,v in enumerate(freq_df["Count"]): ax2.text(i, v+0.3, str(v), ha='center', fontsize=8, fontweight='bold')
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
            fig3, ax3 = plt.subplots(figsize=(2.5,1.6))  # MORE SMALL
            # Give percentage for pie chart also - FIX
            wedges, texts, autotexts = ax3.pie(factor_dict.values(), labels=factor_dict.keys(), autopct='%1.1f%%', textprops={'fontsize':6})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            plt.tight_layout()
            st.pyplot(fig3)
            # Show percentage text also below
            for k,v in factor_dict.items():
                st.caption(f"{k}: {v} ({v/total_f*100:.1f}%)")

    with tab2:
        st.subheader("1) Collect Evidence - Real Evidence from YOUR File")
        c1, c2, c3 = st.columns(3)
        c1.metric("Missing Evidence", missing)
        c2.metric("Duplicate Evidence", duplicates)
        c3.metric(f"Outlier {max_col}", total_out)
        if outlier_details:
            out_df = pd.DataFrame.from_dict(outlier_details, orient='index', columns=['Count','Max Value'])
            st.dataframe(out_df, use_container_width=True)
        st.divider()
        st.subheader("2) Timeline: Before / During / After")
        timeline_df = pd.DataFrame({
            "Stage": ["Before", "During", "After"],
            "What Happened": [
                f"File had {len(df)} rows, {max_col} normal",
                f"{total_out} outliers, Max {max_val} in {max_col}",
                f"Crashed - Missing {missing}, Dup {duplicates}, Outlier {total_out}"
            ],
            "Evidence": [f"{len(df.columns)} cols", f"Max {max_col}={max_val}", f"Total {missing+duplicates+total_out}"]
        })
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("3) Causes with 3 Evidence Each")
        st.markdown(f"**Cause 1: Data Quality Failure {risk_df.iloc[0]['Risk %']}%**")
        st.write(f"- Ev1: Missing {missing} | Ev2: Outlier {total_out} in {max_col} | Ev3: Max {max_val}")
        st.markdown(f"**Cause 2: System Migration 65%**")
        st.write(f"- Ev1: Dup {duplicates} | Ev2: {len(df.columns)} cols | Ev3: {uploaded.size/1024:.1f} KB")
        st.markdown(f"**Cause 3: App Logic Error 45%**")
        st.write(f"- Ev1: {max_col} no validation for {max_val} | Ev2: {total_out} logic fails | Ev3: No try-except")
        st.divider()
        st.subheader("4) Why Data Crashed?")
        st.error(f"Because {max_col} has extreme {max_val} - {total_out} outliers! System can't handle {max_val}, crashed {total_out} times.")

    with tab4:
        st.subheader("5) Preventive Actions - 10 Actions")
        prevent_df = pd.DataFrame({
            "No": list(range(1,11)),
            "Action": [
                f"Check missing: df.isnull().sum() → {missing}",
                f"Remove dup: df.drop_duplicates() → {duplicates}",
                f"IQR filter {max_col} → {total_out} outliers",
                f"Validation: if max > {max_val*0.8}: Alert",
                f"Try-except for {max_col}",
                f"Size alert if rows > {int(len(df)*1.5)}",
                f"Daily auto-clean pipeline",
                f"Backup before migration",
                f"Log extreme {max_col} > {max_val*0.5}",
                f"Real-time dashboard alert"
            ]
        })
        st.dataframe(prevent_df, use_container_width=True, hide_index=True)
        st.success(f"Apply 10 steps → 0 crashes for {uploaded.name}! Fixes {missing+duplicates+total_out} issues.")

    with tab5:
        # FIX 4: AI Assistant good, not boring + Clear Chat option
        st.markdown("### 🤖 AI Assistant - ChatGPT Like, With Clear Chat")
        st.info("💡 **Ask:** collect evidence? timeline? causes? why crashed? preventive? what is rca? which to solve first?")
        
        col_chat1, col_chat2 = st.columns([3,1])
        with col_chat2:
            st.markdown("**Options**")
            if st.button("🗑️ Clear Chat", use_container_width=True, type="primary"):
                st.session_state.messages = [{"role":"assistant","content":f"Chat cleared! 👋 I analyzed **{uploaded.name}** - {len(df)} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}. Ask again!"}]
                st.rerun()
            if st.button("📋 Copy Summary", use_container_width=True):
                st.toast(f"Summary: {uploaded.name} {len(df)} rows, Missing {missing}, Outlier {total_out} in {max_col}")
        
        with col_chat1:
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role":"assistant","content":f"Hello! 👋 I'm your **RCA (Root Cause Analysis) AI Assistant** - Real like ChatGPT!\n\nI analyzed **{uploaded.name}**:\n- {len(df)} rows\n- Missing {missing}, Duplicate {duplicates}\n- Outlier {total_out} in {max_col} Max {max_val}\n- Top Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%\n\n**Ask me anything:** collect evidence? timeline? causes with 3 evidence? why crashed? preventive actions? what is rca?"}]
            
            # Chat bubbles attractive
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if prompt := st.chat_input("Ask like ChatGPT: what is rca? timeline? preventive?"):
                st.session_state.messages.append({"role":"user","content":prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                ans = get_real_answer(prompt, df, uploaded.name, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details)
                with st.chat_message("assistant"):
                    st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})

else:
    # Attractive empty state
    st.markdown("""
    <div style='text-align:center; padding:30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius:20px; color:white;'>
    <h2>👋 Welcome to RCA Tool</h2>
    <p>Root Cause Analysis = Finding WHY data crashed</p>
    <p>Upload ANY CSV to see Evidence, Timeline, Causes, Why, Preventive, AI Chatbot</p>
    </div>
    """, unsafe_allow_html=True)
