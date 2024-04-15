import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin

base_url = "https://download.bls.gov/pub/time.series/pr/"


contact_info = {
    "name": "First Last",
    "email": "firstlast@email.com"
}

# Construct the User-Agent header with contact information
user_agent = f"PythonRequests (contact: {contact_info['name']}, email: {contact_info['email']})"


html_page = requests.get(base_url, headers={"User-Agent": user_agent}).content
for link in BeautifulSoup(html_page, "html.parser", parse_only=SoupStrainer('a')):
    print(link['href'], link.get_text())
    # link_href = link['href']
    # link_url = urljoin(base_url, link_href)
    # print(link_url)