import os
import time
import gvanim
import imageio
import osmnx as ox

import utils


def render_path_as_gif(initial_graph_edges, path,
                       img_size=1000, duration_between_steps=0.8, edge_batch_size=1):
    """
    Render final path as a gif (optional)
    """
    ga = gvanim.Animation()
    for edge in initial_graph_edges:
        ga.add_edge(edge[0], edge[1])
    ga.next_step()

    visit_times = {}
    for edge in path:
        edge = utils.normalize_pair(*edge)
        visit_times[edge] = 0

    drawn_path = []

    def draw_path():
        for edge in drawn_path:
            if visit_times[edge] > 1:
                ga.highlight_edge(*edge, color='blue')
            else:
                ga.highlight_edge(*edge, color='red')

    # for raw_edge in path:
    #     new_edge = utils.normalize_pair(*raw_edge)
    #     draw_path()
    #     ga.highlight_edge(*new_edge, color='red')
    #     drawn_path.append(new_edge)
    #     visit_times[new_edge] += 1
    #     ga.next_step()

    cs = edge_batch_size  # Chunk size to process paths by
    for chunk in [path[cs * i:cs * (i + 1)] for i in range(len(path) // cs + 1)]:
        for raw_edge in chunk:
            new_edge = utils.normalize_pair(*raw_edge)
            drawn_path.append(new_edge)
            visit_times[new_edge] += 1
        draw_path()
        ga.highlight_edge(*drawn_path[-1], color='yellow')  # Mark last visited edge in red
        ga.next_step()

    # Final result
    draw_path()
    ga.next_step()

    render_directory = 'render_files'
    os.makedirs(render_directory)

    ga_graphs = ga.graphs()
    files = gvanim.render(ga_graphs, f'{render_directory}/step', 'png', size=img_size)
    render_filename = 'render.gif'
    with imageio.get_writer(render_filename, mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)

    print(f'Final path rendering available at "src/theoric_app/{render_filename}"')


def render_osmnx_path(osmnx_graph, edge_path, duration_between_steps=0.5, step_size=1, edge_width=1.0):

    time_stamp = int(time.time())
    output_dir = f'render_files_{time_stamp}'
    os.makedirs(output_dir)

    visit_times = {}
    for edge in edge_path:
        visit_times[utils.normalize_pair(*edge)] = 0

    def get_edge_color(path, u, v, highlight_last=False):
        if highlight_last and ((u, v) == path[-1] or (v, u) == path[-1]):  # Highlight last visited edge
            return 'yellow'
        if visit_times.get(utils.normalize_pair(u, v), 0) > 1:  # Already visited edge
            return 'blue'
        if (u, v) in path or (v, u) in path:  # Visited edge
            return 'red'
        return 'w'

    def get_edge_colors(path, highlight_last=False):
        return [get_edge_color(path, u, v, highlight_last) for (u, v) in osmnx_graph.edges()]

    files = []

    def render_path(path, filename, highlight_last=False):
        edge_colors = get_edge_colors(path, highlight_last)
        ox.plot_graph(osmnx_graph, node_color='w', node_edgecolor='k', node_size=0, node_zorder=3,
                      edge_color=edge_colors, edge_linewidth=edge_width,
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
            visit_times[utils.normalize_pair(*edge)] += 1

    # Render final step
    render_path(edge_path, f'{output_dir}/step_{len(edge_path)}.png')

    print(files)

    # Render final gif
    with imageio.get_writer(f'osmnx_render_{time_stamp}.gif', mode='I', duration=duration_between_steps) as writer:
        for file in files:
            image = imageio.imread(file)
            writer.append_data(image)

    print(output_dir)
