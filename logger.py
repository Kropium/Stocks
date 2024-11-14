import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
