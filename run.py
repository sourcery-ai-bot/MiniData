from utils import utils
from lib import item, monster
from generator import Generator

from loguru import logger


@utils.timefn
@logger.catch
def Run():
    logger.info("程序开始运行...")
    gt = Generator()
    itemList = gt.GetItemList(gt.GetAddress("Item"))
    monsterList = gt.GetMonsterList(gt.GetAddress("Monster"))

    item.ExportItem(itemList)
    monster.ExportMonster(monsterList)


if __name__ == '__main__':
    Run()
