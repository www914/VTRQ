import ast
import csv
import hashlib

from ACC import initialize_accumulator, add_string_element
from hash_collect import edge_vo_hash, no_edge_vo_hash, first_vo_hash_collect2, \
    first_vo_hash_collect1
from vector_cross_product import segment_intersects_rect
from new_interval_tree import Interval

# node_rect = [node.border_lng, node.border_lat]
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


def range_query(root, query_lng_range, query_lat_range):
    # 查询
    traj_set = set()
    rp_path = []
    query_rect = [query_lng_range, query_lat_range]

    # 用于收集所有要写入CSV的数据
    csv_data = []

    def write_to_csv_buffer(ver, data=None):
        if data is not None:
            csv_data.append([ver, data])
        else:
            csv_data.append([ver])

    def process_edge(e, query_rect):
        # 第一种情况判断这条边的两个端点是否至少有一个落在查询范围区域内
        if (query_rect[0][0] <= e.start.lng <= query_rect[0][1] and query_rect[1][0] <= e.start.lat <= query_rect[1][
            1]) or (
                query_rect[0][0] <= e.end.lng <= query_rect[0][1] and query_rect[1][0] <= e.end.lat <= query_rect[1][
            1]):

            # 这种是在查询范围内的边
            ver = edge_vo_hash(e)
            csv_data.append(["e_vo_start"])
            write_to_csv_buffer(ver)
            write_to_csv_buffer(e.traj_hashList)
            traj_set.update(e.traj_hashList)
            csv_data.append(["e_vo_end"])

        # 如果两个端点都不在查询范围，那么判断线段和查询范围是否有交集
        elif segment_intersects_rect(((e.start.lng, e.start.lat), (e.end.lng, e.end.lat)),
                                     ((query_rect[0][0], query_rect[1][0]), (query_rect[0][1], query_rect[1][1]))):

            ver = edge_vo_hash(e)
            csv_data.append(["e_vo_start"])
            write_to_csv_buffer(ver)
            write_to_csv_buffer(e.traj_hashList)
            traj_set.update(e.traj_hashList)
            csv_data.append(["e_vo_end"])
        else:
            # 边不在查询范围内
            ver = no_edge_vo_hash(e)
            data = [str(e.start.lng), str(e.start.lat), str(e.end.lng), str(e.end.lat)]
            csv_data.append(["e_vo_start"])
            write_to_csv_buffer(ver, data)
            csv_data.append(["e_vo_end"])

    def _query(node, query_rect):
        if node is None:
            return
        # 把每一个走过的节点记录
        rp_path.append(node)
        node_rect = [node.border_lng, node.border_lat]
        # 如果该区域范围不符合查询范围要返回经纬度不符合的验证信息
        if not rectangles_intersect(node_rect, query_rect):
            a = list(rp_path)
            ver = first_vo_hash_collect2(a)
            data = [node.border_lng[0], node.border_lng[1], node.border_lat[0], node.border_lat[1]]
            csv_data.append(["lng_lat_vo_start"])
            write_to_csv_buffer(ver, [data])
            csv_data.append(["lng_lat_vo_end"])
            rp_path.pop()
            return

        if node.is_leaf():
            a = list(rp_path)
            ver = first_vo_hash_collect1(a, True)
            csv_data.append(["lng_lat_vo_start"])
            write_to_csv_buffer(ver)
            if node.adjacent_list:
                for e in node.adjacent_list:
                    process_edge(e, query_rect)
                csv_data.append(["lng_lat_vo_end"])

        if not node.is_leaf():
            p = True
            # 如果查询范围和邻接边范围也没有交集，那么可以省略每一条边的逐个查询
            if not rectangles_intersect(node.linking_box, query_rect):
                p = False
            # 首先这个区域满足查询范围先把第一层索引的vo写入
            a = list(rp_path)
            # 如果邻接边范围与查询范围有交集
            if p:
                ver = first_vo_hash_collect1(a, p)
                csv_data.append(["lng_lat_vo_start"])
                write_to_csv_buffer(ver)
                if node.linking:
                    for e in node.linking:
                        process_edge(e, query_rect)
                csv_data.append(["lng_lat_vo_end"])

            else:
                ver = first_vo_hash_collect1(a, p)
                csv_data.append(["lng_lat_vo_start"])
                if node.linking_box:
                    data = [node.linking_box[0][0], node.linking_box[0][1], node.linking_box[1][0],
                            node.linking_box[1][1]]
                    write_to_csv_buffer(ver, data)
                    csv_data.append(["lng_lat_vo_end"])
                # 邻接边范围不存在
                else:
                    data = ["", "", "", ""]
                    write_to_csv_buffer(ver, data)
                    csv_data.append(["lng_lat_vo_end"])

            _query(node.left, query_rect)
            _query(node.right, query_rect)
        rp_path.pop()

    # 查询经纬度范围
    _query(root, query_rect)

    # 将所有收集的数据一次性写入CSV文件
    with open('vo.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    return traj_set








# def range_query(root, query_lng_range, query_lat_range):
#     # 查询
#     traj_set = set()
#     rp_path = []
#     a = []
#     query_rect = [query_lng_range, query_lat_range]
#     # edge_count = 0  # 新增计数器，用于统计在经纬度查询范围内的边的数量
#
#     with (open('vo.csv', 'a', newline='') as csvfile):
#         writer = csv.writer(csvfile)  # 复用同一个writer对象
#         def write_to_csv(ver, data=None):
#             if data is not None:
#                 writer.writerow([ver, data])
#             else:
#                 writer.writerow([ver])
#             # print(f"数据已成功写入到vo.csv文件")
#
#         def process_edge(e, query_rect):
#             # nonlocal edge_count  # 声明使用外部函数的变量
#             # 第一种情况判断这条边的两个端点是否至少有一个落在查询范围区域内
#             if (query_rect[0][0] <= e.start.lng <= query_rect[0][1] and query_rect[1][0] <= e.start.lat <=query_rect[1][1]) or (
#                 query_rect[0][0] <= e.end.lng <= query_rect[0][1] and query_rect[1][0] <= e.end.lat <=query_rect[1][1]):
#
#                 # 这种是在查询范围内的边
#                 ver = edge_vo_hash(e)
#                 writer.writerow(["e_vo_start"])
#                 write_to_csv(ver)
#                 write_to_csv(e.traj_hashList)
#                 traj_set.update(e.traj_hashList)
#                 writer.writerow(["e_vo_end"])
#                 # edge_count += 1  # 边在查询范围内，计数器加一
#             # 如果两个端点都不在查询范围，那么判断线段和查询范围是否有交集
#             elif segment_intersects_rect(((e.start.lng, e.start.lat), (e.end.lng, e.end.lat)),
#                                          ((query_rect[0][0], query_rect[1][0]), (query_rect[0][1], query_rect[1][1]))):
#
#                 ver = edge_vo_hash(e)
#                 writer.writerow(["e_vo_start"])
#                 write_to_csv(ver)
#                 write_to_csv(e.traj_hashList)
#                 traj_set.update(e.traj_hashList)
#                 writer.writerow(["e_vo_end"])
#                 # edge_count += 1  # 边在查询范围内，计数器加一
#             else:
#                 # 边不在查询范围内
#                 ver = no_edge_vo_hash(e)
#                 data = [str(e.start.lng), str(e.start.lat), str(e.end.lng), str(e.end.lat)]
#                 writer.writerow(["e_vo_start"])
#                 write_to_csv(ver, data)
#                 writer.writerow(["e_vo_end"])
#
#         def _query(node, query_rect):
#             if node is None:
#                 return
#             # 把每一个走过的节点记录
#             rp_path.append(node)
#             node_rect = [node.border_lng, node.border_lat]
#             # 如果该区域范围不符合查询范围要返回经纬度不符合的验证信息
#             if not rectangles_intersect(node_rect, query_rect):
#                 # for i in rp_path:
#                 #     a.append(i)
#                 a = list(rp_path)
#                 ver = first_vo_hash_collect2(a)
#                 data = [node.border_lng[0], node.border_lng[1], node.border_lat[0], node.border_lat[1]]
#                 writer.writerow(["lng_lat_vo_start"])  # 正确：英文双引号
#                 write_to_csv(ver, [data])
#                 writer.writerow(["lng_lat_vo_end"])
#                 rp_path.pop()
#                 return
#
#             if node.is_leaf():
#                 # for i in rp_path:
#                 #     a.append(i)
#                 a = list(rp_path)
#                 ver = first_vo_hash_collect1(a, True)
#                 writer.writerow(["lng_lat_vo_start"])
#                 write_to_csv(ver)
#                 if node.adjacent_list:
#                     for e in node.adjacent_list:
#                         process_edge(e, query_rect)
#                     writer.writerow(["lng_lat_vo_end"])
#
#             if not node.is_leaf():
#                 p = True
#                 # 如果查询范围和邻接边范围也没有交集，那么可以省略每一条边的逐个查询
#                 if not rectangles_intersect(node.linking_box, query_rect):
#                     p = False
#                 # 首先这个区域满足查询范围先把第一层索引的vo写入
#                 # for i in rp_path:
#                 #     a.append(i)
#                 a = list(rp_path)
#                 # 如果邻接边范围与查询范围有交集
#                 if p:
#                     ver = first_vo_hash_collect1(a, p)
#                     writer.writerow(["lng_lat_vo_start"])
#                     write_to_csv(ver)
#                     if node.linking:
#                         for e in node.linking:
#                             process_edge(e, query_rect)
#                     writer.writerow(["lng_lat_vo_end"])
#
#                 else:
#                     ver = first_vo_hash_collect1(a, p)
#                     writer.writerow(["lng_lat_vo_start"])
#                     if node.linking_box:
#                         data = [node.linking_box[0][0], node.linking_box[0][1], node.linking_box[1][0], node.linking_box[1][1]]
#                         write_to_csv(ver, data)
#                         writer.writerow(["lng_lat_vo_end"])
#                     # 邻接边范围不存在
#                     else:
#                         data = ["", "", "", ""]
#                         write_to_csv(ver, data)
#                         writer.writerow(["lng_lat_vo_end"])
#
#                 _query(node.left, query_rect)
#                 _query(node.right, query_rect)
#             rp_path.pop()
#
#         # 查询经纬度范围
#         _query(root, query_rect)
#
#     return traj_set  # 返回计数器的值以及原本的轨迹集合

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
            # print(row)
            if row[0] == "lng_lat_vo_start":
                flag1 = next(reader)
                # print(flag1)
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
                    # print(b)
                    # b = b[0]
                    # 如果b是嵌套表说明是大经纬度不满足
                    if  isinstance(b[0], list):
                        b = b[0]

                    # 把经纬度数据插入
                    j = 0
                    for i in range(len(a)):
                        if a[i] == " ":
                            a[i] = str(b[j])
                            j = j + 1
                            if j > 3:
                                break
                    # print(a)
                    all_hash_join = '+'.join(item for item in a if item)
                    # print(all_hash_join)
                    encoded_data = all_hash_join.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    # print(hash_hex)
                    t = c.pop()
                    #
                    # t = c.pop()
                    # print(t)
                    # for i in range(len(t)):
                    #     if t[i] == " ":
                    #         t[i] = hash_hex
                    #         break
                    # all_hash_join = '+'.join(item for item in t)
                    # encoded_data = all_hash_join.encode('utf-8')
                    # hash_object = hashlib.sha256(encoded_data)
                    # hash_hex = hash_object.hexdigest()
                    # print(hash_hex)

                    while c:
                        t = c.pop()
                        # print(t)
                        for i in range(len(t)):
                            if t[i] == " ":
                                t[i] = hash_hex
                                break
                        all_hash_join = '+'.join(item for item in t)
                        # print(all_hash_join)
                        encoded_data = all_hash_join.encode('utf-8')
                        hash_object = hashlib.sha256(encoded_data)
                        hash_hex = hash_object.hexdigest()
                        # print(hash_hex)
                    row = next(reader)
                    # print(row)

                    # print(hash_hex)
                    if hash_hex != "b3f25afb1e216bbfe35660546436ddd46cc4085dd5c450dd1a7812acc832c2a6":

                        return False

            elif row[0] == "e_vo_start":

                flag2 = next(reader)
                # print(flag2)
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
                    all_hash_join = '+'.join(item for item in a if item)

                    encoded_data = all_hash_join.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    list1.append(hash_hex)
                    row = next(reader)
                    # print(row)

            elif row[0] ==  "e_vo_end":
                a = flag2
                if list2:
                    a[-1] = list2[0]
                else:
                    a[-1] = ""
                all_hash_join = '+'.join(item for item in a if item)
                encoded_data = all_hash_join.encode('utf-8')
                hash_object = hashlib.sha256(encoded_data)
                hash_hex = hash_object.hexdigest()
                list1.append(hash_hex)
                # print(list1)

            elif row[0] == "lng_lat_vo_end":


                t = flag1.pop()
                j = 0
                for i in range(len(t)):
                    if t[i] == " ":
                        t[i] = list1[j]
                        j = j + 1

                all_hash_join = '+'.join(item for item in t)
                # print(all_hash_join)
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
                if hash_hex != "b3f25afb1e216bbfe35660546436ddd46cc4085dd5c450dd1a7812acc832c2a6":
                    return False
            # 改这里用累加器
            else:
                a = row[0]
                a = ast.literal_eval(a)
                if a:
                    traj_list = []
                    for traj in a:
                        traj_list.append(traj)
                    all_traj_str = '+'.join(item for item in traj_list)
                    encoded_data = all_traj_str.encode('utf-8')
                    hash_object = hashlib.sha256(encoded_data)
                    hash_hex = hash_object.hexdigest()
                    list2.append(hash_hex)

    return True

