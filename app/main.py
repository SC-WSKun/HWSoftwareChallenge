"""
生成列表的速度，numpy快，调用列表元素的速度，list快

记事本中的地图，字符所在的行列全部减一就是其在ch中的坐标

ch中点的坐标到其编号：number=i*n+j
点的编号到其ch中的坐标：i=number//n  j=number%n

假设货物在22帧出现，那么它会存在1000帧，1022帧会消失。货物初始生命为1000，机器人到它的距离<=货物生命值就可以

修改机器人路径的话，物品的tag和港口的future_goods都要修改

船：
在x帧时，让船从虚拟点出发，假设到港口的距离是y，那么在帧x+y的时候，船会到达港口
在x帧时，假设此时船在海上，临时让船到另外一个港口去，假设虚拟点到港口的距离是y，那么在帧x+y的时候，船会到达港口
"""

import sys
import random
import numpy as np
from collections import deque  # 队列
from Boat import Boat
from Berth import Berth

n = 200  # 地图的边长
N = 210  # 不重要

robot_num = 10  # 机器人的数量
berth_num = 10  # 港口的数量

boat_capacity = 0  # 船的容积
id = 1  # 当前的帧数，最新版的判题器是1到15000帧

ch = np.empty((0, n), dtype="U1")  # 二维列表组成的地图

adjacency_table = {key: [] for key in range(n * n)}  # 整个地图的邻接表

"""
从一个点移动到另一个点，假设前一个点的编号（是编号不是坐标）是a，后一个点的编号是b，a移动到b
b-a=-n，则print("move", index, 2)
b-a=-1，则print("move", index, 1)
b-a=1，则print("move", index, 0)
b-a=n，则print("move", index, 3)
"""
movement_direction = {-n: 2, -1: 1, 1: 0, n: 3}


class Goods:
    def __init__(self, x, y, value):
        self.x = x  # 货物的横坐标
        self.y = y  # 货物的纵坐标
        self.value = value  # 货物价值
        self.life = 1000  # 货物剩余生命值，如果货物正在被搬运，则不扣生命值
        self.reserve = False  # 货物是否被机器人选中
        self.is_carried = False  # 是否正在被机器人搬运


goods = []  # 记录场上的所有货物，这个列表里都是Goods对象
new_goods = []  # 新增货物，列表中每个元素由列表[x, y, val]构成，分别代表货物的横纵坐标和价值


class Robot:
    def __init__(self, startX=0, startY=0, goods=0, status=1, targetX=-1, targetY=-1):
        self.x = startX  # 横坐标
        self.y = startY  # 纵坐标
        self.goods = goods  # 是否携带物品，0表示未携带物品，1表示携带物品
        self.status = status  # 状态，0表示恢复状态（不能走了），1表示正常状态（能走了）
        # 当目标点坐标为(-1,-1)且路径为空列表时，表示当前没有目标，需要指定新的目标
        # 目标点可以是货物，也可以是港口，目标货物价值就是机器人准备搬运或者正在搬运的物品价值
        self.path = []  # 机器人的路径规划，包含机器人到物品以及物品到港口的所有点，第一个元素是机器人所在的点编号，最后一个元素是港口左上角的点编号
        self.targetX = targetX  # 目标点x坐标
        self.targetY = targetY  # 目标点x坐标
        self.targetValue = 0  # 目标货物价值
        self.berth_id = -1
    
    def choose_berth(self):
        pos_id = self.x*n+self.y
        flag = 1 #当前不能够容忍的选择数
        min_num = 40000
        min_id = -1
        while(min_id==-1):
            for b in berth:
                if(b.robots_nums>=flag):
                    continue
                if(pos_id not in b.all_path.keys()):
                    continue
                if(min_num>len(b.all_path[pos_id])):
                    min_num = len(b.all_path[pos_id])
                    min_id = b.id
            flag+=1
        Berth[min_id].robots_nums+=1
        self.berth_id=min_id
        
        
                




global robot 
robot = [Robot() for _ in range(robot_num)] # 机器人列表


def get_adjacent_table():
    """
    得到邻接表，这个经过测试没问题，不用检查
    :return:
    """
    global ch, adjacency_table
    # 上边
    for i in range(1, n):
        if ch[0][i] == "*" or ch[0][i] == "#":
            continue
        if ch[0][i - 1] == "." or ch[0][i - 1] == "A" or ch[0][i - 1] == "B":
            adjacency_table[i].append(i - 1)
            adjacency_table[i - 1].append(i)
    # 左边
    for i in range(1, n):
        if ch[i][0] == "*" or ch[i][0] == "#":
            continue
        if ch[i - 1][0] == "." or ch[i - 1][0] == "A" or ch[i - 1][0] == "B":
            adjacency_table[i * n].append((i - 1) * n)
            adjacency_table[(i - 1) * n].append(i * n)
    # 中间
    for i in range(1, n):  # 行
        for j in range(1, n):  # 列
            if ch[i][j] == "*" or ch[i][j] == "#":
                continue
            # 左边元素
            if ch[i][j - 1] == "." or ch[i][j - 1] == "A" or ch[i][j - 1] == "B":
                adjacency_table[i * n + j].append(i * n + j - 1)
                adjacency_table[i * n + j - 1].append(i * n + j)
            # 上边元素
            if ch[i - 1][j] == "." or ch[i - 1][j] == "A" or ch[i - 1][j] == "B":
                adjacency_table[i * n + j].append((i - 1) * n + j)
                adjacency_table[(i - 1) * n + j].append(i * n + j)
    adjacency_table = {
        key: value for key, value in adjacency_table.items() if len(value) > 0
    }  # 删除不和别的点相连的点


def bfs(start, goal):
    """
    广度优先遍历，gpt4写的，也没问题
    :param start: 起始点编号
    :param goal: 终点编号
    :return: 路径列表，路径长度，无路径则返回None和float('inf')
    """
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
        for neighbor in adjacency_table[current_node]:
            # 如果邻接节点没有被访问过，则将其加入队列，并更新其前驱节点和距离
            if neighbor not in predecessors:
                queue.append(neighbor)
                predecessors[neighbor] = current_node
                distance[neighbor] = distance[current_node] + 1

    # 如果目标节点不可达，返回None
    return None, float("inf")


def find_all_paths(start):
    """
    搜寻指定点到所有点的路径，这个用来处理港口的all_path字典
    :param start: 指定点的编号
    :return: 返回一个字典，字典中的key表示地图中的某个点，value是一个列表，包含了start到key的最短路径
    """
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


def C_to_N(i, j):
    """
    点坐标转换成点编号
    :param i:
    :param j:
    :return:
    """
    return i * n + j


def N_to_C(number):
    """
    点编号转换成点坐标
    :param number:
    :return:返回一个元组，第一个元素是横坐标，第二个元素是纵坐标
    """
    return number // n, number % n


def Robot_Distance(index, i, j):
    """

    :param index:机器人索引
    :param i:物品横坐标
    :param j:物品纵坐标
    :return: 返回index索引的机器人运送坐标为(i,j)货物的路径和所需要的距离
    """
    path1, distance1 = bfs(C_to_N(robot[index].x, robot[index].y), C_to_N(i, j))
    if path1 == None:  # 找不到路径
        return [], float("inf")
    try:
        path2 = berth[index].all_path[C_to_N(i, j)]
        path2.pop()
        path2 = path2[::-1]
    except:  # 港口与物品之间不连通
        return [], float("inf")
    # 连通
    return path1 + path2, distance1 + len(path2)


# def berth_land_location():
#     '''
#     Berth()类中的(land_x,land_y)是最靠近陆地的点位，这个函数是为了得到这个点位
#     :return:
#     '''
#     global berth
#     for i in range(berth_num):
#         berth[i].land_x = berth[i].x
#         berth[i].land_y = berth[i].y
#         if len(adjacency_table[(berth[i].x + 3) * n + berth[i].y]) > len(
#                 adjacency_table[(berth[i].land_x) * n + berth[i].land_y]):
#             berth[i].land_x = berth[i].x + 3
#             berth[i].land_y = berth[i].y
#         if len(adjacency_table[(berth[i].x) * n + berth[i].y + 3]) > len(
#                 adjacency_table[(berth[i].land_x) * n + berth[i].land_y]):
#             berth[i].land_x = berth[i].x
#             berth[i].land_y = berth[i].y + 3
#         if len(adjacency_table[(berth[i].x + 3) * n + berth[i].y + 3]) > len(
#                 adjacency_table[(berth[i].land_x) * n + berth[i].land_y]):
#             berth[i].land_x = berth[i].x + 3
#             berth[i].land_y = berth[i].y + 3


def Init():
    """
    1. 接收判题器传来的数据，并且在ch中记录地图等相关信息
    2. 得到邻接表
    3. 对每个泊位的左上角点进行广度优先搜索，记录地图上每个点（海洋、障碍物除外）到这个最佳放置点的最短路径
    :return:
    """
    global ch, berth, boat_capacity, boat
    for _ in range(0, n):  # 得到判题器的地图
        line = input()
        ch = np.append(ch, [np.fromiter(line, dtype="U1")], axis=0)
    for i in range(berth_num):  # 10个泊位
        line = input()  # id x y time velocity
        berth_list = [int(c) for c in line.split(sep=" ")]
        id = berth_list[0]
        berth.append(
            Berth(
                id=i,
                x=berth_list[1],
                y=berth_list[2],
                transport_time=berth_list[3],
                loading_speed=berth_list[4],
            )
        )
        # berth[id].x = berth_list[1]
        # berth[id].y = berth_list[2]
        # berth[id].transport_time = berth_list[3]
        # berth[id].loading_speed = berth_list[4]
    boat_capacity = int(input())
    # 这里写船的初始化
    boat = [Boat(i, boat_capacity, -1) for i in range(5)]

    okk = input()  # 初始化数据，以ok结束

    get_adjacent_table()

    for i in range(berth_num):  # 处理港口的all_path
        berth[i].all_path = find_all_paths(berth[i].x * n + berth[i].y)

    print("OK")  # 返回ok，告诉判题器比赛开始
    sys.stdout.flush()  # 每次print之后立即接一个这个


def Input():
    global id, goods
    id, money = map(int, input().split(" "))
    num = int(input())  # 新增货物数量
    for i in range(num):  # 新增货物信息被存放在了goods和new_goods中
        x, y, val = map(int, input().split())
        new_goods.append([x, y, val])  # 记录此帧的新增货物
        G = Goods(x, y, value=val)
        goods.append(G)  # 把货物放到goods列表里面
    for i in range(robot_num):
        robot[i].goods, robot[i].x, robot[i].y, robot[i].status = map(
            int, input().split()
        )
    for i in range(5):
        input()  # 船的信息，暂时不需要
        continue
        boat[i].status, boat[i].pos = map(int, input().split())
    okk = input()


def life_minus_one():
    """
    货物生命减1，然后再把生命为0的删除掉，然后清空new_goods
    :return:
    """
    global goods, new_goods
    for G in goods:  # 所有货物生命值减1
        if G.is_carried == False:
            G.life -= 1
    goods = [G for G in goods if G.life > 0]  # 生命值不为0的货物保留下来
    new_goods = []  # 清空new_goods


def Cargo_handling():
    """
    处理新增货物
    :return:
    """
    for new_cargo in new_goods:  # 对当前这个新增货物进行虚拟的分配
        # 这个for循环存在的意义就是判断当前的新增货物分配给谁性价比最高，或者谁都不分配
        gain = 0  # 当前增益
        robot_number = -1  # 这个货物分配给哪个机器人
        path = []  # 机器人拿去这个货物然后去港口的路径
        flag = False  # flag=True表示机器人要舍弃原来的货物，flag=False表示机器人不需要舍弃货物（机器人可能把原来的货物放弃然后选择新的货物）
        G = None  # 被丢弃的那个货物，Goods对象
        for i in range(robot_num):  # 遍历所有的机器人
            if robot[i].status == 0:  # 机器人不能动
                continue
            new_path, new_distance = Robot_Distance(i, new_cargo[0], new_cargo[1])
            if new_distance == float("inf"):  # 无路径，不连通，直接continue
                continue
            if robot[i].goods == 1:  # 当前机器人有货物
                for j in goods:  # 找到需要舍弃的货物
                    if j.x == robot[i].targetX and j.y == robot[i].targetY:
                        G = j
                        break
                new_gain = new_cargo[2] / new_distance - G.value / (
                    len(robot[i].path) - 1
                )  # 计算如果抛弃当前货物的话有多少增益
                if new_gain > gain:  # 新增益更大
                    gain = new_gain
                    robot_number = i
                    path = new_path
                    flag = True
            if robot[i].goods == 0:  # 当前机器人没有货物
                new_gain = new_cargo[2] / new_distance
                if new_gain > gain:  # 新增益更大
                    gain = new_gain
                    robot_number = i
                    path = new_path
                    flag = False
        if robot_number == -1:  # 货物没有被分配给任何机器人
            continue
        if flag == True:  # 机器人需要舍弃货物
            G.reserve = False
        # 机器人
        robot[robot_number].path = path
        robot[robot_number].targetX = new_cargo[0]
        robot[robot_number].targetY = new_cargo[1]
        robot[robot_number].targetValue = new_cargo[2]
        # 物品
        for j in goods:  # 在goods当中找到那个被分配的新增货物
            if j.x == new_cargo[0] and j.y == new_cargo[1]:
                j.reserve = True  # 标识一下这个货物已经被某个机器人看上了
                break
        # 港口

        # berth[robot_number].future_goods[robot_number] = [id + len(path) - 2, new_cargo[2]]
        berth[robot_number].robot_pull(id + len(path) - 2, new_cargo[2])


def Robot_have_goods(index):
    """
    机器人手上有货物的情况
    :param index:机器人的编号
    :return:
    """
    for i in range(
        robot_num
    ):  # robot[index].path[1]记录的是当前这个机器人要走的下一个地方，这个for循环用于判断能不能按照既定路线移动
        if N_to_C(robot[index].path[1]) == (robot[i].x, robot[i].y):
            break
    else:  # 能移动
        print(
            "move",
            index,
            movement_direction[robot[index].path[1] - robot[index].path[0]],
        )
        sys.stdout.flush()
        robot[index].path.pop(0)
        robot[index].x, robot[index].y = N_to_C(robot[index].path[0])
        if ch[robot[index].x][robot[index].y] == "B":  # 到港口了
            print("pull", index)
            sys.stdout.flush()
            G = None
            for g in goods:  # 找到要放下的货物
                if g.x == robot[index].targetX and g.y == robot[index].y:
                    G = g
                    break
            # 处理港口

            # berth[index].total_goods.append(G)
            # berth[index].total_values += G.value
            # del berth[index].future_goods[index]

            # 处理物品
            goods.remove(G)
            # 处理机器人
            robot[index].goods = 0
            robot[index].path = []
            robot[index].targetX = robot[index].targetY = -1
            robot[index].targetValue = 0
        return
    # 不能移动
    direction = [
        robot[index].path[0] - n,
        robot[index].path[0] - 1,
        robot[index].path[0] + 1,
        robot[index].path[0] + n,
    ]
    direction.remove(robot[index].path[1])
    tag = False  # 如果以下的while循环是通过break跳出的，则tag=True，如果是正常跳出的，tag=False，两种跳出while循环的方式决定了不同的处理
    while direction != []:  # 检验另外三个方向还能不能走，能走就走
        a = random.choice(direction)  # 随机往一个方向走，a是接下来要走的编号
        direction.remove(a)
        coordinate_x, coordinate_y = N_to_C(a)  # 接下来要走的坐标
        if (
            ch[coordinate_x][coordinate_y] == "*"
            or ch[coordinate_x][coordinate_y] == "#"
        ):  # 海洋和障碍不能走
            continue
        for i in range(robot_num):  # 检验如果那样走的话会不会和别的机器人碰撞
            if (coordinate_x, coordinate_y) == (robot[i].x, robot[i].y):
                break
        else:  # 可以往a这个地方走
            print("move", index, movement_direction[a - robot[index].path[0]])
            sys.stdout.flush()
            robot[index].x, robot[index].y = coordinate_x, coordinate_y
            robot[index].path = berth[index].all_path[
                C_to_N(robot[index].x, robot[index].y)
            ][::-1]
            # berth[index].future_goods[index][0] = id + len(robot[index].path) - 1
            berth[index].robot_undo(id + len(robot[index].path) - 1)
            tag = True
            break
    if (
        tag == False
    ):  # 说明机器人没有移动，此帧静止，那么只需要改变港口中的future_goods就可以了
        # berth[index].future_goods[index][0] += 1
        berth[index].robot_undo(boat[index].robort_arrive_time + 1)


def Robot_donot_have_goods(index):
    for i in range(
        robot_num
    ):  # robot[index].path[1]记录的是当前这个机器人要走的下一个地方
        if N_to_C(robot[index].path[1]) == (robot[i].x, robot[i].y):
            break
    else:  # 能移动
        print(
            "move",
            index,
            movement_direction[robot[index].path[1] - robot[index].path[0]],
        )
        sys.stdout.flush()
        robot[index].path.pop(0)
        robot[index].x, robot[index].y = N_to_C(robot[index].path[0])
        if (
            robot[index].x == robot[index].targetX
            and robot[index].y == robot[index].targetY
        ):  # 货物在脚下
            print("get", index)
            sys.stdout.flush()
            G = None
            for g in goods:
                if g.x == robot[index].targetX and g.y == robot[index].targetY:
                    G = g
                    break
            G.is_carried = True
            robot[index].targetX = berth[index].x
            robot[index].targetY = berth[index].y
            robot[index].goods = 1
        return
    # 不能移动
    direction = [
        robot[index].path[0] - n,
        robot[index].path[0] - 1,
        robot[index].path[0] + 1,
        robot[index].path[0] + n,
    ]
    direction.remove(robot[index].path[1])
    tag = False  # 如果以下的while循环是通过break跳出的，则tag=True，如果是正常跳出的，tag=False
    while direction != []:  # 检验另外三个方向还能不能走，能走就走
        a = random.choice(direction)  # 随机往一个方向走，a是接下来要走的编号
        direction.remove(a)
        coordinate_x, coordinate_y = N_to_C(a)  # 接下来要走的坐标
        if (
            ch[coordinate_x][coordinate_y] == "*"
            or ch[coordinate_x][coordinate_y] == "#"
        ):  # 海洋和障碍不能走
            continue
        for i in range(robot_num):  # 检验如果那样走的话会不会和别的机器人碰撞
            if (coordinate_x, coordinate_y) == (robot[i].x, robot[i].y):
                break
        else:  # 可以往a这个地方走
            print("move", index, movement_direction[a - robot[index].path[0]])
            sys.stdout.flush()
            robot[index].x, robot[index].y = coordinate_x, coordinate_y
            path, distance = Robot_Distance(
                index, robot[index].targetX, robot[index].targetY
            )
            G = None  # 用G来存储当前机器人原本打算取的货物
            for g in goods:
                if g.x == robot[index].targetX and g.y == robot[index].y:
                    G = g
                    break
            if distance <= G.life:  # 还能继续拿这个货物
                robot[index].path = path  # 机器人更新路径
                # berth[index].future_goods[index][0] += 2    # 通知港口晚两帧到
                berth[index].robot_undo(berth[index].robot_arrive_time + 2)
            else:  # 拿不了这个货物了，机器人变成无目标货物状态
                G.reserve = False
                robot[index].path = []
                robot[index].targetX = robot[index].targetY = -1
                robot[index].targetValue = 0
                # del berth[index].future_goods[index]
                berth[index].robot_undo(-1)
            tag = True
            break
    if tag == False:  # 这个机器人在这一帧动不了，接下来判断原本的货物能不能拿
        G = None  # 用G来存储当前机器人原本打算取的货物
        for g in goods:  # 找到原本要拿的货物
            if g.x == robot[index].targetX and g.y == robot[index].y:
                G = g
                break
        if len(robot[index].path) <= G.life - 1:
            # berth[index].future_goods[index][0] += 1  # 通知港口晚一帧到
            berth[index].robot_undo(berth[index].robot_arrive_time + 1)
        else:  # 拿不了这个货物了，机器人变成无目标货物状态
            G.reserve = False
            robot[index].path = []
            robot[index].targetX = robot[index].targetY = -1
            robot[index].targetValue = 0
            # del berth[index].future_goods[index]
            berth[index].robot_undo(-1)


def Robot_control(index):
    if robot[index].status == 0:  # 机器人处于恢复状态，动不了
        robot[index].targetX = robot[index].targetY = -1
        robot[index].path = []
        # 还要对港口进行操作，我没写，因为目前来看应该不会碰撞
        return
    if robot[index].goods == 0:  # 无货物
        if (
            robot[index].path == []
            and robot[index].targetX == -1
            and robot[index].targetY == -1
        ):  # 无目标货物
            target_good = [
                0,
                -1,
                -1,
            ]  # 可能存在的目标货物，三个元素分别是：价值/将其送到港口需要的距离、物品横坐标、物品纵坐标
            final_path = []  # 拿取这个目标货物要走的路径
            final_distance = 0  # 拿取这个目标货物要走的路程
            good_index = None  # 货物的索引
            for i, G in enumerate(goods):
                if G.reserve == False:  # 这个货物没有被选中
                    path, distance = Robot_Distance(index, G.x, G.y)
                    if distance == float("inf"):  # 无法到达这个货物，不连通
                        continue
                    if (
                        G.value / distance > target_good[0]
                    ):  # 拿取这个货物G性价比更高，把相关信息记录下来
                        target_good[0] = G.value / distance
                        target_good[1] = G.x
                        target_good[2] = G.y
                        final_path = path
                        final_distance = distance
                        good_index = i
            if target_good[0] == 0:  # 搜寻不到合适的货物，这个机器人此帧不动
                return
            # 搜寻到了合适的货物
            # 机器人
            robot[index].path = final_path
            robot[index].targetValue = target_good[0]
            robot[index].targetX = target_good[1]
            robot[index].targetY = target_good[2]
            # 物品
            goods[good_index].reserve = True
            # 港口
            berth[index].future_goods[index] = [
                id + final_distance - 1,
                goods[good_index].value,
            ]
            # berth[index].robot_pull(id+final_distance-1)
            if (
                robot[index].x == robot[index].targetX
                and robot[index].y == robot[index].targetY
            ):  # 货物就在机器人脚下
                print("get", index)
                sys.stdout.flush()
                G = None
                for g in goods:  # 在goods中找到被拿取的货物
                    if g.x == robot[index].targetX and g.y == robot[index].targetY:
                        G = g
                        break
                G.is_carried = True
                robot[index].goods = 1
                robot[index].targetX = berth[index].x
                robot[index].targetY = berth[index].y
                Robot_have_goods(index)
            else:  # 货物不在机器人脚下
                Robot_donot_have_goods(index)
        else:  # 有目标货物
            Robot_donot_have_goods(index)
    else:  # 有货物
        Robot_have_goods(index)


if __name__ == "__main__":
    Init()
    for zhen in range(1, 15001):
        life_minus_one()
        Input()
        Cargo_handling()
        for index in range(robot_num):
            if(zhen==1):
                robot[index].choose_berth()
            Robot_control(index)

        # 船先决策，港口最后决策
        for single_boat in boat:
            single_boat.next_step(zhen, berth)

        for single_berth in berth:
            single_berth.boat_load(zhen)

        print("OK")
        sys.stdout.flush()
