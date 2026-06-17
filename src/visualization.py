import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import HTML
import numpy as np

plt.rcParams['animation.embed_limit'] = 500.0

def _multi_algorithm_generator_wrapper(solver_instance, candidate_indices, end_idx, skip_frames=15):
    """
    Transforms the sequential execution of multiple shortest-path searches 
    into a continuous generator for matplotlib animation.
    """
    frames = []
    best_overall_distance = float('inf')
    best_overall_path = []

    history_paths = []

    for candidate_idx in candidate_indices:
        frame_counter = 0

        # Hook: capturing the spread of the algorithm
        def capture_frame(visited_set, current_vertex):
            nonlocal frame_counter
            if frame_counter % skip_frames == 0:
                frames.append({
                    "state": "searching",
                    "visited": visited_set.copy(),
                    "head": current_vertex,
                    "current_path": [],
                    "best_path": best_overall_path,
                    "history_paths": list(history_paths)
                })
            frame_counter += 1

        # Execute the solver for the current candidate
        distance, path = solver_instance.find_shortest_path(candidate_idx, end_idx, on_visit_callback=capture_frame)

        # Update the best global path if this candidate is better
        if distance < best_overall_distance:
            best_overall_distance = distance
            best_overall_path = path

        # Pause: show the path found by this candidate for a few frames before the next search
        for _ in range(15):
            frames.append({
                "state": "found",
                "visited": set(), # Clears the red dot spread
                "head": None,
                "current_path": path,
                "best_path": best_overall_path,
                "history_paths": list(history_paths)
            })
        if path:
            history_paths.append(path)

    # Final Pause: show only the absolute best path found across all candidates
    for _ in range(30):
        frames.append({
            "state": "finished",
            "visited": set(),
            "head": None,
            "current_path": [],
            "best_path": best_overall_path,
            "history_paths": list(history_paths)
        })

    for frame in frames:
        yield frame


def animate_algorithm(G, solver_instance, origin_graph_node, dest_graph_node, dest_idx, candidate_indices, index_to_node, walk_radius):
    """
    Creates an HTML5 video animation iterating over multiple candidate start nodes.
    """
    fig, ax = ox.plot_graph(
        G, 
        node_size=0,
        edge_color="#333333",
        edge_linewidth=0.5,
        bgcolor="#111111",
        show=False,
        close=False
    )

    origin_x = G.nodes[origin_graph_node]['x']
    origin_y = G.nodes[origin_graph_node]['y']
    dest_x = G.nodes[dest_graph_node]['x']
    dest_y = G.nodes[dest_graph_node]['y']

    # 1. Draw the Search Radius (Approximation: 1 degree latitude ~ 111,320 meters)
    radius_deg = walk_radius / 111320.0
    circle = plt.Circle((origin_x, origin_y), radius_deg, color='white', fill=False, linestyle='--', alpha=0.3, zorder=2)
    ax.add_patch(circle)

    # 2. Draw static markers
    ax.scatter([origin_x], [origin_y], c='#FFFFFF', s=80, zorder=10, marker='*', label='Origem Real')
    ax.scatter([dest_x], [dest_y], c='#00BFFF', s=100, zorder=10, marker='X', label='Destino')

    candidate_graph_nodes = [index_to_node[idx] for idx in candidate_indices]
    cx = [G.nodes[n]['x'] for n in candidate_graph_nodes]
    cy = [G.nodes[n]['y'] for n in candidate_graph_nodes]
    ax.scatter(cx, cy, c='purple', s=40, alpha=0.8, zorder=3, label='Candidatos')

    # 3. Setup dynamic scatter objects and line paths
    scat_visited = ax.scatter([], [], c='#FF4500', s=15, alpha=0.5, zorder=5)
    
    history_lines = [
        ax.plot([], [], c='#FFD700', linewidth=2, alpha=0.5, zorder=6)[0]
        for _ in range(len(candidate_indices))
    ]
    
    current_path_line, = ax.plot([], [], c='cyan', linewidth=2, zorder=7, alpha=0.8)
    best_path_line, = ax.plot([], [], c='#00FF00', linewidth=3, zorder=8)

    # Helper function to convert solver indices to map coordinates
    def get_coords(path_indices):
        if not path_indices:
            return [], []
        graph_nodes = [index_to_node[idx] for idx in path_indices]
        return [G.nodes[n]['x'] for n in graph_nodes], [G.nodes[n]['y'] for n in graph_nodes]

    algo_generator = _multi_algorithm_generator_wrapper(solver_instance, candidate_indices, dest_idx, skip_frames=15)

    def update(frame_data):
        state = frame_data["state"]

        if state == "searching":
            vx, vy = get_coords(frame_data["visited"])
            if vx:
                scat_visited.set_offsets(list(zip(vx, vy)))
            
            current_path_line.set_data([], [])

        elif state in ["found", "finished"]:
            scat_visited.set_offsets(np.empty((0, 2)))
            
            px, py = get_coords(frame_data["current_path"])
            current_path_line.set_data(px, py)

        hist_paths = frame_data.get("history_paths", [])
        for i, h_line in enumerate(history_lines):
            if i < len(hist_paths):
                hx, hy = get_coords(hist_paths[i])
                h_line.set_data(hx, hy)
            else:
                h_line.set_data([], [])

        bx, by = get_coords(frame_data["best_path"])
        best_path_line.set_data(bx, by)

        return scat_visited, current_path_line, best_path_line, *history_lines

    ani = animation.FuncAnimation(
        fig, update, frames=algo_generator, blit=True, repeat=False, interval=30, cache_frame_data=False
    )

    plt.close()
    return HTML(ani.to_jshtml())
