import asyncio,aiohttp,platform,os,json
import pandas as pd

class Downloader:

    def __init__(self, url_list, 
                        type='get', 
                        headers='', 
                        data='', 
                        proxy='',
                        tSleep=1,
                        nCache=500,
                        nRetry=3,
                        str_list=[],
                        decode='utf8',
                        outFilename='out.pkl'):
        self.url_list = url_list
        self.headers = headers
        self.data = data
        self.proxy = proxy
        self.type = type
        self.tSleep = tSleep
        self.nCache = nCache
        self.nRetry = nRetry
        self.str_list = str_list 
        self.decode = decode
        self.errorString = b'NULL from response'
        self.outFilename = outFilename
        
        if os.path.exists(self.outFilename):
            self.df = pd.read_pickle(self.outFilename)
        else:
            self.df = pd.DataFrame()
    
    def fetchError(self):
        url_error = []
        if not self.df.empty:
            url_error = list(self.df.loc[self.df.response == self.errorString].url)
            url_error += list(self.df.loc[self.df.response == b''].url)
            if self.str_list:
                for s in self.str_list:
                    url_error += list(self.df.loc[self.df.response.map(lambda x: x.decode(self.decode).find(s)) > 0].url)

            url_error = list(set(url_error))
        return url_error

    def url_todo(self):
        url_done = []
        if not self.df.empty:
            url_done = list(self.df.url)
        url_error = self.fetchError()
        url_todo = list(set(self.url_list).difference(url_done)) 
        url_todo += url_error
        url_todo = list(set(url_todo))

        return url_todo
    
    async def fetchResponse(self, url):
        if self.type == 'get':
            df = await self.get(url)
        elif self.type == 'post':
            df = await self.post(url)
        return df

    async def get(self, url):
        try:
            async with self.sem:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url=url, headers=self.headers, proxy=self.proxy) as response:
                        res = await response.read()
                        await asyncio.sleep(self.tSleep)
        except:
            res = self.errorString

        return pd.DataFrame(data={'url':url, 'response': res},index=[0])

    async def post(self, url):
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url=self.data, headers=self.headers, data=json.loads(url)) as response:
                    res = await response.read()
        except:
            res = self.errorString
        
        return pd.DataFrame(data={'url':url, 'response': res},index=[0])
    
    async def tasker(self, njob):
        self.sem = asyncio.Semaphore(njob)
        n = 0
        url_todo = self.url_todo()
        print(f'{len(url_todo)} urls to be downloaded')
        while (url_todo != []) and (n < 3):
            for idx in list(range(len(url_todo)))[::self.nCache]:
                task_list = [self.fetchResponse(url) for url in url_todo[idx:idx+self.nCache]]
                L = await asyncio.gather(*task_list)
                self.df = pd.concat([self.df] + L, ignore_index=True).drop_duplicates(subset=['url'],keep='last')
                self.df.to_pickle(self.outFilename)
                print(f'<{n+1}>: Fetching {idx+self.nCache} entries')
            url_todo = self.url_todo()
            n += 1

    def run(self, njob=10):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.tasker(njob))
        print('done')
        