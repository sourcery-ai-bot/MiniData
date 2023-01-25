import json
from utils import utils

from loguru import logger


class Monster:
    def __init__(self, monster_id, monster_name):
        self.monster_id = monster_id
        self.monster_name = monster_name


def OuptutMonsterList(monsterList: list[Monster]):
    """输出生物列表"""
    for i in monsterList:
        print(f"ID: {i.monster_id}\tName: {i.monster_name}")


def ExportMonster(monsterList):
    """导出生物文件 支持json和txt格式"""
    monster = {"data": []}
    for i in monsterList:
        monster["data"].append(
            {
                "ID": i.monster_id,
                "Name": i.monster_name
            }
        )

    with open("export/Monster.json", "w", encoding="utf-8") as fp:
        json.dump(monster, fp, ensure_ascii=False, indent=4)

        szJsonFile = utils.GetFileSize("export/Monster.json")

    with open("export/Monster.txt", "wb") as fp:
        for i in monsterList:
            fp.write(f"{i.monster_id}    {i.monster_name} \n".encode("utf-8"))
        szTxtFile = utils.GetFileSize("export/Monster.txt")

    logger.success(f"已导出Monster数据  Monster.json({szJsonFile}KB) Monster.txt({szTxtFile}KB)")