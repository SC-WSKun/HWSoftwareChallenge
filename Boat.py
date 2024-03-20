berth_move_between = 500

class Boat:
    def __init__(self, id=0, num=0, pos=-1, status=0):
        self.id = id
        self.num = num  # 轮船的载货量
        self.goods = 0  # 轮船的当前货物量
        self.values = 0  # 轮船当前运载价值
        self.pos = pos  # 处在哪个泊位，虚拟点则为-1
        self.future_pos = None  # 下一个位置
        self.arrive_time = 0  # 下一个位置的到达时间
        self.leave_time = 0  # 下一个位置的离开时间
        self.berths = []# 船的泊位
        """
        船的状态
        0: 船在虚拟点
        1: 船在前往泊位的途中
        2: 船在泊位上
        3: 船在前往虚拟点的途中
        """
        self.status = status

    def search_best_berth(self, current_frame, action=1):
        match action:
            case 0:  # 方案一
                # best_berth = None
                # for single_berth in self.berths:
                #     if single_berth.status == 0:
                #         continue
                #     else:
                #         if single_berth.transport_time < best_berth.transport_time:
                #             best_berth = single_berth
                # return best_berth
                return
            case 1:  # 方案二
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
                        # arrive_goods = self.goods
                        leave_goods = self.goods
                        deal_time = 0
                        left = single_berth.nums[arrive_time]
                        while left > 0:
                            deal_time += 1
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
                        sort_keys = single_berth.wait_load_value.keys().sort()
                        for key in sort_keys:
                            if key <= arrive_time + deal_time:
                                single_value = single_berth.wait_load_value[key]
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
                    return {
                        "best_berth_id": best_berth.id,
                        "best_deal_time": best_deal_time,
                        "best_value": best_value,
                        "leave_time": current_frame + best_berth.transport_time + best_deal_time,
                    }

    def search_next_berth(self, current_frame):
        """
        装满就走
        """
        if self.goods == self.num:
            return {"best_berth_id": -1}
        """
        判断返回虚拟点还是下一个泊位
        """
        best_berth_id, best_deal_time, best_value, leave_time = self.search_best_berth(current_frame,1).values()
        if self.values / self.berths[
            self.pos
        ].transport_time > (self.values+best_value) / (
            berth_move_between + best_deal_time + self.berths[best_berth_id].transport_time
        ):
            return {"best_berth_id": -1}
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
        best_berth_id, leave_time, add_goods = self.search_next_berth(
            current_frame
        ).values()
        if best_berth_id == -1:
            self.status = 3
            self.future_pos = -1
            self.arrive_time = current_frame + self.berths[self.pos].transport_time
            print("go", self.id)
        else:
            print("ship", self.id, best_berth_id)
            self.berths[best_berth_id].boat_arrive(self.id, add_goods)
            self.arrive_time = current_frame + self.berths[best_berth_id].transport_time
            self.leave_time = leave_time
            self.future_pos = best_berth_id

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
        match self.status:
            case 0:  # 船在虚拟点，需要前往泊位
                best_berth_id, leave_time,  = self.search_best_berth(
                    current_frame, 1
                ).values()
                print("ship", self.id, best_berth_id)
                self.berths[best_berth_id].boat_arrive(self.id)
                self.arrive_time = (
                    current_frame + self.berths[best_berth_id].transport_time
                )
                self.leave_time = leave_time
                self.future_pos = best_berth_id
            case 1:  # 船在前往泊位的途中（预留后续加入路径规划）
                if current_frame == self.arrive_time - 1:
                    self.status = 2
                    self.pos = self.future_pos
            case 2:  # 船在泊位上
                return
            case 3:  # 船在前往虚拟点的途中
                if current_frame == self.arrive_time - 1:
                    self.status = 0
                    self.pos = -1
                    self.goods = 0


# 测试代码
if __name__ == "__main__":
    boat = [Boat(i, 10, -1, 0) for i in range(10)]

    # for current_frame in range(15000):
    #     for single_boat in boat:
    # single_boat.next_step(current_frame, [Berth(j) for j in range(10)])
    # print("current_frame", i)
