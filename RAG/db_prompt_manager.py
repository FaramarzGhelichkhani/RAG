import os 
import pandas as pd
from typing import List
from tables import Table
from prompts import (get_data_system_prompt, get_initial_triage_prompt, get_table_selection_prompt,
                      get_table_selection_feedback_prompt, get_query_generating_prompt,
                        get_query_generating_feedback_prompt, get_fewshotprompt, get_file_prompt)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from formats import  TableNamesPromptRes, QueryPromptRes
from connection import get_llm, get_mssql_engine
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from pathlib import Path

class PromptHandler:
    
    def __init__(self, user_query, file_path=None):
        self.user_query = user_query
        self.retry_count = 0
        self.max_retries = 3
        self.prompt_number= 0
        self.descriptions = Table.get_tables_descriptions()
        self.schemas = Table.get_table_schema(tables_name=[])
        self.explans = Table.get_table_query_explanation(tables_name=[])
        self.file_path = file_path
        self.file_prompt = []
     
    def _get_chain(self, user_prompt, model_name, struc=None, fewshotprompt=False):
        system_prompt = get_data_system_prompt()
        prompts =[system_prompt]
        if fewshotprompt:
            fewshot_prompt = get_fewshotprompt().format(userinput=self.user_query)
            prompts.append(fewshot_prompt)
        prompts.append(user_prompt)
        prompts.append(MessagesPlaceholder("file_prompt", optional=True))    
        prompt = ChatPromptTemplate.from_messages(prompts)

        llm=  get_llm(model_name=model_name)
        if struc is not None:
            llm = llm.with_structured_output(struc)
        chain = (prompt | llm)
        
        return chain 
    
    def file_hander(self):
        if self.file_path is not None:
            file_extension = Path(self.file_path).suffix.lower()

            if file_extension == '.csv':
                loader = CSVLoader(file_path=self.file_path)
            elif file_extension in ['.xls', '.xlsx']:
                loader = UnstructuredExcelLoader(file_path=self.file_path)
            else:
                raise ValueError("format should be csv or xlsx or xls.")
            
            data = loader.load()
            os.remove(self.file_path) 
            self.file_prompt =  get_file_prompt(file_data=data)

    def initial_triage(self):
        triage_prompt = get_initial_triage_prompt()
        chain = self._get_chain(user_prompt=triage_prompt, model_name="chatgpt-4o-latest")
        chain = (chain |  {"data_context": lambda x: eval(x.content)["data_context"], 
                           "more_info": lambda x:  eval(x.content)["more_info"],
                           "information": lambda x:  eval(x.content)["information"]} )
        
        traige_msg = chain.invoke({"descriptions": self.descriptions, "schema":self.schemas, 
                                   "user_query":self.user_query, "file_prompt":self.file_prompt})
        self.prompt_number += 1

        if traige_msg["data_context"] == "unrelated":
            raise ValueError("unrelatd user query")
        if traige_msg["more_info"] ==1 :
            raise ValueError(traige_msg["information"])
    
    def table_selection(self):
        table_selection_prompt = get_table_selection_prompt()
        chain = self._get_chain(user_prompt=table_selection_prompt, model_name="gpt-4o-mini", struc=TableNamesPromptRes)
        chain = (chain |  {"table_names": lambda x: x.table_names.split(', '),
                            "explanation": lambda x: x.explanation} )
        table_name_msg = chain.invoke({"descriptions": self.descriptions, "schema":self.schemas, 
                                       "user_query":self.user_query})
        self.prompt_number += 1
        return table_name_msg
    
    def table_selection_validation(self, table_names):
        feedback_prompt_template =  get_table_selection_feedback_prompt()
        chain = self._get_chain(user_prompt=feedback_prompt_template, model_name="chatgpt-4o-latest")
        chain = (chain |
                 {"table_names": lambda x: eval(x.content)["table_names"].split(', '), 
                   "explanation": lambda x: eval(x.content)["explanation"]
                   , "confirmation": lambda x: eval(x.content)["confirmation"],}
                )
        table_name_validation = chain.invoke({"descriptions": self.descriptions, "schema":self.schemas,
                                            "user_query":self.user_query, "proposed_tables":', '.join(map(str,table_names))})
        self.prompt_number += 1
        if table_name_validation["confirmation"] == 0:
            return self.table_selection_validation(table_names=table_name_validation["table_names"])
        
        return table_name_validation

    def query_generating(self, tables : List[str]):
        query_generating_prompt = get_query_generating_prompt()
        chain = self._get_chain(user_prompt=query_generating_prompt, model_name="gpt-4o-mini", struc=QueryPromptRes, fewshotprompt=False)
        chain = (
                chain| {"query": lambda x: x.query, "explanation": lambda x: x.explanation, 
                   "confirmation":lambda x: x.confirmation}
                )
        query_msg = chain.invoke({"descriptions": self.descriptions, "schema":self.schemas,
                                           "explanation": self.explans , "user_query":self.user_query,
                                           "main_tables":tables,
                                           "file_prompt":self.file_prompt})
        self.prompt_number += 1
        return query_msg
    
    def query_validation(self,tables,  query):
        feedback_prompt_template =  get_query_generating_feedback_prompt()
        chain = self._get_chain(user_prompt=feedback_prompt_template, model_name="chatgpt-4o-latest", fewshotprompt=True)
        chain = (
                chain
                | {"query": lambda x: eval(x.content)["query"], "explanation": lambda x: eval(x.content)["explanation"]
                   , "confirmation": lambda x: eval(x.content)["confirmation"],}
                )
        query_validation_result = chain.invoke({"descriptions": self.descriptions, "schema":self.schemas,
                                           "explanation": self.explans , "user_query":self.user_query, 
                                           "main_tables":tables,"sql_query":query, 
                                           "file_prompt":self.file_prompt})
        
        self.prompt_number += 1
        if query_validation_result["confirmation"] == 0:
            return self.query_validation(tables=tables, query=query_validation_result["query"])

        return query_validation_result
    
    def sql_execution(self, query):
        engine = get_mssql_engine()
        return pd.read_sql(query, engine) 
    
    def base_algorithm(self):
        self.file_hander()
        self.initial_triage()
        table_name_msg = self.table_selection()
        table_name_validation = self.table_selection_validation(table_names= table_name_msg["table_names"])
        qurry_generating = self.query_generating(tables=table_name_validation["table_names"])
        query_validation = self.query_validation(tables=table_name_validation["table_names"], query=qurry_generating["query"])
 
        return query_validation["query"], self.prompt_number

# test = PromptHandler(user_query="  .ارزش پرتفو تمام دارایی های آنلاین و غیر آنلابن برای همه مشتریان در روز ۱۴۰۳۱۱۲۲. قیمت های روز موزد نظر لحاظ شود. خر.چی باید کاستومر کد باشد" )
# test = PromptHandler(user_query=" ارزش پرتفو طلا مشتریان در روز ۱۴۰۳۱۱۲۲. توجه شود ایشورکی طلا ۱۲۰۵۲ می باشد")
# test = PromptHandler(user_query=" همه مشتریانی که تا به حال عیار خریده اند . عیار یک نماد ای تی اف است. ایشور کی عیار 12052 . ")
# test = PromptHandler(user_query="پرتفو صندوق های صدروی ابطالی در روز 14031201(dateKey)")
# test = PromptHandler(user_query=".  ارزش نمام دارایی های مشتریان در روز ۱۴۰۳۱۱۲۲. به  تفکیک پرتفو  و مانده موجود ")
# test = PromptHandler(user_query=" اثممخم اخص خمی شقث غخ ", file_path="khodro.csv")
# test = PromptHandler(user_query="پرتفو همه مشتریان برای نماد عیار در روز ۱۴۰۳۱۱۲۲")
# print(test.base_algorithm()[0])
