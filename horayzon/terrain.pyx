cimport numpy as np
import numpy as np

cdef extern from "terrain_comp.h" namespace "shapes":
    cdef cppclass CppTerrain:
        CppTerrain()

        void from_raster_mesh(
            float*,
            int,
            int
        )

        void from_triangle_mesh(
            float*,
            np.npy_uint32*,
            np.npy_uint32,
            np.npy_uint32
        )

cdef class Terrain:

    cdef CppTerrain *thisptr

    def __cinit__(self):
        self.thisptr = new CppTerrain()

    def __dealloc__(self):
        del self.thisptr

    def from_raster_mesh(
        self,
        np.ndarray[np.float32_t, ndim = 2] vertices_mesh,
        int raster_size_y,
        int raster_size_x
    ):
        """
        Initialise terrain from raster/grid elevation data.

        Parameters
        ----------
        vertices_mesh : ndarray of float (two-dimensional)
            Elevation at vertices of raster mesh. Raster vertices must be
            arranged in row-major order
            (number of vertices, 3) [metre]
        raster_size_y : int
            Raster size in y-direction (number of rows; height)
        raster_size_x : int
            Raster size in x-direction (number of columns; width)
        """

        # Check consistency and validity of input arguments
        if vertices_mesh.shape[1] != 3:
            raise ValueError("Length of second dimension of array "
                "'vertices_mesh' must be 3")
        if (not vertices_mesh.flags["C_CONTIGUOUS"]):
            raise ValueError("Array 'vertices_mesh' must be C-contiguous")
        if vertices_mesh.shape[0] != (raster_size_y * raster_size_x):
            raise ValueError("Inconsistency in number of vertices")
        if (raster_size_y > 32_767) or (raster_size_x > 32_767):
            raise ValueError("Maximum allowed with and/or height (32767) "
                "for raster exceeded")

        self.thisptr.from_raster_mesh(
            &vertices_mesh[0, 0],
            raster_size_y,
            raster_size_x
        )

    def from_triangle_mesh(
        self,
        np.ndarray[np.float32_t, ndim = 2] vertices_mesh,
        np.ndarray[np.uint32_t, ndim = 2] faces_mesh,
    ):
        """
        Initialise terrain from triangle mesh elevation data.

        Parameters
        ----------
        vertices_mesh : ndarray of float (two-dimensional)
            Elevation at vertices of triangle mesh
            (number of vertices, 3) [metre]
        faces_mesh : ndarray of uint32 (two-dimensional)
            Indices of vertices composing triangles
            (number of faces, 3)
        """

        # Check consistency and validity of input arguments
        if (vertices_mesh.shape[1] != 3) or (faces_mesh.shape[1] != 3):
            raise ValueError("Length of second dimensions of input arrays "
                "must be 3")
        if ((not vertices_mesh.flags["C_CONTIGUOUS"])
            or (not faces_mesh.flags["C_CONTIGUOUS"])):
            raise ValueError("Input arrays must be C-contiguous")
        if ((faces_mesh.min() < 0)
            or (faces_mesh.max() >= vertices_mesh.shape[0])):
            raise ValueError("Face indices out of bounds")
        if (vertices_mesh.nbytes / (10 ** 9)) > 16.0:
            raise MemoryError("Vertex buffer exceeds 16 GB")

        cdef unsigned int num_vertices = vertices_mesh.shape[0]
        cdef unsigned int num_faces = faces_mesh.shape[0]

        self.thisptr.from_triangle_mesh(
            &vertices_mesh[0, 0],
            &faces_mesh[0, 0],
            num_vertices,
            num_faces
        )
