
class Berth:
    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        self.nums = [0 for i in range(15000)]
        self.boat = None # 最快到达港口的船
        self.status = 0 #0没有船要过来，1有船正在泊位上或者将要过来
        self.robort_arrive_time = -1 #机器人到达的时间
        self.all_path = {}  # 字典，(x,y)到所有点的路径，key是点的编号（number），value是(x,y)到这个点的最短路径，不连通的key不会出现在all_path中
        # 这个路径记录的是港口到点的路径，机器人要使用这个路径的话得对value进行逆转，即[::-1]

    def robort_pull(self,time):#机器人放置物品到码头，time是机器人到达的时间
        self.nums[time:]+=1
        self.robort_arrive_time = time

    def robort_undo(self,time=-1):
        # -1 表示当前机器人放弃计划后，暂时没有去拿货物
        self.nums[self.robort_arrive_time:]-=1
        if(time!=-1):
            self.nums[self.time:]+=1
        self.robort_arrive_time=time

    
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



