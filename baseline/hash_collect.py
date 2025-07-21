# 第一层验证哈希收集（这种是区域满足查询范围）
def first_vo_hash_collect1(rp_path):
    stack = []
    # 放每一层的验证数据
    a = []
    flag = rp_path.pop()
    str_border_lng0 = str(flag.border_lng[0])
    a.append(str_border_lng0)
    str_border_lng1 = str(flag.border_lng[1])
    a.append(str_border_lng1)
    str_border_lat0 = str(flag.border_lat[0])
    a.append(str_border_lat0)
    str_border_lat1 = str(flag.border_lat[1])
    a.append(str_border_lat1)

    if flag.is_leaf():
        if flag.adjacent_list:
            for edge in flag.adjacent_list:
                a.append(" ")
    else:
        if flag.linking:
            for edge in flag.linking:
                a.append(" ")

    if flag.left:
        a.append(flag.left.rp_hash_merge)
    if flag.right:
        a.append(flag.right.rp_hash_merge)
    stack.append(a)

    while rp_path:
        b = []
        flag1 = rp_path.pop()
        str_border_lng0 = str(flag1.border_lng[0])
        b.append(str_border_lng0)
        str_border_lng1 = str(flag1.border_lng[1])
        b.append(str_border_lng1)
        str_border_lat0 = str(flag1.border_lat[0])
        b.append(str_border_lat0)
        str_border_lat1 = str(flag1.border_lat[1])
        b.append(str_border_lat1)

        if flag1.is_leaf():
            if flag1.adjacent_list:
                for edge in flag1.adjacent_list:
                    b.append(edge.edge_merge)
        else:
            if flag1.linking:
                for edge in flag1.linking:
                    b.append(edge.edge_merge)
        # 这个节点的左孩子是需要填空的节点
        if flag1.left and flag1.left == flag:
            b.append(" ")
            # 右孩子不空把右孩子的rp_hash_merge放入
            if flag1.right:
                b.append(flag1.right.rp_hash_merge)

        if flag1.right and flag1.right == flag:
            if flag1.left:
                b.append(flag1.left.rp_hash_merge)
            b.append(" ")
        stack.append(b)
        flag = flag1

    return stack

# 第一层验证哈希收集（这种是这个区域不满足查询范围）
def first_vo_hash_collect2(rp_path):
    stack = []
    # 放每一层的验证数据
    a = []
    flag = rp_path.pop()
    a.append(" ")
    a.append(" ")
    a.append(" ")
    a.append(" ")

    if flag.is_leaf():
        if flag.adjacent_list:
            for edge in flag.adjacent_list:
                a.append(edge.edge_merge)
    else:
        if flag.linking:
            for edge in flag.linking:
                a.append(edge.edge_merge)

    if flag.left:
        a.append(flag.left.rp_hash_merge)
    if flag.right:
        a.append(flag.right.rp_hash_merge)
    stack.append(a)

    while rp_path:
        b = []
        flag1 = rp_path.pop()
        str_border_lng0 = str(flag1.border_lng[0])
        b.append(str_border_lng0)
        str_border_lng1 = str(flag1.border_lng[1])
        b.append(str_border_lng1)
        str_border_lat0 = str(flag1.border_lat[0])
        b.append(str_border_lat0)
        str_border_lat1 = str(flag1.border_lat[1])
        b.append(str_border_lat1)

        if flag1.is_leaf():
            if flag1.adjacent_list:
                for edge in flag1.adjacent_list:
                    b.append(edge.edge_merge)
        else:
            if flag1.linking:
                for edge in flag1.linking:
                    b.append(edge.edge_merge)
        # 这个节点的左孩子是需要填空的节点
        if flag1.left and flag1.left == flag:
            b.append(" ")
            # 右孩子不空把右孩子的rp_hash_merge放入
            if flag1.right:
                b.append(flag1.right.rp_hash_merge)

        if flag1.right and flag1.right == flag:
            if flag1.left:
                b.append(flag1.left.rp_hash_merge)
            b.append(" ")
        stack.append(b)
        flag = flag1

    return stack
# 1538461200 , 1538464800
# 在收集到第一层hash之后还要收集第二层hash
def second_vo_hash_collect_find(traj, start_time, end_time):
    flag = 1  #先假设认为这个轨迹是找到的
    a = []
    # 查询到轨迹返回轨迹id
    if  start_time <= traj.end_time and traj.start_time <= end_time:
        start_time_str = str(traj.start_time)
        end_time_str = str(traj.end_time)
        a.append(start_time_str)
        a.append(end_time_str)
        a.append(" ")
    # 加快查询可以在最前面再来一个flag1如果flag1标记变0说明后面的都不用查
    else:
        # 轨迹没有找到
        a.append(" ")
        a.append(" ")
        a.append(traj.traj_hash)
        flag = 0

    return a, flag

# 因为边可能因为经纬度问题不在查询范围内所以对于不在查询范围内的边也要验证
def no_edge_vo_hash(edge):
    a = []
    a.append(" ")
    a.append(" ")
    a.append(" ")
    a.append(" ")
    for traj in edge.traj_hashList:
        a.append(traj.merge_hash)
    return a

def edge_vo_hash(edge):
    a = []
    str1 = str(edge.start.lng)
    str2 = str(edge.start.lat)
    str3 = str(edge.end.lng)
    str4 = str(edge.end.lat)
    a.append(str1)
    a.append(str2)
    a.append(str3)
    a.append(str4)
    for traj in edge.traj_hashList:
        a.append(" ")
    return a

