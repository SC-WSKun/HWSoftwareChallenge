'''
记事本中的地图，字符所在的行列全部减一就是其在ch中的坐标

ch中点的坐标到其编号：number=i*n+j
点的编号到其ch中的坐标：i=number//n  j=number%n

船：
在x帧时，让船从虚拟点出发，假设到港口的距离是y，那么在帧x+y的时候，船会到达港口
在x帧时，假设此时船在海上，临时让船到另外一个港口去，假设虚拟点到港口的距离是y，那么在帧x+y的时候，船会到达港口
'''

import sys
import random
import numpy as np
from collections import deque

import pandas as pd
import time
from boat import Boat

n = 200
N = 210

robot_num = 10
berth_num = 10

money = 0
boat_capacity = 0  # 船的容积
id = 0

ch = np.empty((0, n), dtype='U1')

adjacency_table = {key: [] for key in range(n * n)}  # 整个地图的邻接表
gds = [[0 for _ in range(N)] for _ in range(N)]  # 记录物品的位置和分布


class Robot:
    def __init__(self, startX=0, startY=0, goods=0, status=0, mbx=0, mby=0):
        self.x = startX
        self.y = startY
        self.goods = goods  # 是否携带物品，0表示未携带物品，1表示携带物品
        self.status = status  # 状态，0表示恢复状态（不能走了），1表示正常状态（能走了）
        self.mbx = mbx
        self.mby = mby


robot = [Robot() for _ in range(robot_num + 10)]  # 机器人列表


class Berth:
    '''
    泊位类
    '''

    def __init__(self, x=0, y=0, transport_time=0, loading_speed=0):
        self.x = x
        self.y = y
        self.transport_time = transport_time  # 该泊位轮船运输到虚拟点的时间
        self.loading_speed = loading_speed  # 该泊位的装载速度
        self.land_x = None
        self.land_y = None
        self.all_path = None  # 字典，(land_x,land_y)到所有点的路径，key是点的编号（number），value是(land_x,land_y)到这个点的最短路径
        self.priority = None  # 优先级
        self.status = 0  # 0表示空闲，1表示有船在泊位上
        self.future_goods = {}  # 未来要装的货物



berth = [Berth() for _ in range(berth_num + 10)]  # 泊位列表




boat = [Boat() for _ in range(10)]






def get_adjacent_table():
    '''
    得到邻接表
    :return:
    '''
    global ch, adjacency_table
    # 上边
    for i in range(1, n):
        if ch[0][i] == '*' or ch[0][i] == '#':
            continue
        if ch[0][i - 1] == '.' or ch[0][i - 1] == 'A' or ch[0][i - 1] == 'B':
            adjacency_table[i].append(i - 1)
            adjacency_table[i - 1].append(i)
    # 左边
    for i in range(1, n):
        if ch[i][0] == '*' or ch[i][0] == '#':
            continue
        if ch[i - 1][0] == '.' or ch[i - 1][0] == 'A' or ch[i - 1][0] == 'B':
            adjacency_table[i * n].append((i - 1) * n)
            adjacency_table[(i - 1) * n].append(i * n)
    # 中间
    for i in range(1, n):  # 行
        for j in range(1, n):  # 列
            if ch[i][j] == '*' or ch[i][j] == '#':
                continue
            # 左边元素
            if ch[i][j - 1] == '.' or ch[i][j - 1] == 'A' or ch[i][j - 1] == 'B':
                adjacency_table[i * n + j].append(i * n + j - 1)
                adjacency_table[i * n + j - 1].append(i * n + j)
            # 上边元素
            if ch[i - 1][j] == '.' or ch[i - 1][j] == 'A' or ch[i - 1][j] == 'B':
                adjacency_table[i * n + j].append((i - 1) * n + j)
                adjacency_table[(i - 1) * n + j].append(i * n + j)
    adjacency_table = {key: value for key, value in adjacency_table.items() if len(value) > 0}  # 删除不和别的点相连的点


def bfs(graph, start, goal):
    '''
    广度优先遍历
    :param graph: 邻接表
    :param start: 起始点编号
    :param goal: 终点编号
    :return: 路径列表，路径长度，无路径则返回None和float('inf')
    '''
    # 用于记录每个节点的前驱节点，以便重构最短路径
    predecessors = {start: None}
    # 用于记录到各点的最短距离
    distance = {start: 0}
    # 创建一个队列用于存储待访问的节点及对应的距离
    queue = deque([start])

    # 当队列非空时进行遍历
    while queue:
        # 弹出队列中的当前节点
        current_node = queue.popleft()

        # 如果到达目标节点，开始重构最短路径并返回
        if current_node == goal:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = predecessors[current_node]
            return path[::-1], distance[goal]  # 返回路径和路径长度

        # 遍历当前节点的所有邻接节点
        for neighbor in graph[current_node]:
            # 如果邻接节点没有被访问过，则将其加入队列，并更新其前驱节点和距离
            if neighbor not in predecessors:
                queue.append(neighbor)
                predecessors[neighbor] = current_node
                distance[neighbor] = distance[current_node] + 1

    # 如果目标节点不可达，返回None
    return None, float('inf')


def find_all_paths(start):
    '''
    搜寻指定点到所有点的路径
    :param start: 指定点的编号
    :return: 返回一个字典，字典中的key表示地图中的某个点，value是一个列表，包含了start到key的最短路径
    '''
    global adjacency_table
    paths = {}  # 存储从起点到每个点的路径
    queue = deque([(start, [start])])  # 队列中存储当前节点及到当前节点的路径
    visited = {start}  # 已访问节点集合

    while queue:
        current_node, path = queue.popleft()
        paths[current_node] = path  # 更新路径信息

        for neighbor in adjacency_table[current_node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return paths


def berth_land_location():
    '''
    Berth()类中的(land_x,land_y)是最靠近陆地的点位，这个函数是为了得到这个点位
    :return:
    '''
    global berth, berth_num, adjacency_table
    for i in range(berth_num):
        berth[i].land_x = berth[i].x
        berth[i].land_y = berth[i].y
        if len(adjacency_table[(berth[i].x + 3) * n + berth[i].y]) > len(
                adjacency_table[(berth[i].land_x) * n + berth[i].land_y]):
            berth[i].land_x = berth[i].x + 3
            berth[i].land_y = berth[i].y
        if len(adjacency_table[(berth[i].x) * n + berth[i].y + 3]) > len(
                adjacency_table[(berth[i].land_x) * n + berth[i].land_y]):
            berth[i].land_x = berth[i].x
            berth[i].land_y = berth[i].y + 3
        if len(adjacency_table[(berth[i].x + 3) * n + berth[i].y + 3]) > len(
                adjacency_table[(berth[i].land_x) * n + berth[i].land_y]):
            berth[i].land_x = berth[i].x + 3
            berth[i].land_y = berth[i].y + 3

def set_berth_priority():
    '''
    求出每个泊位的优先级，并对泊位进行排序
    :return:
    '''
    global berth, berth_num
    for i in range(berth_num):
        # berth[i].priority = len(berth[i].future) / berth[i].loading_speed
        

def Init():
    '''
    1. 接收判题器传来的数据，并且在ch中记录地图等相关信息
    2. 得到邻接表
    3. 求出每个泊位的相对最佳放置点
    4. 对每个泊位的最佳放置点进行广度优先搜索，记录地图上每个点（海洋、障碍物除外）到这个最佳放置点的最短路径
    :return:
    '''
    global ch, adjacency_table, berth, berth_num, boat_capacity
    for _ in range(0, n):
        line = input()
        ch = np.append(ch, [np.fromiter(line, dtype='U1')], axis=0)
    for i in range(berth_num):  # 10个泊位
        line = input()  # id x y time velocity
        berth_list = [int(c) for c in line.split(sep=" ")]
        id = berth_list[0]
        berth[id].x = berth_list[1]
        berth[id].y = berth_list[2]
        berth[id].transport_time = berth_list[3]
        berth[id].loading_speed = berth_list[4]
    boat_capacity = int(input())
    okk = input()  # 初始化数据，以ok结束

    get_adjacent_table()
    berth_land_location()
    for i in range(berth_num):
        berth[i].all_path = find_all_paths(berth[i].land_x * n + berth[i].land_y)

    # df = pd.Series([end1 - start1, end2 - start2, end3 - start3, end4 - start4])
    # df.to_excel("output.xlsx", index=True)

    print("OK")  # 返回ok，告诉判题器比赛开始
    sys.stdout.flush()  # 每次print之后立即接一个这个


def Input():
    id, money = map(int, input().split(" "))
    num = int(input())
    for i in range(num):
        x, y, val = map(int, input().split())
        gds[x][y] = val
    for i in range(robot_num):
        robot[i].goods, robot[i].x, robot[i].y, robot[i].status = map(int, input().split())
    for i in range(5):
        boat[i].status, boat[i].pos = map(int, input().split())
    okk = input()
    return id


if __name__ == "__main__":
    Init()
    for zhen in range(15000):
        Input()
        if zhen == 0:
            print("ship", 0, 9)
            sys.stdout.flush()
        if zhen == 1220:
            print("go", 0)
            sys.stdout.flush()
        # if zhen == 500:
        #     print("ship", 0, 8)
        #     sys.stdout.flush()
        if zhen < 22:
            pass
        elif zhen >= 22 and zhen <= 35:
            print("move", 8, 1)
            sys.stdout.flush()
        elif zhen >= 36 and zhen <= 43:
            print("move", 8, 3)
            sys.stdout.flush()
            if zhen == 43:
                print("get", 8)
                sys.stdout.flush()
        elif zhen >= 44 and zhen <= 58:
            print("move", 8, 2)
            # print("pull", 8)
            sys.stdout.flush()
        elif zhen >= 59 and zhen <= 67:
            print("move", 8, 1)
            sys.stdout.flush()
            if zhen == 67:
                print("pull", 8)
                sys.stdout.flush()
        else:
            print("move", 8, 0)
            sys.stdout.flush()

        print("OK")
        sys.stdout.flush()
