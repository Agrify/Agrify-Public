#------------------------ LIBRARIES ----------------------------------------
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate
#--------------------------------------------------------------------------

def generate(system: str,llm_name: Optional[str] = "llama",):
    # if llm_name == "gpt":
    #     llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # elif llm_name == "llama":
    #     llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")
    # else:
    #     llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", timeout=120)

    llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")

    prompt = ChatPromptTemplate.from_messages([ ("system",system), 
                                               MessagesPlaceholder(variable_name="messages")])
    
    generate = prompt | llm

    return generate    

class scoreFormat(BaseModel):
    Score: str = Field(description="This holds the overall score from evaluation")
    Score_Breakdown_Summary: str = Field(description="This holds the summary of how the score was acheived")

class recommendFormat(BaseModel):
    Recommendation_intro: str = Field(description="This holds the introduction before the recommendation")
    phase_1: dict = Field(description="This holds the 3 tasks to be performed in the first phase, Task1: ..., Task2:..., Task3:...")
    phase_2: dict = Field(description="This holds the 3 tasks to be performed in the second phase, Task1: ..., Task2:..., Task3:...")
    phase_3: dict = Field(description="This holds the 3 tasks to be performed in the third phase, Task1: ..., Task2:..., Task3:...")
    Recommendation_summary: str = Field(description="This holds the summary of the recommendation provided")

class translateFormat(BaseModel):
    message: str = Field(description="This holds the translated text")

def format_output(prompt: str,  task: str,llm_name: Optional[str] = "llama"):
    # if llm_name == "gpt":
    #     llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # elif llm_name == "llama":
    #     llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")
    # else:
    #     llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", timeout=120)

    llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")
    
    if task.lower() == "score":
        parser = JsonOutputParser(pydantic_object=scoreFormat)
    elif task.lower() == "recommend":
        parser = JsonOutputParser(pydantic_object=recommendFormat)

    format_prompt = PromptTemplate(
        template="Format the response provided, where description says summary please summarize, also maintain the language used.\n{format_instructions}\n{response}\n",
        input_variables=["response"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        )
    
    chain =  format_prompt | llm | parser

    result = chain.invoke({"response": prompt})

    return result

def translate(text:str, language:str ,llm_name: Optional[str] = "gemini"):
    system: str = """You are a language translation AI. 
    Your task is to accurately translate the given text into the specified target language. 
    Provide only the translated text without any additional explanations, context, or details. 
    Focus strictly on delivering a precise and faithful translation.
    """

    # if llm_name == "gpt":
    #     llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # elif llm_name == "llama":
    #     llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")
    # else:
    #     llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", timeout=120)
    
    llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")

    parser = JsonOutputParser(pydantic_object=translateFormat)

    prompt = PromptTemplate(
        template= system + "\n{format_instructions}\nTranslate to {language}:\n```\n{text}\n```",
        input_variables= ['text', 'language'],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain =  prompt | llm | parser

    try:
        result = chain.invoke({"text": text, 'language': language})
        return result
    except:
        return "Unable to translate"
