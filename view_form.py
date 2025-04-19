
import streamlit as st
from connect2llm import connect2llm, Mofid_API_KEY
import os
import time
import subprocess
import read_from_excel
import latex_creator
import pandas as pd 

class texReport:
    def __init__(self, name, target_funds, target, campain_length, channels, target_customers):
        self.name = name
        self.target_funds = target_funds
        self.target = target
        self.campain_length = campain_length
        self.channels = channels
        self.target_customers = target_customers

def insert2file(file_path, text):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text + "\n")

def compile_tex(tex_file, output_name="my_presentation", compile_iter=2):
    for i in range(compile_iter):
        command = ["xelatex.exe", "-interaction=nonstopmode", f"-jobname={output_name}", tex_file]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        time.sleep(1)
    return output, error

def save_uploaded_file(uploaded_file, save_dir):
    try:
        file_name = "input_file.xlsx"
        # Create the directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Save the file
        file_path = os.path.join(save_dir, file_name)#uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def page1():
    st.title("Brief Campaign Report Generator")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(current_dir, "output_directory")
    tex_file = os.path.join(output_dir, "report1.tex")
    tex_file_AI = os.path.join(output_dir, "report_AI.tex")
    pdf_file = os.path.join(output_dir, "my_presentation1.pdf")

    # Custom CSS for RTL form
    st.markdown(
        """
        <style>
        .rtl-form {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create a form
    with st.form(key='form1', clear_on_submit=False):
        st.markdown('<div class="rtl-form">', unsafe_allow_html=True)
        name = st.text_input("نام کمپین")
        target_funds = st.text_input("صندوق‌های هدف")
        target = st.text_input("هدف")
        campain_length = st.text_input("مدت کمپین")
        channels = st.text_input("کانال")
        target_customers = st.text_input("مشتریان تارگت")
        st.markdown('</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Submit")
    
    if submitted:
        report_obj = texReport(name, target_funds, target, campain_length, channels, target_customers)
        message = f'''
        کد latex برای گزارش زیر رو بهم بده. در خروجی latex از این پکیج‌ها استفاده کن: xepersian – tikz – xcolor – graphic – beamer. یک رنگ کاستوم تعریف کن به rgb با کد(1,74,105) و تمامی متنها و آیتمها رو با این رنگ تنظیم کن. 
        بعد از شروع frame، با استفاده از tikz یک بک گراند با نام background.jpg درست که با opacity یک در وسط صفحه با دستور زیر
        \\tikz[remember picture,overlay] 
        \\node[opacity=1,inner sep=0pt] at (current page.center)
        {{\\includegraphics[width=\\paperwidth,height=\\paperheight]{{background.jpg}}}};
        فونت رو Dana تعریف کن. 
        قبل از begin مربوط به itemize، این دستور رو قرار بده
        \\textbf{{\\Large بریف کمپین}}
        عنواین هر bulletpoint رو bold کن. 
        در خروجی فقط کد latex قابل اجرا بده و هیچ توضیح اضافه‌ای نده
        نام کمپین: {name}
        صندوق‌های هدف: {target_funds}
        هدف: {target}
        مشتریان تارگت: {target_customers}
        کانال: {channels}
        مدت کمپین: {campain_length}
        '''
        response_AI = connect2llm("gpt-3.5-turbo", message, Mofid_API_KEY)
        response_AI = response_AI.replace("latex", "").replace("```", "")
        insert2file(tex_file_AI, response_AI)
        latex_creator.report_creator(tex_file, report_obj)
        compile_tex(tex_file,"output_directory\\my_presentation.pdf")
        with open(pdf_file, "rb") as file:
            btn = st.download_button(
                label="Download Report",
                data=file,
                file_name="my_presentation.pdf",
                mime="application/pdf"
            )
        st.markdown(f"### Your report is ready. Click the button below to download it.")

def page2():
    st.title("Campaign Plan Report Generator")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    input_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "input_directory")
    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "campaign_plan_output_directory")
    input_execl_file = os.path.join(input_dir, "input_file.xlsx")

    # Custom CSS for RTL form
    st.markdown(
        """
        <style>
        .rtl-form {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])

    if uploaded_file is not None:
        # Check the file type and read the file accordingly
        if uploaded_file.name.endswith('.xlsx'):
            # Read Excel file
            file_path = save_uploaded_file(uploaded_file, input_dir)
            if not file_path:
                st.error("Failed to save file")
            else:
                df = pd.read_excel(uploaded_file)
                csvs = read_from_excel.excel_to_csv(input_execl_file)
                counter = 0
                for sheetName, csv in csvs.items():
                    st.write(sheetName)
                    message = f'''
I have some example data and it’s latex code to create pie chart
data 1:
دارایی مشتریان دارای صندوق پیشرو
صندوق,مبلغ
صندوق‌های مفید,2127
صندوق حامی,366
صندوق پیشرو,758
latex code 1:
\\documentclass{{article}}
\\usepackage{{tikz}}
\\usepackage{{pgf-pie}}
\\usepackage{{xepersian}}
\\settextfont{{Dana}}

\\definecolor{{customColor}}{{rgb}}{{0.04,0.29,0.41}}

\\begin{{document}}
\\begin{{center}}
\\begin{{tikzpicture}}
\\pie[sum=auto, explode=0.05, text=pin, /tikz/nodes={{thick, text=customColor}}, radius=2, color={{blue!70, cyan!70, teal!70}}]{{
2127/\\rl{{صندوق‌های مفید}},
366/\\rl{{صندوق حامی}},
758/\\rl{{صندوق پیشرو}}
}}
\\end{{tikzpicture}}
\\par {{\textcolor{{customColor}}{{\\rl{{دارای مشتریان دارای صندوق پیشرو}}}}}}
\\end{{center}}
\\end{{document}}
——————————-
data 2:
دارایی مشتریان بدون صندوق پیشرو
صندوق,مبلع
صندوق‌های مفید,1122
صندوق حامی,595
latex code 2:
\\documentclass{{article}}
\\usepackage{{tikz}}
\\usepackage{{pgf-pie}}
\\usepackage{{xepersian}}
\\settextfont{{Dana}}

\\definecolor{{customColor}}{{rgb}}{{0.04,0.29,0.41}}

\\begin{{document}}
\\begin{{center}}
\\begin{{tikzpicture}}
\\pie[sum=auto, explode=0.05, text=pin, /tikz/nodes={{thick, text=customColor}}, radius=2, color={{blue!70, cyan!70}}]{{
1122/\\rl{{صندوق‌های مفید}},
595/\\rl{{صندوق حامی}}
}}
\\end{{tikzpicture}}
\\par \textcolor{{customColor}}{{\\rl{{دارایی مشتریان بدون صندوق پیشرو}}}}
\\end{{center}}
\\end{{document}}
I want you to create latex code for the following data based on the previous and codes. only provide latex code and do not explain it
{sheetName}
{csv}
'''
                    tex_file = os.path.join(output_dir, f"report_{counter}.tex")
                    pdf_file = os.path.join(output_dir, f"my_presentation_{counter}.pdf")
                    response_AI = connect2llm("gpt-4o-mini", message, Mofid_API_KEY)
                    response_AI = response_AI.replace("latex", "").replace("```", "")
                    insert2file(tex_file, response_AI)
                    compile_tex(tex_file, f"campaign_plan_output_directory\\my_presentation_{counter}.pdf", 1)
                    counter += 1
                
def initaitor():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    output_brief_dir = os.path.join(current_dir, "output_directory")
    output_plan_dir = os.path.join(current_dir, "campaign_plan_output_directory")
    input_dir = os.path.join(current_dir, "input_directory")
    if not os.path.exists(output_brief_dir):
        os.makedirs(output_brief_dir)
    if not os.path.exists(output_plan_dir):
        os.makedirs(output_plan_dir)
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)

def main():
    initaitor()
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Brief Campaign Report Generator", "Campagn Plan Report Generator"])

    if page == "Brief Campaign Report Generator":
        page1()
    elif page == "Campagn Plan Report Generator":
        page2()


if __name__ == "__main__":
    main()