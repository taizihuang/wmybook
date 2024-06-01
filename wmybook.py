import pandas as pd
import re, json

class Book:
    def __init__(self, articleFile, commentFile, title='', ver=''):
        self.article = pd.read_pickle(articleFile) 
        self.comment = pd.read_pickle(commentFile)
        self.title = title
        self.version = ver
        with open('errata.json', 'r', encoding='utf8') as f:
            content = f.read()
        self.errata = json.loads(content)
        self.rep_list = [
            ('&amp;','&'), ('&lt;','<'), ('&gt;','>'), 
            ('&rdquo;','"'), ('&ldquo;','"'),('&middot;','·'),('&mdash;','-'),
            ('<p>','\n'), ('</p>','\n'), ('<br>','\n'),('<br/>','\n'),
            ('%','\%'), ('$','\$'), ('&','\&'),('#','\#'), ('^','\^'), ('_','\_'), ('===','='),
            ('<strike>','\\cancel{'), ('</strike>','}'),
            #math
            ('σ','$\sigma$'), ('θ','$\\theta$'), ('r\^2','$r^2$'), ('λ','$\lambda$'),
            ('π','$\pi$'), ('r\^4','$r^4$'), ('∝','$\propto$'), ('ρ','$\\rho$'),
            ('≈','$\\approx$'), ('\^','\^{}'),
        ]
        self.img_list = [
            ('f_26462958_1'), ('f_25350703_1'), ('2f50f0bffaf439ca5adac6dffafb4618'),
            ('ba77ae1763533d27063da5a3a6da38e0'), ('1255f7d9f3d7178b872880a1ffb96277'),
            ('1e42c210bafb4887d03c25669817fcd7'), ('14f1704e177d6c3985238567b5a613c0'),
            ('29e192984e9ce0086e88a98be3705562'), ('ab6f21134e7dcba1cfbf2e494200f9ef'),
            ('d39156c719714a726b82aae6048a3c41'), ('b314bf52394928e7e7fb213264129366'),
            ('d400eb09ec690963cfd6d651805ad4f0'), ('c624e9ae06a66f951f3d346c7698e9a3'),
        ]
    
    def header(self, single=False):
        content = """
            \\documentclass[twocolumn]{ctexart}
            \\usepackage{ctex}
            \\usepackage{graphicx}
            \\usepackage{titlesec}
            \\usepackage[hyphens]{url}
            \\usepackage[colorlinks=true, urlcolor=blue, linkcolor=black]{hyperref}
            \\usepackage{geometry}
            \\usepackage{cancel}
            \\usepackage{xeCJKfntef}
            \\setCJKmainfont{SimSun}
            \\newCJKfontfamily\Kai{KaiTi}
            \\newCJKfontfamily\Hei{SimHei} 
            \\setcounter{secnumdepth}{0}
            \\setcounter{tocdepth}{1}
            \\titleformat*{\\section}{\\centering\\Large\\bfseries }
            \\titleformat*{\\subsection}{\\centering}
            \\titlespacing*{\\subsection} {0pt}{0pt}{10ex}
            \\geometry{a4paper, scale=0.85}
            \\begin{document} """
        if not single:
            content += "\\begin{titlepage}\\vspace*{8cm}\\begin{center}{\\Huge\\bfseries\\heiti "
            content += self.title + "}(v" 
            content += self.version
            content += ")\\end{center}\\end{titlepage}\\newpage"
        content += """
            \\tableofcontents
            \\newpage
            \\pagestyle{plain}
            """
        return content
    
    def footer(self):
        return '\n \\end{document}'
    
    def formatArticle(self, art_id):

        df = self.article.loc[self.article['id'] == art_id].iloc[0]
        title = f"\\href{{https://wmyblog.site/html/{art_id}.html}}{{{df.title}}}"
        date = df.art_date.strftime('%Y-%m-%d %H:%M')
        post = df.post

        #header
        post = f"\n\\twocolumn[\\begin{{@twocolumnfalse}}\n\\section{{{title}}}\n\\subsection{{ \\break {date}}}\n\\end{{@twocolumnfalse}}]" + post

        #character
        for rep in self.rep_list:
            post = post.replace(*rep)

        #tag
        post = re.sub(r'<span .*標楷體.*?>(.*)<\/span>',r'{\\Kai{\1}}',post)
        post = re.sub(r'<strong>(.*)<\/strong>',r'{\\centering\\Hei{\1}}',post)
        post = re.sub(r'<span .*?underline.*?>(.*)<\/span>',r'\\CJKunderline{\1}',post)
        post = re.sub(r'<div .*?>((\n|.)*)<\/div>',r'\1', post)
        post = re.sub(r'<div .*?>((\n|.)*)<\/div>',r'\1', post)
        post = re.sub(r'<div .*?>((\n|.)*)<\/div>',r'\1', post)
        post = re.sub(r'<div .*?>((\n|.)*)<\/div>',r'\1', post)
        post = re.sub(r'<em>((\n|.)*)<\/em>',r'\1', post)
        post = re.sub(r'<font .*?>(.*)<\/font>',r'\1', post)
        post = re.sub(r'<p .*?>','', post)
        post1 = re.sub(r'<span .*?>((\n|.)*)<\/span>',r'\1', post)
        while post1 != post:
            post = post1
            post1 = re.sub(r'<span .*?>(.*)<\/span>',r'\1', post1)
        post = re.sub(r'<span .*?>', '', post)
        post = re.sub(r'</span>', '', post)

        #link
        # post = re.sub(r'<a\ +href="(.+?)".*?>(http)?(.+?)<.*?\/a>',r'\\href{\1}{\2\3\\footnote{\\url{\1}}}',post)
        post = re.sub(r'<a\ +href="(.+?)".*?>(.+?)<.*?\/a>',r'\\href{\1}{\2\\footnote{\\url{\1}}}',post)
        # post = re.sub(r'\\href{(.*?)}{http(.*?)\\footnote{.*?}}}',r'\\href{\1}{链接\\footnote{\\url{\1}}}',post)
        post = re.sub(r'<a href="(.*?)">',r'\\href{\1}{链接\\footnote{\\url{\1}}}',post)
        post = re.sub(r'}{(http.?:.*)\\footnote',r'}{链接\\footnote',post)

        #image
        matches = re.findall('<img .*src="(.*)".*\/>',post)
        for match in matches:
            post = post.replace(match, match.replace('\_','_').replace('.gif','.jpg'))
            for img in self.img_list:
                post = post.replace(f'{img}.jpg',f'{img}.png')
        post = re.sub(f'<img .*src="(.*?)".*\/>',r'\\begin{figure}[h]\\centering\\includegraphics[width = 0.9\\linewidth]{\1}\\end{figure}',post)
        post = post.replace('\\begin{figure}[h]\\centering\\includegraphics[width = 0.9\\linewidth]{./img/empty.png}\\end{figure}','')
        post = post.replace('\\begin{figure}[h]\\centering\\includegraphics[width = 0.9\\linewidth]{./img/empty.jpg}\\end{figure}','')

        #list
        if '<ol>' in post:
            post = post.replace('<ol>','\\begin{enumerate}\n').replace('</ol>','\\end{enumerate}\n').replace('<li>','\\item ').replace('</li>','\n').replace('<p style="margin-left:30px">','\n')

        #errata
        if art_id in self.errata['post']:
            rep_list = self.errata['post'][art_id]
            for rep in rep_list:
                # print(*eval(rep))
                post = re.sub(*eval(rep), post)

        return post

    def formatComment(self, art_id):
        df = self.comment.loc[self.comment.id == art_id].sort_values('comment_date',ascending=True).reset_index(drop=True)
        df = df.loc[~(df.comment.str.contains('<strike'))]

        content = f'\\section{{{len(df)}条问答}}\n\n'

        for idx in df.index:
            nickname = df.loc[idx,'nickname']
            comment = df.loc[idx,'comment'].replace('\n','\n\n')
            comment_date = df.loc[idx,'comment_date'].strftime('%Y/%m/%d %H:%M')
            reply = df.loc[idx,'reply'].replace('<br>','<br><br>')
            if pd.isnull(df.loc[idx,'latest_reply_date']):
                reply_date = ''
            else:
                reply_date = df.loc[idx,'latest_reply_date'].strftime('%Y/%m/%d %H:%M')

            if comment_date > "2017/12/01 00:00":
                comment = re.sub(r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)',r'\\href{\1}{链接\\footnote{\\url{\1}}}', comment)
                reply = re.sub(r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)',r'\\href{\1}{链接\\footnote{\\url{\1}}}', reply)
            else:
                comment = re.sub(r'<a\ +href="(.+?)".*?>(http)?(.+?)<.*?\/a>',r'\\href{\1}{链接\\footnote{\\url{\1}}}',comment)
                reply = re.sub(r'<a\ +href="(.+?)".*?>(http)?(.+?)<.*?\/a>',r'\\href{\1}{链接\\footnote{\\url{\1}}}',reply)
                pass

            for rep in self.rep_list:
                nickname = nickname.replace(*rep)
                comment = comment.replace(*rep)
                reply = reply.replace(*rep)
                #header

            if reply != '':
                content += f"\\textit{{\\hfill\\noindent\\small {comment_date} 提问；{reply_date} 回答}}\n\n"
                content += f"{{\\noindent[{idx+1}.]\\ \\ \\ \\ \\Kai {nickname} 问：{comment}}}\n\n"
                content += f"{{\\Hei 答}}：{reply}\\\\\n\n"
            else:
                content += f"\\textit{{\\hfill\\noindent\\small {comment_date} 提问}}\n\n"
                content += f"{{\\noindent[{idx+1}.]\\ \\ \\ \\ \\Kai {nickname} 问：{comment}}}\n\n"

        content = content.replace('答}：\n\n','答}：\n')
        content = content.replace('\(\^{}o\^{})/~','')
        content = content.replace('disagree  : {','disagree :')
        content = content.replace('/noteshare?id=a21f4c3f44eeea0f3f86e7948512525d&sub=40E2F646692742EB87CDF9103F','')

        return content



    def export(self):
        content = self.header()
        for id in self.article.id[::-1]:
            article = self.formatArticle(id)
            if len(article) > 250:
                content += article
                content += self.formatComment(id)
        content += self.footer()

        with open(f'comment.tex', 'w', encoding='utf8') as f:
            f.write(content)


if __name__ == "__main__":
    Book('./data/article_full.pkl', './data/comment_full.pkl', '王孟源文集', '0.1.0').export()    


