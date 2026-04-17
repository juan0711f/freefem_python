import argparse # Lecture of command-line options

import numpy as np # Maths
import matplotlib.pyplot as plt # Plots

def read_mesh(mesh_path):
    with open(mesh_path) as mesh:
        lines = mesh.readlines()
        lines_aux = []

        # For remove spaces, tabs, line breaks, and comments
        for line in lines:
            text = line.strip()
            if not text or text.startswith("#") or text.startswith("//"):
                continue
            lines_aux.append(text)

        index = 0
        vertices_list = []
        triangle_list = []
        dimension = None

        while index < len(lines_aux):
            block = lines_aux[index].split()[0].lower()

            if block == "dimension":
                partes = lines_aux[index].split()
                if len(partes) >= 2:
                    dimension = int(partes[1])
                    index += 1
                    continue
                dimension = int(lines_aux[index + 1])
                index += 2
                continue

            if block == "vertices":
                vertices_cant = int(lines_aux[index+1])
                index += 2

                for i in range(vertices_cant):
                    parts = lines_aux[index].split()
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2]) if len(parts) >= 4 else 0
                    vertices_list.append([x, y, z])
                    index += 1
                continue

            if block == "triangles":
                triangle_cant = int(lines_aux[index + 1])
                index += 2
                for i in range(triangle_cant):
                    parts = lines_aux[index].split()
                    triangle_list.append(
                        [int(parts[0])-1, int(parts[1])-1, int(parts[2])-1]
                    )
                    index += 1
                continue
                
            index += 1

        vertices_np = np.asarray(vertices_list, dtype=np.float64)
        triangle_np = np.asarray(triangle_list, dtype=np.int32) if triangle_list else None
        print(
            f"[Mesh loaded] Vertices: {vertices_np.shape[0]} | Triangles: {0 if triangle_np is None else triangle_np.shape[0]} | Dimension: {dimension}"
        )
        return vertices_np, triangle_np, dimension

def mesh_plot(vertices, triangles):
    fig, ax = plt.subplots(figsize = (7,6))
    x = vertices[:, 0]
    y = vertices[:, 1]

    ax.triplot(x, y, triangles, color="steelblue", linewidth=0.6) if triangles is not None and len(triangles) > 0 else ax.scatter(x, y, s=8, color="steelblue")
    
    ax.set_title("Mesh 2D)")
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(alpha=0.2)

    fig.tight_layout()
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--mesh", required=True, help="Path to the .mesh file")
    cli.add_argument("--plot-mesh", action="store_true", help="Path to the .mesh file")
    args = cli.parse_args()

    vertices, triangles, dimension = read_mesh(args.mesh)

    if args.plot_mesh:
        mesh_plot(vertices, triangles)