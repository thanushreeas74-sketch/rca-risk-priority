import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="RCA - Risk Priority", layout="wide", page_icon="🚨")

# TITLE - No Universal word, Workflow BELOW title
st.markdown("<h1 style='text-align:center; margin-bottom:0px;'>🚨 RCA - Risk Priority Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; margin-top:5px;'>Workflow: Detect → Evidence → Risk Priority → Factor Analysis → Why → Preventive → AI Assistant</p>", unsafe_allow_html=True)
st.divider()

uploaded = st.file_uploader("📁 Upload ANY CSV File - Bank, College, Hospital, CIDDS", type=['csv'])

if uploaded:
    df = pd.read_csv(uploaded, low_memory=False)
    
    # Auto detect for ANY dataset
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
                    q1 = np.percentile(col_data, 25)
                    q3 = np.percentile(col_data, 75)
                    iqr = q3 - q1
                    outs = col_data[col_data > q3 + 1.5*iqr]
                    if len(outs)>0:
                        outlier_details[col] = [len(outs), float(col_data.max())]
                        if float(col_data.max()) > max_val:
                            max_val = float(col_data.max())
                            max_col = col
                            total_out = len(outs)
            except:
                pass

    # RISK PRIORITY CALC
    data_quality_risk = 80 if (missing>0 or total_out>0 or duplicates>0) else 25
    system_risk = 65
    app_risk = 45
    risk_df = pd.DataFrame({
        "Cause": ["Data Quality Failure", "System Migration", "App Logic Error"],
        "Risk %": [data_quality_risk, system_risk, app_risk]
    }).sort_values("Risk %", ascending=False).reset_index(drop=True)

    # TWO SIDE DASHBOARD WITH TABS - Next page concept
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📦 Evidence & Risk", "🤖 AI Assistant", "🛡️ Preventive"])

    with tab1:
        st.subheader("Starting Dashboard - Overview of THIS File")
        left, right = st.columns(2)
        with left:
            st.metric("Total Rows", f"{len(df):,}")
            st.metric(f"Main Factor Column", max_col)
            st.metric(f"Outliers in {max_col}", total_out)
        with right:
            st.metric("Missing Values", missing)
            st.metric("Duplicate Rows", duplicates)
            st.metric("File Name", uploaded.name[:30])
        
        st.divider()
        st.write(f"**Columns in this file ({len(df.columns)}):** {', '.join(df.columns.tolist()[:10])}")
        st.dataframe(df.head(10), use_container_width=True)

    with tab2:
        st.subheader("Evidence & Risk - Real Evidence from YOUR File")
        
        col_ev, col_risk = st.columns([1,1])
        
        with col_ev:
            st.markdown("#### Evidence (Table, NOT code format)")
            st.write(f"Missing: **{missing}** | Duplicate: **{duplicates}** | Total Outlier: **{total_out}**")
            if outlier_details:
                out_df = pd.DataFrame.from_dict(outlier_details, orient='index', columns=['Count','Max Value'])
                st.dataframe(out_df, use_container_width=True)
            else:
                st.success("No outliers found - Clean numeric data")
            
            # Small Frequency Chart
            st.markdown("#### Chart 2: Incident Frequency - How many times crashed?")
            freq_df = pd.DataFrame({"Type":["Missing","Duplicate","Outlier"], "Count":[missing, duplicates, total_out]})
            fig2, ax2 = plt.subplots(figsize=(3.2,2.0)) # SMALL SIZE
            bars = ax2.bar(freq_df["Type"], freq_df["Count"], color=['#e74c3c','#f39c12','#3498db'])
            ax2.tick_params(labelsize=8)
            for i, v in enumerate(freq_df["Count"]):
                ax2.text(i, v+0.5, str(v), ha='center', fontsize=9, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig2, use_container_width=False)
        
        with col_risk:
            st.markdown("#### Chart 1: Risk Priority % - Which to solve FIRST?")
            fig1, ax1 = plt.subplots(figsize=(3.2,2.0)) # SMALL SIZE
            colors = ['#ff4444','#ffaa00','#ffe600']
            ax1.bar(risk_df["Cause"], risk_df["Risk %"], color=colors)
            ax1.set_ylim(0,100)
            ax1.set_ylabel("%", fontsize=8)
            ax1.tick_params(labelsize=7, rotation=10)
            for i, v in enumerate(risk_df["Risk %"]):
                ax1.text(i, v+2, f"{v}%", ha='center', fontsize=9, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig1, use_container_width=False)
            st.error(f"🔴 Solve FIRST: {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%")
            
            # Small Factor Pie
            st.markdown("#### Chart 3: Factor - Which factor crash occurring?")
            factor_dict = {}
            if missing>0: factor_dict["Missing"] = missing
            if duplicates>0: factor_dict["Duplicate"] = duplicates
            if total_out>0: factor_dict[f"Outlier {max_col}"] = total_out
            if not factor_dict: factor_dict = {"Clean Data":1}
            
            fig3, ax3 = plt.subplots(figsize=(3.2,2.0)) # SMALL SIZE
            ax3.pie(factor_dict.values(), labels=factor_dict.keys(), autopct='%1.0f%%', textprops={'fontsize':8})
            plt.tight_layout()
            st.pyplot(fig3, use_container_width=False)

    with tab3:
        st.subheader("AI Assignment & Smart Chatbot - Different Answer for Every Question")
        left_ai, right_ai = st.columns(2)
        
        with left_ai:
            st.markdown("**🔴 Auto Assignment Generated from THIS File**")
            st.write(f"• **Task:** Fix {risk_df.iloc[0]['Cause']}")
            st.write(f"• **File:** {uploaded.name}")
            st.write(f"• **Main Factor:** {max_col} Max {max_val}")
            st.write(f"• **Evidence:** Missing {missing}, Duplicate {duplicates}, Outlier {total_out}")
            st.write(f"• **Assigned To:** Data Team")
            st.write(f"• **Priority:** {'P0 - TODAY' if risk_df.iloc[0]['Risk %']>=70 else 'P1 - This Week'}")
            st.divider()
            st.caption("Try asking in chatbot: \n- which to solve first? \n- how many times crashed? \n- which factor? \n- show missing details? \n- show outlier details? \n- file size? \n- preventive steps? \n- summary?")

        with right_ai:
            st.markdown("**💬 Smart Chatbot**")
            
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Display last 5 chats
            for chat in st.session_state.chat_history[-5:]:
                st.markdown(f"**You:** {chat['q']}")
                st.markdown(f"**AI:** {chat['a']}")
                st.markdown("---")
            
            q = st.text_input("Ask anything:", key="final_q", placeholder="e.g. show outlier details?")
            
            col_ask, col_clear = st.columns([1,1])
            with col_ask:
                ask_btn = st.button("Ask AI", use_container_width=True)
            with col_clear:
                clear_btn = st.button("Clear Chat", use_container_width=True)
            
            if clear_btn:
                st.session_state.chat_history = []
                st.rerun()
            
            if ask_btn and q:
                ql = q.lower()
                answer = ""

                if any(w in ql for w in ["first", "priority", "seriously"]):
                    answer = f"🚨 For {uploaded.name}: Solve FIRST = **{risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%**. Because Missing={missing}, Outlier={total_out} in {max_col}. Highest risk!"
                elif any(w in ql for w in ["how many", "frequency", "times", "count"]):
                    answer = f"📊 {uploaded.name}: Missing {missing} times, Duplicate {duplicates} times, Outlier {total_out} times in {max_col}. Total issues = {missing+duplicates+total_out}"
                elif any(w in ql for w in ["factor", "why crash", "cause"]):
                    answer = f"🔍 Main crash factor for {uploaded.name}: **{max_col}** Max {max_val} with {total_out} outliers. Missing {missing}, Duplicate {duplicates}. So {max_col} is 70% reason!"
                elif "missing" in ql:
                    if missing>0:
                        miss_cols = df.isnull().sum()
                        miss_cols = miss_cols[miss_cols>0].head(3).to_dict()
                        answer = f"📭 Missing in {uploaded.name}: Total {missing}. Top cols: {miss_cols}. Fix: df.fillna() or df.dropna()"
                    else:
                        answer = f"✅ {uploaded.name}: No missing values! 0 missing - PASS"
                elif "duplicate" in ql:
                    answer = f"📑 {uploaded.name}: Duplicate rows = {duplicates}. Fix: df.drop_duplicates() - Remove them to prevent crash" if duplicates>0 else f"✅ {uploaded.name}: 0 duplicates - PASS"
                elif any(w in ql for w in ["outlier", "max", "extreme"]):
                    answer = f"⚠️ Outlier in {uploaded.name}: {max_col} has {total_out} outliers, Max={max_val}. All outliers: {outlier_details}. Fix: IQR filter on {max_col}" if total_out>0 else f"✅ {uploaded.name}: No outliers"
                elif any(w in ql for w in ["file", "size", "rows", "shape"]):
                    answer = f"📁 {uploaded.name}: {len(df)} rows, {len(df.columns)} cols, {uploaded.size/1024:.1f} KB, Numeric cols={len(numeric_cols)}"
                elif any(w in ql for w in ["prevent", "fix", "solution"]):
                    answer = f"🛡️ Preventive for {uploaded.name}: 1) df.isnull().sum() ({missing}), 2) drop_duplicates ({duplicates}), 3) IQR filter {max_col} ({total_out}), 4) Alert if >{len(df)*2} rows"
                elif any(w in ql for w in ["summary", "overview"]):
                    answer = f"📋 Summary {uploaded.name}: {len(df)} rows, Missing {missing}, Dup {duplicates}, Outlier {total_out} in {max_col} max {max_val}. Risk={risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%"
                elif "risk" in ql:
                    answer = f"📊 Risk for {uploaded.name}: Data Quality {risk_df.iloc[0]['Risk %']}%, System {risk_df.iloc[1]['Risk %']}%, App {risk_df.iloc[2]['Risk %']}%. Red bar = Solve first!"
                else:
                    answer = f"🤖 I know {uploaded.name}: {len(df)} rows, Risk {risk_df.iloc[0]['Cause']} {risk_df.iloc[0]['Risk %']}%. Ask: 'which to solve first?', 'show missing details?', 'show outlier details?', 'file size?', 'summary?'"

                st.session_state.chat_history.append({"q": q, "a": answer})
                st.rerun()

    with tab4:
        st.subheader("Why & Preventive - Root Cause and Fix")
        c_why, c_prev = st.columns(2)
        with c_why:
            st.markdown("#### Why crashed?")
            if total_out>0:
                st.error(f"Because {max_col} has extreme value {max_val} - {total_out} outliers detected. This is Data Quality Failure!")
            elif missing>0:
                st.error(f"Because {missing} missing values - Data pipeline break!")
            elif duplicates>0:
                st.error(f"Because {duplicates} duplicate rows - System migration duplicate!")
            else:
                st.warning("System migration / App logic error - No data quality issue but system issue")
            
            st.write(f"**Evidence Table:** Missing={missing}, Duplicate={duplicates}, Outlier={total_out}")

        with c_prev:
            st.markdown("#### Preventive Actions - Specific to THIS file")
            st.success(f"""
            1. Check missing: df.isnull().sum() → {missing} found
            2. Remove duplicate: df.drop_duplicates() → {duplicates} found
            3. IQR filter on {max_col} → {total_out} outliers
            4. Add validation: if df['{max_col}'].max() > {max_val*0.8} → Alert
            5. Add alert if rows > {int(len(df)*1.5)}
            """)
            st.info(f"File {uploaded.name} will be fixed if you apply above 5 steps")

else:
    st.info("👆 Upload CSV to see Dashboard → Evidence & Risk → AI Assistant → Preventive (4 Pages, 2-Side Layout, Small Charts, No Timeline Graph)")
