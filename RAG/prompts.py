from langchain.prompts import  SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.prompts import FewShotChatMessagePromptTemplate, FewShotPromptTemplate
from query_examples import get_query_examples
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from connection import get_OpenAIEmbeddings

def get_data_system_prompt():
    system_prompt = SystemMessagePromptTemplate.from_template(
                                    """ You are an AI assistant to work with a database.
                                    below provided descriptions and schema of tables. 
                                    ---
                                    descriptions: \n{descriptions}
                                    ---
                                    schemas: \n{schema}
                                    ---
                                    """
                                    ,  input_variables=["descriptions", "schema"] 
                                    )
    return system_prompt

def get_initial_triage_prompt():
        traige_prompt = HumanMessagePromptTemplate.from_template(
            """You have been provided with a description and schema of a database. Your task is to determine how to handle the following user query:

            User Query: "{user_query}"
            
            answer with a (python) dictionary **without formatting**  with below keys:
            1. data_context : If the query is unrelated to the database, return: "unrelated" otherwise return "reletad".
            2. more_info : If the query requires more information to be answered return 1 other wise return 0.
            3. information : If the query requires more information to be answered explain it shortly at most in one line.
            """
            ,  input_variables=["user_query"]
        )
        return traige_prompt

def get_table_selection_prompt():
    table_selection_prompt = HumanMessagePromptTemplate.from_template(
        """You have been provided with a description and schema of a database. Your task is to identify the name of the table that best matches the user's question based on the given database details.

            User Query: "{user_query}"

            Based on this query, list tables that are relevant to this query. Please provide only the name of that table in a comma seperates str, after that add  a brief explanation of your choice.
        """
        ,  input_variables=["user_query"]
    )
    return table_selection_prompt

def get_table_selection_feedback_prompt():
    feedback_prompt_template = HumanMessagePromptTemplate.from_template(
        """
        You are an expert in understanding database schemas and SQL queries. Your task is to evaluate whether the provided list of table names is relevant to the user's query. 

        User Query: "{user_query}"

        Proposed Tables: "{proposed_tables}"

        answer with a python dictionary without formatting  with below keys:

        1. table_names: If you doesnot confirm. list your table names, comma seperated.
        2. explanation: justify a little your correction.
        3. confirmation: Confirm whether proposed tables in the list is relevant to the user query. 1 or 0.
        """  ,  input_variables=["user_query", "proposed_tables"])

    return feedback_prompt_template

def get_query_generating_prompt():
    prompt = HumanMessagePromptTemplate.from_template(
    """
    You are an expert in understanding database schemas and SQL queries. Your task is to create a sql query regarding  database information 
        and user question, Also considering and the name of main tables is provided . 

    User question: {user_query}

    main Tables: {main_tables}

    considering: {explanation}

    """  ,  input_variables=["user_query", "main_tables", "explanation"])

    return prompt

def get_query_generating_feedback_prompt():
    feedback_prompt_template = HumanMessagePromptTemplate.from_template(
    """
    You are an expert in understanding database schemas and SQL queries. Your task is to evaluate whether the provided sql query is relevant to the user's query. 
        Also considering and the name of main tables is provided.

    User Query: "{user_query}"

    main Tables: {main_tables}

    Proposed sql query: "{sql_query}"

    considering: {explanation}

    answer with a python dictionary without formatting with below keys:

    1. query: If you doesnot confirm. create a sql query with sql format.
    2. explanation: justify a little your corrections.
    3. confirmation: Confirm whether proposed sql query is relevant to the user query. 1 or 0.
    """  ,  input_variables=["user_query",  "main_tables", "explanation", "sql_query"])

    return feedback_prompt_template

def get_fewshotprompt():
    example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])
    examples =  get_query_examples()
    
    example_selector = SemanticSimilarityExampleSelector.from_examples(
    # The list of examples available to select from.
    examples,
    # The embedding class used to produce embeddings which are used to 
    # measure semantic similarity.
    get_OpenAIEmbeddings(),
    # The VectorStore class that is used to store the embeddings 
    # and do a similarity search over.
    Chroma,
    # The number of examples to produce.
    k=2,
)

   
    few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    example_selector=example_selector,
    input_variables=["userinput"],
)
    return few_shot_prompt

def get_file_prompt(file_data=None):
    if file_data is not None:  
        file_prompt = HumanMessagePromptTemplate.format_messages(
            """
            consider below provided file to answer:
            {file_data}
            """, file_data=file_data)
        
        return file_prompt

    return []
