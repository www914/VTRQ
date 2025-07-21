import ast
import hashlib
import json
import csv
import unittest

BLACK = 0
RED = 1


class Interval:
    def __init__(self, low, high):
        self.low = low
        self.high = high


class IntervalTNode:
    def __init__(self, key, inte, traj_hash="", merge_hash=""):
        self.key = key
        self.color = RED
        self.parent = None
        self.left = None
        self.right = None
        self.inte = inte
        self.max = inte.high
        self.min = inte.low
        self.traj_hash = traj_hash  # 添加字符串属性
        self.merge_hash = merge_hash



class IntervalTree:
    def __init__(self):
        self.NIL = IntervalTNode(-1, Interval(-1, -1))
        self.NIL.color = BLACK
        self.NIL.max = -1
        self.NIL.min = float('inf')   # 初始化 NIL 节点的 min 值
        self.root = self.NIL

    @staticmethod
    def max_of_three(a, b, c):
        return max(a, max(b, c))

    @staticmethod
    def min_of_three(a, b, c):
        return min(a, min(b, c))

    @staticmethod
    def overlap(a, b):
        return not (a.high < b.low or a.low > b.high)

    def interval_t_search(self, i):
        x = self.root
        while x != self.NIL:
            if x.inte.low == i.low and x.inte.high == i.high:
                return x
            elif i.low < x.inte.low:
                x = x.left
            else:
                x = x.right
        return self.NIL

    def interval_t_inorder_walk(self, x, count=0):
        if x != self.NIL:
            # 递归遍历左子树
            count = self.interval_t_inorder_walk(x.left, count)
            color_str = "Red" if x.color == RED else "Black"
            print(f"[{x.inte.low:3d} {x.inte.high:3d}]     {color_str}     {x.min}   {x.max}  ")
            # 每输出一次，计数器加一
            count += 1
            # 递归遍历右子树
            count = self.interval_t_inorder_walk(x.right, count)
        return count


    def interval_t_minimum(self, x):
        if x.left:
            while x.left != self.NIL:
                x = x.left
            return x

    def interval_t_successor(self, x):
        if x.right != self.NIL:
            return self.interval_t_minimum(x.right)
        y = x.parent
        while y != self.NIL and x == y.right:
            x = y
            y = y.parent
        return y

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        y.max = x.max
        y.min = x.min
        x.max = self.max_of_three(x.inte.high, x.left.max, x.right.max)
        x.min = self.min_of_three(x.inte.low, x.left.min, x.right.min)

    def right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.right = x
        x.parent = y
        y.max = x.max
        y.min = x.min
        x.max = self.max_of_three(x.inte.high, x.left.max, x.right.max)
        x.min = self.min_of_three(x.inte.low, x.left.min, x.right.min)

    def interval_t_insert_fixup(self, z):
        while z.parent.color == RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self.left_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self.right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.left_rotate(z.parent.parent)
        self.root.color = BLACK

    def interval_t_insert(self, inte, traj_hash="", merge_hash=""):
        z = IntervalTNode(inte.low, inte, traj_hash, merge_hash)
        y = self.NIL
        x = self.root
        while x != self.NIL:
            x.max = max(x.max, z.max)
            x.min = min(x.min, z.min)
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y == self.NIL:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        z.left = self.NIL
        z.right = self.NIL
        self.interval_t_insert_fixup(z)
        # 更新祖先节点的 min 和 max
        current = z.parent
        while current != self.NIL:
            current.max = self.max_of_three(current.inte.high, current.left.max, current.right.max)
            current.min = self.min_of_three(current.inte.low, current.left.min, current.right.min)
            current = current.parent

    def interval_t_delete_fixup(self, x):
        while x != self.root and x.color == BLACK:
            if x == x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self.left_rotate(x.parent)
                    w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self.right_rotate(w)
                        w = x.parent.right
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self.left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self.right_rotate(x.parent)
                    w = x.parent.left
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self.left_rotate(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self.right_rotate(x.parent)
                    x = self.root
        x.color = BLACK

    def interval_t_delete(self, z):
        if z.left == self.NIL or z.right == self.NIL:
            y = z
        else:
            y = self.interval_t_successor(z)

        g = y.parent
        while g != self.NIL and g:
            g.max = self.max_of_three(g.inte.high, g.left.max, g.right.max)
            g.min = self.min_of_three(g.inte.low, g.left.min, g.right.min)
            g = g.parent

        if y.left != self.NIL:
            x = y.left
        else:
            x = y.right
        x.parent = y.parent

        if y.parent == self.NIL:
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x

        if y != z:
            z.key = y.key
            z.inte = y.inte
            z.max = y.max
            z.min = y.min
            z.traj_hash = y.traj_hash  # 同步字符串数据
            z.merge_hash = y.merge_hash
            z.traj = y.traj

        if y.color == BLACK:
            self.interval_t_delete_fixup(x)

        # 更新祖先节点的 min 和 max
        current = x.parent
        while current != self.NIL:
            current.max = self.max_of_three(current.inte.high, current.left.max, current.right.max)
            current.min = self.min_of_three(current.inte.low, current.left.min, current.right.min)
            current = current.parent

    # def search_intersecting_intervals(self, query):
    #     tra = []
    #     a = []
    #     traj = set()
    #
    #     with open(f'vo_time.csv', 'a', newline='') as csvfile:
    #         writer = csv.writer(csvfile)
    #
    #         def _search(x):
    #             if x == self.NIL:
    #                 return
    #
    #             tra.append(x)
    #             if x.max < query.low or x.min > query.high:
    #                 a = list(tra)
    #                 ver = self.verify_hash_collect3(a)
    #                 writer.writerow([ver, [str(x.min), str(x.max)]])
    #                 tra.pop()
    #                 return
    #
    #             if self.overlap(x.inte, query):
    #                 traj.add(x.traj_hash)
    #                 a = list(tra)
    #                 ver = self.verify_hash_collect1(a)
    #                 writer.writerow([ver,[x.traj_hash]])
    #                 # print(f"数据已成功写入到 vo_time.csv 文件中")
    #
    #             else:
    #                 a = list(tra)
    #                 ver = self.verify_hash_collect2(a)
    #                 writer.writerow([ver,[str(x.inte.low),str(x.inte.high)]])
    #                 # print(f"数据已成功写入到 vo_time.csv 文件中")
    #
    #
    #
    #             if x.left != self.NIL and x.left.max >= query.low:
    #                 _search(x.left)
    #             elif x.left != self.NIL and x.left.max < query.low:
    #                 t = x.left
    #                 tra.append(t)
    #                 a = list(tra)
    #                 ver = self.verify_hash_collect3(a)
    #                 tra.pop()
    #                 writer.writerow([ver,[str(t.min),str(t.max)]])
    #                 # print(f"数据已成功写入到 vo_time.csv 文件中")
    #
    #             if x.right != self.NIL and x.right.min <= query.high:
    #                 _search(x.right)
    #             elif x.right != self.NIL and x.right.min > query.high:
    #                 t = x.right  # 修正为 x.txt.right
    #                 tra.append(t)
    #                 a = list(tra)
    #                 ver = self.verify_hash_collect3(a)
    #                 tra.pop()
    #                 writer.writerow([ver,[str(t.min),str(t.max)]])
    #                 # print(f"数据已成功写入到 vo_time.csv 文件中")
    #             tra.pop()
    #
    #         _search(self.root)
    #     return traj

    def search_intersecting_intervals(self, query):
        tra = []
        a = []
        traj = set()
        output_rows = []  # 存储所有待写入的行

        def _search(x):
            if x == self.NIL:
                return

            tra.append(x)
            if x.max < query.low or x.min > query.high:
                a = list(tra)
                ver = self.verify_hash_collect3(a)
                output_rows.append([ver, [str(x.min), str(x.max)]])
                tra.pop()
                return

            if self.overlap(x.inte, query):
                traj.add(x.traj_hash)
                a = list(tra)
                ver = self.verify_hash_collect1(a)
                output_rows.append([ver, [x.traj_hash]])
            else:
                a = list(tra)
                ver = self.verify_hash_collect2(a)
                output_rows.append([ver, [str(x.inte.low), str(x.inte.high)]])

            if x.left != self.NIL and x.left.max >= query.low:
                _search(x.left)
            elif x.left != self.NIL and x.left.max < query.low:
                t = x.left
                tra.append(t)
                a = list(tra)
                ver = self.verify_hash_collect3(a)
                tra.pop()
                output_rows.append([ver, [str(t.min), str(t.max)]])

            if x.right != self.NIL and x.right.min <= query.high:
                _search(x.right)
            elif x.right != self.NIL and x.right.min > query.high:
                t = x.right
                tra.append(t)
                a = list(tra)
                ver = self.verify_hash_collect3(a)
                tra.pop()
                output_rows.append([ver, [str(t.min), str(t.max)]])
            tra.pop()

        _search(self.root)

        # 一次性写入所有收集的数据
        with open(f'vo_time.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(output_rows)

        return traj


    # 注意
    def node_to_dict(self, node):
        if node == self.NIL:
            return None
        return {
            "color": node.color,
            "key": node.key,
            "interval": [node.inte.low, node.inte.high],
            "max": node.max,
            "min": node.min,  # 包含 min 值
            "traj_hash": node.traj_hash,  # 包含字符串数据
            "merge_hash": node.merge_hash,
            "left": self.node_to_dict(node.left),
            "right": self.node_to_dict(node.right)
        }

    def save_to_json(self, filename):
        tree_dict = self.node_to_dict(self.root)
        with open(filename, 'w') as f:
            json.dump(tree_dict, f, indent=4)

    @staticmethod
    def dict_to_node(tree_dict, NIL):
        if tree_dict is None:
            return NIL
        inte = Interval(tree_dict["interval"][0], tree_dict["interval"][1])
        node = IntervalTNode(tree_dict["key"], inte, tree_dict.get("traj_hash", ""), tree_dict.get("merge_hash", ""))
        node.color = tree_dict["color"]
        node.max = tree_dict["max"]
        node.min = tree_dict["min"]
        node.left = IntervalTree.dict_to_node(tree_dict["left"], NIL)
        node.right = IntervalTree.dict_to_node(tree_dict["right"], NIL)
        if node.left != NIL:
            node.left.parent = node
        if node.right != NIL:
            node.right.parent = node
        return node

    @classmethod
    def load_from_json(cls, filename):
        with open(filename, 'r') as f:
            tree_dict = json.load(f)
        tree = cls()
        tree.root = cls.dict_to_node(tree_dict, tree.NIL)
        if tree.root != tree.NIL:
            tree.root.parent = tree.NIL
        return tree

    def trag_hash_merge(self, x):
        if x != self.NIL:
            self.trag_hash_merge(x.left)
            self.trag_hash_merge(x.right)
            # print(f"[{x.txt.inte.low:3d} {x.txt.inte.high:3d}] {x.txt.traj_hash} {x.txt.merage_hash}")
            # 如果这棵树的左右孩子至少有一个不是空的，则说明不是叶子节点，要计算merage_hash
            if x.left != self.NIL or x.right != self.NIL:
                if x.left != self.NIL:
                    str_interval_node = str(x.left.min) + str(x.left.max) + str(x.left.inte.low) + str(x.left.inte.high) + x.left.traj_hash + x.left.merge_hash
                    x.merge_hash = x.merge_hash + str_interval_node
                if x.right != self.NIL:
                    str_interval_node = str(x.right.min) + str(x.right.max) + str(x.right.inte.low) + str(x.right.inte.high) + x.right.traj_hash + x.right.merge_hash
                    x.merge_hash = x.merge_hash + str_interval_node
                encoded_data = x.merge_hash.encode('utf-8')
                hash_object = hashlib.sha256(encoded_data)
                hash_hex = hash_object.hexdigest()
                x.merge_hash = hash_hex


    def root_hash(self):
        # 这个地方到时候要改成hash计算
        interval_tree_root_hash = str(self.root.min) + str(self.root.max) + str(self.root.inte.low) + str(self.root.inte.high) + self.root.traj_hash + self.root.merge_hash

        encoded_data = interval_tree_root_hash.encode('utf-8')
        hash_object = hashlib.sha256(encoded_data)
        hash_hex = hash_object.hexdigest()
        interval_tree_root_hash = hash_hex
        return interval_tree_root_hash

    # 收集如果是查到轨迹的验证结果
    def verify_hash_collect1(self, interval_tree_path):
        # 先把目标节点出栈
        # print(interval_tree_path)
        stack = []
        flag = interval_tree_path.pop()
        a = []
        if flag == self.root:
            a.append(str(flag.min))
            a.append(str(flag.max))
            a.append(str(flag.inte.low))
            a.append(str(flag.inte.high))
            a.append(" ")
            a.append(flag.merge_hash)
        # 这个标记节点是父节点的左孩子
        if interval_tree_path:
            if interval_tree_path[-1].left != self.NIL and flag == interval_tree_path[-1].left:
                a.append(str(flag.min))
                a.append(str(flag.max))
                a.append(str(flag.inte.low))
                a.append(str(flag.inte.high))
                a.append(" ")
                a.append(flag.merge_hash)
                if interval_tree_path[-1].right != self.NIL:
                    a.append(str(interval_tree_path[-1].right.min))
                    a.append(str(interval_tree_path[-1].right.max))
                    a.append(str(interval_tree_path[-1].right.inte.low))
                    a.append(str(interval_tree_path[-1].right.inte.high))
                    a.append(interval_tree_path[-1].right.traj_hash)
                    a.append(interval_tree_path[-1].right.merge_hash)

            elif interval_tree_path[-1].right != self.NIL and flag == interval_tree_path[-1].right:
                if interval_tree_path[-1].left != self.NIL:
                    a.append(str(interval_tree_path[-1].left.min))
                    a.append(str(interval_tree_path[-1].left.max))
                    a.append(str(interval_tree_path[-1].left.inte.low))
                    a.append(str(interval_tree_path[-1].left.inte.high))
                    a.append(interval_tree_path[-1].left.traj_hash)
                    a.append(interval_tree_path[-1].left.merge_hash)
                    a.append(str(flag.min))
                    a.append(str(flag.max))
                    a.append(str(flag.inte.low))
                    a.append(str(flag.inte.high))
                    a.append(" ")
                    a.append(flag.merge_hash)
                else:
                    a.append(str(flag.min))
                    a.append(str(flag.max))
                    a.append(str(flag.inte.low))
                    a.append(str(flag.inte.high))
                    a.append(" ")
                    a.append(flag.merge_hash)
        stack.append(a)

        while interval_tree_path:
            b = []
            flag = interval_tree_path.pop()
            # 如果是空
            if not interval_tree_path:
                b.append(str(flag.min))
                b.append(str(flag.max))
                b.append(str(flag.inte.low))
                b.append(str(flag.inte.high))
                b.append(flag.traj_hash)
                b.append(" ")
            if interval_tree_path:
                if interval_tree_path[-1].left != self.NIL and flag == interval_tree_path[-1].left:
                    b.append(str(flag.min))
                    b.append(str(flag.max))
                    b.append(str(flag.inte.low))
                    b.append(str(flag.inte.high))
                    b.append(flag.traj_hash)
                    b.append(" ")
                    if interval_tree_path[-1].right != self.NIL:
                        b.append(str(interval_tree_path[-1].right.min))
                        b.append(str(interval_tree_path[-1].right.max))
                        b.append(str(interval_tree_path[-1].right.inte.low))
                        b.append(str(interval_tree_path[-1].right.inte.high))
                        b.append(interval_tree_path[-1].right.traj_hash)
                        b.append(interval_tree_path[-1].right.merge_hash)

                if interval_tree_path[-1].right != self.NIL and flag == interval_tree_path[-1].right:
                    if interval_tree_path[-1].left != self.NIL:
                        b.append(str(interval_tree_path[-1].left.min))
                        b.append(str(interval_tree_path[-1].left.max))
                        b.append(str(interval_tree_path[-1].left.inte.low))
                        b.append(str(interval_tree_path[-1].left.inte.high))
                        b.append(interval_tree_path[-1].left.traj_hash)
                        b.append(interval_tree_path[-1].left.merge_hash)
                    b.append(str(flag.min))
                    b.append(str(flag.max))
                    b.append(str(flag.inte.low))
                    b.append(str(flag.inte.high))
                    b.append(flag.traj_hash)
                    b.append(" ")
            stack.append(b)
        return stack


    # 收集时间戳不在查询范围内的验证
    def verify_hash_collect2(self, interval_tree_path):
        # 先把目标节点出栈
        # print(interval_tree_path)
        stack = []
        flag = interval_tree_path.pop()
        a = []
        if flag == self.root:
            a.append(str(flag.min))
            a.append(str(flag.max))
            a.append(" ")
            a.append(" ")
            a.append(flag.traj_hash)  # 保持原始类型
            a.append(flag.merge_hash)  # 保持原始类型
        # 这个标记节点是父节点的左孩子
        if interval_tree_path:
            if interval_tree_path[-1].left != self.NIL and flag == interval_tree_path[-1].left:
                a.append(str(flag.min))
                a.append(str(flag.max))
                a.append(" ")
                a.append(" ")
                a.append(flag.traj_hash)  # 保持原始类型
                a.append(flag.merge_hash)  # 保持原始类型
                if interval_tree_path[-1].right != self.NIL:
                    a.append(str(interval_tree_path[-1].right.min))
                    a.append(str(interval_tree_path[-1].right.max))
                    a.append(str(interval_tree_path[-1].right.inte.low))
                    a.append(str(interval_tree_path[-1].right.inte.high))
                    a.append(interval_tree_path[-1].right.traj_hash)  # 保持原始类型
                    a.append(interval_tree_path[-1].right.merge_hash)  # 保持原始类型

            elif interval_tree_path[-1].right != self.NIL and flag == interval_tree_path[-1].right:
                if interval_tree_path[-1].left != self.NIL:
                    a.append(str(interval_tree_path[-1].left.min))
                    a.append(str(interval_tree_path[-1].left.max))
                    a.append(str(interval_tree_path[-1].left.inte.low))
                    a.append(str(interval_tree_path[-1].left.inte.high))
                    a.append(interval_tree_path[-1].left.traj_hash)  # 保持原始类型
                    a.append(interval_tree_path[-1].left.merge_hash)  # 保持原始类型
                    a.append(str(flag.min))
                    a.append(str(flag.max))
                    a.append(" ")
                    a.append(" ")
                    a.append(flag.traj_hash)  # 保持原始类型
                    a.append(flag.merge_hash)  # 保持原始类型
                else:
                    a.append(str(flag.min))
                    a.append(str(flag.max))
                    a.append(" ")
                    a.append(" ")
                    a.append(flag.traj_hash)  # 保持原始类型
                    a.append(flag.merge_hash)  # 保持原始类型
        stack.append(a)

        while interval_tree_path:
            b = []
            flag = interval_tree_path.pop()
            # 如果是空
            if not interval_tree_path:
                b.append(str(flag.min))
                b.append(str(flag.max))
                b.append(str(flag.inte.low))
                b.append(str(flag.inte.high))
                b.append(flag.traj_hash)  # 保持原始类型
                b.append(" ")
            if interval_tree_path:
                if interval_tree_path[-1].left != self.NIL and flag == interval_tree_path[-1].left:
                    b.append(str(flag.min))
                    b.append(str(flag.max))
                    b.append(str(flag.inte.low))
                    b.append(str(flag.inte.high))
                    b.append(flag.traj_hash)  # 保持原始类型
                    b.append(" ")
                    if interval_tree_path[-1].right != self.NIL:
                        b.append(str(interval_tree_path[-1].right.min))
                        b.append(str(interval_tree_path[-1].right.max))
                        b.append(str(interval_tree_path[-1].right.inte.low))
                        b.append(str(interval_tree_path[-1].right.inte.high))
                        b.append(interval_tree_path[-1].right.traj_hash)  # 保持原始类型
                        b.append(interval_tree_path[-1].right.merge_hash)  # 保持原始类型

                if interval_tree_path[-1].right != self.NIL and flag == interval_tree_path[-1].right:
                    if interval_tree_path[-1].left != self.NIL:
                        b.append(str(interval_tree_path[-1].left.min))
                        b.append(str(interval_tree_path[-1].left.max))
                        b.append(str(interval_tree_path[-1].left.inte.low))
                        b.append(str(interval_tree_path[-1].left.inte.high))
                        b.append(interval_tree_path[-1].left.traj_hash)  # 保持原始类型
                        b.append(interval_tree_path[-1].left.merge_hash)  # 保持原始类型
                    b.append(str(flag.min))
                    b.append(str(flag.max))
                    b.append(str(flag.inte.low))
                    b.append(str(flag.inte.high))
                    b.append(flag.traj_hash)  # 保持原始类型
                    b.append(" ")
            stack.append(b)
        return stack

    # 收集查询时候剪枝的查询证明
    def verify_hash_collect3(self, interval_tree_path):
        # 先把目标节点出栈
        # print(interval_tree_path)
        stack = []
        flag = interval_tree_path.pop()
        a = []
        if flag == self.root:
            a.append(" ")
            a.append(" ")
            a.append(str(flag.inte.low))
            a.append(str(flag.inte.high))
            a.append(flag.traj_hash)  # 保持原始类型
            a.append(flag.merge_hash)  # 保持原始类型
        # 这个标记节点是父节点的左孩子
        if interval_tree_path:
            if interval_tree_path[-1].left != self.NIL and flag == interval_tree_path[-1].left:
                a.append(" ")
                a.append(" ")
                a.append(str(flag.inte.low))
                a.append(str(flag.inte.high))
                a.append(flag.traj_hash)  # 保持原始类型
                a.append(flag.merge_hash)  # 保持原始类型
                if interval_tree_path[-1].right != self.NIL:
                    a.append(str(interval_tree_path[-1].right.min))
                    a.append(str(interval_tree_path[-1].right.max))
                    a.append(str(interval_tree_path[-1].right.inte.low))
                    a.append(str(interval_tree_path[-1].right.inte.high))
                    a.append(interval_tree_path[-1].right.traj_hash)  # 保持原始类型
                    a.append(interval_tree_path[-1].right.merge_hash)  # 保持原始类型

            elif interval_tree_path[-1].right != self.NIL and flag == interval_tree_path[-1].right:
                if interval_tree_path[-1].left != self.NIL:
                    a.append(str(interval_tree_path[-1].left.min))
                    a.append(str(interval_tree_path[-1].left.max))
                    a.append(str(interval_tree_path[-1].left.inte.low))
                    a.append(str(interval_tree_path[-1].left.inte.high))
                    a.append(interval_tree_path[-1].left.traj_hash)  # 保持原始类型
                    a.append(interval_tree_path[-1].left.merge_hash)  # 保持原始类型
                    a.append(" ")
                    a.append(" ")
                    a.append(str(flag.inte.low))
                    a.append(str(flag.inte.high))
                    a.append(flag.traj_hash)  # 保持原始类型
                    a.append(flag.merge_hash)  # 保持原始类型
                else:
                    a.append(" ")
                    a.append(" ")
                    a.append(str(flag.inte.low))
                    a.append(str(flag.inte.high))
                    a.append(flag.traj_hash)  # 保持原始类型
                    a.append(flag.merge_hash)  # 保持原始类型
        stack.append(a)

        while interval_tree_path:
            b = []
            flag = interval_tree_path.pop()
            # 如果是空
            if not interval_tree_path:
                b.append(str(flag.min))
                b.append(str(flag.max))
                b.append(str(flag.inte.low))
                b.append(str(flag.inte.high))
                b.append(flag.traj_hash)  # 保持原始类型
                b.append(" ")
            if interval_tree_path:
                if interval_tree_path[-1].left != self.NIL and flag == interval_tree_path[-1].left:
                    b.append(str(flag.min))
                    b.append(str(flag.max))
                    b.append(str(flag.inte.low))
                    b.append(str(flag.inte.high))
                    b.append(flag.traj_hash)  # 保持原始类型
                    b.append(" ")
                    if interval_tree_path[-1].right != self.NIL:
                        b.append(str(interval_tree_path[-1].right.min))
                        b.append(str(interval_tree_path[-1].right.max))
                        b.append(str(interval_tree_path[-1].right.inte.low))
                        b.append(str(interval_tree_path[-1].right.inte.high))
                        b.append(interval_tree_path[-1].right.traj_hash)  # 保持原始类型
                        b.append(interval_tree_path[-1].right.merge_hash)  # 保持原始类型

                if interval_tree_path[-1].right != self.NIL and flag == interval_tree_path[-1].right:
                    if interval_tree_path[-1].left != self.NIL:
                        b.append(str(interval_tree_path[-1].left.min))
                        b.append(str(interval_tree_path[-1].left.max))
                        b.append(str(interval_tree_path[-1].left.inte.low))
                        b.append(str(interval_tree_path[-1].left.inte.high))
                        b.append(interval_tree_path[-1].left.traj_hash)  # 保持原始类型
                        b.append(interval_tree_path[-1].left.merge_hash)  # 保持原始类型
                    b.append(str(flag.min))
                    b.append(str(flag.max))
                    b.append(str(flag.inte.low))
                    b.append(str(flag.inte.high))
                    b.append(flag.traj_hash)  # 保持原始类型
                    b.append(" ")
            stack.append(b)
        return stack


def proof_root_hash(verify_hash_list):
        # print(verify_hash_list)
        verify_hash_list.reverse()
        a = verify_hash_list.pop()
        str1 = ""
        for i in a:
            str1 = str1 + i
        encoded_data = str1.encode('utf-8')
        hash_object = hashlib.sha256(encoded_data)
        str1 = hash_object.hexdigest()
        # print(str1)

        while verify_hash_list:
            a = verify_hash_list.pop()
            str2 = ""
            for i in a:
                if i == " ":
                    str2 = str2 + str1
                else:
                    str2 = str2 + i
            encoded_data = str2.encode('utf-8')
            hash_object = hashlib.sha256(encoded_data)
            str2 = hash_object.hexdigest()
            str1 = str2
        # print(str1)
        return str1


def proof_interval(filename):
    file_path = filename
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            col1 = ast.literal_eval(row[0])
            col2 = ast.literal_eval(row[1])
            if len(col2) == 1:
                i = 0
                for j in col1[0]:
                    if j == " ":
                         col1[0][i] = col2[0]
                         break
                    i = i + 1
                if proof_root_hash(col1) != "12d88230b3d2070cb048f981212705b3bca05bd06fe21346ccfca7404e8b36ea":
                    print("验证失败")
                    return
            if len(col2) == 2:
                i = 0
                p = 0
                for j in col1[0]:
                    if j == " ":
                         col1[0][i] = col2[p]
                         p = p + 1
                         if p == 2:
                             break
                    i = i + 1
                if proof_root_hash(col1) != "12d88230b3d2070cb048f981212705b3bca05bd06fe21346ccfca7404e8b36ea":
                    print("验证失败")
                    return
    return True


if __name__ == "__main__":

    A = [Interval(16, 21), Interval(8, 9), Interval(25, 30), Interval(5, 8),
             Interval(15, 23), Interval(17, 19), Interval(26, 26),
             Interval(0, 3), Interval(6, 10), Interval(19, 20)]
    str_list = ["data1", "data2", "data3", "data4", "data5", "data6", "data7", "data8", "data9", "data10"]
    # str_list1 = ["data11", "data21", "data31", "data41", "data51", "data61", "data71", "data81", "data91", "data101"]
    n = len(A)

    T = IntervalTree()
    for i in range(n):
        T.interval_t_insert(A[i], str_list[i])
    T.interval_t_inorder_walk(T.root)
