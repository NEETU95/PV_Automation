import requests
from PyPDF2 import PdfReader
from general_reporter import get_general_reporter
from patient_tab import get_patient_text
from parent import get_parent_text
import spacy
import pysftp
import streamlit as st

def pdf_extraction(pdf_info: str):
    try:
        ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969')
        with ftp.cd('/var/sftp/upload/pvtestusers/'):
            files = ftp.listdir()
            for file in files:
                if pdf_info in file:
                    ftp.get(file)
                    st.write('Yes, downloaded both files')
                    if 'Weekly' in file:
                        weekly_reader = file
                    else:
                        source_document = file

        weekly_reader = PdfReader(weekly_reader)
        source_file_reader = PdfReader(source_document)

        weekly_reader_num_pages = len(weekly_reader.pages)
        source_file_num_pages = len(source_file_reader.pages)

        weekly_text = ""
        all_text = ""
        nlp = spacy.load("en_core_web_sm")
        nlp_1 = spacy.load("en_ner_bc5cdr_md")

        # Loop through all pages and extract text
        for page_num in range(source_file_num_pages):
            page = source_file_reader.pages[page_num]
            text = page.extract_text()
            all_text += text

        for page_num in range(weekly_reader_num_pages):
            page = weekly_reader.pages[page_num]
            text = page.extract_text()
            weekly_text += text

        meta = source_file_reader.metadata
        general_extraction, reporter_extraction = get_general_reporter(
            source_text=all_text,
            weekly_text_1=weekly_text,
            en_core=nlp,
            meta_data=meta
        )

        st.write(general_extraction, reporter_extraction)

        patient_extraction = get_patient_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)
        parent_extraction = get_parent_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)

        response_data = {
            "general_information": general_extraction,
            "reporter": reporter_extraction,
            "patient": patient_extraction,
            "parent": parent_extraction
        }

        st.write(response_data)  # Display response_data in Streamlit

        url = "https://demo.topiatech.co.uk/PV/createCaseAI"
        response_api = requests.post(url, json=response_data)

        if response_api.status_code == 200:
            st.success("API request successful.")
            st.write("Status Code:", response_api.status_code)
            st.write("Response Headers:", response_api.headers)
        else:
            st.error(f"API request failed with status code {response_api.status_code}: {response_api.text}")
            st.write(response_api.text)

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")

# Streamlit UI
st.title("PDF Extraction and Analysis")
pdf_info = st.text_input("Enter PDF Info:")
if st.button("Extract and Analyze"):
    pdf_extraction(pdf_info)
