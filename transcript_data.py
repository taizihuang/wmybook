from downloader import Downloader
from bs4 import BeautifulSoup
import requests
import pandas as pd

data_dir = './data'

with open("suffix", "r") as f:
    suffix = f.read().replace("\n","")

# 龙行天下
url = 'https://drive.google.com/drive/folders/1eg78LVciM913PhvRtsgtWV3VDLojynDA'
doc = BeautifulSoup(requests.get(url).content, features="lxml")
df = pd.DataFrame()
data_list = []
for i in doc.findAll("div", {'data-target':"doc"}):
    if i.find("div",{'role':"link"}):
        i.find("div",{'role':"link"}).decompose()
    data_list.append((i.text, i["data-id"]))

# 八方论谈
url = 'https://drive.google.com/drive/folders/1xOlm5O7NUVG3Aq1oXdS2UsUgO9pLuHIM'
doc = BeautifulSoup(requests.get(url).content, features="lxml")
for i in doc.findAll("div", {'data-target':"doc"}):
    if i.find("div",{'role':"link"}):
        i.find("div",{'role':"link"}).decompose()
    data_list.append((i.text, i["data-id"]))

df = pd.DataFrame(data=data_list, columns=["filename", "id"]) 
df = df.loc[df.filename.str.contains('八方论坛|龙行天下|讲座')]
df.to_pickle(f'{data_dir}/transcript_info{suffix}.pkl')
print(f"{len(df)} items in total")

url_list = [f'https://docs.google.com/document/d/{id}/edit' for id in df['id']]
Downloader(url_list, nCache=2, outFilename=f'{data_dir}/transcript{suffix}.pkl').run()
