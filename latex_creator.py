
def report_creator(file_path, report_obj):
    latex_code = f'''
\\documentclass[aspectratio=169]{{beamer}}
\\usepackage{{xepersian}}
\\settextfont{{Dana}}
\\usepackage{{graphicx}}
\\usepackage{{tikz}}
\\usepackage{{xcolor}}

\\definecolor{{customcolor}}{{RGB}}{{1,74,105}}

\\begin{{document}}

\\begin{{frame}}
\\tikz[remember picture,overlay] 
\\node[opacity=1,inner sep=0pt] at (current page.center)
{{\\includegraphics[width=\\paperwidth,height=\\paperheight]{{background.jpg}}}};

\\textcolor{{customcolor}}{{\\textbf{{\\Large بریف کمپین}}}}
\\begin{{itemize}}
\\item \\textcolor{{customcolor}}{{\\textbf{{نام کمپین:}} {report_obj.name}}}
\\item \\textcolor{{customcolor}}{{\\textbf{{صندوق‌های هدف:}} {report_obj.target_funds}}}
\\item \\textcolor{{customcolor}}{{\\textbf{{هدف:}} {report_obj.target}}}
\\item \\textcolor{{customcolor}}{{\\textbf{{مشتریان تارگت:}} {report_obj.target_customers}}}
\\item \\textcolor{{customcolor}}{{\\textbf{{مدت کمپین:}} {report_obj.campain_length}}}
\\item \\textcolor{{customcolor}}{{\\textbf{{کانال:}} {report_obj.channels}}}
\\end{{itemize}}

\\end{{frame}}

\\end{{document}}
'''
    with open(file_path, "w", encoding="utf-8") as file:
            file.write(latex_code + "\n")