from downloader import Downloader
from bs4 import BeautifulSoup
import requests
import pandas as pd

url = 'https://drive.google.com/drive/folders/1eg78LVciM913PhvRtsgtWV3VDLojynDA'
doc = BeautifulSoup(requests.get(url).content, features="lxml")
df = pd.DataFrame()
for i in doc.findAll("div", {'data-target':"doc"}):
    if i.find("div",{'role':"link"}):
        i.find("div",{'role':"link"}).decompose()
    df = pd.concat([df, pd.DataFrame(data={'filename': i.text, 'id': i['data-id']}, index=[0])], ignore_index=True)
df = df.loc[(df.filename.str.contains('八方论坛')) | (df.filename.str.contains('龙行天下')) | (df.filename.str.contains('大学讲座'))]

url = 'https://drive.google.com/drive/folders/1xOlm5O7NUVG3Aq1oXdS2UsUgO9pLuHIM'
doc = BeautifulSoup(requests.get(url).content, features="lxml")
for i in doc.findAll("div", {'data-target':"doc"}):
    if i.find("div",{'role':"link"}):
        i.find("div",{'role':"link"}).decompose()
    df = pd.concat([df, pd.DataFrame(data={'filename': i.text, 'id': i['data-id']}, index=[0])], ignore_index=True)
df = df.loc[(df.filename.str.contains('八方论坛')) | (df.filename.str.contains('龙行天下')) | (df.filename.str.contains('大学讲座'))]

df.to_pickle('trascript_info.pkl')

url_list = [f'https://docs.google.com/document/d/{id}/edit' for id in df['id']]
Downloader(url_list, nCache=2, outFilename='transcript.pkl').run()