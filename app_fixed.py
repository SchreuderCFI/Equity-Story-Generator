import streamlit as st
import requests
import openai
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📈 Equity Story Generator</h1>
    <p>Transform company data into compelling investment narratives</p>
</div>
""", unsafe_allow_html=True)

# Simple Research Function (without BeautifulSoup)
def simple_research_company(company_url: str):
    """Simple company research using basic text extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(company_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Simple text extraction without BeautifulSoup
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
        keywords = ['technology', 'software', 'services', 'solutions', 'innovation', 'digital', 'platform', 'consulting', 'finance', 'healthcare']
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

# Story Generator with Fixed Error Handling
def generate_story_with_openai(company_data: dict, api_key: str) -> str:
    """Generate equity story using OpenAI"""
    try:
        openai.api_key = api_key
        
        company_name = company_data.get('company_name', 'the company')
        description = company_data.get('description', '')
        keywords = company_data.get('business_keywords', [])
        
        prompt = f"""
You are a professional equity research analyst creating an investment story for {company_name}.

Company Information:
- Company Name: {company_name}
- Description: {description}
- Business Focus: {', '.join(keywords) if keywords else 'General business operations'}
- Website: {company_data.get('website_url', '')}

Please create a compelling equity story that includes:

1. **Executive Summary** (2-3 sentences)
   - Clear value proposition and investment thesis

2. **Business Overview** (1-2 paragraphs)
   - What the company does and market position
   - Core competencies and value creation

3. **Investment Highlights** (4-5 key points)
   - Main reasons why this is an attractive investment
   - Growth drivers and competitive advantages

4. **Market Opportunity** (1 paragraph)
   - Target market and growth potential
   - Industry trends

5. **Risk Considerations** (3-4 points)
   - Key risks and mitigation factors

6. **Investment Conclusion** (1 paragraph)
   - Summary investment recommendation

Write in a professional, analytical tone suitable for institutional investors.
Length: Approximately 600-800 words.
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional equity research analyst with expertise in creating compelling investment narratives."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Handle all OpenAI errors with improved error messages
        error_msg = str(e).lower()
        
        if "invalid api key" in error_msg or "authentication" in error_msg:
            return "❌ **Authentication Error**: Invalid OpenAI API key. Please check your API key and try again."
        elif "rate limit" in error_msg or "quota" in error_msg:
            return "❌ **Rate Limit Error**: OpenAI API rate limit exceeded. Please try again in a moment."
        elif "insufficient_quota" in error_msg:
            return "❌ **Quota Error**: OpenAI API quota exceeded. Please check your account billing."
        else:
            return f"❌ **Error**: {str(e)}"

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
        "🔑 OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Get your API key from https://openai.com/api/"
    )
    
    generate_button = st.button("✨ Generate Equity Story", type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### 📋 How to Use
    
    1. **Enter Company URL**: Paste any company website
    2. **Add API Key**: Get free key from [OpenAI](https://openai.com/api/)
    3. **Generate Story**: Click the button below
    4. **Get Results**: Professional equity story in seconds
    
    ### 🔑 API Key Setup
    - Visit [OpenAI API](https://openai.com/api/)
    - Sign up for free account
    - Create new API key
    - Copy and paste above
    
    ### 💡 Examples
    - `https://apple.com`
    - `https://microsoft.com`
    - `https://tesla.com`
    """)

# Processing and Results
if generate_button:
    if not company_url or not api_key:
        st.error("⚠️ Please provide both company URL and API key")
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
                with st.spinner("🤖 Generating equity story with AI..."):
                    company_data = research_results['data']
                    story = generate_story_with_openai(company_data, api_key)
                    
                    if story.startswith("❌"):
                        st.error(story)
                        if "Authentication Error" in story:
                            st.info("💡 **Get your API key**: Visit [OpenAI API](https://openai.com/api/) to create a free account and generate an API key.")
                    else:
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
                                <strong>Website:</strong><br>
                                <a href="{company_url}" target="_blank">Visit Site</a>
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
                                st.experimental_rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem 0;">
    <p>📈 <strong>Equity Story Generator</strong> • Powered by AI • Built with Streamlit</p>
    <p><em>Disclaimer: This analysis is for informational purposes only and does not constitute investment advice.</em></p>
    <p>Made with ❤️ for professional investors</p>
</div>
""", unsafe_allow_html=True)