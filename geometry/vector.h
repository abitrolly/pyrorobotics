#ifdef __cplusplus
extern "C" {
#endif

float dot(int dim,float* va, float* vb);
float* cross3D(float* va, float* vb, float* dest);
float* normalize(int dim,float* v);

#ifdef __cplusplus
}
#endif
