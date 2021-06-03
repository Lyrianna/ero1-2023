import os
import time
import imageio

import osmnx as ox


def render_osmnx_path(osmnx_graph, edge_path, duration_between_steps=0.5, step_size=1, edge_width=1.0):

    time_stamp = int(time.time())
    output_dir = f'render_files_{time_stamp}'
    os.makedirs(output_dir)

    visit_times = {}
    for edge in edge_path:
        visit_times[edge] = 0

    def get_edge_color(path, edge, highlight_last=False):
        if highlight_last and edge == path[-1]:  # Highlight last visited edge
            return 'yellow'
        if visit_times.get(edge, 0) > 1:  # Already visited edge
            return 'blue'
        if edge in path:  # Visited edge
            return 'red'
        return 'w'

    def get_edge_colors(path, highlight_last=False):
        return [get_edge_color(path, edge, highlight_last) for edge in osmnx_graph.edges()]

    files = []

    def render_path(path, filename, highlight_last=False):
        edge_colors = get_edge_colors(path, highlight_last)
        ox.plot_graph(osmnx_graph, node_color='w', node_edgecolor='k', node_size=0, node_zorder=3,
                      edge_color=edge_colors, edge_linewidth=edge_width, edge_alpha=0.5,
                      show=False, close=True, save=True, filepath=filename)
        files.append(filename)

    # # Render step by step
    # for i in range(len(edge_path)):
    #     current_path = edge_path[:(i + 1)]
    #     render_path(current_path, f'{output_dir}/step_{i:05}.png', highlight_last=True)
    #     visit_times[utils.normalize_pair(*edge_path[i])] += 1  # Update last visited pair

    # Render by big steps
    for i in range(len(edge_path) // step_size + 1):
        start_i, end_i = step_size * i, step_size * (i + 1)
        current_path = edge_path[:end_i]
        render_path(current_path, f'{output_dir}/step_{i:05}.png', highlight_last=True)
        for edge in edge_path[start_i:end_i]:
            visit_times[edge] += 1

    # Render final step
    render_path(edge_path, f'{output_dir}/step_{len(edge_path)+1:05}.png')

    print(files)

    # Render final gif
    with imageio.get_writer(f'osmnx_render_{time_stamp}.gif', mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)

    print(output_dir)
