# Description: Temporary stuff for testing purposes...

import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from numba import njit

# -----------------------------------------------------------------------------

@njit
def poisson_disk_sampling(x_min, x_max, y_min, y_max,
                          r, k, max_points, seed=42):
    """
    Poisson disk sampling within a 2D rectangular domain using 
    Bridson's algorithm.

    Parameters
    ----------
    x_min : float
        Left boundary of the domain
    x_max : float
        Right boundary of the domain
    y_min : float
        Lower boundary of the domain
    y_max : float
        Upper boundary of the domain
    r : float
        Minimum distance between points
    k : int
        Attempts per active point
    max_points : int
        Maximum number of points to generate
    seed : int or None
        Random seed

    Returns
    -------
    points : ndarray (number of points, 2)
    """

    width  = x_max - x_min
    height = y_max - y_min

    cell_size = r / np.sqrt(2.0)
    grid_w = int(np.ceil(width / cell_size))
    grid_h = int(np.ceil(height / cell_size))

    grid = -np.ones((grid_h, grid_w), dtype=np.int32)
    points = np.empty((max_points, 2), dtype=np.float64)
    active = np.empty(max_points, dtype=np.int32)

    # Initial points (shift carried out later)
    np.random.seed(seed)
    px = np.random.random() * width
    py = np.random.random() * height
    points[0, 0] = px
    points[0, 1] = py

    gi = int(py // cell_size)
    gj = int(px // cell_size)
    grid[gi, gj] = 0
    active[0] = 0

    n_points = 1
    n_active = 1

    while n_active > 0 and n_points < max_points:
        idx = active[int(np.random.random() * n_active)]
        base = points[idx]
        found = False

        for _ in range(k):
            angle = 2.0 * np.pi * np.random.random()
            radius = r * (1.0 + np.random.random())

            px = base[0] + radius * np.cos(angle)
            py = base[1] + radius * np.sin(angle)

            if px < 0.0 or px >= width or py < 0.0 or py >= height:
                continue

            gi = int(py // cell_size)
            gj = int(px // cell_size)

            ok = True
            for ii in range(max(0, gi - 2), min(grid_h, gi + 3)):
                for jj in range(max(0, gj - 2), min(grid_w, gj + 3)):
                    pidx = grid[ii, jj]
                    if pidx != -1:
                        dx = points[pidx, 0] - px
                        dy = points[pidx, 1] - py
                        if dx * dx + dy * dy < r * r:
                            ok = False
                            break
                if not ok:
                    break

            if ok:
                points[n_points, 0] = px
                points[n_points, 1] = py
                grid[gi, gj] = n_points
                active[n_active] = n_points
                n_points += 1
                n_active += 1
                found = True
                break

        if not found:
            for i in range(n_active):
                if active[i] == idx:
                    active[i] = active[n_active - 1]
                    break
            n_active -= 1

    # Shift to [x_min, x_max] and [y_min, y_max]
    for i in range(n_points):
        points[i, 0] += x_min
        points[i, 1] += y_min

    return points[:n_points]

@njit
def clip_triangles(triangles, x_min, x_max, y_min, y_max):
    """
    Clip triangles to a rectangular domain.

    Parameters
    ----------
    triangles : ndarray (number of triangles, 3, 2)
        Array of triangles defined by their vertex coordinates.
    x_min : float
        Left boundary of the domain
    x_max : float
        Right boundary of the domain
    y_min : float
        Lower boundary of the domain
    y_max : float
        Upper boundary of the domain

    Returns
    -------
    mask : ndarray (number of triangles)
        Boolean mask indicating which triangles are outside the domain.
    """

    mask = np.zeros(triangles.shape[0], dtype=np.bool_)
    for i in range(triangles.shape[0]):
        x = triangles[i, :, 0]
        y = triangles[i, :, 1]
        if (np.any(x < x_min) | np.any(x > x_max) |
            np.any(y < y_min) | np.any(y > y_max)):
            mask[i] = True
    return mask

# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # Generate points
    domain = {"x_min": 0.0, "x_max": 2.0, "y_min": 0.0, "y_max": 2.0}
    points = poisson_disk_sampling(
        x_min = domain["x_min"] - 0.02,
        x_max = domain["x_max"] + 0.02,
        y_min = domain["y_min"] - 0.02, 
        y_max = domain["y_max"] + 0.02,
        r=0.01,
        k=30,
        max_points=50_000,
        seed=42
    )
    print(f"Number of generated points: {points.shape[0]}")

    # Delaunay triangulation
    tri = Delaunay(points)

    # Clip triangles to domain
    triangles = points[tri.simplices]
    mask = clip_triangles(triangles,
                          domain["x_min"], domain["x_max"], 
                          domain["y_min"], domain["y_max"])
    tri.simplices = tri.simplices[~mask]

    # Test plot
    plt.figure()
    plt.triplot(points[:, 0], points[:, 1], tri.simplices, linewidth=0.5, 
                color="black")
    plt.scatter(points[:, 0], points[:, 1], s=10, color="red")
    plt.show()
