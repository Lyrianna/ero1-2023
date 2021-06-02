import numpy as np
from directed_chinese_postman_problem import CPP


def main():
    # dir_mat = np.matrix([
    #     [0, 2, 0, 0, 4],
    #     [0, 0, 1, 0, 0],
    #     [0, 0, 0, 3, 5],
    #     [5, 0, 0, 0, 0],
    #     [0, 0, 0, 6, 0],
    # ])
    # print(dir_mat)
    #
    # res = dcpp(5, dir_mat)
    # print(res)

    cpp_graph = CPP(4)
    cpp_graph.add_arcs([
        (0, 1, 1),
        (0, 2, 1),
        (1, 2, 1),
        (1, 3, 1),
        (2, 3, 1),
        (3, 0, 1),
    ])  # Start at 0

    # cpp_graph = CPP(5)
    # cpp_graph.add_arcs([
    #     (0, 1, 2),
    #     (0, 4, 4),
    #     (1, 2, 1),
    #     (2, 3, 3),
    #     (2, 4, 5),
    #     (3, 0, 5),
    #     (4, 3, 6),
    # ])

    cpp_graph.solve()
    path = cpp_graph.get_optimal_path(start_v=0)
    print(path)
    print('cost: ', cpp_graph.cost())


if __name__ == '__main__':
    main()
