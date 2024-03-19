
class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        self.nums = [0 for i in range(15000)]
        self.boat = None # 最快到达港口的船
        self.status = 0 #0没有船要过来，1有船正在泊位上或者将要过来
    def robort_pull(self,time):#机器人放置物品到码头，time是机器人到达的时间，value是机器人带来的价值
        self.nums[time:]+=1

    
    def boat_load(self,current_time): #每帧执行
        if(self.boat==None): #当前没有船要到达该码头
            return
        if(current_time>=self.boat.leave_time):
            if(self.boat_leave(max(current_time,self.boat.leave_time))):
                return #船离开结束boat_load
            #船没有离开，继续装货
            nums_arr = self.nums[current_time]
            load_nums = self.boat.load_goods(min(nums_arr,self.loading_speed))
            self.nums[self.current_time:]-=load_nums



    def boat_leave(self,current_time):
        if(self.nums[current_time]==0 or self.boat.is_full()):
            self.boat.leave_berth(self, current_time)
            self.boat=None
            self.status = 0
            return True
        return False
    
    def boat_arive(self,boat_id):
        self.boat = boat[boat_id]
        self.status = 1



