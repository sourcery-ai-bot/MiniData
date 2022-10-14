import json
from utils import utils

from loguru import logger


class Item:
    def __init__(self, item_id, item_name):
        self.item_id = item_id
        self.item_name = item_name


def OuptutItemList(itemList: list[Item]):
    """输出物品列表"""
    for i in itemList:
        print(f"ID: {i.item_id}\tName: {i.item_name}")


def ExportItem(itemList):
    """导出物品文件 支持json和txt格式"""
    item = {"data": []}
    for i in itemList:
        item["data"].append(
            {
                "ID": i.item_id,
                "Name": i.item_name
            }
        )

    with open("export/Item.json", "w", encoding="utf-8") as fp:
        json.dump(item, fp, ensure_ascii=False, indent=4)

        szJsonFile = utils.GetFileSize("export/Item.json")

    with open("export/Item.txt", "wb") as fp:
        for i in itemList:
            fp.write(f"{i.item_id}    {i.item_name} \n".encode("utf-8"))
        szTxtFile = utils.GetFileSize("export/Item.txt")

    logger.success(f"已导出Item数据  Item.json({szJsonFile}KB) Item.txt({szTxtFile}KB)")