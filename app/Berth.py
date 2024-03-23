import numpy as np


class Berth:
    def __init__(self, id=0, x=0, y=0, transport_time=0, loading_speed=0, test_boat=[]):
        self.id = id
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        self.nums = np.array([0 for i in range(15000)])
        self.boat = None  # 最快到达港口的船
        self.status = 0  # 0没有船要过来，1有船正在泊位上或者将要过来
        self.all_path = {}  # 字典，(x,y)到所有点的路径，key是点的编号（number），value是(x,y)到这个点的最短路径，不连通的key不会出现在all_path中
        # 这个路径记录的是港口到点的路径，机器人要使用这个路径的话得对value进行逆转，即[::-1]
        # self.total_goods = deque([])  # 用队列记录当前的货物放置顺序，里面都是Goods对象
        self.total_values = 0  # 当前港口上货物的总价值
        self.future_goods = {}  # 记录港口未来到达的货物，key是货物在那一帧到达，value是货物的价值
        self.temp_boat = test_boat
        self.robots_nums = 0  # 选择这个港口的机器人数量
        self.benefit = 1 / self.transport_time
        self.boat_list = []  # 记录了船的列表
        self.ban_flag = 0  # 1表示开始废弃港口
        self.wait_load_goods = []

    def robot_pull(self, time, value):  # 机器人放置物品到码头，time是机器人到达的时间
        self.nums[time:] += 1
        while time in self.future_goods.keys():
            time += 0.01
        self.future_goods[time] = value

    def robot_undo(self, robot_origin_time, time=-1):
        # origin_time机器人原本到达的时间
        # time是机器人现在到达的时间
        # -1 表示当前机器人放弃计划后，暂时没有去拿货物
        self.nums[robot_origin_time:] -= 1
        if time != -1:
            value = self.future_goods[robot_origin_time]
            self.nums[time:] += 1
            while time in self.future_goods.keys():
                time += 0.01
            self.future_goods[time] = value
        else:
            self.wait_load_goods[0] -= 1
            for boat in self.boat_list:
                if time < boat.leave_time:
                    boat.goods -= 1
                    break
        del self.future_goods[robot_origin_time]

    def boat_load(self, current_time):  # 每帧执行
        if len(self.boat_list) == 0:  # 当前没有船要到达该码头
            return
        if current_time >= 15000 - 3 * self.transport_time:
            self.ban_flag = 1
        self.boat = self.boat_list[0]
        if current_time >= self.boat.leave_time:
            if self.boat_leave(max(current_time, self.boat.leave_time)):
                goods_key = sorted(self.future_goods.keys())
                for i in range(self.wait_load_goods[0]):
                    if self.future_goods == {}:
                        break
                    del self.future_goods[goods_key[i]]
                self.wait_load_goods.pop(0)

                return  # 船离开结束boat_load
                # 船没有离开，继续装货
            nums_arr = self.nums[current_time]
            load_nums = self.boat.load_goods(min(nums_arr, self.loading_speed))
            self.nums[current_time:] -= load_nums
            self.wait_load_goods[0] += load_nums
            # 对价值进行更新

    def boat_leave(self, current_time):
        self.boat = self.boat_list[0]
        if (
            self.nums[current_time] == 0
            or self.boat.is_full()
            or (15000 - current_time) < self.transport_time
        ):
            self.boat.leave_berth(current_time)
            self.boat = None
            self.status = 0
            self.boat_list.pop(0)
            if self.ban_flag:
                self.status = -1
            return True
        return False

    def boat_arrive(self, boat, good_nums):
        self.boat_list.append(boat)
        self.nums[boat.arrive_time :] -= good_nums
        self.wait_load_goods.append(good_nums)
        self.status = 1
