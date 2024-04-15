import os

FTP_SERVER_LINK = "https://download.bls.gov/pub/time.series/pr/"
API_LINK = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"
API_FILENAME = "api_response.json"
S3_BUCKET_NAME = "rearc-quest-bucket-roman"

INPUT_DIR = "in"
OUTPUT_DIR = "out"
API_DIR = INPUT_DIR
LOGS_DIR = "logs"
TEMP_DIR = "/tmp"

WORK_PATH = TEMP_DIR
INPUT_PATH = os.path.join(WORK_PATH, INPUT_DIR)
OUTPUT_PATH = os.path.join(WORK_PATH, OUTPUT_DIR)
API_PATH = os.path.join(WORK_PATH, API_DIR)
LOGS_PATH = os.path.join(WORK_PATH, LOGS_DIR)

contact_info = {"name": "First Last", "email": "firstlast@email.com"}
USER_AGENT = (
    f"PythonRequests (contact: {contact_info['name']}, email: {contact_info['email']})"
)