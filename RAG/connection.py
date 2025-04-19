import os
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine
from langchain_openai import OpenAIEmbeddings
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

def get_llm(model_name, temperature=0):
    llm=  ChatOpenAI(temperature=temperature, model_name=model_name,
        openai_api_key=api_key,
        openai_api_base=api_base)
    return llm

def get_OpenAIEmbeddings():
    return OpenAIEmbeddings(base_url=api_base, api_key=api_key,
                            model='text-embedding-3-small')

def create_chat_bot(llm, initial_prompt):
        memory = ConversationBufferMemory()

        conversation = ConversationChain(prompt=initial_prompt, 
        llm=llm,
        memory=memory,
        verbose=False
        )

        return conversation

def get_mssql_engine():
    engine = create_engine(f"mssql+pyodbc://{db_user}:{db_password}@{db_host}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes")
    return engine
