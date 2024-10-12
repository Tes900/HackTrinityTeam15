from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import traceback
import uvicorn

# Import the utility functions
from .utils import extract_text_from_pdf, find_relevant_clauses, generate_letter, create_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # Replace "*" with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-letter/")
async def generate_letter_endpoint(
    file: UploadFile = File(...),
    name: str = Form(...),
    user_address: str = Form(...),
    date: str = Form(...),
    landlord_name: str = Form(...),
    landlord_address: str = Form(...),
    problems: str = Form(...),
    communication_history: str = Form(...),
    tone: str = Form(...)
):
    try:
        # Read the uploaded PDF file content
        pdf_content = await file.read()
        
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_content)

        # Find relevant clauses related to the problems
        clauses = find_relevant_clauses(pdf_text, problems)

        # Generate the tailored letter based on the extracted clauses
        letter = generate_letter(
            name, landlord_name, landlord_address, problems,
            communication_history, tone, clauses,
            user_address, date)
        
        # Return the letter as JSON response
        return {"letter": letter}

    except Exception as e:
        logging.error(f"Error in generate_letter_endpoint: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "An error occurred while processing your request."},
            status_code=500
        )

# Define a Pydantic model for the request body
class LetterContent(BaseModel):
    letter: str

@app.post("/generate-pdf/")
async def generate_pdf_endpoint(letter_content: LetterContent):
    try:
        letter_text = letter_content.letter

        # Create a PDF from the letter text
        pdf_buffer = create_pdf(letter_text)

        pdf_buffer.seek(0)
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename=edited_letter.pdf"
            }
        )

    except Exception as e:
        logging.error(f"Error in generate_pdf_endpoint: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "An error occurred while generating the PDF."},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
