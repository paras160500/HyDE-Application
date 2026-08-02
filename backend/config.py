#==========================================================================================
#                                   Import Statements
#==========================================================================================

import os 
from dotenv import load_dotenv
from groq import Groq 
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone 

load_dotenv()

# API Key init 

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GROQ_MODEL = os.getenv("GROQ_MODEL")
EMBEDDING_MODEL = "text-embedding-3-small"

# For lazy Loading and not init each time 

_groq_client = None 
_embedder = None 
_pc_index = None 

#==========================================================================================
#                                   Logical Statements
#==========================================================================================

def get_groq():
    """
        Checking if Client already init and if not then init a new one 
        and return to the caller 
    """
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def get_embedder():
    """
        Checking if embedder already init and if not then init a new one 
        and return to the caller 
    """
    global _embedder
    if _embedder is None:
        _embedder = OpenAIEmbeddings(api_key=OPENAI_API_KEY , model = EMBEDDING_MODEL)
    return _embedder


def get_index():
    """
        Checking if index already init and if not then init a new one 
        and return to the caller 
    """
    global _pc_index
    if _pc_index is None:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        _pc_index = pc.index(PINECONE_INDEX)
    return _pc_index 