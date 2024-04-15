import os
import shutil
import hashlib
import filecmp
import logging
from config import LOGS_DIR, INPUT_PATH, OUTPUT_PATH, API_PATH, LOGS_PATH
logger = logging.getLogger("data-quest-logger")

def clean_temp_files():
    """Remove temporary files from filesystem"""
    for folder in [INPUT_PATH, OUTPUT_PATH, API_PATH, LOGS_PATH]: 
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)

def upload_to_s3(resource, file, s3_bucket_name, s3_obj_key):
    resource.Bucket(s3_bucket_name).upload_file(file, s3_obj_key)

def delete_from_s3(resource, file, s3_bucket_name):
    resource.Object(s3_bucket_name, file).delete()

def download_from_s3(resource, s3_key, filename, s3_bucket_name):
    """Downloads file from s3 bucket"""
    if LOGS_DIR not in s3_key:
        s3_bucket = resource.Bucket(s3_bucket_name)
        s3_bucket.download_file(s3_key, filename)
        
def file_hash(filepath):
    """Calculates file hash"""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()        
        
def compare_hash(input_path, output_path, filename):
    """Compare hash of two files"""
    source_hash = file_hash(os.path.join(input_path, filename))
    target_hash = file_hash(os.path.join(output_path, filename))
    if source_hash == target_hash:
        return True
    else:
        return False

def delete_files_from_s3(resource, files_list, s3_bucket_name):
    """Delete files from s3 using file list"""
    for file in files_list:
        delete_from_s3(resource, file, s3_bucket_name)


def compare_files(source_dir, target_dir):
    """Compares files in specified directories"""
    files_to_upload = []
    files_to_delete = []

    dcmp = filecmp.dircmp(source_dir, target_dir)

    logger.debug(f"Common files:  {dcmp.common_files}")
    logger.debug(f"Files in  {source_dir}, but not in  {target_dir} : {dcmp.left_only}")
    logger.debug(
        f"Files in {target_dir}, but not in {source_dir} : {dcmp.right_only}"
    )

    for file in dcmp.common_files:
        similar_hash = compare_hash(INPUT_PATH, OUTPUT_PATH, file)
        if similar_hash:
            logger.debug(f"File {file}: no need to update")
        else:
            logger.debug(f"File {file}: should be updated")
            files_to_upload.append(os.path.join(INPUT_PATH, file))

    for file in dcmp.left_only:
        files_to_upload.append(os.path.join(INPUT_PATH, file))

    for file in dcmp.right_only:
        files_to_delete.append(file)

    return files_to_upload, files_to_delete


def upload_files_to_s3(resource, files_to_upload, s3_bucket_name):
    """Uploads files to s3 bucket from given files list"""
    for file in files_to_upload:
        s3_obj_key = os.path.relpath(file, INPUT_PATH)
        upload_to_s3(resource, file, s3_bucket_name, s3_obj_key)


def sync_s3(resource, s3_bucket_name):
    """Sync files in s3 bucket"""
    files_to_upload, files_to_delete = compare_files(INPUT_PATH, OUTPUT_PATH)

    logger.debug(
        f"Files to upload: {files_to_upload}, Files to delete: {files_to_delete}"
    )

    delete_files_from_s3(resource, files_to_delete, s3_bucket_name)
    upload_files_to_s3(resource, files_to_upload, s3_bucket_name)