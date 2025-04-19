import os
import tempfile
import streamlit as st
import pandas as pd
from db_prompt_manager import PromptHandler

def get_file(file):
    if file is not None:
        if file.name.endswith('.csv'):
            suffix = '.csv'
        elif file.name.endswith('.xlsx'):
            suffix = '.xlsx'
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(file.getbuffer())
                temp_filename = temp_file.name
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        temp_filename = None
    return temp_filename
    
def main():
    st.title("Text to Query Converter")
    
    if 'first_button_clicked' not in st.session_state:
        st.session_state.first_button_clicked = False 
    if 'query' not in st.session_state:
        st.session_state.query = None
  
    text_input = st.text_input("Enter your text input, and this tool will convert it into a query.")
    file = st.file_uploader(
        "Upload a CSV or Excel file (optional):", type=['csv', 'xlsx'])
    file_path = get_file(file)
    p = PromptHandler(user_query=text_input, file_path=file_path)
    
    if st.button("Generate Response"):
        st.session_state.first_button_clicked = True
        try:
            if text_input == "":
                raise ValueError("text input is empty")     
            query , prompt_number = p.base_algorithm()
            st.success(f"Generated Response with {prompt_number} prompts:")
            st.session_state.query = query
            st.code(query)
        except Exception as e:
            st.error(f"Error prompt handling: {e}")

    if st.session_state.first_button_clicked:
        if st.button("execute query"):
            data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                 'Age': [24, 27, 22, 32, 29],
                'City': ['New York', 'San Francisco', 'Los Angeles', 'Chicago', 'Houston']
                }
            df = pd.DataFrame(data)
            st.dataframe(df.head())
            # df = p.sql_execution(query=st.session_state.query)
            # st.dataframe(df.head())
            csv = df.to_csv(index=False)
            st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='data.csv',
            mime='text/csv'
                )    
        
main()
