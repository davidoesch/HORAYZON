#include <embree4/rtcore.h>

namespace shapes {
class CppTerrain {
public:
    RTCDevice device;
    RTCScene scene;
    int dem_dim_0_cl, dem_dim_1_cl;
    float* vert_grid_cl;
    int offset_0_cl, offset_1_cl;
    float* vec_tilt_cl;
    float* vec_norm_cl;
    int dim_in_0_cl, dim_in_1_cl;
    CppTerrain();
    ~CppTerrain();

    void init_from_raster(
        float* vert_grid,
    	int dem_dim_0, int dem_dim_1,
    	int offset_0, int offset_1,
    	float* vec_tilt,
    	float* vec_norm,
    	int dim_in_0, int dim_in_1,
    	char* geom_type);

    void shadow(float* sun_position, unsigned char* shadow_buffer);
};
}