from dotenv import load_dotenv
from langserve import add_routes
from langchain_mistralai.chat_models import ChatMistralAI
from fastapi import FastAPI, UploadFile, File, Form
import os
from retrival_model_chain import Retrival_Model_Class
from fastapi.responses import JSONResponse
import pandas as pd
import pdfplumber


load_dotenv()

#llm initialization
app = FastAPI()
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
    # other params...
)
Retrival_Model_Chain = Retrival_Model_Class()
retriever_chain = Retrival_Model_Chain.initialize_chain(llm)


def text_extractor_pdf(path):
    data = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=0)
            sections = page_text.split("\n")
            data.extend(sections)
    return data

#take in resume and description and return the cover letter
@app.post('/generate')
async def generate(resume:UploadFile = File(...), description:str = Form(...)):
    contents = await resume.read()
    with open(resume.filename, 'wb') as f:
        f.write(contents)

    resume_text = text_extractor_pdf(resume.filename)
    resume_string = " ".join(resume_text)
    print(resume_string)
    response = retriever_chain.invoke({"job_description": description, "resume": resume_string})
    return JSONResponse(content={"cover_letter": response})
