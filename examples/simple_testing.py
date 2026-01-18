# Description: Simple testing of (intermediate) HORAYZON code...
#

import numpy as np
import rioxarray
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.spatial import Delaunay
from scipy.interpolate import RegularGridInterpolator

import terrain
from horayzon.temporary import poisson_disk_sampling, clip_triangles

# -----------------------------------------------------------------------------
# Initialise terrain with raster DEM
# -----------------------------------------------------------------------------

# Load DEM data
file = "/Users/csteger/Downloads/swissaltiregio_2056_5728.tif"
ds = rioxarray.open_rasterio(file, masked=True)
ds = ds.isel(y=slice(21500, 21500 + 5_000),  # type: ignore
             x=slice(27500, 27500 + 7_000))
x = ds["x"].values.astype(np.float32)
y = ds["y"].values.astype(np.float32)
elevation = ds.values.squeeze().astype(np.float32) # type: ignore
ds.close()

# Plot
plt.figure()
plt.imshow(elevation, cmap="terrain", origin="upper",
           extent=(x.min(), x.max(), y.min(), y.max()))
plt.show()

# Reshape data
x_2d, y_2d = np.meshgrid(x, y)
# vert_grid = np.hstack((
#     x_2d.reshape(elevation.size, 1),
#     y_2d.reshape(elevation.size, 1),
#     elevation.reshape(elevation.size, 1)
#     )).ravel() # old way as input for HORAYZON -----------------------------> remove later!
vertices_mesh = np.hstack((
    x_2d.reshape(elevation.size, 1),
    y_2d.reshape(elevation.size, 1),
    elevation.reshape(elevation.size, 1)
    )) # (number of vertices, 3), must be C-contiguous
# print(np.all(vert_grid == vertices_mesh.ravel()))
print(vertices_mesh.nbytes / (10 ** 9), "GB")
raster_size_y = elevation.shape[0]
raster_size_x = elevation.shape[1]
del x_2d, y_2d, elevation

# Initialise terrain
terrain_raster = terrain.Terrain()
terrain_raster.from_raster_mesh(
    vertices_mesh=vertices_mesh,
    raster_size_x=raster_size_x,
    raster_size_y=raster_size_y,
)

del terrain_raster

# -----------------------------------------------------------------------------
# Initialise terrain with triangle mesh DEM
# -----------------------------------------------------------------------------

# Load DEM data
file = "/Users/csteger/Downloads/swissaltiregio_2056_5728.tif"
ds = rioxarray.open_rasterio(file, masked=True)
ds = ds.isel(y=slice(21500, 21500 + 3_000),  # type: ignore
             x=slice(27500, 27500 + 4_000))
x = ds["x"].values.astype(np.float32)
y = ds["y"].values.astype(np.float32)
elevation = ds.values.squeeze().astype(np.float32) # type: ignore
ds.close()

# -------------------------------------------------
# Interpolate to triangle mesh
# -------------------------------------------------

# Create triangle mesh
add = 300
points = poisson_disk_sampling(
    x_min = x.min() - add,
    x_max = x.max() + add,
    y_min = y.min() - add, 
    y_max = y.max() + add,
    r=50.0,
    k=30,
    max_points=400_000,
    seed=42
)
print(f"Number of generated points: {points.shape[0]}")
tri = Delaunay(points)
triangles = points[tri.simplices]
mask = clip_triangles(triangles,
                      x.min(), x.max(),
                      y.min(), y.max())
tri.simplices = tri.simplices[~mask]

# Plot
plt.figure()
plt.triplot(points[:, 0], points[:, 1], tri.simplices, linewidth=0.5, 
            color="black")
plt.scatter(points[:, 0], points[:, 1], s=10, color="red")
plt.show()

# Interpolate elevation to triangle mesh vertices
f_ip = RegularGridInterpolator(
    (x, y), elevation.T,
    method="linear",
    bounds_error=False,
    fill_value=np.nan
)
elevation_vertices = f_ip(points).astype(np.float32)
elevation_faces = elevation_vertices[tri.simplices].mean(axis=1)

# Plot
plt.figure(figsize=(14, 5)) # width, height
gs = gridspec.GridSpec(1, 2, left=0.1, bottom=0.1, right=0.9, top=0.9)
ax = plt.subplot(gs[0])
plt.imshow(elevation, cmap="terrain", origin="upper",
           extent=(x.min(), x.max(), y.min(), y.max()), aspect="auto")
ax = plt.subplot(gs[1])
plt.tripcolor(points[:, 0], points[:, 1], tri.simplices,
              facecolors=elevation_faces, cmap="terrain", 
              edgecolors="none", linewidth=0.2)
plt.axis((x.min(), x.max(), y.min(), y.max()))
plt.show()

# Reshape data
vertices_mesh = np.hstack((
    points[:, 0].reshape(points.shape[0], 1),
    points[:, 1].reshape(points.shape[0], 1),
    elevation_vertices.reshape(points.shape[0], 1)
    )).astype(np.float32)

# Initialise terrain
faces_mesh = tri.simplices.astype(np.uint32)
terrain_tri_mesh = terrain.Terrain()
terrain_tri_mesh.from_triangle_mesh(
    vertices_mesh=vertices_mesh,
    faces_mesh=faces_mesh,
)

del terrain_tri_mesh
