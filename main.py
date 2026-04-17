import argparse # Lecture of command-line options

import numpy as np # Maths
import matplotlib.pyplot as plt # Plots

from PIL import Image, ImageDraw # Python Imaging Library

from pathlib import Path

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

"""
    To convert from mesh coordinates (xy) to image coordinates (uv), the following operator is used:

    T(x,y) = (T_1(x), T_2(y)), con T_i(s) = m_i * s + b_i

    that satisfies:

    T_1(xmin) = umin
    T_1(xmax) = umax
    T_2(ymin) = vmin
    T_2(ymax) = vmax

    With a few simple calculations, we arrive at:

    m_1 = (umax - umin) / (xmax - xmin)
    m_2 = (vmax - vmin) / (ymax - ymin)
    b_1 = umin - m_1 * xmin
    b_2 = vmin - m_2 * ymin
"""
def xy_to_uv(bbox_mesh, bbox_img, xy):
    xmin, xmax, ymin, ymax = bbox_mesh
    umin, umax, vmin, vmax = bbox_img

    m_1 = (umax - umin) / (xmax - xmin + 1e-12)
    m_2 = (vmax - vmin) / (ymax - ymin + 1e-12)

    b_1 = umin - m_1 * xmin
    b_2 = vmin - m_2 * ymin

    A = np.array([[m_1, 0], [0, m_2]], dtype=np.float64)
    B = np.array([b_1, b_2], dtype=np.float64)

    return xy @ A.T + B 


def export_mesh_image(vertices, triangles, img_path, width=2048):
    
    xy = vertices[:, :2]

    # bbox of mesh
    bbox_mesh = [xy[:, 0].min(), xy[:, 0].max(), xy[:, 1].min(), xy[:, 1].max()]

    aspect = (xy[:, 1].max() - xy[:, 1].min()) / (xy[:, 0].max() - xy[:, 0].min() + 1e-12) # (ymax - ymin) / (xmax - xmin). To maintain the same proportion of the domain.
    height = max(1, int(round(aspect*width))) # Starting with the fixed width, the image height is determined maintaining the same aspect ratio.

    # bbox of img to export
    bbox_img = [0, width-1, 0, height-1]
    
    uv = xy_to_uv(bbox_mesh, bbox_img, xy)

    img = Image.new("RGBA", (width, height), color=(0,0,0,0))
    draw = ImageDraw.Draw(img)

    for a, b, c in triangles:
        draw.polygon([[int(uv[a, 0]), int(uv[a, 1])], [int(uv[b, 0]), int(uv[b, 1])], [int(uv[c, 0]), int(uv[c, 1])]], fill=(255, 255, 255, 255))
    
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    img.save(img_path)

    print(
        f"[Mesh template saved] File: {img_path} | Width: {width} | Height: {height}"
    )

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
    cli.add_argument("--plot-mesh", action="store_true", help="Plot the mesh")
    cli.add_argument("--template", action="store_true", help="Export a template (image) of mesh")
    args = cli.parse_args()

    vertices, triangles, dimension = read_mesh(mesh_path=args.mesh)

    if args.plot_mesh:
        mesh_plot(vertices= vertices, triangles= triangles)

    if args.template:
        export_mesh_image(vertices = vertices, triangles = triangles, img_path = Path(args.mesh).with_name(f"{Path(args.mesh).stem}_template.png"))