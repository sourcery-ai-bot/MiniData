from loguru import logger

from generator import Generator
from lib import item


@logger.catch
def Run():
    logger.info("程序开始运行...")
    gt = Generator()
    itemList = gt.GetItemList(gt.GetAddress("ItemCsv"))
    item.ExportItem(itemList)


if __name__ == '__main__':
    Run()
