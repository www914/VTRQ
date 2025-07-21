# import csv
# import hashlib
#
#
# def insert_time_stamp(node,V):
#     for i in range(1,62):
#         traj_name_path = f"C:\\Users\\maoyusen\\Desktop\\Graph-Diffusion-Planning-main\\traj\\traj-{i}.json"
#         # 打开 JSON 文件
#
#         with open(traj_name_path, 'r', encoding='utf-8') as file:
#             # 解析 JSON 数据
#             nested_list = json.load(file)
#         j = 0
#         for traj in nested_list:
#             j = j + 1
#             id_origin(traj, V)
#             print(f"traj-{i}的第{j}条轨迹完成")
#
# def id_origin(traj, V):
#     global v_lng, v_lat
#     traj_str = '->'.join(str(item) for item in traj[0])
#     traj_start_time = traj[2][0][0][0]
#     traj_end_time = traj[2][-1][-1][0]
#     traj_start_time_str = str(traj_start_time)
#     traj_end_time_str = str(traj_end_time)
#     str_time_traj = traj_str + traj_start_time_str + traj_end_time_str
#     encoded_data = str_time_traj.encode('utf-8')
#     hash_object = hashlib.sha256(encoded_data)
#     # 把traj_id作为轨迹的id
#     traj_id = hash_object.hexdigest()
#     i = -1
#     list_traj_point = []
#     for v in traj[0]:
#         i = i + 1
#         for vertex in V:
#             if vertex.id == v:
#                 v_lng = vertex.lng
#                 v_lat = vertex.lat
#                 break
#         if i != len(traj[0]) - 1:
#             v_time = traj[2][i][0][0]
#             traj_tuple = (v, v_lng, v_lat, v_time)
#             list_traj_point.append(traj_tuple)
#         else:
#             v_time = traj[2][i-1][-1][0]
#             traj_tuple = (v, v_lng, v_lat, v_time)
#             list_traj_point.append(traj_tuple)


import csv
import json
import hashlib
import os


def idtraj(V):
    csv_file = "trajectories_xian.csv"

    # 检查并创建CSV文件头
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['traj_id', 'points_data'])

    for i in range(1, 32):
        traj_name_path = f"C:\\Users\\maoyusen\\Desktop\\Graph-Diffusion-Planning-main\\loader\\preprocess\\mm\\sets_data\\real2\\trajectories\\traj_mapped_xian_xian10-{i}.json"

        try:
            with open(traj_name_path, 'r', encoding='utf-8') as file:
                nested_list = json.load(file)
        except Exception as e:
            print(f"Error loading {traj_name_path}: {e}")
            continue

        j = 0
        for traj in nested_list:
            j += 1
            traj_id, list_traj_point = id_origin(traj, V)
            write_to_csv(traj_id, list_traj_point, csv_file)
            print(f"traj-{i}的第{j}条轨迹完成")


def id_origin(traj, V):
    global v_lng, v_lat
    traj_str = '->'.join(str(item) for item in traj[0])
    traj_start_time = traj[2][0][0][0]
    traj_end_time = traj[2][-1][-1][0]
    traj_start_time_str = str(traj_start_time)
    traj_end_time_str = str(traj_end_time)
    str_time_traj = traj_str + traj_start_time_str + traj_end_time_str
    encoded_data = str_time_traj.encode('utf-8')
    hash_object = hashlib.sha256(encoded_data)
    traj_id = hash_object.hexdigest()

    i = -1
    list_traj_point = []
    for v in traj[0]:
        i += 1
        for vertex in V:
            if vertex.id == v:
                v_lng = vertex.lng
                v_lat = vertex.lat
                break
        if i != len(traj[0]) - 1:
            v_time = traj[2][i][0][0]
            traj_tuple = (v, v_lng, v_lat, v_time)
            list_traj_point.append(traj_tuple)
        else:
            v_time = traj[2][i - 1][-1][0]
            traj_tuple = (v, v_lng, v_lat, v_time)
            list_traj_point.append(traj_tuple)

    return traj_id, list_traj_point


def write_to_csv(traj_id, list_traj_point, csv_file):
    # 将 list_traj_point 序列化为 JSON 字符串
    points_json = json.dumps(list_traj_point)

    # 追加到 CSV 文件
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([traj_id, points_json])



