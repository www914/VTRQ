def orientation(p, q, r):
    """
    此函数用于判断三个点 p, q, r 的方向关系。
    通过计算向量叉积来确定三点的相对位置，结果可以是共线、顺时针或逆时针。
    :param p: 第一个点，格式为 (x.txt, y)
    :param q: 第二个点，格式为 (x.txt, y)
    :param r: 第三个点，格式为 (x.txt, y)
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
    :param p: 线段的一个端点，格式为 (x.txt, y)
    :param q: 待判断的点，格式为 (x.txt, y)
    :param r: 线段的另一个端点，格式为 (x.txt, y)
    :return: 如果点 q 在线段 pr 上返回 True，否则返回 False
    """
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))


def do_intersect(p1, q1, p2, q2):
    """
    判断两条线段 p1q1 和 p2q2 是否相交。
    先通过 orientation 函数判断点的方向关系，再处理共线且重叠的特殊情况。
    :param p1: 第一条线段的一个端点，格式为 (x.txt, y)
    :param q1: 第一条线段的另一个端点，格式为 (x.txt, y)
    :param p2: 第二条线段的一个端点，格式为 (x.txt, y)
    :param q2: 第二条线段的另一个端点，格式为 (x.txt, y)
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


def test_segment_intersects_rect():
    # 测试用例 1: 线段与矩形相交
    segment1 = ((104.05057 ,30.68449 ),( 104.04993 ,30.68676))
    rect1 = ((104.05, 30.65), (104.06, 30.66))
    if segment_intersects_rect(segment1, rect1):
        print("测试通过：线段与矩形相交")
    else:
        print("测试未通过：线段与矩形不相交")




if __name__ == "__main__":
    test_segment_intersects_rect()
