import time

from common import TempUtils, PortUtils
from common.AutoAdb import AutoAdb
from common.Slider import Slider


class TeamLeader:
    adb = AutoAdb()
    current_team_num = 1  # 当前是第几个队伍

    def __init__(self):
        self.current_team_num = self.get_team_num()

    # 判断当前是第几个队伍
    # 此操作会导致地图发生位移！！因此，此方法被调用前的位置信息会失效
    def get_team_num(self):
        # 先滑动到地图最左边
        Slider().slide_unidirectional(4, 2)
        # 尝试匹配队伍
        is_team_1 = self.adb.check("temp_images/stage/team-1.png")
        # 滑动回来
        Slider().slide_unidirectional(3, 1)

        # 判断
        if is_team_1:
            return 1
        return 2

    # 切换队伍。
    def switch(self):
        self.adb.click("temp_images/stage/team-switch.png")
        self.current_team_num = 2 if self.current_team_num == 1 else 1

    # 招惹敌军.
    # True 说明已经找到
    # False 说明关卡结束
    # 异常退出 说明关卡未结束, 可是无法分辨出敌人
    def provoke_enemy(self):
        adb = self.adb
        # 这里要多等待几秒, 因为经常会有个动画影响寻敌
        time.sleep(3)

        check = adb.check('temp_images/stage/in-unit.png')
        if check:
            print('关卡已经结束')
            return False

        # 弹药为空且当前是第一队时切换队伍
        if self.current_team_num == 1 and adb.check('temp_images/stage/bullet-empty.png'):
            self.switch()

        image_rel_path_list = TempUtils.get_temp_rel_path_list('temp_images/enemy')

        slider = Slider()
        while True:
            print('寻找敌人 ... ')
            enemy_loc = adb.get_location(*image_rel_path_list)
            if enemy_loc is None:
                slider.slide()
                continue

            # 如果当前是第一队, 且找到的是boss, 则切换到第二队开始寻找敌人
            if self.current_team_num == 1 and 'boss' in enemy_loc.temp_rel_path:
                self.switch()
                continue

            enemy_loc.click()
            # 等待进击按钮出现, 期间会不断处理意外情况, 如果指定时间内出现按钮, 则执行结束, 否则再次循环
            res = adb.wait('temp_images/fight/fight.png', max_wait_time=8,
                                episode=self.deal_accident_when_provoke_enemy).click()
            if res:
                # 是否出现满员提示
                PortUtils.check_port_full()
                return True
            else:
                # 如果点击后未进入确认界面, 说明那里不可到达, 此时去除image_rel_path_list中的值
                image_rel_path_list.remove(enemy_loc.temp_rel_path)

    # 处理进击时的意外情况
    def deal_accident_when_provoke_enemy(self):
        adb = self.adb
        # 自动战斗
        res = adb.click('temp_images/fight/auto-fight-confirm-1.png')
        if res:
            print('确认自律战斗')
            adb.wait('temp_images/fight/auto-fight-confirm-2.png').click()
        # 处理途中获得道具的提示
        adb.click('temp_images/stage/get-tool.png')
        # 处理伏击
        adb.click('temp_images/stage/escape.png')