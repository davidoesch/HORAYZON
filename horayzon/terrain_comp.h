#include <embree4/rtcore.h>

namespace shapes {
class CppTerrain {
public:
    RTCDevice device;
    RTCScene scene;

    float* vertices_mesh_cl;
    int raster_size_y_cl;
    int raster_size_x_cl;
    unsigned int* faces_mesh_cl;
    int num_vertices_cl;
    int num_faces_cl;

    CppTerrain();
    ~CppTerrain();

    void from_raster_mesh(
        float* vertices_mesh,
        int raster_size_y,
        int raster_size_x
    );

    void from_triangle_mesh(
        float* vertices_mesh,
        unsigned int* faces_mesh,
        int num_vertices,
        int num_faces
    );

};
}
