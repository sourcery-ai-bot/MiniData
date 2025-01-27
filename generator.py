from utils.utils import *
from lib import item, monster

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

        if isInit := self.InitProcess():
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

        logger.info(f"PID: {self.pm.process_id} | HPROCESS: {hex(self.pm.process_handle)}")
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

        dic = {
            "Item": address,
            "String": address + 0x3C,
            "Monster": address + 0x40,
            "Block": address + 0x54,
            "Tool": address + 0x6C,
            "PhysicsActor": address + 0xA0,
            "Projectile": address + 0xB4,
            "MusicalInstruments": address + 0xC8,
            "SprayPaint": address + 0xDC,
            "DevUIResource": address + 0xF0,
            "Food": address + 0xF4,
            "HorseEgg": address + 0x108,
            "RuleOption": address + 0x11C,
            "ItemSkill": address + 0x120,
            "Lua": address + 0x134,
            "AntiFraud": address + 0x13C,
            "Particles": address + 0x140,
            "Buff": address + 0x144,
            "MinicodeMonster": address + 0x158,
            "Score": address + 0x16C,
            "BuffEffectBank": address + 0x180,
            "BuffEffectEnum": address + 0x194,
            "ResourcePack": address + 0x1A8,
            "RoleSkin": address + 0x1BC,
            "BuffEffectSliding": address + 0x1C0,
            "SkinAct": address + 0x1D4,
            "CreateRoleAvatar": address + 0x1D8,
            "Summon": address + 0x1EC,
            "SoundStr": address + 0x1F0,
            "ParticlesStr": address + 0x204,
        }

        if key not in dic.keys():
            logger.error(f"{key}不存在, 请检查输入错误!")
            return 0

        return dic[key]

    @logger.catch
    def GetItemList(self, address) -> list[item.Item]:
        """
        获取物品列表
        :param address: Item实例的地址
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
            length = self.pm.read_int(baseAddress + 0x60)
            item_name = ""
            if 0 < length < 16:
                item_name = self.pm.read_bytes(baseAddress + 0x50, length).decode("utf-8")
            elif 16 <= length < 100:
                name_address = self.pm.read_int(baseAddress + 0x50)
                item_name = self.pm.read_bytes(name_address, length).decode("utf-8")
            if item_name == "":
                item_name = "未知"

            # 读取物品类型ID
            # item_type = self.pm.read_int(baseAddress + 0x44)

            item_ = item.Item(item_id, item_name)
            itemList.append(item_)

        return itemList

    @logger.catch
    def GetMonsterList(self, address) -> list[monster.Monster]:
        """
        获取生物列表
        :param address: Monster实例的地址
        :return: 返回生物列表
        """
        address = self.pm.read_int(address)
        monsterList = []

        base = self.pm.read_int(address + 0x20)
        base = self.pm.read_int(base)

        dataAddress = base + 0x8
        next_ = self.pm.read_int(base + 0x4)

        # 读取链表 (一路next读过去完事了)
        while next_ != base:
            while True:
                # ID
                monster_id = self.pm.read_int(dataAddress)
                if monster_id <= 0:
                    break

                # Name
                name_len = self.pm.read_int(dataAddress + 0x24)
                monster_name = ""
                if 0 < name_len < 16:
                    monster_name = self.pm.read_bytes(dataAddress + 0x14, name_len).decode("utf-8")
                elif 16 <= name_len < 100:
                    name_address = self.pm.read_int(dataAddress + 0x14)
                    monster_name = self.pm.read_bytes(name_address, name_len).decode("utf-8")

                if monster_name == "":
                    monster_name = "未知"

                monster_ = monster.Monster(monster_id, monster_name)
                monsterList.append(monster_)
                break

            next_ = self.pm.read_int(next_ + 0x4)
            dataAddress = next_ + 0x8

        monsterList.sort(key=lambda x: x.monster_id, reverse=False)

        return monsterList


if __name__ == '__main__':
    logger.info("程序开始运行...")
    gt = Generator()
    addr = gt.GetAddress("Monster")
    lst = gt.GetMonsterList(addr)
    monster.OuptutMonsterList(lst)
    # item.ExportItem(lst)
