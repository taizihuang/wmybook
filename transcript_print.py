import pandas as pd
import json

def extract(response):
    doc = response.decode('utf8') 

    string_left = 'DOCS_modelChunk = [{'
    string_right = '},{"'
    text = ''
    while string_left in doc:
        loc1 = doc.index(string_left)
        loc2 = doc[loc1:].index(string_right)
        doc_dict = json.loads(doc[loc1+18:loc1+loc2] + '}]')
        loc_idx = 0
        if 's' not in doc_dict[0]:
            loc3 = doc[loc1+loc2+2:].index(string_right)
            doc_dict = json.loads(doc[loc1+18:loc1+loc2+2+loc3] + '}]')
            loc_idx = 1
            if 's' not in doc_dict[1]:
                loc4 = doc[loc1+loc2+2+loc3+2:].index(string_right)
                doc_dict = json.loads(doc[loc1+18:loc1+loc2+loc3+2+loc4+2] + '}]')
                loc_idx = 2
        text += doc_dict[loc_idx]['s']
        doc = doc[loc1+loc2+2:]
    return text

data_dir = './data'

with open("version", "r") as f:
    version = f.read().replace("\n","")
df = pd.read_pickle(f'{data_dir}/transcript_{version}.pkl')
df_info = pd.read_pickle(f'{data_dir}/transcript_info_{version}.pkl')

filename = df_info['filename'].iloc[0]
if '已隱藏' in filename:
    key = '已隱藏'
elif 'オーナー' in filename:
    key = 'オーナー'
elif '已隐藏' in filename:
    key = '已隐藏'
else:
    key = ''

df['id'] = df['url'].map(lambda x: x.split('/')[-2])
df_merge = pd.merge(df, df_info, on='id')
df_merge['title'] = df_merge['filename'].map(lambda x: x.split(key)[0].split(']')[-1].replace('✅','').replace('.docx',''))
df_merge['art_date'] = df_merge['filename'].map(lambda x: '20'+ x.split(key)[0].split('[')[0])
df_merge['text'] = df_merge['response'].map(extract)
df_merge = df_merge.sort_values('art_date',ascending=True)

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
('<strike>','\\cancel{'), ('</strike>','}')]

for idx in df_merge.index:
    id = df_merge.loc[idx, 'id']
    url = f'https://docs.google.com/document/d/{id}/edit' 
    title_str = df_merge.loc[idx,'title'].replace(' ','、').replace('&', '\\&')
    title = f"\\href{{{url}}}{{{title_str}}}"
    date = df_merge.loc[idx,'art_date']
    text = df_merge.loc[idx,'text']
    for rep in rep_list:
        text = text.replace(*rep)
    
    content += f"\\twocolumn[\\begin{{@twocolumnfalse}}\n\\section{{{title}}}\n\\subsection{{{date}}}\n\\end{{@twocolumnfalse}}]"
    content += text.replace('\n','\n\n').replace('','').replace('Putin}','Putin').replace('\源源','/源源')
    content

content += '\n \\end{document}'

with open(f'transcript_{version}.tex','w',encoding='utf8') as f:
    f.write(content)
