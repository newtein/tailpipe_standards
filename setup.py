import os
from local_logger import LocalLogger

logging = LocalLogger().setup()



def make_dir(name):
    if not os.path.exists(name):
        os.mkdir(name)


if __name__ == "__main__":
    try:
        mandetory_dirs = ["input_configs", "output_tables", "output_images"]
        for dir in mandetory_dirs:
            make_dir(dir)
        logging.info("Setup successful!")
    except Exception as e:
        logging.error(e)

