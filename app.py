import streamlit as st
import requests
import time
import re
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="Equity Story Generator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 1px solid #e1e5e9;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: #2563eb;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: #6b7280;
        font-size: 1.2rem;
    }
    .input-section {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .story-output {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    .metric-card {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2563eb;
        margin: 0.5rem 0;
    }
    .success-msg {
        background: #ecfdf5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .demo-notice {
        background: #fef3c7;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📈 Equity Story Generator</h1>
    <p>Transform company data into compelling investment narratives</p>
</div>
""", unsafe_allow_html=True)

# Simple Research Function
def simple_research_company(company_url: str):
    """Simple company research using basic text extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(company_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Simple text extraction
        html_content = response.text.lower()
        
        # Extract company name from URL
        domain = urlparse(company_url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        company_name = domain.split('.')[0].title()
        
        # Look for description in meta tags using regex
        description_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        description = description_match.group(1) if description_match else "Professional company with online presence"
        
        # Look for common business keywords
        business_indicators = []
        keywords = ['technology', 'software', 'services', 'solutions', 'innovation', 'digital', 'platform', 'consulting', 'finance', 'healthcare', 'manufacturing', 'retail', 'energy']
        for keyword in keywords:
            if keyword in html_content:
                business_indicators.append(keyword)
        
        return {
            'success': True,
            'data': {
                'company_name': company_name,
                'description': description[:200] if description else "Established company with professional web presence",
                'business_keywords': business_indicators[:5],
                'website_url': company_url
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Template Story Generator (works without OpenAI)
def generate_template_story(company_data: dict) -> str:
    """Generate a professional template story based on company data"""
    
    company_name = company_data.get('company_name', 'the company')
    description = company_data.get('description', 'established business')
    keywords = company_data.get('business_keywords', [])
    website = company_data.get('website_url', '')
    
    # Determine business focus
    if 'technology' in keywords or 'software' in keywords or 'digital' in keywords:
        sector = "technology"
        focus = "technological innovation and digital solutions"
    elif 'finance' in keywords or 'consulting' in keywords:
        sector = "financial services"
        focus = "financial expertise and client advisory services"
    elif 'healthcare' in keywords:
        sector = "healthcare"
        focus = "healthcare solutions and patient care"
    else:
        sector = "business services"
        focus = "operational excellence and customer value"
    
    story = f"""
# Investment Analysis: {company_name}

## Executive Summary

{company_name} represents a compelling investment opportunity in the {sector} sector. The company demonstrates strong market positioning with a focus on {focus}. Based on our analysis of their online presence and business model, {company_name} appears well-positioned for sustainable growth and value creation.

## Business Overview

{company_name} operates as an established player in the {sector} industry. {description}

The company's business model centers around delivering value through their core competencies in {', '.join(keywords[:3]) if keywords else 'business operations'}. Their professional web presence and market positioning suggest a mature organization with established operational capabilities.

## Investment Highlights

• **Market Position**: {company_name} maintains a professional market presence with established brand recognition
• **Operational Focus**: Strong emphasis on {focus}
• **Digital Presence**: Professional online platform demonstrating commitment to customer engagement
• **Business Model**: Diversified approach to value creation in the {sector} space
• **Growth Potential**: Positioned to capitalize on industry trends and market opportunities

## Market Opportunity

The {sector} industry continues to show resilience and growth potential. Companies like {company_name} that demonstrate operational excellence and market awareness are well-positioned to capture increasing market share. Industry trends favor organizations that can adapt to changing customer needs while maintaining operational efficiency.

## Risk Considerations

• **Market Competition**: Competitive pressures within the {sector} industry may impact margins
• **Economic Sensitivity**: Business performance may be influenced by broader economic conditions
• **Operational Execution**: Success depends on continued effective management and strategic execution
• **Technology Evolution**: Need to adapt to changing technology and customer expectations

## Investment Conclusion

{company_name} presents an interesting investment opportunity for investors seeking exposure to the {sector} sector. The company's established market presence, professional operations, and strategic focus on {focus} provide a solid foundation for potential returns.

Further due diligence would be recommended to validate financial performance, competitive positioning, and specific growth strategies. Overall, {company_name} appears to offer a balanced risk-return profile consistent with established players in the {sector} industry.

---

**Analysis Date**: {time.strftime('%B %d, %Y')}  
**Source**: Company website analysis ({website})  
**Disclaimer**: This analysis is for informational purposes only and does not constitute investment advice.
"""
    
    return story.strip()

# OpenAI Story Generator (when API key is provided)
def generate_ai_story(company_data: dict, api_key: str) -> str:
    """Generate AI story - placeholder for future OpenAI integration"""
    
    # For now, return template story with note about AI upgrade
    template_story = generate_template_story(company_data)
    
    ai_notice = """
---
**🤖 AI Enhancement Available**: This story was generated using our professional template system. 
For AI-powered custom analysis, OpenAI integration will be added in the next update!
"""
    
    return template_story + ai_notice

# Main App Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    company_url = st.text_input(
        "🔗 Company Website URL",
        placeholder="https://example.com",
        help="Enter the full URL of the company's website"
    )
    
    api_key = st.text_input(
        "🔑 OpenAI API Key (Optional)",
        type="password",
        placeholder="sk-... (leave blank for template story)",
        help="Optional: Add API key for AI-generated stories"
    )
    
    generate_button = st.button("✨ Generate Equity Story", type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### 📋 How to Use
    
    1. **Enter Company URL**: Paste any company website
    2. **Generate Story**: Click the button to create professional analysis
    3. **Get Results**: Download your equity story
    
    ### 🚀 Current Features
    - ✅ **Website Analysis**: Extracts company data
    - ✅ **Professional Templates**: Investment-grade stories
    - ✅ **Instant Generation**: No waiting, works immediately
    - 🔜 **AI Integration**: OpenAI support coming soon
    
    ### 💡 Examples
    - `https://apple.com`
    - `https://microsoft.com`
    - `https://tesla.com`
    """)

# Demo Notice
st.markdown("""
<div class="demo-notice">
    <strong>🎉 Demo Version:</strong> This version works immediately without OpenAI dependencies. 
    Professional template stories are generated based on company analysis. AI enhancement coming in next update!
</div>
""", unsafe_allow_html=True)

# Processing and Results
if generate_button:
    if not company_url:
        st.error("⚠️ Please provide a company URL")
    else:
        # Research phase
        with st.spinner("🔍 Analyzing company website..."):
            research_results = simple_research_company(company_url)
            
            if not research_results.get('success'):
                st.error(f"❌ Failed to research company: {research_results.get('error')}")
                st.info("💡 **Tip**: Make sure the URL is accessible and includes 'https://'")
            else:
                st.markdown("""
                <div class="success-msg">
                    ✅ <strong>Company data extracted successfully!</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Story generation phase
                with st.spinner("📝 Generating professional equity story..."):
                    company_data = research_results['data']
                    
                    # Use template story for now (AI integration coming)
                    story = generate_template_story(company_data)
                    
                    # Display results
                    st.markdown('<div class="story-output">', unsafe_allow_html=True)
                    
                    st.markdown("## 📄 Your Professional Equity Story")
                    
                    # Company info metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>Company:</strong><br>
                            {company_data.get('company_name', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>Sector:</strong><br>
                            {', '.join(company_data.get('business_keywords', ['Business'])[:2])}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>Generated:</strong><br>
                            {time.strftime('%B %d, %Y')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Story content
                    st.markdown(story)
                    
                    # Download functionality
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Story as Text",
                            data=story,
                            file_name=f"equity_story_{company_data.get('company_name', 'company').replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        if st.button("🔄 Generate Another Story"):
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem 0;">
    <p>📈 <strong>Equity Story Generator</strong> • Professional Investment Analysis • Built with Streamlit</p>
    <p><em>Disclaimer: This analysis is for informational purposes only and does not constitute investment advice.</em></p>
    <p>Made with ❤️ for professional investors</p>
</div>
""", unsafe_allow_html=True)