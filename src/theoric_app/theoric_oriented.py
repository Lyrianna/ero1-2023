import numpy as np
from directed_chinese_postman_problem_v1 import dcpp
from directed_chinese_postman_problem_v2 import CPP


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

    graph = CPP(4)
    graph.add_arcs([
        (0, 1, 1),
        (0, 2, 1),
        (1, 2, 1),
        (1, 3, 1),
        (2, 3, 1),
        (3, 0, 1),
    ])

    graph.solve()
    graph.print_cpp(start_v=0)
    print('cost: ', graph.cost())


if __name__ == '__main__':
    main()
