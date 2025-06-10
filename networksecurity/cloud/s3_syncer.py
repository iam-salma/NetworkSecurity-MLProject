import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class S3Sync:
    def sync_folder_to_s3(self, folder: str, aws_bucket_url: str):
        command = ["aws", "s3", "sync", folder, aws_bucket_url]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info("Sync to S3 successful:\n%s", result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error("Error syncing to S3:\n%s", e.stderr)

    def sync_folder_from_s3(self, folder: str, aws_bucket_url: str):
        command = ["aws", "s3", "sync", aws_bucket_url, folder]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info("Sync from S3 successful:\n%s", result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error("Error syncing from S3:\n%s", e.stderr)

# import os

# class S3Sync:
#     def sync_folder_to_s3(self,folder,aws_bucket_url):
#         command = f"aws s3 sync {folder} {aws_bucket_url} "
#         os.system(command)

#     def sync_folder_from_s3(self,folder,aws_bucket_url):
#         command = f"aws s3 sync  {aws_bucket_url} {folder} "
#         os.system(command)
