import logging; from logging_config import setup_logging

# Set up logging
logger = setup_logging()


def main():
    logger.debug("Main function executed")

if __name__ == "__main__":
    main()