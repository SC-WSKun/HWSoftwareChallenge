class Boat:
    def __init__(self, id=0 ,num=0, pos=0, status=0):
        self.id = id
        self.num = num # 轮船的载货量
        self.goods = 0 # 轮船的当前货物量
        self.pos = pos  # 处在哪个泊位，虚拟点则为-1
        self.future_pos = None # 下一个位置
        self.arrive_time = 0  # 下一个位置的到达时间
        '''
        船的状态
        0: 船在虚拟点
        1: 船在前往泊位的途中
        2: 船在泊位上
        3: 船在前往虚拟点的途中
        '''
        self.status = status
class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        self.nums = [0 for i in range(15000)]
        # self.t = 0 #当前时间
        self.boat = None # 最快到达港口的船
    def robort_pull(self,time):#机器人放置物品到码头，time是机器人到达的时间，value是机器人带来的价值
        self.nums[time:]+=1

    def boat_load(self,boat): #每一帧做个判断实时维护
        if(boat==None): #当前没有船要到达该码头
            return
        if(self.boat.goods==self.boat.num): #船已经被预先决策装满了，不必再校正goods和nums
            return
        max_load = self.boat.num-self.boat.goods #船还剩的最大装货量
        nums_arr = self.nums[self.boat.arrive_time]
        if(max_load>=nums_arr):
            self.nums[self.boat.arrive_time:]-=nums_arr
            self.boat.goods+=nums_arr
        else:#轮船装满
            self.nums[self.boat_arive_time]-=max_load
            self.boat.goods=self.nums 


    def boat_leave(self):
        self.bota=None
    def boat_arive(self,boat):
        self.boat = boat



