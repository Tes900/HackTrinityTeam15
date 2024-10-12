import pdfplumber
import logging
import html
from io import BytesIO
from openai import OpenAI  # Ensure you have the OpenAI Python library installed
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set your OpenAI API key securely
# Replace 'YOUR_API_KEY' with your actual OpenAI API key
client = OpenAI(api_key='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')

def extract_text_from_pdf(pdf_content):
    """Extracts text from a PDF file using pdfplumber."""
    text = ""
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

def split_text_into_chunks(text, max_tokens=2000):
    """Splits the text into chunks to meet the token limit."""
    max_length = max_tokens * 4  # Approximate character length
    for i in range(0, len(text), max_length):
        yield text[i:i + max_length]

def find_relevant_clauses(pdf_text, problems):
    """Extracts relevant clauses by sending chunks to the OpenAI API."""
    chunks = list(split_text_into_chunks(pdf_text))
    relevant_clauses = []
    
    for chunk in chunks:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Use a valid model name
                messages=[
                    {"role": "system", "content": "You are an intelligent legal assistant designed to extract clauses relevant to rental problems."},
                    {"role": "user", "content": f"Identify and extract any clauses from the following rental contract section that directly address or are relevant to the following issues: {problems}. If no relevant clause is found for a specific issue, return 'NULL' for that issue. Focus on clauses that contain specific terms, conditions, or obligations related to each issue listed. Only provide the exact clause(s) that pertain to the issues without additional commentary. Contract Section: {chunk}"}
                ],
                max_tokens=300,
                temperature=0.3
            )
            clause_text = completion.choices[0].message.content.strip()
            logging.debug(f"OpenAI API response for clauses: {clause_text}")
            if clause_text:
                relevant_clauses.append(clause_text)
            else:
                logging.error("Received empty clause text from OpenAI API.")
        except Exception as e:
            logging.error(f"Error finding relevant clauses: {e}", exc_info=True)
            clause_text = "No relevant clauses found due to an error."
            relevant_clauses.append(clause_text)
    
    return "\n\n".join(relevant_clauses)

def generate_letter(name, landlord_name, landlord_address, problems, communication_history, tone, clauses, user_address, date):
    """Generates a letter based on user inputs and extracted clauses."""
    # Escape user inputs
    name = html.escape(name)
    landlord_address = html.escape(landlord_address)
    landlord_name = html.escape(landlord_name)
    user_address = html.escape(user_address)
    problems = html.escape(problems)
    communication_history = html.escape(communication_history)
    tone = html.escape(tone)
    clauses = html.escape(clauses)
    date = html.escape(date)
    
    prompt = (
        f"""Compose a {tone} letter from the tenant, {name}, to their landlord, {landlord_name}, addressing the ongoing dispute.
Use the information provided below, focusing particularly on the 'Problems' and 'Relevant Clauses' sections to construct a well-supported argument or request.
Ensure the letter maintains a professional tone and is concise, clear, and respectful, given the context of a dispute.

Include the following in the letter:
- A brief introduction that references the ongoing issues and the tenant's objective in reaching out.
- A clear, structured outline of the problems being addressed, supported by the relevant clauses from the rental contract.
- Any important details from the communication history that support the tenant's position or provide context.
- A polite closing statement, reiterating the tenant's desired outcome or next steps.

Details for the Letter:

Tenant Name: {name}
Tenant Address: {user_address}
Date: {date}
Landlord Name: {landlord_name}
Landlord Address: {landlord_address}
Problems: {problems}
Communication History: {communication_history}
Relevant Clauses from the Rental Contract: {clauses}"""
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use a valid model name
            messages=[
                {"role": "system", "content": "You are an assistant designed to create tailored letters for rental disputes based on user inputs and extracted clauses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.4
        )
        if completion.choices and completion.choices[0].message.content:
            letter = completion.choices[0].message.content.strip()
            logging.debug(f"Generated letter: {letter}")
            return letter
        else:
            logging.error("No content in OpenAI API response for letter.")
            return "An error occurred while generating the letter."
    except Exception as e:
        logging.error(f"Error generating letter: {e}", exc_info=True)
        return "An error occurred while generating the letter."

def create_pdf(text):
    """Creates a PDF from text and returns it as bytes."""
    logging.debug("Starting PDF creation.")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    # Normalize newlines
    import re
    text = re.sub(r'\r\n', '\n', text)  # Convert Windows newlines to Unix format
    text = re.sub(r'\r', '\n', text)     # Convert Mac newlines to Unix format

    # Replace multiple newlines with a paragraph separator
    text = re.sub(r'\n{2,}', '\n\n', text)  # Ensure paragraphs are separated by exactly two newlines

    # Split the text into paragraphs based on double newlines
    paragraphs = text.strip().split('\n\n')

    flowables = []
    for para in paragraphs:
        # Replace single newlines within paragraphs with <br/> for line breaks
        para = para.replace('\n', '<br/>')

        # Create a Paragraph object, which can handle basic HTML tags
        flowables.append(Paragraph(para.strip(), style))
        flowables.append(Spacer(1, 12))  # Add space between paragraphs

    # Build the PDF
    try:
        doc.build(flowables)
        logging.debug("PDF built successfully.")
    except Exception as e:
        logging.error(f"Error creating PDF: {e}", exc_info=True)
        raise

    buffer.seek(0)
    return buffer
