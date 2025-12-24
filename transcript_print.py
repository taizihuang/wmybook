import pandas as pd
import json

with open("version", "r") as f:
    version = f.read().replace("\n","")

content = """
\\documentclass[twocolumn]{ctexart}
\\usepackage{ctex}
\\usepackage{graphicx}
\\usepackage{titlesec}
\\usepackage[hyphens]{url}
\\usepackage[colorlinks=true, urlcolor=blue, linkcolor=black]{hyperref}
\\usepackage{geometry}
\\usepackage{cancel}
\\setCJKmainfont{SimSun}
\\newCJKfontfamily\\Kai{STKaiti}
\\newCJKfontfamily\\Hei{SimHei} 
\\setcounter{secnumdepth}{0}
\\setcounter{tocdepth}{1}
\\titleformat*{\\section}{\\centering\\Large\\bfseries }
\\titleformat*{\\subsection}{\\centering}
\\titlespacing*{\\subsection} {0pt}{0pt}{10ex}
\\geometry{a4paper, scale=0.85}
\\begin{document}
\\begin{titlepage}\\vspace*{8cm}\\begin{center}{\\Huge\\bfseries\\heiti 王孟源访谈}(v"""
content += version
content += """)\\end{center}\\end{titlepage}\\newpage
\\tableofcontents
\\newpage
\\pagestyle{plain}
\\twocolumn[\\begin{@twocolumnfalse}
\\section{说明}
\\subsection{ \\break 2024-12-21}
本书采用 \\href{https://creativecommons.org/licenses/by-nc/4.0/legalcode.zh-Hans}{CC BY-NC 4.0} 协议开源，供读者免费阅读。

王孟源博客镜像网址为 https://wmyblog.site 。本书网址为 https://book.wmyblog.site ，用于发布修订说明。
\\end{@twocolumnfalse}]
"""

rep_list = [('&lt;','<'), ('&gt;','>'), ('&amp;','&'),
('<p>','\n'), ('</p>','\n'), ('<br>','\n'),('<br/>','\n'),
('%','\\%'), ('$','\\$'), ('&','\\&'),('#','\\#'), ('^','\\^'), ('_','\\_'), ('===','='),
('<h2>','\\section{\\ \\ \\ \\ '), ('</h2>','\\ \\ \\ \\ }'), ('≈', '$\\approx$')]

def extract(response):
    doc = response.decode("utf8")
    string_left = '"chunk":[{'
    string_right = '},{'
    len_left = len(string_left)-2
    text = ''
    while string_left in doc:
        loc1 = doc.index(string_left)
        loc2 = doc[loc1:].index(string_right)
        doc_dict = json.loads(doc[loc1+len_left:loc1+loc2] + '}]')
        loc_idx = 0
        if 's' not in doc_dict[0]:
            loc3 = doc[loc1+loc2+2:].index(string_right)
            doc_dict = json.loads(doc[loc1+len_left:loc1+loc2+2+loc3] + '}]')
            loc_idx = 1
            if 's' not in doc_dict[1]:
                loc4 = doc[loc1+loc2+2+loc3+2:].index(string_right)
                doc_dict = json.loads(doc[loc1+len_left:loc1+loc2+loc3+2+loc4+2] + '}]')
                loc_idx = 2
        text += doc_dict[loc_idx]['s']
        doc = doc[loc1+loc2+2:]
    return text

data_dir = './data'

df = pd.read_pickle(f'{data_dir}/transcript_data.pkl')
with open(f"{data_dir}/transcript_info.json", "r") as f:
    info_dict = json.loads(f.read())
id_dict = {}
for key in info_dict.keys():
    id = info_dict[key]["id"]
    name = info_dict[key]["name"]
    id_dict[id] = name


df['id'] = df['url'].map(lambda x: x.split('/')[-2])
df["fullname"] = df["id"].map(id_dict)
df['title'] = df['fullname'].map(lambda x: x.split("]")[-1])
df['art_date'] = df['fullname'].map(lambda x: x.split("[")[0])
df['art_date'] = df['art_date'].map(lambda x: f"20{x[:2]}/{x[2:4]}/{x[4:6]}")
df['text'] = df['response'].map(extract)
df = df.sort_values('art_date', ascending=True)

for idx in df.index:
    id = df.loc[idx, 'id']
    fullname = df.loc[idx, "fullname"]
    title_str = df.loc[idx,'title']
    date = df.loc[idx, 'art_date']
    text = df.loc[idx, 'text']
    url = f'https://wmyblog.site/html/{fullname[:12]}.html' 
    title = f"\\href{{{url}}}{{{title_str}}}"
    for rep in rep_list:
        text = text.replace(*rep)
    
    content += f"\\twocolumn[\\begin{{@twocolumnfalse}}\n\\section{{{title}}}\n\\subsection{{{date}}}\n\\end{{@twocolumnfalse}}]"
    content += text.replace('\n','\n\n')
    content

content += '\n \\end{document}'

with open(f'transcript_{version}.tex','w',encoding='utf8') as f:
    f.write(content)
