import os
import time
import random

import push
import login
import tools
import config
import mihoyobbs
import competition
import gamecheckin
import hoyo_checkin
import cloudgames
import os_cloudgames
from error import *
from loghelper import log


def random_pause():
    """添加随机暂停，范围为0.5到4秒，并输出等待信息"""
    pause_time = random.uniform(0.5, 4)  # 生成0.5到4秒之间的随机浮点数
    log.info(f"等待 {pause_time:.3f} 秒...")
    time.sleep(pause_time)


def main():
    log.info("BASE ON GITHUB ACTION(RAN)")
    # 初始化，加载配置
    config.load_config()
    if not config.config["enable"]:
        log.warning("Config未启用！")
        return 1, "Config未启用！"

    # 检测参数是否齐全，如果缺少就进行登入操作
    if any([config.config["account"]["stuid"] == "", config.config["account"]["stoken"] == "",
            login.require_mid() and config.config["account"]["mid"] == ""]):
        # 登入，如果没开启bbs全局没打开就无需进行登入操作 (实际上也可以登录)
        if config.config["mihoyobbs"]["enable"]:
            log.info("开始登录操作...")
            login.login()
            random_pause()
        # 整理 cookie，在字段重复时优先使用最后出现的值
        config.config["account"]["cookie"] = tools.tidy_cookie(config.config["account"]["cookie"])

    # 米游社签到
    ret_code = 0
    return_data = "\n"
    raise_stoken = False

    # 升级stoken
    if config.config["account"]["stoken"] != "" and not login.require_mid():
        try:
            log.info("正在升级Stoken...")
            login.update_stoken_v2()
            random_pause()
        except StokenError:
            raise_stoken = True

    if config.config["mihoyobbs"]["enable"]:
        if config.config["account"]["stoken"] == "StokenError":
            raise_stoken = True
            return_data += "米游社: \n账号Stoken异常"
        else:
            try:
                log.info("正在运行米游社任务...")
                bbs = mihoyobbs.Mihoyobbs()
                return_data += bbs.run_task()
                random_pause()
            except StokenError:
                raise_stoken = True

    # 国服签到
    if config.config["account"]["cookie"] == "CookieError":
        raise CookieError('Cookie expires')
    if config.config['games']['cn']["enable"]:
        log.info("正在进行国服游戏签到...")
        return_data += gamecheckin.run_task()
        random_pause()

    # 云游戏
    if config.config['cloud_games']['cn']["enable"]:
        log.info("正在进行云游戏签到...")
        return_data += "\n\n" + cloudgames.run_task()
        random_pause()

    # 国际签到
    if config.config['games']['os']["enable"]:
        log.info("正在进行国际版签到...")
        os_result = hoyo_checkin.run_task()
        if os_result != '':
            return_data += "\n\n" + "海外版:" + os_result
        random_pause()

    if config.config['cloud_games']['os']["enable"]:
        log.info("正在进行云游戏国际版签到...")
        return_data += "\n\n" + os_cloudgames.run_task()
        random_pause()

    # 米游社竞赛活动签到
    if config.config['competition']['enable']:
        log.info("正在进行米游社竞赛活动签到...")
        competition_result = competition.run_task()
        if competition_result != '':
            return_data += "\n\n" + "米游社竞赛活动:" + competition_result
        random_pause()

    if raise_stoken:
        raise StokenError("Stoken异常")
    if "触发验证码" in return_data:
        ret_code = 3
    return ret_code, return_data


if __name__ == "__main__":
    push_message = ""
    message = ""
    try:
        status_code, message = main()
    except CookieError:
        status_code = 1
        push_message = "账号Cookie出错！\n"
        log.error("账号Cookie有问题！")
    except StokenError:
        status_code = 1
        push_message = "账号Stoken出错！\n"
        log.error("账号Stoken有问题！")
    push_message += message
    push.push(status_code, push_message)