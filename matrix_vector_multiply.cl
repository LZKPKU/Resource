__kernel void matrix_vector_multiply (
	const int m,
	const int n,
	__global const float *matrixA,
	__global const float *vectorB,
	__global float *resultC)
{
	int i = get_global_id(0);

	int k = 0;
	float result = 0;

	if(i < m) 
	{
		for(; k < n; k++)
			result += matrixA[i * n + k] * vectorB[k];

		resultC[i] = result;
	}
}