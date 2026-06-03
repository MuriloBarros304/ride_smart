import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import HTML

def _dijkstra_generator_wrapper(dijkstra_instance, start, end):
    """
    Transforms the synchronous execution of Dijkstra's algorithm into a generator 
    for matplotlib using the callback system. Marked as internal with an underscore.

    Args:
        dijkstra_instance: An initialized instance of the Dijkstra solver.
        start (int): The starting node ID.
        end (int): The destination node ID.

    Yields:
        tuple: A tuple containing a copy of the visited set and the current vertex.
    """
    frames = []

    # Create the callback function that Dijkstra will call at each step
    def capture_frame(visited_set, current_vertex):
        # The heavy memory copy happens HERE, strictly outside the core algorithm
        frames.append((visited_set.copy(), current_vertex))

    # Execute the algorithm passing our hook (callback)
    dijkstra_instance.find_shortest_path(start, end, on_visit_callback=capture_frame)

    # Yield the captured frames for the animation loop
    for frame in frames:
        yield frame


def animate_dijkstra(G, dijkstra_instance, start_node, end_node):
    """
    Creates an HTML5 video animation of Dijkstra's algorithm exploring an OSMnx graph.
    
    Args:
        G (networkx.MultiDiGraph): The geographic graph loaded via OSMnx.
        dijkstra_instance: An initialized instance of the Dijkstra solver.
        start_node (int): The ID of the starting node in the graph.
        end_node (int): The ID of the destination node in the graph.
        
    Returns:
        IPython.display.HTML: An HTML5 video player element compatible with Jupyter/Colab.
    """
    # 1. Draw the static background map (black edges, white nodes)
    fig, ax = ox.plot_graph(
        G, 
        node_color="w", 
        node_edgecolor="k", 
        node_size=10, 
        edge_color="#999999", 
        show=False, 
        close=False
    )

    # 2. Prepare the empty scatter plot object that will be animated (red dots)
    scat = ax.scatter([], [], c='red', s=20, zorder=5)

    # Initialize the generator using our wrapper
    dijkstra_generator = _dijkstra_generator_wrapper(dijkstra_instance, start_node, end_node)

    # 3. The update function called for each frame of the animation
    def update(frame_data):
        visited_nodes, _ = frame_data
        
        # Extract X and Y coordinates of visited nodes from the OSMnx graph
        x_coords = [G.nodes[n]['x'] for n in visited_nodes]
        y_coords = [G.nodes[n]['y'] for n in visited_nodes]
        
        # Update the scatter plot with the new coordinates
        scat.set_offsets(list(zip(x_coords, y_coords)))
        
        return scat,

    # 4. Create the animation binding the figure, update function, and generator
    ani = animation.FuncAnimation(
        fig, 
        update, 
        frames=dijkstra_generator, 
        blit=True, 
        repeat=False,
        interval=50  # Milliseconds between frames
    )

    # Close the plot to prevent the static image from rendering twice in the notebook
    plt.close()
    
    # 5. Return the rendered HTML video player
    return HTML(ani.to_jshtml())
