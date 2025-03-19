import os
import tempfile
import traceback
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import google.generativeai as genai

# Import the CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Medical Report Analyzer",
              description="API for analyzing medical reports using Gemini API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (very permissive for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AnalysisResult(BaseModel):
    report: str

@app.on_event("startup")
async def startup_event():
    # Check if API key is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY environment variable not set")

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_medical_report(file: UploadFile = File(...)):
    """
    Analyze a medical report PDF using Gemini API.

    - **file**: PDF file containing medical report data

    Returns a structured, human-friendly medical report analysis.
    """
    print(f"Received file: {file.filename}")
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Ensure API key is available
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    print("API key validated")
    temp_path = None
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Write uploaded file content to temp file
            content = await file.read()
            print(f"Read {len(content)} bytes from uploaded file")
            temp_file.write(content)
            temp_path = temp_file.name
            print(f"Saved to temporary file: {temp_path}")

        # Initialize Gemini client
        print("Configuring Gemini API")
        genai.configure(api_key=api_key)

        # System prompt for Gemini
        system_prompt = """Please analyze the provided medical report PDF and follow these instructions:

1. Overall Summary:
   - Provide a clear, detailed overview of the report.
   - Highlight any significant trends, abnormalities, or notable findings.
   - Use simple language so a non-medical person can understand.

2. Potential Diagnoses:
   - Suggest possible medical conditions based on abnormal biomarker values.
   - Use probability-based language (e.g., "This may indicate...", "There is a possibility of...").
   - Explain how each abnormal biomarker relates to potential diagnoses.
   - Avoid definitive medical conclusions—this is for informational purposes only.

3. Medical Recommendations:
   - Provide actionable health advice based on the findings.
   - Include dietary, lifestyle, and medical check-up recommendations.
   - If necessary, suggest consulting a doctor for further evaluation.

Use easy-to-understand language and explain each biomarker's role with real-world analogies.
Use a traffic light system 🚦 to indicate risk:
- 🟢 Normal: Healthy range, no concern.
- 🟡 Borderline: Slightly off, needs monitoring.
- 🔴 Concerning: Needs medical attention.

Format your response to include:
- Medical Report Summary
- Biomarker Analysis with Overall Summary, Potential Diagnoses, and Medical Recommendations
- What's Good? section
- What Needs Attention? section
- What Should You Do? section"""

        # Create a generative model - compatible with older versions
        print("Creating generative model")
        try:
            # Create the model with basic parameters
            generation_config = {
                "temperature": 1.0,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",  # Using more widely available model
                generation_config=generation_config
            )
            
            print("Model created successfully")
        except Exception as model_error:
            print(f"Error creating model: {str(model_error)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500, 
                detail=f"Error creating Gemini model: {str(model_error)}"
            )
        
        # Process the PDF file - read as binary
        print(f"Reading PDF file from {temp_path}")
        with open(temp_path, "rb") as f:
            file_data = f.read()
            print(f"Read {len(file_data)} bytes from PDF file")
        
        # Generate content with the PDF data
        print("Attempting to generate content")
        try:
            # Send the PDF along with the system prompt
            response = model.generate_content(
                [system_prompt,
                 {"mime_type": "application/pdf", "data": file_data}]
            )
            
            print("Content generation successful")
            
            # Extract the result
            result = response.text
            print(f"Response length: {len(result)} characters")
        except Exception as gen_error:
            print(f"Error generating content: {str(gen_error)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating content: {str(gen_error)}"
            )

        # Clean up the temporary file
        try:
            os.unlink(temp_path)
            print(f"Deleted temporary file: {temp_path}")
            temp_path = None
        except Exception as cleanup_error:
            print(f"Error cleaning up temp file: {str(cleanup_error)}")

        return AnalysisResult(report=result)

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path:
            try:
                os.unlink(temp_path)
                print(f"Cleaned up temp file during exception handling: {temp_path}")
            except:
                print("Failed to clean up temp file during exception")
                pass

        error_traceback = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(error_traceback)
        
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error analyzing report: {str(e)}", "traceback": error_traceback}
        )

@app.get("/test")
async def test_endpoint():
    """
    Simple test endpoint to verify the API is running properly
    """
    try:
        # Try to get the version of the google-generativeai library
        version = getattr(genai, "__version__", "unknown")
        return {
            "status": "API is running", 
            "api_key_set": bool(os.environ.get("GEMINI_API_KEY")),
            "library_version": version
        }
    except Exception as e:
        return {
            "status": "API is running, but encountered an error", 
            "error": str(e)
        }

@app.get("/")
async def root():
    return {"message": "Medical Report Analysis API is running. Use /analyze endpoint to analyze reports."}

if __name__ == "__main__":
    import uvicorn
    print("Starting server on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)