from utils import utils
from lib import item
from generator import Generator

from loguru import logger


@utils.timefn
@logger.catch
def Run():
    logger.info("程序开始运行...")
    gt = Generator()
    itemList = gt.GetItemList(gt.GetAddress("ItemCsv"))
    item.ExportItem(itemList)


if __name__ == '__main__':
    Run()
