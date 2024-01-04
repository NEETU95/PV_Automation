from tornado.web import RequestHandler, Application
from tornado.routing import Rule, PathMatches
import gc
import requests
from PyPDF2 import PdfReader
from general_reporter import get_general_reporter
from patient_tab import get_patient_text
from parent import get_parent_text
import spacy
import pysftp
import streamlit as st


@st.cache_resource()
def setup_api_handler(uri, handler):
    print("Setup Tornado. Should be called only once")

    # Get instance of Tornado
    tornado_app = next(o for o in gc.get_referrers(Application) if o.__class__ is Application)

    # Setup custom handler
    tornado_app.wildcard_router.rules.insert(0, Rule(PathMatches(uri), handler))

# Tornado handler with PDF extraction functionality
class PdfExtractionHandler(RequestHandler):
    def get(self, pdf_info):
        try:
            # Your existing pdf_extraction code
            # Replace 'pdf_info' with the actual value or information you want to pass
            pdf_extraction(pdf_info)
        except Exception as e:
            self.set_status(500)
            self.write(f"Error processing PDF: {str(e)}")

def pdf_extraction(pdf_info:str):
    try:     
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None        
        ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969', cnopts=cnopts)
        ftp._sftp_live = False
        ftp._transport = None        
        with ftp.cd('/var/sftp/upload/pvtestusers/'):
            files = ftp.listdir()
            for file in files:
                if pdf_info in file:
                    ftp.get(file)
                    print('yes downloaded both files')
                    if 'Weekly' in file:
                        weekly_reader = file
                    else:
                        source_document = file
        weekly_reader = PdfReader(weekly_reader)
        source_file_reader = PdfReader(source_document)
        # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
        weekly_reader_num_pages = len(weekly_reader.pages)

        source_file_num_pages = len(source_file_reader.pages)
        weekly_text = ""
        all_text = ""
        nlp = spacy.load("en_core_web_sm")
        nlp_1 = spacy.load("en_ner_bc5cdr_md-0.5.3/en_ner_bc5cdr_md/en_ner_bc5cdr_md-0.5.3")
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
        print(general_extraction, reporter_extraction)
        patient_extraction = get_patient_text(source_text=all_text, en_core=nlp,bcd5r=nlp_1)
        parent_extraction = get_parent_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)

        response = {
            "general_information": general_extraction,
            "reporter": reporter_extraction,
            "patient": patient_extraction,
            "parent": parent_extraction
        }


        url = "https://demo.topiatech.co.uk/PV/createCaseAI"

        # Send the POST request with JSON data
        response = requests.post(url, json=response)

        # Check the response status code
        if response.status_code == 200:
            # Request was successful
            print("API request successful.")
            print("Status Code:", response.status_code)
            print("Response Headers:", response.headers)

        else:
            # Request failed
            print(f"API request failed with status code {response.status_code}: {response.text}")
            print(response.text)

    #   if ftp:
    #         ftp.close()

        return response.status_code

    except Exception as e:
        # raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
        return response.status_code




# New Tornado handler for handling POST requests
class PostHandler(RequestHandler):
    def post(self, data):
        try:
            # Handle POST request logic here
            response_data = {"message": f"Handling POST request with data: {data}"}
            self.set_status(200)
            self.finish(response_data)
        except Exception as e:
            self.set_status(500)
            response_data = {"error": f"Error processing POST request: {str(e)}"}
            self.finish(response_data)

# New Tornado handler for handling GET requests
class GetHandler(RequestHandler):
    def get(self, data):
        try:
            # Handle GET request logic here
            response_data = {"message": f"Handling GET request with data: {data}"}
            self.set_status(200)
            self.finish(response_data)
        except Exception as e:
            self.set_status(500)
            response_data = {"error": f"Error processing GET request: {str(e)}"}
            self.finish(response_data)

class PdfExtractionHandlerWithPysftp(RequestHandler):
    def get(self, pdf_info):
        try:
            # Your existing pdf_extraction code
            # Replace 'pdf_info' with the actual value or information you want to pass
            pdf_extraction_with_pysftp(pdf_info)
        except Exception as e:
            self.set_status(500)
            self.write(f"Error processing PDF: {str(e)}")


def pdf_extraction_with_pysftp(pdf_info: str):
    class My_Connection(pysftp.Connection):
        def __init__(self, *args, **kwargs):
            try:
                if kwargs.get('cnopts') is None:
                    kwargs['cnopts'] = pysftp.CnOpts()
                    kwargs['cnopts'].hostkeys.load('ssh_host_key_new')
                    # cnopts = pysftp.CnOpts()
                    # cnopts.hostkeys.load('ssh_host_rsa_key')
                    # kwargs['cnopts'].hostkeys = None
            except pysftp.HostKeysException as e:
                self._init_error = True
                raise paramiko.ssh_exception.SSHException(str(e))
            else:
                self._init_error = False

            self._sftp_live = False
            self._transport = None
            super().__init__(*args, **kwargs)

        def __del__(self):
            if not self._init_error:
                self.close()

    try:
        # cnopts.hostkeys.load('ssh_host_rsa_key')
        with My_Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969') as sftp:
            l = sftp.listdir()
            with sftp.cd('/var/sftp/upload/pvtestusers/'):
                files = sftp.listdir()
                print(files)
            for file in files:
                if 'main_file.pdf' in file:
                    print('yes')
                    sftp.get(file)
                    print('yes downloaded both files')
                    # if 'Weekly' in file:
                    #     weekly_reader = file
                    #     downloaded = True
                    # else:
                    #     downloaded = False

    except paramiko.ssh_exception.SSHException as e:
        print(e)

# Usage of setup_api_handler with PdfExtractionHandler
setup_api_handler('/api/pdf_extraction/([^/]+)?', PdfExtractionHandler)
setup_api_handler('/api/get_demo/([^/]+)?', GetHandler)
setup_api_handler('/api/post_demo/([^/]+)?', PostHandler)
setup_api_handler('/api/pdftest/([^/]+)?', PdfExtractionHandlerWithPysftp)


# from tornado.web import RequestHandler, Application
# from tornado.routing import Rule, PathMatches
# import gc
# import requests
# from PyPDF2 import PdfReader
# from general_reporter import get_general_reporter
# from patient_tab import get_patient_text
# from parent import get_parent_text
# import spacy
# import pysftp
# import streamlit as st


# @st.cache_resource()
# def setup_api_handler(uri, handler):
#     print("Setup Tornado. Should be called only once")

#     # Get instance of Tornado
#     tornado_app = next(o for o in gc.get_referrers(Application) if o.__class__ is Application)

#     # Setup custom handler
#     tornado_app.wildcard_router.rules.insert(0, Rule(PathMatches(uri), handler))

# # Tornado handler with PDF extraction functionality
# class PdfExtractionHandler(RequestHandler):
#     def get(self, pdf_info):
#         try:
#             # Your existing pdf_extraction code
#             # Replace 'pdf_info' with the actual value or information you want to pass
#             pdf_extraction(pdf_info)
#         except Exception as e:
#             self.set_status(500)
#             self.write(f"Error processing PDF: {str(e)}")

# def pdf_extraction(pdf_info:str):
#     try:     
#         ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969')
#         with ftp.cd('/var/sftp/upload/pvtestusers/'):
#             files = ftp.listdir()
#             for file in files:
#                 if pdf_info in file:
#                     ftp.get(file)
#                     print('yes downloaded both files')
#                     if 'Weekly' in file:
#                         weekly_reader = file
#                     else:
#                         source_document = file
#         weekly_reader = PdfReader(weekly_reader)
#         source_file_reader = PdfReader(source_document)
#         # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
#         weekly_reader_num_pages = len(weekly_reader.pages)

#         source_file_num_pages = len(source_file_reader.pages)
#         weekly_text = ""
#         all_text = ""
#         nlp = spacy.load("en_core_web_sm")
#         nlp_1 = spacy.load("en_ner_bc5cdr_md")
#         # Loop through all pages and extract text
#         for page_num in range(source_file_num_pages):
#             page = source_file_reader.pages[page_num]
#             text = page.extract_text()
#             all_text += text
#         for page_num in range(weekly_reader_num_pages):
#             page = weekly_reader.pages[page_num]
#             text = page.extract_text()
#             weekly_text += text
#         meta = source_file_reader.metadata
#         general_extraction, reporter_extraction = get_general_reporter(
#             source_text=all_text,
#             weekly_text_1=weekly_text,
#             en_core=nlp,
#             meta_data=meta
#         )
#         print(general_extraction, reporter_extraction)
#         patient_extraction = get_patient_text(source_text=all_text, en_core=nlp,bcd5r=nlp_1)
#         parent_extraction = get_parent_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)

#         response = {
#             "general_information": general_extraction,
#             "reporter": reporter_extraction,
#             "patient": patient_extraction,
#             "parent": parent_extraction
#         }


#         url = "https://demo.topiatech.co.uk/PV/createCaseAI"

#         # Send the POST request with JSON data
#         response = requests.post(url, json=response)

#         # Check the response status code
#         if response.status_code == 200:
#             # Request was successful
#             print("API request successful.")
#             print("Status Code:", response.status_code)
#             print("Response Headers:", response.headers)

#         else:
#             # Request failed
#             print(f"API request failed with status code {response.status_code}: {response.text}")
#             print(response.text)

#     #   if ftp:
#     #         ftp.close()

#         return response.status_code

#     except Exception as e:
#         # raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
#         return response.status_code

# # Usage of setup_api_handler with PdfExtractionHandler
# setup_api_handler('/api/pdf_extraction/([^/]+)?', PdfExtractionHandler)
