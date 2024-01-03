from typing import List
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import create_extraction_chain_pydantic
from langchain.llms import LlamaCpp
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_experimental.chat_models import Llama2Chat

class Actor(BaseModel):
    Age: str = Field(description="age of a patient")
    diseases: List[str] = Field(description="list of diseases of patient")


llm = LlamaCpp(
    model_path="./llama.cpp/models/llama-2-7b-chat.gguf.q4_0.bin",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    verbose=True
)
parser = PydanticOutputParser(pydantic_object=Actor)
context = """A 15-months-old girl who  has admitted with shocks, fever, vomitings, confusion, excessive fatigue and diarrhea.
she was diagnosed with COVID-19. she had no previous history of immunodeficiency or medical comorbidities. Moderate splenomegaly was evident without lymphadenopathy.
complete blood count revealed pancytopenia. Her mother had a medical history of cancer."""

prompt = PromptTemplate(
    template="Extract fields from a given text.\n{format_instructions}\n{text}\n",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# _input = prompt.format_prompt(text=context)
# output = llm(_input.to_string())
#
# parsed = parser.parse(output)
#
# print("parsed output is", parsed)

model = Llama2Chat(llm=llm)
extractor = create_extraction_chain_pydantic(pydantic_schema=Actor, llm=llm)
extracted = extractor.run(context=context)
print("extracted", extracted)