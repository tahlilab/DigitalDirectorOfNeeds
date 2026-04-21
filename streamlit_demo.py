"""
Streamlit Demo - Digital Director of Needs
Interactive visualization of AI-enhanced call flow
"""

import streamlit as st
import json
from pathlib import Path
import time

# Page config
st.set_page_config(
    page_title="Digital Director of Needs - Demo",
    page_icon="📞",
    layout="wide"
)

# Title
st.title("📞 Digital Director of Needs")
st.subheader("AI-Enhanced LTC Insurance Call Flow Demo")

# Sidebar - Test Scenarios
st.sidebar.header("Test Scenarios")
scenario = st.sidebar.radio(
    "Select a scenario:",
    [
        "🟢 Claim Status - Self-Service",
        "🔵 Payment Inquiry",
        "🟡 Third-Party Call (Needs Auth)",
        "🔴 Agent Request",
        "⚪ Coverage Question"
    ]
)

# Define scenarios
scenarios = {
    "🟢 Claim Status - Self-Service": {
        "utterance": "I need to check my claim status",
        "expected_intent": "CLAIM_STATUS",
        "expected_confidence": 85,
        "expected_path": "Self-Service",
        "call_time": "15 seconds",
        "old_time": "90 seconds"
    },
    "🔵 Payment Inquiry": {
        "utterance": "I want to pay my premium",
        "expected_intent": "PAYMENT",
        "expected_confidence": 90,
        "expected_path": "Self-Service",
        "call_time": "20 seconds",
        "old_time": "90 seconds"
    },
    "🟡 Third-Party Call (Needs Auth)": {
        "utterance": "I'm calling about my mother's claim",
        "expected_intent": "CLAIM_STATUS",
        "expected_confidence": 85,
        "expected_path": "Transfer to Auth Flow",
        "call_time": "45 seconds",
        "old_time": "6 minutes"
    },
    "🔴 Agent Request": {
        "utterance": "I need to speak to an agent",
        "expected_intent": "AGENT_REQUEST",
        "expected_confidence": 95,
        "expected_path": "Immediate Transfer",
        "call_time": "10 seconds",
        "old_time": "90 seconds"
    },
    "⚪ Coverage Question": {
        "utterance": "What's covered under my policy?",
        "expected_intent": "COVERAGE_INQUIRY",
        "expected_confidence": 88,
        "expected_path": "Self-Service",
        "call_time": "25 seconds",
        "old_time": "90 seconds"
    }
}

selected = scenarios[scenario]

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🕰️ OLD IVR (Current)")
    st.markdown("**5 DTMF Questions**")
    
    old_flow = st.container()
    with old_flow:
        st.markdown("""
        1. ⏱️ "Press 1 if you're the policy holder..."
        2. ⏱️ "Press 1 for agent commissions..."
        3. ⏱️ "Press 1 for rate increase..."
        4. ⏱️ "Press 1 to use text chat..."
        5. ⏱️ "Press 1 for claims, 2 for payments..."
        
        **Average Time:** 60-90 seconds  
        **Self-Service Rate:** 5%  
        **Abandonment:** 15%
        """)
        
        st.metric("Call Duration", selected["old_time"], delta=None)
        st.metric("Customer Effort", "High 😞", delta_color="off")

with col2:
    st.header("🚀 NEW AI IVR (Enhanced)")
    st.markdown("**Single AI Question**")
    
    new_flow = st.container()
    with new_flow:
        st.markdown(f"""
        **AI:** "Thank you for calling. How can I help you today?"
        
        **Customer:** "{selected['utterance']}"
        
        **AI Classifies:**
        - Intent: `{selected['expected_intent']}`
        - Confidence: `{selected['expected_confidence']}%`
        - Path: `{selected['expected_path']}`
        
        **Average Time:** 15-45 seconds  
        **Self-Service Rate:** 37%  
        **Abandonment:** 8%
        """)
        
        st.metric("Call Duration", selected["call_time"], delta=f"-{selected['old_time']}", delta_color="inverse")
        st.metric("Customer Effort", "Low 😊", delta_color="off")

# Simulation Button
st.markdown("---")
if st.button("▶️ Run Simulation", type="primary", use_container_width=True):
    st.header("📊 Live Call Flow Simulation")
    
    # Progress container
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        ("🔊 AI Greeting", "Thank you for calling. I'm your digital assistant. How can I help you today?"),
        ("🎤 Customer Speaks", selected['utterance']),
        ("🤖 Lex Bot Captures", "Speech-to-text transcription complete"),
        ("⚡ GPT-4o Classification", f"Intent: {selected['expected_intent']}, Confidence: {selected['expected_confidence']}%"),
        ("🔀 Route Decision", f"Routing to: {selected['expected_path']}"),
    ]
    
    # Add outcome step
    if selected['expected_path'] == "Self-Service":
        if "CLAIM_STATUS" in selected['expected_intent']:
            outcome = ("✅ Self-Service Complete", "Your claim #12345 was approved on 04/10/2026 for $2,800. Check mailed 04/18.")
        elif "PAYMENT" in selected['expected_intent']:
            outcome = ("✅ Self-Service Complete", "Your premium is $285/month, due 05/01/2026. Last payment received 04/01.")
        else:
            outcome = ("✅ Self-Service Complete", "Your daily benefit is $200 with $300K lifetime maximum.")
    else:
        outcome = ("📲 Transfer", f"Transferring to {selected['expected_path']}...")
    
    steps.append(outcome)
    
    # Animate steps
    for i, (step_name, step_detail) in enumerate(steps):
        progress_bar.progress((i + 1) / len(steps))
        status_text.markdown(f"**{step_name}**  \n{step_detail}")
        time.sleep(1.5)
    
    st.success("✅ Simulation Complete!")
    
    # Show metrics
    st.markdown("### 📈 Impact Metrics")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        time_saved = int(selected['old_time'].split()[0]) - int(selected['call_time'].split()[0])
        st.metric("Time Saved", f"{time_saved} sec", delta=f"-{time_saved}s", delta_color="inverse")
    
    with metric_col2:
        if selected['expected_path'] == "Self-Service":
            st.metric("Agent Needed?", "No ✅", delta="Saved 1 agent call", delta_color="inverse")
        else:
            st.metric("Agent Needed?", "Yes", delta="Context passed", delta_color="off")
    
    with metric_col3:
        nps_gain = "+25 points" if selected['expected_path'] == "Self-Service" else "+15 points"
        st.metric("NPS Impact", nps_gain, delta=nps_gain, delta_color="normal")

# Business Impact
st.markdown("---")
st.header("💰 Business Impact (Annual)")

impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)

with impact_col1:
    st.metric("Cost Savings", "$1.14M", help="Based on 50K calls/month, 37% self-service rate")

with impact_col2:
    st.metric("NPS Improvement", "+25 pts", help="From 55 to 80 for self-served calls")

with impact_col3:
    st.metric("Abandonment Reduction", "-47%", help="From 15% to 8%")

with impact_col4:
    st.metric("Self-Service Rate", "37%", help="Up from 5%")

# Technical Architecture
with st.expander("🔧 Technical Architecture"):
    st.markdown("""
    ### Components
    
    1. **Amazon Lex V2** - Speech recognition and natural language understanding
    2. **AWS Lambda (GPT-4o Classifier)** - Azure OpenAI GPT-4o for intent classification
    3. **AWS Lambda (Self-Service)** - Salesforce integration for data lookup
    4. **Amazon Connect** - Contact flow orchestration
    
    ### Data Flow
    
    ```
    Customer Call → Lex V2 Capture → GPT-4o Classification → Confidence Check
                                                                     ↓
                                          >70%: Self-Service ←─────┘
                                          <70%: Clarification
                                          
    Self-Service → Salesforce Lookup → Response → Disconnect
    
    Third-Party → Auth Flow Transfer (with context)
    ```
    
    ### Integration Points
    
    - **Salesforce:** Claim status, policy data, payment info
    - **Azure OpenAI:** GPT-4o model for intent classification
    - **Amazon Connect:** Contact attributes for context passing
    """)

# Footer
st.markdown("---")
st.caption("Digital Director of Needs - AI-Enhanced Insurance Call Center | Built for Microsoft & Amazon Hackathon 2026")
