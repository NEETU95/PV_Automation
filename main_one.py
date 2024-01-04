from fastapi import FastAPI, HTTPException
import requests
from PyPDF2 import PdfReader
from general_reporter import get_general_reporter
from patient_tab import get_patient_text
from parent import get_parent_text
import spacy
import pysftp


# Create a FastAPI instance
app = FastAPI(
    openapi_url="/api/v1/openapi",  # Set the OpenAPI schema URL
    docs_url="/documentation",  # Set the Swagger UI URL
    redoc_url=None  # Disable ReDoc by setting its URL to None
)

@app.post("/")
def pdf_to_json(pdf_info:str):
    #try:
        # ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969')
        # with ftp.cd('/var/sftp/upload/pvtestusers/'):
        #     files = ftp.listdir()
        #     for file in files:
        #         if pdf_info in file:
        #             ftp.get(file)
        #             print('yes downloaded both files')
        #             if 'Weekly' in file:
        #                 weekly_reader = file
        #                 downloaded = True
        #             else:
        #                 downloaded = False
    # except Exception as e:
    #     raise HTTPException(status_code=404, detail=e)
    return pdf_info
