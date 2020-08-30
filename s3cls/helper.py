"""
Contains all the helper functions
"""


def get_logger(name=__file__, logfile_name='s3-cleanup-runtime'):
    from datetime import datetime
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('{}-{:%Y-%m-%d}.log'.format(logfile_name, datetime.now()))
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler), logger.addHandler(f_handler)
    return logger


def load_aws_secrets():
    """
    Loads all the secrets required to connect to AWS from environment variables
    """
    from os import environ
    import sys
    try:
        region_name = environ.get("AWS_DEFAULT_REGION", "us-west-2")
        aws_access_key_id = environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = environ["AWS_SECRET_ACCESS_KEY"]
        aws_session_token = environ.get("AWS_SESSION_TOKEN", "")

        _secrets = {
            'region_name': region_name,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            **({'aws_session_token': aws_session_token} if aws_session_token != "" else {})
        }
        return _secrets
    except KeyError as ke:
        print("Please set the environment variables", ke)
        sys.exit(1)
