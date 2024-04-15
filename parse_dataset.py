import requests
import urllib.request
import os
import logging
from config import USER_AGENT, INPUT_PATH, OUTPUT_PATH
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
from utils import download_from_s3

custom_headers = {"User-Agent": USER_AGENT}
opener = urllib.request.build_opener()
opener.addheaders = [(key, value) for key, value in custom_headers.items()]
urllib.request.install_opener(opener)
logger = logging.getLogger("data-quest-logger")


def parse_links(link):
    """Parses file links from resource"""
    links_list = []
    html_page = requests.get(link, headers=custom_headers).content
    for item in BeautifulSoup(html_page, "html.parser", parse_only=SoupStrainer("a")):
        link_href = item["href"]
        if item.get_text() != "[To Parent Directory]":
            file_url = urljoin(link, link_href)
            file_name = item.get_text()
            links_list.append({file_name: file_url})
    return links_list


def download_files_from_ftp(link):
    """Downloads files from server"""
    files_to_download = parse_links(link)
    logger.debug(f"Files to download: {files_to_download}")
    for link in files_to_download:
        for key, value in link.items():
            file_path = os.path.join(INPUT_PATH, key)
            urllib.request.urlretrieve(value, file_path)


def download_files_from_s3(resource, dir, s3_bucket_name):
    """Downloads latest version of files from s3 bucket"""
    s3_bucket = resource.Bucket(s3_bucket_name)
    files_list = []

    for s3_object in s3_bucket.objects.all():
        path, filename = os.path.split(s3_object.key)
        if filename:
            files_list.append(s3_object.key)
        if not filename:
            os.mkdir(os.path.join(dir, path))

    logger.debug(f"File list: {files_list}")

    for file in files_list:
        download_from_s3(resource, file, os.path.join(dir, file), s3_bucket_name)


def get_updates(link, resource, s3_bucket_name):
    """Downloads files from server and s3 bucket"""
    download_files_from_ftp(link)
    download_files_from_s3(resource, OUTPUT_PATH, s3_bucket_name)
