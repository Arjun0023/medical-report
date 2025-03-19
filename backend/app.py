import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Medical Report Analyzer",
    page_icon="🏥",
    layout="wide",
)

# Custom CSS to improve the appearance
st.markdown("""
<style>
    .title {
        font-size: 42px;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 24px;
        font-weight: 500;
        color: #424242;
        margin-bottom: 30px;
    }
    .report-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E88E5;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 22px;
        font-weight: bold;
        color: #424242;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .normal {
        color: green;
        font-weight: bold;
    }
    .borderline {
        color: orange;
        font-weight: bold;
    }
    .concerning {
        color: red;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    .upload-section {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def process_pdf_with_gemini(uploaded_file):
    """Process the PDF file using Google Gemini API"""
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Gemini API key not found in .env file. Please add GEMINI_API_KEY to your .env file.")
        return None
    
    # Initialize Gemini API
    genai.configure(api_key=api_key)
    
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name
    
    try:
        # System prompt for Gemini
        system_instruction = """🔹 Task:
    Analyze the provided biomarker data and generate a structured, human-friendly medical report.

    ### ***Instructions***:

    1️⃣ Overall Summary: (This Points must be included )
    Provide a clear, detailed overview of the report.
    Highlight any significant trends, abnormalities, or notable findings.
    Use simple language so a non-medical person can understand.

    2️⃣ Potential Diagnoses: (This Points must be included )
    Suggest possible medical conditions based on abnormal biomarker values.
    Use probability-based language (e.g., "This may indicate...", "There is a possibility of...").
    Explain how each abnormal biomarker relates to potential diagnoses.
    Avoid definitive medical conclusions—this is for informational purposes only.

   3️⃣Medical Recommendations: (This Points must be included )
    Provide actionable health advice based on the findings.
    Include dietary, lifestyle, and medical check-up recommendations.
    If necessary, suggest consulting a doctor for further evaluation.

   ### **How to Analyze:**
    - Use **easy-to-understand language**.
    - Definition: A simple explanation of what it is.
    - Function: Why it is important for health.
    - Implications: What an abnormal value could indicate.
    - Explain one line definition
    - Explain each biomarker's role with **real-world analogies**.
    - Use a **traffic light system** 🚦 to indicate risk: (This Points must be included and use color so easy understanding)
      - 🟢 **Normal**: Healthy range, no concern.
      - 🟡 **Borderline**: Slightly off, needs monitoring.
      - 🔴 **Concerning**: Needs medical attention.
    - Explain **why it matters** for health.
    - Provide **simple lifestyle & diet tips**.

    ### **Format Output Like This:**

    📋 **Medical Report Summary**

    ### **Biomarker Analysis**

      This Points must be included
    - Overall Summary
    - Potential Diagnoses
    - Medical Recommendations

    ✅ **What's Good?** (This Points must be included )
    - Hemoglobin: 14.2 g/dL 🟢 (Normal) - Your oxygen levels are good!
    - Calcium: 9.5 mg/dL 🟢 (Normal) - Great for bones & muscles.

    ⚠️ **What Needs Attention?** (This Points must be included )

    - Cholesterol: 210 mg/dL 🟡 (Borderline) - Slightly high, keep an eye on diet.

    🏥 **What Should You Do?** (This Points must be included )
    - Do this step for all biomarker present
    - Do it as the example is given
    - **Cholesterol:** 🔴 (High) → Risk of heart issues. Try adding fiber (oats, nuts), avoid fried food."""
        
        # Create a Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a generation config
        generation_config = {
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Generate content with progress bar
        with st.spinner("Analyzing medical report... This may take a minute"):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)  # Simulate processing time
                progress_bar.progress(i + 1)
            
            # Use the correct method to process the PDF
            with open(temp_path, 'rb') as f:
                pdf_data = f.read()
            
            # Generate the content
            response = model.generate_content(
                contents=[
                    {
                        "parts": [
                            {"text": system_instruction},
                            {"inline_data": {"mime_type": "application/pdf", "data": pdf_data}}
                        ]
                    }
                ],
                generation_config=generation_config
            )
            
            # Extract the result
            result = response.text
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return result
    
    except Exception as e:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        st.error(f"❌ Error analyzing the report: {str(e)}")
        return None

def render_markdown_with_colored_indicators(text):
    """Format the text with colored indicators"""
    # Replace specific indicators with colored spans
    text = text.replace("🟢 (Normal)", "<span class='normal'>🟢 (Normal)</span>")
    text = text.replace("🟡 (Borderline)", "<span class='borderline'>🟡 (Borderline)</span>")
    text = text.replace("🔴 (Low)", "<span class='concerning'>🔴 (Low)</span>")
    text = text.replace("🔴 (High)", "<span class='concerning'>🔴 (High)</span>")
    text = text.replace("🔴 (Concerning)", "<span class='concerning'>🔴 (Concerning)</span>")
    
    return text

def main():
    # App Header
    st.markdown("<div class='title'>🏥 Medical Report Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Upload your medical report for a comprehensive analysis</div>", unsafe_allow_html=True)
    
    # Sidebar information
    with st.sidebar:
        st.image("https://img.freepik.com/free-vector/medical-report-concept-illustration_114360-1765.jpg?size=338&ext=jpg&ga=GA1.1.1826414947.1709856000&semt=ais", width=250)
        st.markdown("### How It Works")
        st.markdown("""
        1. Upload your medical report PDF
        2. Our AI analyzes your biomarkers
        3. Get a comprehensive analysis with:
           - Overall health summary
           - Potential diagnoses
           - Personalized recommendations
        """)
        
        st.markdown("### About")
        st.markdown("""
        This application uses Google's Gemini 2.0 Flash model to analyze medical reports and provide insights in an easy-to-understand format.
        
        ⚠️ **Disclaimer**: This tool is for informational purposes only and does not replace professional medical advice.
        """)
    
    # File Upload Section
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your medical report (PDF)", type="pdf")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_button = st.button("🔍 Analyze Report", type="primary", disabled=not uploaded_file)
    with col2:
        if not uploaded_file:
            st.info("Please upload a PDF file of your medical report to get started")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Analysis and Results
    if uploaded_file and analyze_button:
        st.markdown("<div class='report-header'>📋 Analysis Results</div>", unsafe_allow_html=True)
        
        # Process the PDF with Gemini
        result = process_pdf_with_gemini(uploaded_file)
        
        if result:
            # Format and display the result with colored indicators
            formatted_result = render_markdown_with_colored_indicators(result)
            st.markdown(formatted_result, unsafe_allow_html=True)
            
            # Add download button for the report
            st.download_button(
                label="📥 Download Report",
                data=result,
                file_name="medical_report_analysis.md",
                mime="text/markdown",
            )
        else:
            st.error("Failed to analyze the report. Please try again.")

if __name__ == "__main__":
    main()