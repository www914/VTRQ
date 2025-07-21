import csv
import ast
import hashlib

from hash_collect import first_vo_hash_collect2, first_vo_hash_collect1, edge_vo_hash, second_vo_hash_collect_find, \
    no_edge_vo_hash


def orientation(p, q, r):
    """
    此函数用于判断三个点 p, q, r 的方向关系。
    通过计算向量叉积来确定三点的相对位置，结果可以是共线、顺时针或逆时针。
    :param p: 第一个点，格式为 (x, y)
    :param q: 第二个点，格式为 (x, y)
    :param r: 第三个点，格式为 (x, y)
    :return: 0 表示共线，1 表示顺时针，2 表示逆时针
    """
    # 计算向量叉积
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0
    elif val > 0:
        return 1
    return 2


def on_segment(p, q, r):
    """
    判断点 q 是否在线段 pr 上。
    通过比较点 q 的坐标是否在 p 和 r 的坐标范围之内来判断。
    :param p: 线段的一个端点，格式为 (x, y)
    :param q: 待判断的点，格式为 (x, y)
    :param r: 线段的另一个端点，格式为 (x, y)
    :return: 如果点 q 在线段 pr 上返回 True，否则返回 False
    """
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))


def do_intersect(p1, q1, p2, q2):
    """
    判断两条线段 p1q1 和 p2q2 是否相交。
    先通过 orientation 函数判断点的方向关系，再处理共线且重叠的特殊情况。
    :param p1: 第一条线段的一个端点，格式为 (x, y)
    :param q1: 第一条线段的另一个端点，格式为 (x, y)
    :param p2: 第二条线段的一个端点，格式为 (x, y)
    :param q2: 第二条线段的另一个端点，格式为 (x, y)
    :return: 如果两条线段相交返回 True，否则返回 False
    """
    # 计算四个方向值，用于判断点的相对位置
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # 正常相交情况：两条线段的端点分别在对方线段所在直线的两侧
    if o1 != o2 and o3 != o4:
        return True

    # 处理共线且重叠的特殊情况
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False


def segment_intersects_rect(segment, rect):
    """
    判断线段是否与矩形相交。
    将矩形的四条边分别与线段进行相交判断。
    :param segment: 线段，格式为 ((x1, y1), (x2, y2))
    :param rect: 矩形，格式为 ((x_min, y_min), (x_max, y_max))
    :return: 若相交返回 True，否则返回 False
    """
    # 提取矩形的左下角和右上角坐标
    x_min, y_min = rect[0]
    x_max, y_max = rect[1]
    # 提取线段的两个端点
    p1, q1 = segment
    # 定义矩形的四条边
    rect_edges = [
        ((x_min, y_min), (x_max, y_min)),  # 底边
        ((x_max, y_min), (x_max, y_max)),  # 右边
        ((x_max, y_max), (x_min, y_max)),  # 顶边
        ((x_min, y_max), (x_min, y_min))  # 左边
    ]
    # 遍历矩形的四条边，判断线段与每条边是否相交
    for rect_edge in rect_edges:
        p2, q2 = rect_edge
        if do_intersect(p1, q1, p2, q2):
            return True
    return False



#判断两个经纬度方框是否有交集
def rectangles_intersect(rect1, rect2):
    if rect1 != []:# 因为有的节点不是叶子节点，但他什么边也不存
        min_lat1, max_lat1 = rect1[1]
        min_lng1, max_lng1 = rect1[0]
        min_lat2, max_lat2 = rect2[1]
        min_lng2, max_lng2 = rect2[0]
        return not (max_lat1 <= min_lat2 or min_lat1 >= max_lat2 or max_lng1 <= min_lng2 or min_lng1 >= max_lng2)
    else:
        return False


def range_query(root, query_lng_range, query_lat_range, query_time_start, query_time_end):
    # 查询
    traj_set = []
    rp_path = []
    a = []
    query_rect = [query_lng_range, query_lat_range]
    query_time = [query_time_start, query_time_end]

    with open('vo.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        def write_to_csv(ver, data=None):
            if data is not None:
                writer.writerow([ver, data])
            else:
                writer.writerow([ver])

        def process_edge(e, query_rect, query_time):
            # 保持原有逻辑不变
            if (query_rect[0][0] <= e.start.lng <= query_rect[0][1] and query_rect[1][0] <= e.start.lat <=
                query_rect[1][1]) or (
                    query_rect[0][0] <= e.end.lng <= query_rect[0][1] and query_rect[1][0] <= e.end.lat <=
                    query_rect[1][1]):
                ver = edge_vo_hash(e)
                writer.writerow(["e_vo_start"])
                write_to_csv(ver)

                for traj in e.traj_hashList:
                    ver, flag = second_vo_hash_collect_find(traj, query_time[0], query_time[1])
                    data = [traj.traj_hash] if flag == 1 else [str(traj.start_time), str(traj.end_time)]
                    if flag == 1:
                        # 手动检查重复项（低效操作）
                        if traj.traj_hash not in traj_set:
                            traj_set.append(traj.traj_hash)
                    write_to_csv(ver, data)
                writer.writerow(["e_vo_end"])

            elif segment_intersects_rect(((e.start.lng, e.start.lat), (e.end.lng, e.end.lat)),
                                         ((query_rect[0][0], query_rect[1][0]), (query_rect[0][1], query_rect[1][1]))):
                ver = edge_vo_hash(e)
                writer.writerow(["e_vo_start"])
                write_to_csv(ver)

                for traj in e.traj_hashList:
                    ver, flag = second_vo_hash_collect_find(traj, query_time[0], query_time[1])
                    data = [traj.traj_hash] if flag == 1 else [str(traj.start_time), str(traj.end_time)]
                    if flag == 1:
                        # 手动检查重复项（低效操作）
                        if traj.traj_hash not in traj_set:
                            traj_set.append(traj.traj_hash)
                    write_to_csv(ver, data)
                writer.writerow(["e_vo_end"])

            else:
                ver = no_edge_vo_hash(e)
                data = [str(e.start.lng), str(e.start.lat), str(e.end.lng), str(e.end.lat)]
                writer.writerow(["e_vo_start"])
                write_to_csv(ver, data)
                writer.writerow(["e_vo_end"])

        # 保持_query函数不变
        def _query(node, query_rect, query_time):
            if node is None:
                return
            rp_path.append(node)
            node_rect = [node.border_lng, node.border_lat]

            if not rectangles_intersect(node_rect, query_rect):
                for i in rp_path:
                    a.append(i)
                ver = first_vo_hash_collect2(a)
                data = [node.border_lng[0], node.border_lng[1], node.border_lat[0], node.border_lat[1]]
                writer.writerow(["lng_lat_vo_start"])
                write_to_csv(ver, [data])
                writer.writerow(["lng_lat_vo_end"])
                rp_path.pop()
                return

            for i in rp_path:
                a.append(i)
            ver = first_vo_hash_collect1(a)
            writer.writerow(["lng_lat_vo_start"])
            write_to_csv(ver)

            if node.is_leaf():
                if node.adjacent_list:
                    for e in node.adjacent_list:
                        process_edge(e, query_rect, query_time)
                    writer.writerow(["lng_lat_vo_end"])
            if not node.is_leaf():
                if node.linking:
                    for e in node.linking:
                        process_edge(e, query_rect, query_time)
                writer.writerow(["lng_lat_vo_end"])

                _query(node.left, query_rect, query_time)
                _query(node.right, query_rect, query_time)
            rp_path.pop()

        _query(root, query_rect, query_time)

    return traj_set


def proof_vo(filename):

    # 文件路径
    file_path = filename
    # 打开文件
    with open(file_path, 'r', encoding='utf-8') as file:

        # 逐行读取文件内容
        flag1 = []
        flag2 = []
        list1 = []
        list2 = []
        reader = csv.reader(file)

        for row in reader:


            if row[0] == "lng_lat_vo_start":

                flag1 = next(reader)

                # 如果lag_lat_vo长度是一说明这个区域与查询范围是有交集的
                if len(flag1) <= 1:
                    flag1 = ast.literal_eval(flag1[0])
                    flag1.reverse()
                    list1 = []
                # 如果lag_lat_vo长度是大于一的说明这个区域与查询范围没有交集，要把后面的四个经纬度数据填入计算hash
                else:
                    c = flag1[0]
                    b = flag1[1]
                    c = ast.literal_eval(c)
                    c.reverse()
                    a = c[-1]
                    # 读取要填入的经纬度数据

                    b = ast.literal_eval(b)
                    b = b[0]
                    # 把经纬度数据插入
                    j = 0
                    for i in range(len(a)):
                        if a[i] == " ":
                            a[i] = str(b[j])
                            j = j + 1
                            if j > 3:
                                break
                    all_hash_join = '+'.join(item for item in a)
                    encoded_data = all_hash_join.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()

                    t = c.pop()


                    while c:
                        t = c.pop()
                        for i in range(len(t)):
                            if t[i] == " ":
                                t[i] = hash_hex
                                break
                        all_hash_join = '+'.join(item for item in t)
                        encoded_data = all_hash_join.encode('utf-8')
                        hash_object = hashlib.sha256(encoded_data)
                        hash_hex = hash_object.hexdigest()
                    row = next(reader)

                    liat1 = []
                    # print(hash_hex)
                    if hash_hex != "fc421bb31903f9d66342df4420abb46ce19450894525c2d42c7fe38a5da0db33":

                        return False

            elif row[0] == "e_vo_start":

                flag2 = next(reader)

                # 如果e_vo长度是一说明这个边与查询范围有交集
                if len(flag2) <= 1:
                    flag2 = ast.literal_eval(flag2[0])
                    list2 = []
                # 如果e_vo长度大于一说明这条边是因为不在范围内所以把后面经纬度数据插入验证
                else:
                    a = flag2[0]

                    b = flag2[1]

                    a = ast.literal_eval(a)
                    b = ast.literal_eval(b)
                    for i in range(4):
                        a[i] = b[i]
                    # print(a)
                    # print(44)
                    all_hash_join = '+'.join(item for item in a)

                    encoded_data = all_hash_join.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    list1.append(hash_hex)
                    # print(hash_hex)
                    row = next(reader)


            elif row[0] ==  "e_vo_end":
                a = flag2
                # print(list2)
                # print("1")
                j = 0
                for i in range(len(a)):
                    if a[i] == " ":
                        a[i] = list2[j]
                        j = j + 1
                # print(a)
                # print("2")
                all_hash_join = '+'.join(item for item in a)
                # print(all_hash_join)
                # print(3)
                encoded_data = all_hash_join.encode('utf-8')
                hash_object = hashlib.sha256(encoded_data)
                hash_hex = hash_object.hexdigest()
                list1.append(hash_hex)
                # print(hash_hex)

            elif row[0] == "lng_lat_vo_end":
                # print(flag1)

                t = flag1.pop()
                j = 0
                for i in range(len(t)):
                    if t[i] == " ":
                        t[i] = list1[j]
                        j = j + 1

                all_hash_join = '+'.join(item for item in t)
                encoded_data = all_hash_join.encode('utf-8')
                hash_object = hashlib.sha256(encoded_data)
                hash_hex = hash_object.hexdigest()

                while flag1:
                    t = flag1.pop()
                    for i in range(len(t)):
                        if t[i] == " ":
                            t[i] = hash_hex
                            break
                    all_hash_join = '+'.join(item for item in t)
                    encoded_data = all_hash_join.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                list1 = []
                # print(hash_hex)
                if hash_hex != "fc421bb31903f9d66342df4420abb46ce19450894525c2d42c7fe38a5da0db33":
                    return False
            else:
                a = row[0]
                b = row[1]
                a = ast.literal_eval(a)
                b = ast.literal_eval(b)
                j = 0
                for i in range(len(a)):
                    if a[i] == " ":
                        a[i] = b[j]
                        j = j + 1
                # print(a)
                str_all = a[0] + a[1] + a[2]

                encoded_data = str_all.encode('utf-8')
                hash_object = hashlib.sha256(encoded_data)
                hash_hex = hash_object.hexdigest()
                list2.append(hash_hex)

    return True












# # 范围查询函数
# def range_query(root, query_lng_range, query_lat_range, query_time_start, query_time_end):
#     # 查询
#     rp_path = []
#     a = []
#
#     def _query(node, query_rect, query_time):
#         if node is None:
#             return
#         # 把每一个走过的节点记录
#         rp_path.append(node)
#         node_rect = [node.border_lng, node.border_lat]
#         # 如果该区域范围不符合查询范围要返回经纬度不符合的验证信息
#         if not rectangles_intersect(node_rect, query_rect):
#             for i in rp_path:
#                 a.append(i)
#             ver = first_vo_hash_collect2(a)
#             try:
#                 # 以追加模式打开 CSV 文件
#                 with open(f'vo.csv', 'a', newline='') as csvfile:
#                     writer = csv.writer(csvfile)
#                     # 写入数据行
#                     writer.writerow([ver, [node.border_lng[0], node.border_lng[1], node.border_lat[0], node.border_lat[1]]])
#                 print(f"collect2数据已成功写入到 vo.csv 文件")
#             except Exception as e:
#                 print(f"写入文件时出现错误: {e}")
#             return
#
#         # 首先这个区域满足查询范围先把第一层索引的vo写入
#         for i in rp_path:
#             a.append(i)
#         ver = first_vo_hash_collect1(a)
#         try:
#             # 以追加模式打开 CSV 文件
#             with open(f'vo.csv', 'a', newline='') as csvfile:
#                 writer = csv.writer(csvfile)
#                 # 写入数据行
#                 writer.writerow([ver])
#             print(f"collect1数据已成功写入到 vo.csv 文件")
#         except Exception as e:
#             print(f"写入文件时出现错误: {e}")
#
#
#         if node.is_leaf():
#                 # 写函数判断这个区域内具体哪条边和查询范围有交集
#             for e in node.adjacent_list:
#                 # 第一种情况判断这条边的两个端点是否至少有一个落在查询范围区域内
#                 if (query_rect[0][0] <= e.start.lng <= query_rect[0][1] and query_rect[1][0] <= e.start.lat <=
#                     query_rect[1][1]) or (
#                         query_rect[0][0] <= e.end.lng <= query_rect[0][1] and query_rect[1][0] <= e.end.lat <=
#                         query_rect[1][1]):
#
#                 #这种是在查询范围内的边
#                     ver = edge_vo_hash(e)
#                     try:
#                         # 以追加模式打开 CSV 文件
#                         with open(f'vo.csv', 'a', newline='') as csvfile:
#                             writer = csv.writer(csvfile)
#                             # 写入数据行
#                             writer.writerow([ver])
#                         print(f"edge数据已成功写入到 vo.csv 文件")
#                     except Exception as e:
#                         print(f"写入文件时出现错误: {e}")
#
#                 # 开始对这条边的轨迹进行查询
#                     for traj in e.traj_hashList:
#                         ver, flag = second_vo_hash_collect_find(traj, query_time[0], query_time[1])
#                         try:
#                             # 以追加模式打开 CSV 文件
#                             with open(f'vo.csv', 'a', newline='') as csvfile:
#                                 writer = csv.writer(csvfile)
#                                 if flag == 1:
#                                 # 写入数据行
#                                     writer.writerow([ver, [traj.traj_hash]])
#                                 else:
#                                     writer.writerow([ver, [str(traj.start_time), str(traj.end_time)]])
#                             print(f"traj数据已成功写入到 vo.csv 文件")
#                         except Exception as e:
#                             print(f"写入文件时出现错误: {e}")
#
#                 # 如果两个端点都不在查询范围，那么判断线段和查询范围是否有交集
#                 elif segment_intersects_rect(((e.start.lng, e.start.lat), (e.end.lng, e.end.lat)), (
#                 (query_rect[0][0], query_rect[1][0]), (query_rect[0][1], query_rect[1][1]))):
#                     # 这种是在查询范围内的边
#                     ver = edge_vo_hash(e)
#                     try:
#                         # 以追加模式打开 CSV 文件
#                         with open(f'vo.csv', 'a', newline='') as csvfile:
#                             writer = csv.writer(csvfile)
#                             # 写入数据行
#                             writer.writerow([ver])
#                         print(f"edge数据已成功写入到 vo.csv 文件")
#                     except Exception as e:
#                         print(f"写入文件时出现错误: {e}")
#
#                     # 开始对这条边的轨迹进行查询
#                     for traj in e.traj_hashList:
#                         ver, flag = second_vo_hash_collect_find(traj, query_time[0], query_time[1], flag)
#                         try:
#                             # 以追加模式打开 CSV 文件
#                             with open(f'vo.csv', 'a', newline='') as csvfile:
#                                 writer = csv.writer(csvfile)
#                                 if flag == 1:
#                                     # 写入数据行
#                                     writer.writerow([ver, [traj.traj_hash]])
#                                 else:
#                                     writer.writerow([ver, [str(traj.start_time), str(traj.end_time)]])
#                             print(f"traj数据已成功写入到 vo.csv 文件")
#                         except Exception as e:
#                             print(f"写入文件时出现错误: {e}")
#                 else:
#             #边不在查询范围内
#                     ver = no_edge_vo_hash(e)
#                     try:
#                         # 以追加模式打开 CSV 文件
#                         with open(f'vo.csv', 'a', newline='') as csvfile:
#                             writer = csv.writer(csvfile)
#                             # 写入数据行
#                             writer.writerow([ver,[str(e.start.lng),str(e.start.lat),str(e.end.lat),str(e.emd.lat)]])
#                         print(f"no_edge数据已成功写入到 vo.csv 文件")
#                     except Exception as e:
#                         print(f"写入文件时出现错误: {e}")
#
#
#         if not node.is_leaf():
#             if node.linking:
#
#                 for e in node.linking:
#                     # 第一种情况判断这条边的两个端点是否至少有一个落在查询范围区域内
#                     if (query_rect[0][0] <= e.start.lng <= query_rect[0][1] and query_rect[1][0] <= e.start.lat <=
#                         query_rect[1][1]) or (
#                             query_rect[0][0] <= e.end.lng <= query_rect[0][1] and query_rect[1][0] <= e.end.lat <=
#                             query_rect[1][1]):
#                         # 这种是在查询范围内的边
#                         ver = edge_vo_hash(e)
#                         try:
#                             # 以追加模式打开 CSV 文件
#                             with open(f'vo.csv', 'a', newline='') as csvfile:
#                                 writer = csv.writer(csvfile)
#                                 # 写入数据行
#                                 writer.writerow([ver])
#                             print(f"edge数据已成功写入到 vo.csv 文件")
#                         except Exception as e:
#                             print(f"写入文件时出现错误: {e}")
#
#                         # 开始对这条边的轨迹进行查询
#                         for traj in e.traj_hashList:
#                             ver, flag = second_vo_hash_collect_find(traj, query_time[0], query_time[1])
#                             try:
#                                 # 以追加模式打开 CSV 文件
#                                 with open(f'vo.csv', 'a', newline='') as csvfile:
#                                     writer = csv.writer(csvfile)
#                                     if flag == 1:
#                                         # 写入数据行
#                                         writer.writerow([ver, [traj.traj_hash]])
#                                     else:
#                                         writer.writerow([ver, [str(traj.start_time), str(traj.end_time)]])
#                                 print(f"traj数据已成功写入到 vo.csv 文件")
#                             except Exception as e:
#                                 print(f"写入文件时出现错误: {e}")
#
#                     # 如果两个端点都不在查询范围，那么判断线段和查询范围是否有交集
#                     elif segment_intersects_rect(((e.start.lng, e.start.lat), (e.end.lng, e.end.lat)),
#                                                  ((query_rect[0][0], query_rect[1][0]),
#                                                   (query_rect[0][1], query_rect[1][1]))):
#                         ver = edge_vo_hash(e)
#                         try:
#                             # 以追加模式打开 CSV 文件
#                             with open(f'vo.csv', 'a', newline='') as csvfile:
#                                 writer = csv.writer(csvfile)
#                                 # 写入数据行
#                                 writer.writerow([ver])
#                             print(f"edge数据已成功写入到 vo.csv 文件")
#                         except Exception as e:
#                             print(f"写入文件时出现错误: {e}")
#
#                         # 开始对这条边的轨迹进行查询
#                         for traj in e.traj_hashList:
#                             ver, flag = second_vo_hash_collect_find(traj, query_time[0], query_time[1], flag)
#                             try:
#                                 # 以追加模式打开 CSV 文件
#                                 with open(f'vo.csv', 'a', newline='') as csvfile:
#                                     writer = csv.writer(csvfile)
#                                     if flag == 1:
#                                         # 写入数据行
#                                         writer.writerow([ver, [traj.traj_hash]])
#                                     else:
#                                         writer.writerow([ver, [str(traj.start_time), str(traj.end_time)]])
#                                 print(f"traj数据已成功写入到 vo.csv 文件")
#                             except Exception as e:
#                                 print(f"写入文件时出现错误: {e}")
#                     else:
#                         # 边不在查询范围内
#                         ver = no_edge_vo_hash(e)
#                         try:
#                             # 以追加模式打开 CSV 文件
#                             with open(f'vo.csv', 'a', newline='') as csvfile:
#                                 writer = csv.writer(csvfile)
#                                 # 写入数据行
#                                 writer.writerow(
#                                     [ver, [str(e.start.lng), str(e.start.lat), str(e.end.lat), str(e.emd.lat)]])
#                             print(f"no_edge数据已成功写入到 vo.csv 文件")
#                         except Exception as e:
#                             print(f"写入文件时出现错误: {e}")
#
#             _query(node.left, query_rect, query_time)
#             _query(node.right, query_rect, query_time)
#         rp_path.pop()
#
#     # 查询经纬度范围
#     query_rect = [query_lng_range, query_lat_range]
#     query_time = [query_time_start, query_time_end]
#     _query(root, query_rect, query_time)


