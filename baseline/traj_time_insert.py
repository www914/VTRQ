import hashlib
import json

class Traj:
    def __init__(self, start_time, end_time, traj_hash, merge_hash = ""):
        self.start_time = start_time
        self.end_time = end_time
        self.traj_hash = traj_hash
        self.merge_hash = merge_hash


    def output_info(self):
        return f"开始时间: {self.start_time}, 结束时间: {self.end_time}, 轨迹哈希: {self.traj_hash}"


def traj_to_dict(traj):
        return {
            "start_time": traj.start_time,
            "end_time": traj.end_time,
            "traj_hash": traj.traj_hash,
            "merge_hash": traj.merge_hash
        }

def dict_to_traj(traj_data):
        return Traj(traj_data["start_time"], traj_data["end_time"], traj_data["traj_hash"], traj_data["merge_hash"])



#判断两个经纬度方框是否有交集
def rectangles_intersect(rect1, rect2):
    if rect1 != []:# 因为有的节点不是叶子节点，但他什么边也不存
        min_lng1, max_lng1 = rect1[0]
        min_lat1, max_lat1 = rect1[1]
        min_lng2, max_lng2 = rect2[0]
        min_lat2, max_lat2 = rect2[1]
        return not (max_lat1 <= min_lat2 or min_lat1 >= max_lat2 or max_lng1 <= min_lng2 or min_lng1 >= max_lng2)

def traj_timestamp_insert(node,traj,V):
    # 先计算这条轨迹所有点构成的最小矩形
    traj_point_list = []
    for v in V:
        if v.id in traj[0]:
            traj_point_list.append(v)
    # 计算当前节点所覆盖区域的最小纬度
    min_lat = min(v.lat for v in traj_point_list)
    # 计算当前节点所覆盖区域的最大纬度
    max_lat = max(v.lat for v in traj_point_list)
    # 计算当前节点所覆盖区域的最小经度
    min_lng = min(v.lng for v in traj_point_list)
    # 计算当前节点所覆盖区域的最大经度
    max_lng = max(v.lng for v in traj_point_list)
    border_lat = (min_lat,max_lat)
    border_lng = (min_lng,max_lng)
    # 这条轨迹的最小矩形边界范围
    rect_range = (border_lng, border_lat)

    time_insert_query(node,rect_range,traj)

# 更改后的范围查询函数   应该改成每一条边插入的轨迹的开始和结束时间都是一样的
def time_insert_query(node,rect_range,traj):


    if node is None:
        return
    node_rect = (node.border_lng, node.border_lat)
    # 轨迹最小范围和该区域没有交集
    if  not rectangles_intersect(node_rect, rect_range):
        return
    # 对于有交集的叶子节点要考虑边是否存在
    if node.is_leaf():
        # 轨迹在边表中的边
        for e in node.adjacent_list:

            # 从轨迹中拿出一条边
            i = -1
            for e1 in traj[1]:
                i = i + 1
                e1_start = e1[0]
                e1_end = e1[1]
                # 如果从轨迹中拿出来的一条边和列表中的这条边有重合证明轨迹经过这条边
                if (e.start.id == e1_start and e.end.id == e1_end) or (e.start.id == e1_end and e.end.id == e1_start):
                    # 这里写一个逻辑把这个轨迹插入这个边的列表下面  先创建一个轨迹对象  插入是按照开始时间顺序
                    if i != len(traj[1]) - 1:
                        start_time = traj[2][i][0][0]
                        end_time = traj[2][i+1][0][0]
                    else:
                        start_time = traj[2][i][0][0]
                        end_time = traj[2][i][-1][0]
                    traj_str = '->'.join(str(item) for item in traj[0])
                    # 找到轨迹总开始和结束的时间
                    traj_start_time = traj[2][0][0][0]
                    traj_end_time = traj[2][-1][-1][0]
                    traj_start_time_str = str(traj_start_time)
                    traj_end_time_str = str(traj_end_time)
                    str_time_traj = traj_str + traj_start_time_str + traj_end_time_str
                    encoded_data = str_time_traj.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    trajectory = Traj(start_time, end_time, hash_hex)

                    start_time_str = str(start_time)
                    end_time_str = str(end_time)
                    str_all = start_time_str + end_time_str + trajectory.traj_hash
                    encoded_data = str_all.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    trajectory.merge_hash = hash_hex
                    index = 0
                    while index < len(e.traj_hashList) and e.traj_hashList[index].start_time <= trajectory.start_time:
                        index = index + 1
                    e.traj_hashList.insert(index, trajectory)


    if not node.is_leaf():
        # 如果是分支节点考虑linking
        for e in node.linking:
            # 从轨迹中拿出一条边
            i = -1
            for e1 in traj[1]:
                i = i + 1
                e1_start = e1[0]
                e1_end = e1[1]
                # 如果从轨迹中拿出来的一条边和列表中的这条边有重合证明轨迹经过这条边
                if (e.start.id == e1_start and e.end.id == e1_end) or (e.start.id == e1_end and e.end.id == e1_start):
                    # 这里写一个逻辑把这个轨迹插入这个边的列表下面  先创建一个轨迹对象  插入是按照开始时间顺序
                    if i != len(traj[1]) - 1:
                        start_time = traj[2][i][0][0]
                        end_time = traj[2][i+1][0][0]
                    else:
                        start_time = traj[2][i][0][0]
                        end_time = traj[2][i][-1][0]
                    traj_str = '->'.join(str(item) for item in traj[0])
                    # 找到轨迹总开始和结束的时间
                    traj_start_time = traj[2][0][0][0]
                    traj_end_time = traj[2][-1][-1][0]
                    traj_start_time_str = str(traj_start_time)
                    traj_end_time_str = str(traj_end_time)
                    str_time_traj = traj_str + traj_start_time_str + traj_end_time_str
                    encoded_data = str_time_traj.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    trajectory = Traj(start_time, end_time, hash_hex)

                    start_time_str = str(start_time)
                    end_time_str = str(end_time)
                    str_all = start_time_str + end_time_str + trajectory.traj_hash
                    encoded_data = str_all.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    trajectory.merge_hash = hash_hex
                    index = 0
                    while index < len(e.traj_hashList) and e.traj_hashList[index].start_time <= trajectory.start_time:
                        index = index + 1
                    e.traj_hashList.insert(index, trajectory)

        time_insert_query(node.left, rect_range,traj)
        time_insert_query(node.right, rect_range,traj)

def insert_time_stamp(node,V):
    for i in range(1,4):
        traj_name_path = f"C:\\Users\\maoyusen\\Desktop\\Graph-Diffusion-Planning-main\\loader\\preprocess\\mm\\sets_data\\real2\\trajectories\\traj_mapped_xian_xian10-{i}.json"
        # 打开 JSON 文件
        with open(traj_name_path, 'r', encoding='utf-8') as file:
            # 解析 JSON 数据
            nested_list = json.load(file)
        j = 0
        for traj in nested_list:
            j = j + 1
            traj_timestamp_insert(node,traj,V)
            print(f"traj-10-{i}的第{j}条轨迹完成")
    # for i in range(1,31):
    #     traj_name_path = f"C:\\Users\\maoyusen\\Desktop\\Graph-Diffusion-Planning-main\\chengdu-tra-json\\traj-11-{i}.json"
    #     # 打开 JSON 文件
    #     with open(traj_name_path, 'r', encoding='utf-8') as file:
    #         # 解析 JSON 数据
    #         nested_list = json.load(file)
    #     j = 0
    #     for traj in nested_list:
    #         j = j + 1
    #         traj_timestamp_insert(node,traj,V)
    #         print(f"traj-11-{i}的第{j}条轨迹完成")

def update(node,V):
    j = 0
    for i in range(16,30):
        traj_name_path = f"C:\\Users\\maoyusen\\Desktop\\Graph-Diffusion-Planning-main\\loader\\preprocess\\mm\\sets_data\\real2\\trajectories\\traj_mapped_xian_xian10-{i}.json"
        # 打开 JSON 文件
        with open(traj_name_path, 'r', encoding='utf-8') as file:
            # 解析 JSON 数据
            nested_list = json.load(file)

        for traj in nested_list:
            if j == 5000:
                return
            j = j + 1
            traj_timestamp_insert(node,traj,V)
            print(f"traj-11-{i}的第{j}条轨迹完成")
# def insert_time_stamp11(node,V):
#     traj_set = set()
#
#     for i in range(1,2):
#         traj_name_path = f"traj-10-{i}.json"
#         # 打开 JSON 文件
#
#         with open(traj_name_path, 'r', encoding='utf-8') as file:
#             # 解析 JSON 数据
#             nested_list = json.load(file)
#         j = 0
#         for traj in nested_list:
#             flag = 0
#             j = j + 1
#
#             if j == 3144:
#                 flag = traj_timestamp_insert(node,traj,V)
#
#
#             print(f"10-{i}的第{j}条轨迹完成")
#     # print(tt)
