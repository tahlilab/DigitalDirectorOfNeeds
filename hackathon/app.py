"""
Streamlit Demo Application
Main UI for Digital Director of Needs hackathon demo
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mock_data import data_generator
from intent_classifier import classifier
from nba_recommender import recommender
from fraud_detector import detector

# Page configuration
st.set_page_config(
    page_title="Digital Director of Needs - AI Demo",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<p class="main-header">🎯 Digital Director of Needs</p>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Contact Center Intelligence Platform** | Hackathon Demo")
    st.markdown("---")
    
    # Sidebar - Customer Selection
    st.sidebar.header("📋 Demo Controls")
    
    customers = data_generator.get_all_customers()
    customer_options = [f"{c['customer_id']} - {c['name']}" for c in customers]
    
    selected_customer = st.sidebar.selectbox(
        "Select Customer Profile",
        customer_options,
        help="Choose a mock customer for the demo"
    )
    
    customer_id = selected_customer.split(" - ")[0]
    customer_context = data_generator.get_customer_by_id(customer_id)
    
    # Display customer context in sidebar
    st.sidebar.markdown("### 👤 Customer Profile")
    st.sidebar.write(f"**Name:** {customer_context['name']}")
    st.sidebar.write(f"**Policy:** {customer_context['policy_type']}")
    st.sidebar.write(f"**Number:** {customer_context['policy_number']}")
    st.sidebar.write(f"**Status:** {customer_context['policy_status']}")
    st.sidebar.write(f"**Sentiment:** {customer_context['sentiment']}")
    st.sidebar.write(f"**LTV:** ${customer_context['lifetime_value']:,}")
    st.sidebar.write(f"**Payment:** {customer_context['payment_status']}")
    
    if customer_context.get('interaction_history'):
        with st.sidebar.expander("📞 Recent Interactions"):
            for interaction in customer_context['interaction_history']:
                st.write(f"• {interaction}")
    
    # Sample message selector
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 Quick Load Samples")
    
    sample_messages = data_generator.get_sample_messages()
    
    # Create buttons for first 5 sample messages
    for i, sample in enumerate(sample_messages[:5]):
        if st.sidebar.button(f"💬 {sample['intent'].replace('_', ' ').title()}", key=f"sample_{i}"):
            st.session_state['message'] = sample['message']
            st.session_state['expected_intent'] = sample['intent']
    
    if st.sidebar.button("🔄 Clear Message"):
        st.session_state['message'] = ""
        if 'expected_intent' in st.session_state:
            del st.session_state['expected_intent']
    
    # Main content area
    st.header("💬 Customer Message Input")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        message = st.text_area(
            "Enter or paste customer message:",
            value=st.session_state.get('message', ''),
            height=120,
            placeholder="Example: I was charged twice for my premium this month...",
            help="Type a customer inquiry or use the sample buttons in the sidebar"
        )
        
        if 'expected_intent' in st.session_state:
            st.info(f"📌 Sample intent: {st.session_state['expected_intent']}")
        
        analyze_button = st.button("🔍 Analyze Message", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("**AI Processing Stages:**")
        st.write("1️⃣ Intent Classification")
        st.write("2️⃣ NBA Recommendations")
        st.write("3️⃣ Fraud Detection")
        st.write("")
        st.caption("⚡ Processing time: ~4-6 seconds")
    
    # Process message
    if analyze_button and message:
        st.markdown("---")
        
        with st.spinner("🤖 AI is analyzing the message..."):
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            # Stage 1: Intent Classification
            status_container.info("🎯 Stage 1/3: Classifying customer intent...")
            progress_bar.progress(33)
            try:
                intent_result = classifier.classify(message, customer_context)
                st.session_state['intent_result'] = intent_result
            except Exception as e:
                st.error(f"Intent classification failed: {e}")
                return
            
            # Stage 2: NBA Recommendations
            status_container.info("💡 Stage 2/3: Generating next-best-actions...")
            progress_bar.progress(66)
            try:
                nba_result = recommender.recommend(
                    intent_result['intent'],
                    customer_context,
                    intent_result['confidence']
                )
                st.session_state['nba_result'] = nba_result
            except Exception as e:
                st.error(f"NBA recommendation failed: {e}")
                return
            
            # Stage 3: Fraud Detection
            status_container.info("⚠️ Stage 3/3: Analyzing fraud risk...")
            progress_bar.progress(100)
            try:
                fraud_result = detector.analyze(
                    message,
                    intent_result['intent'],
                    customer_context
                )
                st.session_state['fraud_result'] = fraud_result
            except Exception as e:
                st.error(f"Fraud detection failed: {e}")
                return
            
            status_container.success("✅ Analysis complete!")
    
    # Display results if available
    if 'intent_result' in st.session_state:
        st.markdown("---")
        st.header("📊 AI Analysis Results")
        
        # Create 2x2 grid layout
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        
        # Panel 1: Intent Classification
        with row1_col1:
            st.subheader("🎯 Intent Classification")
            intent_result = st.session_state['intent_result']
            
            # Display metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Detected Intent", intent_result['intent'].replace('_', ' '))
            with col_b:
                confidence_pct = f"{intent_result['confidence']:.0%}"
                st.metric("Confidence", confidence_pct)
            
            st.write(f"**💭 Reasoning:** {intent_result['reasoning']}")
            st.write(f"**📂 Subcategory:** {intent_result['subcategory']}")
            st.write(f"**😊 Sentiment:** {intent_result['sentiment']}")
            
            # Confidence indicator
            if intent_result['confidence'] >= 0.9:
                st.success("✅ High confidence classification")
            elif intent_result['confidence'] >= 0.7:
                st.info("✓ Good confidence")
            else:
                st.warning("⚠️ Lower confidence - may need human review")
        
        # Panel 2: Next-Best-Actions
        with row1_col2:
            st.subheader("💡 Recommended Actions")
            nba_result = st.session_state['nba_result']
            
            st.write("**🔴 Primary Actions:**")
            for i, action in enumerate(nba_result['primary_actions'], 1):
                priority_emoji = "🔴" if action['priority'] == "IMMEDIATE" else "🟠"
                st.write(f"{priority_emoji} **{i}.** {action['action']}")
                st.caption(f"   ⏱️ {action['estimated_time']} | Priority: {action['priority']}")
            
            if nba_result.get('follow_up_actions'):
                st.write("**🟢 Follow-up Actions:**")
                for i, action in enumerate(nba_result['follow_up_actions'][:2], 1):
                    st.write(f"   {i}. {action['action']}")
            
            st.info(f"**⏰ Estimated Resolution:** {nba_result.get('estimated_resolution_time', 'N/A')}")
            
            if nba_result.get('escalation_required'):
                st.error(f"⚠️ **Escalation Required:** {nba_result.get('escalation_reason', 'See details')}")
        
        # Panel 3: Fraud Risk Analysis
        with row2_col1:
            st.subheader("⚠️ Fraud Risk Analysis")
            fraud_result = st.session_state['fraud_result']
            
            # Color-code risk level
            risk_colors = {
                "LOW": ("🟢", "success"),
                "MEDIUM": ("🟡", "warning"),
                "HIGH": ("🟠", "warning"),
                "CRITICAL": ("🔴", "error")
            }
            
            risk_emoji, risk_type = risk_colors.get(fraud_result['risk_level'], ("⚪", "info"))
            
            col_x, col_y = st.columns(2)
            with col_x:
                st.metric("Fraud Score", f"{fraud_result['fraud_score']}/100")
            with col_y:
                st.metric("Risk Level", f"{risk_emoji} {fraud_result['risk_level']}")
            
            if fraud_result.get('indicators'):
                st.write("**🔍 Indicators:**")
                for indicator in fraud_result['indicators']:
                    st.write(f"• {indicator}")
            
            if fraud_result.get('verification_required'):
                st.error("⛔ **Additional verification REQUIRED before processing**")
            
            if fraud_result.get('reasoning'):
                with st.expander("📋 Detailed Analysis"):
                    st.write(fraud_result['reasoning'])
        
        # Panel 4: Agent Script & Resources
        with row2_col2:
            st.subheader("📝 Agent Resources")
            
            st.write("**💬 Suggested Script:**")
            st.info(nba_result.get('agent_script', 'No script available'))
            
            if nba_result.get('knowledge_articles'):
                st.write("**📚 Knowledge Articles:**")
                for article in nba_result['knowledge_articles']:
                    st.write(f"• {article}")
            
            if nba_result.get('potential_upsell'):
                st.write("**💼 Upsell Opportunity:**")
                st.write(nba_result['potential_upsell'])
            
            # Action buttons
            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Accept & Process", use_container_width=True, type="primary"):
                    st.success("✓ Recommendations accepted")
            with col_btn2:
                if st.button("✏️ Override & Edit", use_container_width=True):
                    st.info("Opening override mode...")
        
        # Export/Download options
        st.markdown("---")
        with st.expander("💾 Export Analysis Results"):
            st.json({
                "customer_id": customer_context['customer_id'],
                "message": message,
                "intent": intent_result,
                "recommendations": nba_result,
                "fraud_analysis": fraud_result
            })
    
    # Footer
    st.markdown("---")
    st.caption("🎯 Digital Director of Needs | 8-Hour Hackathon Demo | Built with Streamlit + GPT-4o")

if __name__ == "__main__":
    main()
