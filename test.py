import logging
import test2

logger = logging.getLogger()

logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler('trader.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


for i in range(10):
    logger.info(f'{i} 번 째 방문입니다.')
    test2.log(logger)
    