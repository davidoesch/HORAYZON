# HORAYZON

Package to efficiently compute terrain parameters (like **horizon**, **sky view factor**, **topographic openness**, slope angle/aspect) from high-resolution digital elevation model (DEM) data.
The package also allows to compute **shadow maps** and **correction factors for downwelling direct shortwave radiation** for specific sun positions.
Horizon computation is based on the high-performance ray-tracing library Intel&copy; Embree. Calculations are parallelised with Threading Building Blocks (C++ code).

When you use HORAYZON, please cite:

**Steger, C. R., Steger, B. and Schär, C. (2022): HORAYZON v1.2: an efficient and flexible ray-tracing algorithm to compute horizon and sky view factor, Geosci. Model Dev., 15, 6817–6840, https://doi.org/10.5194/gmd-15-6817-2022**

and

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7013764.svg)](https://doi.org/10.5281/zenodo.7013764)

Please refer to the sections [Known issues](#Known-issues) and [Support and collaboration](#Support-and-collaboration) in case you encounter any **issues** with HORAYZON.

The animation below illustrates the method applied in HORAYZON to find the terrain horizon for individual azimuth directions. Note that for performance reasons, HORAYZON determines the horizon for the first azimuth direction with a binary search (in contrast to the animation).
![Alt text](https://github.com/ChristianSteger/Media/blob/master/Terrain3D_terrain_horizon_new.gif?raw=true "Output from triangles_terrain_horizon.py")

# Package dependencies

HORAYZON depends on multiple external libraries and packages. The essential ones are listed below under **Core dependencies**.
Further dependencies are needed to run the examples (**Base dependencies for examples**).
The examples **horizon/gridded_curved_DEM_masked.py**, **horizon/gridded_planar_DEM_2m.py** and **shadow/gridded_curved_DEM_NASADEM.py** require more complex dependencies, which are listed under **All dependencies for examples**.

**Core dependencies**
- [Intel Embree](https://www.embree.org) and [Threading Building Blocks (TBB)](https://github.com/oneapi-src/oneTBB)
- Python packages: Cython, NumPy, SciPy, GeographicLib, tqdm, requests, xarray

**Base dependencies for examples**
- Python packages: netCDF4, Matplotlib, Pillow, Skyfield, pyproj, IPython

**All dependencies for examples (masking and high-resolution DEM examples; GDAL dependency)**
- Python packages: Shapely, fiona, scikit-image, Rasterio, Trimesh
- [heightmap meshing utility (hmm)](https://github.com/fogleman/hmm)

# Installation

HORAYZON has been tested with **Python 3.13.3** (Linux) and **Python 3.13.3** (Mac OS X).
It is recommended to install dependencies via [Conda](https://docs.conda.io/en/latest/#), which covers all dependencies except **hmm**.
Alternatively, HORAYZON can also be [installed without Conda](#Installation-without-Conda) (by e.g. using **pip** to install Python packages).
Installation via **Conda** can be accomplished as follows for different platforms:

## Linux / Mac OS X

Create an appropriate Conda environment

**Core dependencies**
```bash
conda create -n horayzon_core -c conda-forge embree tbb-devel cython setuptools numpy scipy geographiclib tqdm requests xarray
```

**Base dependencies for examples**
```bash
conda create -n horayzon_base -c conda-forge embree tbb-devel cython setuptools numpy scipy geographiclib tqdm requests xarray netcdf4 matplotlib pillow skyfield pyproj ipython
```

**All dependencies for examples (masking and high-resolution DEM examples; GDAL dependency)**
```bash
conda create -n horayzon_all -c conda-forge embree tbb-devel cython setuptools numpy scipy geographiclib tqdm requests xarray netcdf4 matplotlib pillow skyfield pyproj ipython shapely fiona scikit-image rasterio trimesh
```

and **activate this environment**. The HORAYZON package can then be installed with:
```bash
git clone https://github.com/ChristianSteger/HORAYZON.git
cd HORAYZON  
python -m pip install .
```

## Windows

The installation under Windows has not yet been tested.

# Usage

# Support and collaboration
In case of issues or questions, contact Christian R. Steger (christian.steger@env.ethz.ch). Please report any bugs you find in HORAYZON. You are welcome to fork this repository to modify the source code - we are open to consider *pull requests* for future HORAYZON versions/releases.
