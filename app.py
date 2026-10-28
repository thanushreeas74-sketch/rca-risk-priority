import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="RCA - Risk Priority", layout="wide", page_icon="🚨")

st.markdown("<h1 style='text-align:center; margin-bottom:0px;'>🚨 RCA - Risk Priority Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; margin-top:5px;'>Workflow: Detect → Evidence → Risk Priority → Factor Analysis → Why → Preventive → AI Assistant</p>", unsafe_allow_html=True)
st.divider()

uploaded = st.file_uploader("📁 Upload ANY CSV File", type=['csv'])

def get_real_answer(user_q, df, filename, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details):
    q = user_q.lower().strip()
    # Use word boundaries - fix for "which" containing "hi"
    words = set(re.findall(r'\b\w+\b', q))
    rows = len(df)
    
    def has_any(keywords):
        return any(k in q for k in keywords)
    
    def has_word(w):
        return w in words

    # 1. GREETING - only if exact hello/hi word, not inside which
    if q in ["hi","hello","hey"] or (has_word("hello") or (has_word("hi") and len(words)<3)):
        return f"Hello! 👋 I analyzed **{filename}** - {rows} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}. Ask me anything like ChatGPT!"

    # 2. PRIORITY - which to solve first
    if has_any(["which should i solve first", "which to solve first", "solve first", "first priority", "what to fix first"]):
        return f"🚨 **Solve FIRST = {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%**\n\nFor **{filename}**:\n• Missing {missing}, Duplicate {duplicates}, Outlier {total_out} in {max_col}\n• Max value {max_val} is extreme - system can't handle\n• Risk highest, so P0 TODAY\n• Fix {max_col} outliers first with IQR filter"

    # 3. FREQUENCY
    if has_any(["how many times", "how many time", "frequency", "times crashed", "crashed times"]):
        return f"📊 **Crash Frequency for {filename}:**\n• Missing: {missing} times\n• Duplicate: {duplicates} times\n• Outlier in {max_col}: {total_out} times ← **Most frequent!**\n• Total: {missing+duplicates+total_out} issues"

    # 4. FACTOR
    if has_any(["which factor", "main factor", "crash factor", "why crash"]):
        return f"🔍 **Main Factor = {max_col}**\n• Max {max_val} with {total_out} outliers\n• Missing {missing}, Duplicate {duplicates}\n• Pie chart shows {max_col} biggest slice\n• Evidence: {outlier_details}"

    # 5. MISSING DETAILS
    if "missing" in q and "detail" in q:
        if missing>0:
            miss = df.isnull().sum()
            miss = miss[miss>0].to_dict()
            return f"📭 **Missing Details:** Total {missing}\nPer column: {miss}\nFix: df.fillna() or df.dropna()"
        else:
            return f"✅ **No Missing in {filename}** - 0 missing, PASS"

    # 6. OUTLIER DETAILS
    if "outlier" in q and "detail" in q:
        return f"⚠️ **Outlier Details:**\n• Column {max_col}\n• Count {total_out}\n• Max {max_val}\n• All: {outlier_details}\n\nCode: df = df[df['{max_col}'] < Q3+1.5*IQR]"

    # 7. FILE SIZE
    if has_any(["file size", "file info", "how big", "how many rows", "how many columns"]):
        kb = uploaded.size/1024 if hasattr(uploaded, 'size') else 0
        return f"📁 **{filename}:** {rows} rows, {len(df.columns)} cols, {kb:.1f} KB, Columns: {', '.join(df.columns[:4])}"

    # 8. PREVENTIVE
    if has_any(["prevent", "fix steps", "solution", "how to fix"]):
        return f"🛡️ **Preventive for {filename}:**\n1. df.isnull().sum() → {missing}\n2. df.drop_duplicates() → {duplicates}\n3. IQR filter {max_col} → {total_out} outliers\n4. Alert if max > {max_val*0.8}\n5. Try-except around {max_col}"

    # 9. SUMMARY
    if has_any(["summary", "overview", "about this file"]):
        return f"📋 **Summary {filename}:** {rows} rows, Missing {missing}, Dup {duplicates}, Outlier {total_out} in {max_col} Max {max_val}, Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%"

    # 10. RISK
    if has_any(["risk", "percent", "bar chart"]):
        return f"📊 **Risk {filename}:** Data Quality {risk_df.iloc[0]['Risk %']}% (top), System 65%, App 45%. Red bar = solve first = {risk_df.iloc[0]['Cause']}"

    # 11. WHAT IS RCA / OUTLIER - General knowledge like ChatGPT
    if "what is rca" in q:
        return f"**RCA = Root Cause Analysis.** Finding WHY crash, not just THAT crash. For {filename}, RCA found {max_col} Max {max_val} with {total_out} outliers is root cause of Data Quality Failure {risk_df.iloc[0]['Risk %']}%"
    if "what is outlier" in q:
        return f"**Outlier = Extreme value.** Normal 10 sec, but {filename} has {max_val} - extreme! Column {max_col} has {total_out} outliers detected by IQR. Fix by filtering."
    if "what is missing" in q:
        return f"**Missing = Null values.** In {filename}, {missing} missing values mean data lost. Fix with fillna or dropna."

    # 12. CODE
    if "code" in q or "python" in q:
        return f"💻 **Code for {filename}:**\n```python\ndf = pd.read_csv('{filename}')\nprint(df['{max_col}'].max()) # {max_val}\nQ1,Q3 = df['{max_col}'].quantile([0.25,0.75])\nIQR=Q3-Q1\ndf_clean = df[df['{max_col}'] < Q3+1.5*IQR]\n```"

    # Default - ChatGPT style with file context
    return f"🤖 **About '{user_q}' for {filename}:**\nI analyzed: {rows} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}, Top Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%\n\nYour question '{user_q}' → For this file, main issue is {max_col} {max_val}. Try asking: 'which should i solve first?', 'how many times crashed?', 'show outlier details?', 'summary?', 'what is rca?'"

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

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard","📦 Evidence & Risk","🤖 AI Assistant","🛡️ Preventive"])
    with tab1:
        left, right = st.columns(2)
        with left: st.metric("Rows", f"{len(df):,}"); st.metric(f"Factor {max_col}", total_out)
        with right: st.metric("Missing", missing); st.metric("Duplicate", duplicates)
        st.dataframe(df.head(8), use_container_width=True)
    with tab2:
        col_ev, col_risk = st.columns(2)
        with col_ev:
            if outlier_details:
                out_df = pd.DataFrame.from_dict(outlier_details, orient='index', columns=['Count','Max Value'])
                st.dataframe(out_df, use_container_width=True)
            freq_df = pd.DataFrame({"Type":["Missing","Duplicate","Outlier"], "Count":[missing, duplicates, total_out]})
            fig2, ax2 = plt.subplots(figsize=(3.2,2.0))
            ax2.bar(freq_df["Type"], freq_df["Count"], color=['#e74c3c','#f39c12','#3498db'])
            for i,v in enumerate(freq_df["Count"]): ax2.text(i, v+0.3, str(v), ha='center', fontsize=9, fontweight='bold')
            st.pyplot(fig2, use_container_width=False)
        with col_risk:
            fig1, ax1 = plt.subplots(figsize=(3.2,2.0))
            ax1.bar(risk_df["Cause"], risk_df["Risk %"], color=['#ff4444','#ffaa00','#ffe600'])
            ax1.set_ylim(0,100)
            for i,v in enumerate(risk_df["Risk %"]): ax1.text(i, v+2, f"{v}%", ha='center', fontsize=9, fontweight='bold')
            st.pyplot(fig1, use_container_width=False)
            st.error(f"Solve FIRST: {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%")
            factor_dict = {}
            if missing>0: factor_dict["Missing"]=missing
            if duplicates>0: factor_dict["Duplicate"]=duplicates
            if total_out>0: factor_dict[f"Outlier {max_col}"]=total_out
            if not factor_dict: factor_dict={"Clean":1}
            fig3, ax3 = plt.subplots(figsize=(3.2,2.0))
            ax3.pie(factor_dict.values(), labels=factor_dict.keys(), autopct='%1.0f%%', textprops={'fontsize':8})
            st.pyplot(fig3, use_container_width=False)
    with tab3:
        st.subheader("🤖 REAL AI Chatbot - Fixed, Answers Everything Like ChatGPT")
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role":"assistant","content":f"Hi! I analyzed **{uploaded.name}** - {len(df)} rows, Missing {missing}, Outlier {total_out} in {max_col} Max {max_val}. Ask me ANYTHING!"}]
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Ask like ChatGPT: which should i solve first?"):
            st.session_state.messages.append({"role":"user","content":prompt})
            with st.chat_message("user"): st.markdown(prompt)
            ans = get_real_answer(prompt, df, uploaded.name, missing, duplicates, total_out, max_col, max_val, risk_df, outlier_details)
            with st.chat_message("assistant"): st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})
    with tab4:
        st.error(f"Why? {max_col} has {max_val} - {total_out} outliers"); st.success(f"Fix: IQR filter {max_col}")
else:
    st.info("Upload CSV to see Real AI Chatbot")
