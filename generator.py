from utils.utils import *
from lib import item

from pymem import *
from pymem.process import module_from_name
from pymem.pattern import pattern_scan_module
from pymem.exception import *

# logger的导入一定要Pymem放在下面 不然会被Pymem的logging覆盖
from loguru import logger

address_pattern = b"\xA1....\x85\xC0\x75.\x6A\x1C\xE8....\x8B\xF8\x83"


class Generator:
    def __init__(self):
        self.pm = None
        self.module_handle = None

        isInit = self.InitProcess()
        if isInit:
            logger.success("初始化进程信息成功!")
        else:
            logger.error("初始化进程信息失败, 请检查错误信息, 如无法解决请前往GitHub提交Issue")
            exit()

    def __del__(self):
        if self.pm is not None:
            self.pm.close_process()
        logger.info("生成器已退出!")

    @timefn
    @logger.catch
    def InitProcess(self) -> bool:

        """初始化进程信息"""
        try:
            self.pm = Pymem("iworldpc3.exe")
        except ProcessNotFound:
            logger.error("获取iworldpc3.exe进程失败, 请先打开游戏再运行此程序!")
            return False

        try:
            self.module_handle = module_from_name(self.pm.process_handle, "libiworld_micro.dll")
        except ModuleNotFoundError:
            logger.error("获取libiworld_micro.dll模块失败, 请前往GitHub提交Issue!")
            self.pm.close_process()
            return False

        return True

    @logger.catch
    def GetAddress(self, key) -> int:
        """
        获取存放csv数据(猜测应该是csv)的内存地址
        :param key: csv名
        :return: 返回对应csv数据的内存地址
        """
        address = pattern_scan_module(self.pm.process_handle, self.module_handle, address_pattern)
        address = self.pm.read_int(address + 1)

        if address != 0:
            logger.success(f"获取csv数据地址成功! address: 0x{hex(address)[2:].upper()}")
        else:
            logger.error("获取csv数据地址失败!")
            return 0

        dic = dict()

        dic["ItemCsv"] = address
        dic["String"] = address + 0x3C
        dic["Monster"] = address + 0x40
        dic["Block"] = address + 0x54
        dic["Tool"] = address + 0x6C
        dic["PhysicsActor"] = address + 0xA0
        dic["Projectile"] = address + 0xB4
        dic["MusicalInstruments"] = address + 0xC8
        dic["SprayPaint"] = address + 0xDC
        dic["DevUIResource"] = address + 0xF0
        dic["Food"] = address + 0xF4
        dic["HorseEgg"] = address + 0x108
        dic["RuleOption"] = address + 0x11C
        dic["ItemSkill"] = address + 0x120
        dic["AntiFraud"] = address + 0x134
        dic["Particles"] = address + 0x138
        dic["BuffDef"] = address + 0x13C
        dic["MinicodeMonsterDef"] = address + 0x150
        dic["Score"] = address + 0x164
        dic["BuffEffectBank"] = address + 0x178
        dic["BuffEffectEnum"] = address + 0x18C
        dic["RoleSkin"] = address + 0x1A0
        dic["BuffEffectSliding"] = address + 0x1A4
        dic["SkinActCsv"] = address + 0x1BC
        dic["SoundStrDev"] = address + 0x1BC
        dic["ParticlesStr"] = address + 0x1D0

        if key not in dic.keys():
            logger.error(f"{key}不存在, 请检查输入错误!")
            return 0

        return dic[key]

    @timefn
    @logger.catch
    def GetItemList(self, address) -> list[item.Item]:
        """
        获取物品列表
        :param address: ItemCsv实例的地址
        :return: 返回物品列表
        """
        address = self.pm.read_int(address)

        begin = self.pm.read_int(address + 0x8)
        end = self.pm.read_int(address + 0xC)
        length = (end - begin) >> 2

        if begin == 0 or end == 0 or length < 10000 or length > 2000000:
            return []

        itemList = []

        for i in range(1, length):

            baseAddress = self.pm.read_int(begin + i * 4)
            if baseAddress == 0:
                continue

            # 读取物品ID
            item_id = self.pm.read_int(baseAddress)

            # 读取物品名称
            length = self.pm.read_int(baseAddress + 0x5C)
            item_name = ""
            if 0 < length < 16:
                item_name = self.pm.read_bytes(baseAddress + 0x4C, length).decode("utf-8")
            elif 16 <= length < 100:
                name_address = self.pm.read_int(baseAddress + 0x4C)
                item_name = self.pm.read_bytes(name_address, length).decode("utf-8")
            if item_name == "":
                item_name = "未知"

            # 读取物品类型ID
            # item_type = self.pm.read_int(baseAddress + 0x40)

            item_ = item.Item(item_id, item_name)
            itemList.append(item_)

        return itemList


if __name__ == '__main__':
    logger.info("程序开始运行...")
    gt = Generator()
    addr = gt.GetAddress("ItemCsv")
    lst = gt.GetItemList(addr)
    # item.OuptutItemList(lst)
    item.ExportItem(lst)
