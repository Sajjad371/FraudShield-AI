import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="ABC Bank FraudShield", layout="wide")

# ---------------------------------------------------
# PROFESSIONAL UI STYLE
# ---------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"] {
font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"]{
background-color:#F4F6F8;
}

.header{
background:#0B3D91;
padding:20px;
color:white;
border-radius:6px;
box-shadow:0 4px 10px rgba(0,0,0,0.1);
display:flex;
justify-content:space-between;
align-items:center;
}

.logo{
font-size:26px;
font-weight:600;
}

.system{
font-size:14px;
opacity:0.9;
}

.status{
background:#2ECC71;
padding:5px 12px;
border-radius:4px;
font-size:13px;
}

.section{
font-size:22px;
font-weight:600;
margin-top:35px;
color:#0B3D91;
}

.metric-card{
background:white;
padding:18px;
border-radius:8px;
box-shadow:0 2px 8px rgba(0,0,0,0.05);
text-align:center;
}

.metric-value{
font-size:24px;
font-weight:600;
}

.metric-label{
font-size:13px;
color:#666;
}

.result-card{
padding:30px;
border-radius:8px;
text-align:center;
font-size:28px;
font-weight:700;
}

.approve{
background:#D4EDDA;
color:#155724;
}

.flag{
background:#FFF3CD;
color:#856404;
}

.block{
background:#F8D7DA;
color:#721C24;
font-size:34px;
}

.stButton button{
width:100%;
background:#0B3D91;
color:white;
border-radius:6px;
height:48px;
font-size:16px;
}

.stButton button:hover{
background:#072E6F;
}

.footer{
text-align:center;
margin-top:40px;
color:#777;
font-size:14px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown("""
<div class="header">
<div>
<div class="logo">ABC Bank</div>
<div class="system">FraudShield AI Monitoring Platform</div>
</div>
<div class="status">System Online</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "stats" not in st.session_state:
    st.session_state.stats = {"APPROVE":0,"FLAG":0,"BLOCK":0}

if "fraud_table" not in st.session_state:
    st.session_state.fraud_table = []

if "total_transactions" not in st.session_state:
    st.session_state.total_transactions = 0

# ---------------------------------------------------
# METRIC TILES
# ---------------------------------------------------

c1,c2,c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-value">{st.session_state.total_transactions}</div>
    <div class="metric-label">Transactions Scanned</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-value">{st.session_state.stats["BLOCK"]}</div>
    <div class="metric-label">Fraud Detected</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
    <div class="metric-value">{st.session_state.stats["FLAG"]}</div>
    <div class="metric-label">Flagged Transactions</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------

left,right = st.columns([1,1])

with left:

    st.markdown('<div class="section">Transaction Input</div>', unsafe_allow_html=True)

    row1 = st.columns(2)
    row2 = st.columns(2)
    row3 = st.columns(2)

    with row1[0]:
        type_option = st.selectbox("Transaction Type",
        ["PAYMENT","TRANSFER","CASH_OUT","DEBIT"])

    with row1[1]:
        amount = st.number_input("Transaction Amount", value=1000.0)

    with row2[0]:
        oldbalanceOrg = st.number_input("Old Balance Origin", value=5000.0)

    with row2[1]:
        newbalanceOrig = st.number_input("New Balance Origin", value=4000.0)

    with row3[0]:
        oldbalanceDest = st.number_input("Old Balance Destination", value=2000.0)

    with row3[1]:
        newbalanceDest = st.number_input("New Balance Destination", value=3000.0)

    if amount > 1000000:
        st.warning("High value transaction detected")

type_mapping = {
"PAYMENT":3,
"TRANSFER":4,
"CASH_OUT":1,
"DEBIT":2
}

type_encoded = type_mapping[type_option]

# ---------------------------------------------------
# ACTION BUTTON
# ---------------------------------------------------

analyze = st.button("Run AI Fraud Analysis")

# ---------------------------------------------------
# ANALYSIS RESULT
# ---------------------------------------------------

with right:

    st.markdown('<div class="section">Risk Analysis</div>', unsafe_allow_html=True)

    if analyze:

        data = {
        "step":1,
        "type":type_encoded,
        "amount":amount,
        "oldbalanceOrg":oldbalanceOrg,
        "newbalanceOrig":newbalanceOrig,
        "oldbalanceDest":oldbalanceDest,
        "newbalanceDest":newbalanceDest,
        "isFlaggedFraud":0
        }

        try:

            response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=data
            )

            result = response.json()

            fraud_prob = result.get("fraud_probability")
            risk_score = result.get("risk_score")
            decision = result.get("decision")

            st.session_state.total_transactions += 1

            if decision in st.session_state.stats:
                st.session_state.stats[decision]+=1

            fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text':"Risk Score"},
            gauge={
            'axis':{'range':[0,100]},
            'bar':{'color':"black"},
            'steps':[
            {'range':[0,40],'color':"#2ECC71"},
            {'range':[40,70],'color':"#F1C40F"},
            {'range':[70,100],'color':"#E74C3C"}
            ]
            }))

            st.plotly_chart(fig,use_container_width=True)

            if decision == "APPROVE":
                st.markdown('<div class="result-card approve">APPROVED</div>', unsafe_allow_html=True)

            elif decision == "FLAG":
                st.markdown('<div class="result-card flag">FLAGGED FOR REVIEW</div>', unsafe_allow_html=True)

            else:
                st.markdown('<div class="result-card block">BLOCKED</div>', unsafe_allow_html=True)

            if decision in ["FLAG","BLOCK"]:

                st.session_state.fraud_table.append({
                "Time":datetime.now().strftime("%H:%M:%S"),
                "Amount":f"${amount:,.0f}",
                "Type":type_option,
                "Risk Score":risk_score,
                "Status":"Open",
                "Decision":decision
                })

        except Exception as e:

            st.error("API connection error")
            st.write(e)

    else:

        st.info("Awaiting transaction analysis")

# ---------------------------------------------------
# FRAUD MONITORING
# ---------------------------------------------------

st.markdown('<div class="section">Fraud Monitoring</div>', unsafe_allow_html=True)

stats_df = pd.DataFrame(
list(st.session_state.stats.items()),
columns=["Decision","Count"]
)

fig = go.Figure()

fig.add_bar(
x=stats_df["Decision"],
y=stats_df["Count"],
marker_color=["#2ECC71","#F1C40F","#E74C3C"]
)

st.plotly_chart(fig,use_container_width=True)

# ---------------------------------------------------
# INVESTIGATION LOG
# ---------------------------------------------------

st.markdown('<div class="section">Investigation Log</div>', unsafe_allow_html=True)

if len(st.session_state.fraud_table)>0:

    fraud_df = pd.DataFrame(st.session_state.fraud_table)

    st.dataframe(fraud_df,use_container_width=True)

else:

    st.write("No suspicious transactions detected.")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown("""
<div class="footer">
ABC Bank Cyber Security Division<br>
FraudShield AI Monitoring Platform<br><br>
All Rights Reserved — Sajjad Dahani
</div>
""", unsafe_allow_html=True)
