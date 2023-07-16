import os
import configparser

import globalVar

# 全局配置路径： 文档\HCVS_Verifier\config.ini
ConfigPath = os.path.join(os.path.expanduser("~"), "HCVS_Verifier", "config.ini")


def initConfig():
    # 如果配置文件不存在，则创建配置文件
    if not os.path.exists(ConfigPath):
        os.makedirs(os.path.dirname(ConfigPath), exist_ok=True)
        with open(ConfigPath, "w", encoding="utf-8") as f:
            f.write("[Data]\n")
            f.write("path=%s\n" % os.path.join(os.path.expanduser("~"), "HCVS_Verifier", "data"))


def getConfig():
    initConfig()
    # 将ini文件读取到字典中
    config = configparser.ConfigParser()
    config.read(ConfigPath, encoding="utf-8")
    ini_dict = {}
    for section in config.sections():
        section_dict = {}
        for key, value in config[section].items():
            section_dict[key] = value
        ini_dict[section] = section_dict
    return ini_dict


def setConfig(section, key, value):
    initConfig()
    config = configparser.ConfigParser()
    config.read(ConfigPath, encoding="utf-8")
    # 如果没有该section，则创建该section
    if section not in config.sections():
        config.add_section(section)
    config.set(section, key, str(value))
    config.write(open(ConfigPath, "w", encoding="utf-8"))
    return True


def getUserKey(UserID):
    configs = getConfig()
    DataPath = configs["Data"]["path"]
    UserFilePath = os.path.join(DataPath, "UserList.bin")
    globalVar.UserListBinLock.acquire()
    if not os.path.exists(UserFilePath):
        # 如果没有该文件，则创建该文件
        with open(UserFilePath, "wb") as f:
            f.write(b"")
    # 定位到用户信息
    with open(UserFilePath, "rb") as f:
        # print((UserID - 1) * 70 + 6)
        f.seek((UserID - 1) * 70 + 6)
        userKey = f.read(64)
    globalVar.UserListBinLock.release()
    return userKey