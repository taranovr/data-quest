import requests
from config import USER_AGENT, API_PATH, API_FILENAME, OUTPUT_PATH
from utils import compare_hash
import json
import os
import logging

logger = logging.getLogger("data-quest-logger")
custom_headers = {"User-Agent": USER_AGENT}


def store_api_response(
    api_link, resource, s3_bucket_name, file_name=API_FILENAME
):
    """Downloads API response to filesystem and s3 bucket"""
    html_page = requests.get(api_link, headers=custom_headers).content
    json_file = json.loads(html_page)
    file_bytes = bytes(json.dumps(json_file['data']).encode("UTF-8"))
    file_name = os.path.join(API_PATH, file_name)
    
    with open(file_name, "wb") as binary_file:
        binary_file.write(file_bytes)
    
    try:
        similar_hash = compare_hash(API_PATH, OUTPUT_PATH, API_FILENAME)
        if similar_hash:
            logger.debug(f"No need to update {API_FILENAME}")
        else:
            object = resource.Object(s3_bucket_name, API_FILENAME)
            object.put(Body=file_bytes)
            logger.debug(f"{API_FILENAME} was updated in s3")
    except FileNotFoundError:
        object = resource.Object(s3_bucket_name, API_FILENAME)
        object.put(Body=file_bytes)
        logger.debug(f"{API_FILENAME} was updated in s3")
        
        
    logger.debug(file_name)
