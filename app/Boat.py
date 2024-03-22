import sys

from numpy import single
from Berth import Berth

berth_move_between = 500


class Boat:
    def __init__(self, id=0, num=0, pos=-1):
        self.id = id
        self.num = num  # 轮船的载货量
        self.goods = 0  # 轮船的当前货物量
        self.values = 0  # 轮船当前运载价值
        self.pos = pos  # 处在哪个泊位，虚拟点则为-1
        self.arrive_time = 0  # 下一个位置的到达时间
        self.leave_time = 0  # 下一个位置的离开时间
        self.berths = []  # 船的泊位
        """
        船的状态
        0: 船在移动中
        1: 船在装货或运输完成
        2: 船在泊位上等待
        """
        self.status = 1

    def search_best_berth(self, current_frame):
        """
        计算每个泊位的连续装货最大货物量
        """
        best_berth = None
        # best_deal_goods = None
        best_deal_time = -1
        best_value = -1
        for single_berth in self.berths:
            """
            判断泊位有无船只，且非当前泊位
            """
            if single_berth.status == 1 or single_berth.id == self.pos:
                continue
            else:
                """
                计算装货时间
                """
                arrive_time = current_frame + single_berth.transport_time
                if arrive_time >= 15000:
                    continue
                # arrive_goods = self.goods
                leave_goods = self.goods
                deal_time = 0
                left = single_berth.nums[arrive_time]
                while left > 0:
                    deal_time += 1
                    if arrive_time + deal_time >= 15000:
                        deal_time -= 1
                        break
                    if (
                        leave_goods + single_berth.loading_speed > self.num
                    ):  # 船装不下了
                        left -= self.num - self.goods
                        leave_goods = self.num
                        break
                    left += (
                        single_berth.nums[arrive_time + deal_time]
                        - single_berth.nums[arrive_time + deal_time - 1]
                    )
                    if left < single_berth.loading_speed:  # 货物不够了
                        left = 0
                        leave_goods += left
                        break
                    left -= single_berth.loading_speed
                    leave_goods += single_berth.loading_speed
                """
                        1. 计算获取价值
                        """
                single_value = 0
                # sort_keys = single_berth.future_goods.keys().sort()
                sort_keys = sorted(single_berth.future_goods.keys())
                for key in sort_keys:
                    if key <= arrive_time + deal_time:
                        single_value = single_berth.future_goods[key]
                    else:
                        break
                """
                        2. 与best_value比较
                        """
                if single_value > best_value:
                    best_berth = single_berth
                    # best_deal_goods = leave_goods - arrive_goods
                    best_deal_time = deal_time
                    best_value = single_value
        if best_berth is None:
            return {
                "best_berth_id": -1,
                "best_deal_time": 0,
                "best_value": 0,
                "leave_time": 0,
            }
        else:
            return {
                "best_berth_id": best_berth.id,
                "best_deal_time": best_deal_time,
                "best_value": best_value,
                "leave_time": current_frame
                + best_berth.transport_time
                + best_deal_time,
            }

    def search_next_berth(self, current_frame):
        """
        装满就走
        """
        if self.goods == self.num:
            return {
                "best_berth_id": -1,
                "best_deal_time": 0,
                "best_value": 0,
                "leave_time": 0,
            }
        """
        判断返回虚拟点还是下一个泊位
        """
        best_berth_id, best_deal_time, best_value, leave_time = self.search_best_berth(
            current_frame
        ).values()
        if self.values / self.berths[self.pos].transport_time > (
            self.values + best_value
        ) / (
            berth_move_between
            + best_deal_time
            + self.berths[best_berth_id].transport_time
        ):
            return {
                "best_berth_id": -1,
                "best_deal_time": 0,
                "best_value": 0,
                "leave_time": 0,
            }
        elif (
            self.berths[best_berth_id].transport_time
            + berth_move_between
            + current_frame
            >= 15000
        ):
            return {
                "best_berth_id": -1,
                "best_deal_time": 0,
                "best_value": 0,
                "leave_time": 0,
            }
        else:
            return {
                "best_berth_id": best_berth_id,
                "best_deal_time": best_deal_time,
                "best_value": best_value,
                "leave_time": current_frame + berth_move_between + best_deal_time,
            }

    """
    离开泊位
    """

    def leave_berth(self, current_frame):
        best_berth_id, best_deal_time, best_value, leave_time = self.search_next_berth(
            current_frame
        ).values()
        if best_berth_id == -1:
            # self.status = 3
            self.arrive_time = current_frame + self.berths[self.pos].transport_time
            print("go", self.id)
            sys.stdout.flush()
        else:
            print("ship", self.id, best_berth_id)
            sys.stdout.flush()
            self.berths[best_berth_id].boat_arrive(self)
            self.arrive_time = current_frame + self.berths[best_berth_id].transport_time
            self.leave_time = leave_time

    """
    装货
    """

    def load_goods(self, goods_num):
        if self.goods + goods_num > self.num:
            self.goods = self.num
            return self.num - self.goods
        else:
            self.goods += goods_num
            return 0

    """
    船是否满载
    """

    def is_full(self):
        return self.goods == self.num

    def next_step(self, current_frame, berths):
        self.berths = berths
        if self.pos == -1 and self.status == 1:
            # 船在虚拟点，需要前往泊位
            best_berth_id, best_deal_time, best_value, leave_time = (
                self.search_best_berth(current_frame).values()
            )
            if 2 * self.berths[best_berth_id].transport_time + current_frame >= 15000:
                return
            else:
                print("ship", self.id, best_berth_id)
            sys.stdout.flush()
            self.goods = 0
            self.berths[best_berth_id].boat_arrive(self)
            self.arrive_time = current_frame + self.berths[best_berth_id].transport_time
            self.leave_time = leave_time
        #     self.status = 1
        # elif self.status == 1:  # 船在前往泊位的途中（预留后续加入路径规划）
        #     if current_frame == self.arrive_time - 1:
        #         self.status = 2
        # elif self.status == 2:  # 船在泊位上
        #     return
        # elif self.status == 3:  # 船在前往虚拟点的途中
        #     if current_frame == self.arrive_time - 1:
        #         self.status = 0
        #         self.pos = -1
        #         self.goods = 0


# 测试代码
if __name__ == "__main__":
    boat = [Boat(i, 10, -1) for i in range(5)]
    berth = [
        Berth(
            id=i, x=10, y=10, transport_time=10 * i, loading_speed=4 * i, test_boat=boat
        )
        for i in range(10)
    ]
    for zhen in range(100):
        for single_boat in boat:
            single_boat.next_step(zhen, berth)
    # for current_frame in range(15000):
    #     for single_boat in boat:
    # single_boat.next_step(current_frame, [Berth(j) for j in range(10)])
    # print("current_frame", i)
