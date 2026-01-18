#include "terrain_comp.h"
#include <cstdio>
#include <embree4/rtcore.h>
#include <stdio.h>
#include <math.h>
#include <limits>
#include <stdio.h>
#include <cstdlib>
#include <chrono>
#include <iostream>
#include <string.h>
#include <tbb/parallel_for.h>
#include <sstream>
#include <iomanip>

using namespace std;
using namespace shapes;

//#############################################################################
// Miscellaneous
//#############################################################################

// Namespace
#if defined(RTC_NAMESPACE_USE)
	RTC_NAMESPACE_USE
#endif

// Error function
void errorFunction(void* userPtr, enum RTCError error, const char* str) {
	printf("error %d: %s\n", error, str);
}

// Initialisation of device and registration of error handler
RTCDevice initializeDevice() {
	RTCDevice device = rtcNewDevice(NULL);
  	if (!device) {
    	printf("error %d: cannot create device\n", rtcGetDeviceError(NULL));
    }
  	rtcSetDeviceErrorFunction(device, errorFunction, NULL);
  	return device;
}

//#############################################################################
// Create scene from geometries
//#############################################################################

RTCScene initializeSceneFromRaster(
	RTCDevice device,
	float* vertices_mesh,
	int raster_size_y,
	int raster_size_x
)
{

	cout << "Raster dimensions: (" << raster_size_y
		<< ", " << raster_size_x << ") " << endl;
	size_t num_vertices = (raster_size_y * raster_size_x);
	cout << "Number of vertices: " << num_vertices << endl;

	RTCScene scene = rtcNewScene(device);
  	rtcSetSceneFlags(scene, RTC_SCENE_FLAG_ROBUST);
	RTCGeometry geom = rtcNewGeometry(device, RTC_GEOMETRY_TYPE_GRID);

	rtcSetSharedGeometryBuffer(
		geom,
		RTC_BUFFER_TYPE_VERTEX,
		0,
		RTC_FORMAT_FLOAT3,
		vertices_mesh,
		0,
		3 * sizeof(float),
		num_vertices
	);

	RTCGrid* grid = (RTCGrid*)rtcSetNewGeometryBuffer(
		geom,
		RTC_BUFFER_TYPE_GRID,
		0,
		RTC_FORMAT_GRID,
		sizeof(RTCGrid),
		1
	);
	grid[0].startVertexID = 0;
	grid[0].stride        = raster_size_x;
	grid[0].width         = raster_size_x;
	grid[0].height        = raster_size_y;

	// Commit geometry and scene (build BVH)
	auto start = std::chrono::high_resolution_clock::now();
	rtcCommitGeometry(geom);
	rtcAttachGeometry(scene, geom);
	rtcReleaseGeometry(geom);
	rtcCommitScene(scene);
	auto end = std::chrono::high_resolution_clock::now();
	std::chrono::duration<double> time = end - start;
	cout << "BVH build time: " << fixed << setprecision(2)
		<< time.count() << " s" << endl;

	return scene;

}

RTCScene initializeSceneFromTriangles(
	RTCDevice device,
	float* vertices_mesh,
	unsigned int* faces_mesh,
	unsigned int num_vertices,
	unsigned int num_faces
)
{

	cout << "Number of vertices: " << num_vertices << endl;
	cout << "Number of faces: " << num_faces << endl;

	RTCScene scene = rtcNewScene(device);
	rtcSetSceneFlags(scene, RTC_SCENE_FLAG_ROBUST);
	RTCGeometry geom = rtcNewGeometry(device, RTC_GEOMETRY_TYPE_TRIANGLE);

    rtcSetSharedGeometryBuffer(
		geom,
		RTC_BUFFER_TYPE_VERTEX,
		0,
		RTC_FORMAT_FLOAT3,
		vertices_mesh,
		0,
		3 * sizeof(float),
		num_vertices
	);

    rtcSetSharedGeometryBuffer(
		geom,
		RTC_BUFFER_TYPE_INDEX,
		0,
		RTC_FORMAT_UINT3,
		faces_mesh,
		0,
		3 * sizeof(int),
		num_faces
	);

	auto start = std::chrono::high_resolution_clock::now();

	// Commit geometry and scene (build BVH)
	rtcCommitGeometry(geom);
	rtcAttachGeometry(scene, geom);
	rtcReleaseGeometry(geom);
	rtcCommitScene(scene);
	auto end = std::chrono::high_resolution_clock::now();
	std::chrono::duration<double> time = end - start;
	cout << "BVH build time: " << fixed << setprecision(2)
		<< time.count() << " s" << endl;

	return scene;

}

//#############################################################################
// Initialise terrain
//#############################################################################

CppTerrain::CppTerrain() {
    
    device = initializeDevice();
    
}

CppTerrain::~CppTerrain() {

  	// Release resources allocated through Embree
  	rtcReleaseScene(scene);
  	rtcReleaseDevice(device);

}

void CppTerrain::from_raster_mesh(
	float* vertices_mesh,
	int raster_size_y,
	int raster_size_x
)
{

	raster_size_y_cl = raster_size_y;
	raster_size_x_cl = raster_size_x;
	vertices_mesh_cl = vertices_mesh;

	auto start_ini = std::chrono::high_resolution_clock::now();

	scene = initializeSceneFromRaster(
		device,
		vertices_mesh,
		raster_size_y,
		raster_size_x
	);

	auto end_ini = std::chrono::high_resolution_clock::now();
  	std::chrono::duration<double> time = end_ini - start_ini;
	cout << "Total initialisation time: " << fixed << setprecision(2)
		<< time.count() << " s" << endl;

}

void CppTerrain::from_triangle_mesh(
	float* vertices_mesh,
    unsigned int* faces_mesh,
	unsigned int num_vertices,
	unsigned int num_faces
)
{

	num_vertices_cl = num_vertices;
	num_faces_cl = num_faces;
	vertices_mesh_cl = vertices_mesh;
    faces_mesh_cl = faces_mesh;

	auto start_ini = std::chrono::high_resolution_clock::now();

	scene = initializeSceneFromTriangles(
		device,
		vertices_mesh,
		faces_mesh,
		num_vertices,
		num_faces
	);

	auto end_ini = std::chrono::high_resolution_clock::now();
	std::chrono::duration<double> time = end_ini - start_ini;
	cout << "Total initialisation time: " << fixed << setprecision(2)
		<< time.count() << " s" << endl;

}
