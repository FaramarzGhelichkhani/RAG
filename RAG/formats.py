from pydantic import BaseModel, Field

class TableNamesPromptRes(BaseModel):
        table_names: str = Field(description="The comma seperated, with a space ,tables name")
        explanation: str = Field(description="a brief explanation by AI")
        confirmation: int = Field(description="The confirmation, 1 means confirm , 0 mean not confirm")

class QueryPromptRes(BaseModel):
        query: str = Field(description="sql query")
        explanation: str = Field(description="a brief explanation by AI")
        confirmation: int = Field(description="The confirmation, 1 means confirm , 0 mean not confirm")
