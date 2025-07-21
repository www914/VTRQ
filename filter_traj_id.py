import csv
import json

from vector_cross_product import segment_intersects_rect


def filter_id(result,input_file):
    # 输出的新 CSV 文件路径
    output_file = "traj_filtered_xian.csv"

    with open(input_file, "r", newline="") as infile, open(output_file, "w", newline="") as outfile:
        # 创建 CSV 读取器和写入器
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 读取输入文件的表头并写入到输出文件
        header = next(reader)
        writer.writerow(header)

        # 遍历输入文件的每一行
        for row in reader:
            # 假设轨迹 id 在第一列，若实际情况不同，请修改索引
            traj_id = row[0]

            # 如果当前行的轨迹 id 在目标集合中，就将这一行写入到输出文件
            if traj_id in result:
                writer.writerow(row)


import csv
import json
import time



def final_filter_id(csv_file_path, min_lng, max_lng, min_lat, max_lat, start_time, end_time):
    rect = (min_lng, min_lat, max_lng, max_lat)
    result_ids = set()
    start_time_find = time.time()
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过表头
        for row in reader:
            traj_id = row[0]
                # 使用 json.loads 代替 eval
            traj_data = json.loads(row[1])
            for i in range(len(traj_data)-1):
                _, lng, lat, timestamp = traj_data[i]
                # 一条线段两个端点都落在查询范围内:
                if min_lng <= lng <= max_lng and min_lat <= lat <= max_lat and min_lng <= traj_data[i+1][1] <= max_lng and min_lat <= traj_data[i+1][2] <= max_lat:
                        next_timestamp = traj_data[i+1][3]
                        if timestamp <= end_time and start_time <= next_timestamp:
                            # print(lng,lat,timestamp,traj_data[i+1][1],traj_data[i+1][2],traj_data[i+1][3])
                            result_ids.add(traj_id)
                            break
                # 不是完全在范围
                else:
                    traj_start = (lng, lat, timestamp)
                    traj_end = (traj_data[i+1][1], traj_data[i+1][2], traj_data[i+1][3])
                    time_interval = get_time_interval_in_rect(traj_start, traj_end, rect)
                    if time_interval:
                        t_start, t_end = time_interval
                        if t_start <= end_time and start_time <= t_end:
                            # print("2",lng, lat, t_start, traj_data[i + 1][1], traj_data[i + 1][2], t_end)
                            result_ids.add(traj_id)
                            break
    end_time_find = time.time()
    time_all = end_time_find - start_time_find
    # print("轨迹过滤时间",end_time_find - start_time_find)
    print(len(result_ids))
    # print(result_ids)
    return time_all


def line_rect_intersection(line_start, line_end, rect):
    """
    检测线段是否与矩形相交并计算交点坐标和时间

    参数:
    line_start: 线段起点坐标和时间戳，格式为(x, y, t)
    line_end: 线段终点坐标和时间戳，格式为(x, y, t)
    rect: 矩形坐标，格式为(x_min, y_min, x_max, y_max)

    返回:
    若相交，返回交点列表，每个交点包含坐标和时间；若不相交，返回空列表
    """
    # 提取矩形的四个顶点
    x_min, y_min, x_max, y_max = rect

    # 提取线段的起点和终点坐标及时间戳
    x1, y1, t1 = line_start
    x2, y2, t2 = line_end

    # 矩形的四条边
    edges = [
        ((x_min, y_min), (x_max, y_min)),  # 下边
        ((x_max, y_min), (x_max, y_max)),  # 右边
        ((x_max, y_max), (x_min, y_max)),  # 上边
        ((x_min, y_max), (x_min, y_min))  # 左边
    ]

    intersections = []

    # 检查线段是否与矩形的每条边相交
    for edge_start, edge_end in edges:
        intersection = line_line_intersection((x1, y1), (x2, y2), edge_start, edge_end)
        if intersection:
            # 计算交点的时间
            x, y = intersection
            # 计算参数t
            if x2 - x1 != 0:
                t = (x - x1) / (x2 - x1)
            else:
                t = (y - y1) / (y2 - y1)
            # 计算时间
            intersection_time = t1 + t * (t2 - t1)
            intersections.append((x, y, intersection_time))

    # 检查线段的两个端点是否在矩形内部
    if is_point_in_rect((x1, y1), rect):
        intersections.append((x1, y1, t1))
    if is_point_in_rect((x2, y2), rect):
        intersections.append((x2, y2, t2))

    # 去重
    unique_intersections = []
    for point in intersections:
        if point not in unique_intersections:
            unique_intersections.append(point)

    return unique_intersections


def line_line_intersection(line1_start, line1_end, line2_start, line2_end):
    """
    计算两条线段的交点

    参数:
    line1_start, line1_end: 第一条线段的起点和终点
    line2_start, line2_end: 第二条线段的起点和终点

    返回:
    若相交，返回交点坐标；若不相交，返回None
    """
    x1, y1 = line1_start
    x2, y2 = line1_end
    x3, y3 = line2_start
    x4, y4 = line2_end

    # 计算分母
    denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

    # 如果分母为0，则两线段平行或共线
    if denominator == 0:
        return None

    # 计算参数t和s
    t = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
    s = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

    # 如果t和s都在[0,1]范围内，则两线段相交
    if 0 <= t <= 1 and 0 <= s <= 1:
        # 计算交点坐标
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)

    return None


def is_point_in_rect(point, rect):
    """
    检查点是否在矩形内部

    参数:
    point: 点的坐标，格式为(x, y)
    rect: 矩形坐标，格式为(x_min, y_min, x_max, y_max)

    返回:
    若点在矩形内部，返回True；否则返回False
    """
    x, y = point
    x_min, y_min, x_max, y_max = rect
    return x_min <= x <= x_max and y_min <= y <= y_max


def get_time_interval_in_rect(line_start, line_end, rect):
    """
    获取线段在矩形内的时间区间

    参数:
    line_start: 线段起点坐标和时间戳，格式为(x, y, t)
    line_end: 线段终点坐标和时间戳，格式为(x, y, t)
    rect: 矩形坐标，格式为(x_min, y_min, x_max, y_max)

    返回:
    若线段与矩形相交，返回在矩形内的最早和最晚时间戳；若不相交，返回None
    """
    # 获取所有交点
    intersections = line_rect_intersection(line_start, line_end, rect)

    if not intersections:
        return None

    # 提取所有交点的时间戳
    timestamps = [point[2] for point in intersections]

    # 对时间戳进行排序
    timestamps.sort()

    # 检查线段的起点和终点是否在矩形内
    x1, y1, t1 = line_start
    x2, y2, t2 = line_end

    # 确定线段在矩形内的部分
    if is_point_in_rect((x1, y1), rect) and is_point_in_rect((x2, y2), rect):

        # 线段完全在矩形内
        return t1, t2
    elif is_point_in_rect((x1, y1), rect):

        # 起点在矩形内，终点在矩形外
        return t1, timestamps[0]
    elif is_point_in_rect((x2, y2), rect):

        # 终点在矩形内，起点在矩形外
        return timestamps[-1], t2
    else:

        # 线段部分在矩形内
        return timestamps[0], timestamps[-1]
