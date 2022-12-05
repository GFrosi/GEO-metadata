import urllib.request
import lxml.html as lh
from bs4 import BeautifulSoup
import requests
from time import sleep
from retry import retry
from tqdm import tqdm

@retry(TimeoutError, tries=5, delay=3)
def srr_web_scrapping(list_srx_address):

    SRR_srx_ncbi = []
    for url in tqdm(list_srx_address):
        # url = srx
        response = requests.get(url)
        sleep(1)
        data = response.text
        soup = BeautifulSoup(data, 'lxml')

        for a in soup.findAll('b'):
            inf = a.get_text()
            srx = inf.split(':')[0]

        for td in soup.findAll("td"):
            for link in td.find_all('a'):
                SRR_srx_ncbi.append([srx, link.get_text()])

    return SRR_srx_ncbi