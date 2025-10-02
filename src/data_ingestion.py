import os
from src.custom_exception import CustomException
from src.logger import get_logger
import pandas as pd
import numpy as np
from google.cloud import storage
from utils.common_functions import read_yaml
from config.config_path import *


logger=get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config=config['data_ingestion']
        self.bucket_name=self.config['bucket_name']
        self.file_names=self.config['bucket_file_names']
        
        os.makedirs(RAW_DIR,exist_ok=True)
        
        logger.info(" Data Ingesetion to artifacts")
    def download_csv_from_gcp(self):
        try:
            client  = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR,file_name)

                if file_name=="animelist.csv":
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    data = pd.read_csv(file_path,nrows=9000000)
                    data.to_csv(file_path,index=False)
                    logger.info("Large file detected Only downloading 9M rows")
                else:
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    logger.info("Downloading Smaller Files ie anime and anime_with synopsis")
        
        except Exception as e:
            logger.error("Error while downloading data from GCP")
            raise CustomException("Failed to download data",e)
        
    def run(self):
        try:
            logger.info("Starting the Data Ingestion Process.....")
            self.download_csv_from_gcp()
            logger.info("Data Ingestion completed.....")
        except Exception as e:
            logger.error("Data Ingestion Failed")
            raise CustomException("Data Ingestion not completed...",e)
        finally:
            logger.info("Data Ingestion done")
if __name__=="__main__":
    ingestion=DataIngestion(read_yaml(CONFIG_PATH))
    ingestion.run()
            
        
        