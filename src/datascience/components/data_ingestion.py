import os
import urllib.request as request
from src.datascience import logger
import zipfile
from src.datascience.entity.config_entity import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config
        
    def download_data(self):
        if not self.config.local_data_file.exists():
            filename, headers = request.urlretrieve(self.config.source_URL, self.config.local_data_file)
            logger.info(f"Downloaded file: {filename}")
        else:
            logger.info(f"File already exists: {self.config.local_data_file}")
            
    def extract_zip_file(self):
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(self.config.unzip_dir)
            logger.info(f"Extracted file to: {self.config.unzip_dir}")