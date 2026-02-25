import os
import sys
import logging

logging_str="%(asctime)s: %(levelname)s: %(module)s: %(message)s"
logs_dir="logs"
log_filepath=os.path.join(logs_dir,"logging.log")
os.makedirs(logs_dir,exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filepath)
    ]
)

logger=logging.getLogger("datasciencelogger")


