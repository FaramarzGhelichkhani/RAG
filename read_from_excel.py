import pandas as pd
from os.path import dirname, realpath, join
from io import StringIO

def get_sheet_names(file_path):
    """
    Extracts sheet names from an Excel file.
    
    :param file_path: Path to the Excel file.
    :return: List of sheet names.
    """
    excel_file = pd.ExcelFile(file_path)
    return excel_file.sheet_names

def read_from_excel(file_path, sheet_names=None):
    """
    Reads specified sheets from an Excel file.
    
    :param file_path: Path to the Excel file.
    :param sheet_names: List of sheet names to read. If None, all sheets are read.
    :return: Dictionary of DataFrames with sheet names as keys.
    """
    df_dict = pd.read_excel(file_path, sheet_name=sheet_names)
    return df_dict

def dataframe_to_csv_text(df):
    """
    Converts a DataFrame to CSV text.
    
    :param df: DataFrame to convert.
    :return: CSV text as a string.
    """
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def dataframes_to_csv_string(dataframes: dict):
    """
    Converts a DataFrame to a CSV string.
    
    :param df: DataFrame to convert.
    """
    csv_sheets = {}
    for sheet in dataframes.keys():
        dataframe_sheet  = dataframes[sheet]
        csv_sheets[sheet] = dataframe_to_csv_text(dataframe_sheet)
    return csv_sheets

# def excel_to_csv(file_path, sheet_names=None):
#     # Extract sheet names
#     sheet_names = get_sheet_names(file_path)
#     # print("Sheet names:", sheet_names)

#     # Read specific sheets
#     dataframes = read_from_excel(file_path, sheet_names=sheet_names)  # Replace with your sheet names

#     # Access individual DataFrames
#     csv_sheets = {}
#     for sheet in sheet_names:
#         dataframe_sheet  = dataframes[sheet]
#         csv_sheets[sheet] = dataframe_to_csv_text(dataframe_sheet)
#     return csv_sheets

def excel_to_csv(file_path):
    # Extract sheet names
    sheet_names = get_sheet_names(file_path)
    # print("Sheet names:", sheet_names)

    # Read specific sheets
    dataframes = read_from_excel(file_path, sheet_names=sheet_names)  # Replace with your sheet names

    csv_sheets = {}
    for sheet in dataframes.keys():
        for item in dataframes[sheet][dataframes[sheet].columns[0]].unique():
            data_set = dataframes[sheet][dataframes[sheet][dataframes[sheet].columns[0]] == item][dataframes[sheet].columns[1:].to_list()]
            csv_sheets[f"{sheet}-{item}"] = dataframe_to_csv_text(data_set)

    # Access individual DataFrames
    for sheet in sheet_names:
        dataframe_sheet  = dataframes[sheet]
        csv_sheets[sheet] = dataframe_to_csv_text(dataframe_sheet)
    return csv_sheets


if __name__ == "__main__":
    cur_dir = dirname(realpath(__file__))
    input_dir = join(cur_dir, 'input_directory')

    file_path = join(input_dir, 'input_file.xlsx') 
    dataframes = pd.read_excel(file_path)
    # csvs = dataframes_to_csv_string(dataframes)
    csvs = excel_to_csv(file_path)
    for sheetName, csv in csvs.items():
        print(sheetName)
        print(csv)