#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <iostream>
#include <fstream>
#include <CL/cl.h>
#include <sys/time.h>
using namespace std;

// some definitions
#define MEM_SIZE (128)
#define MAX_SOURCE_SIZE (0x10000000)

/*
 *   Based on the number given
 *   Give the nearest 2 exponent
 */
int getNearest2Ex(int number)
{
	int result = 1;
	while(result < number)
		result *= 2;

	return result;
}

/*
 *   Function 'rerror' is called when the program detects an
 *   error and wishes to print an appropriate message and exit.
 */
void rerror (char *s)
{
   printf ("%s\n", s);
   exit (-1);
}

/*
 *   Given the name of a file containing a matrix of floats
 *   function returns the dimensions of the matrix or the vector
 */
void getDimensions(char *s, int *m, int *n)
{
	char error_msg[80];
	FILE *fptr;          /* Input file pointer */

   	fptr = fopen(s, "r");
   	if(fptr == NULL)
   	{
   		sprintf(error_msg, "Can't open file '%s'", s);
   		rerror(error_msg);
   	}

   	fread(m, sizeof(int), 1, fptr);
   	fread(n, sizeof(int), 1, fptr);

   	fclose(fptr);
}

/*
 *   Given the name of a file containing a matrix of floats, function
 *   'read_matrix' opens the file and reads its contents.
 */
void readMatrix(char *s, float *matrix)
{
   char error_msg[80];
   FILE *fptr;          /* Input file pointer */

   fptr = fopen(s, "r");
   if(fptr == NULL)
   {
      sprintf(error_msg, "Can't open file '%s'", s);
      rerror(error_msg);
   }

   // the dimensions of the matrix
   int m, n;

   fread(&m, sizeof(int), 1, fptr);
   fread(&n, sizeof(int), 1, fptr);

   // copy the data to the matrix
   // note we store it as 1D array
   fread(matrix, sizeof(float), m * n, fptr);
   fclose(fptr);
   return;
}

int main(int argc, char *argv[])
{
	if(argc != 2)
	{
		printf("Please put in the number of work group\n");
		exit(-1);
	}

	/*******************************************************
	* given by the instructions
	* I think it's better not to modify it
	*******************************************************/
	cl_device_id device_id = NULL;
	cl_context context = NULL;
	cl_command_queue command_queue = NULL;
	// cl_mem memobj = NULL;
	cl_program program = NULL;
	cl_kernel kernel = NULL;
	cl_platform_id platform_id = NULL;
	cl_uint ret_num_devices;
	cl_uint ret_num_platforms;
	cl_int ret;

	// char string[MEM_SIZE];
	FILE *fp;
	// modify the fileName
	char fileName[] = "./matrix_vector_multiply.cl";
	char *source_str;
	size_t source_size;

	/* Load the source code containing the kernel */
	fp = fopen(fileName, "r");
	if (!fp)
	{
		fprintf(stderr, "Failed to load kernel.\n");
		exit(1);
	}
	source_str = (char*)malloc(MAX_SOURCE_SIZE);
	source_size = fread(source_str, 1, MAX_SOURCE_SIZE, fp);
	fclose(fp);

	/* Get Platform and Device Info */
	ret = clGetPlatformIDs(1, &platform_id, &ret_num_platforms);
	ret = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_GPU, 1, &device_id,
    &ret_num_devices);

	/* Create OpenCL context */
	context = clCreateContext(NULL, 1, &device_id, NULL, NULL, &ret);

	/* Create Command Queue */
	command_queue = clCreateCommandQueue(context, device_id, 0, &ret);

	/*******************************************************
	* load the data
	*******************************************************/

	int m1, n1;		// dimensions of matrix_a
	int m2, n2;		// dimension of vector_b
	char error_msg[80];		// error message

	// get the dimensions of matrix and the vector
	getDimensions("matrix_a", &m1, &n1);
	getDimensions("vector_b", &m2, &n2);

	// alert if it's invalid
	if(n1 != m2)
	{
		sprintf(error_msg, "Matrix doesn't match vector");
   		rerror(error_msg);
	}

	if(n2 != 1)
	{
		sprintf(error_msg, "Vector is not a vector");
   		rerror(error_msg);
	}

	// allocate the space for matrix and vector
	float *matrixA = (float *) malloc(m1 * n1 * sizeof(float *));
	float *vectorB = (float *) malloc(m2 * n2 * sizeof(float *));
	float *resultC = (float *) malloc(m1 * n2 * sizeof(float *));

	// read the matrix and the vector
	readMatrix("matrix_a", matrixA);
	readMatrix("vector_b", vectorB);

	/*******************************************************
	* given by the instructions
	* I think it's better not to modify it
	*******************************************************/

    /* Create Kernel Program from the source */
	program = clCreateProgramWithSource(context, 1, (const char **)&source_str,
	(const size_t *)&source_size, &ret);

	if(ret != CL_SUCCESS)
	{
		printf("Unable to create Program Object. Error code = %d", ret);
		exit(1);
	}

	/* Build Kernel Program */
	ret = clBuildProgram(program, 1, &device_id, NULL, NULL, NULL);

	/* Create OpenCL Kernel */
	/* The name is given by this program */
	kernel = clCreateKernel(program, "matrix_vector_multiply", &ret);

	/*******************************************************
	* set arguments
	*******************************************************/

	// create memory buffer
	cl_mem memObjects[3] = { 0, 0, 0 };

	memObjects[0] = clCreateBuffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, 
	    sizeof(float)* m1 * n1, matrixA, NULL);
	memObjects[1] = clCreateBuffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, 
		sizeof(float)* m2 * n2, vectorB, NULL);
	memObjects[2] = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 
		sizeof(float)* m1 * n2, resultC, NULL);
	if (memObjects[0] == NULL || memObjects[1] == NULL || memObjects[2] == NULL) 
	    perror("Error in clCreateBuffer.\n");

	ret = clSetKernelArg(kernel, 0, sizeof(int), &m1);
	ret = clSetKernelArg(kernel, 1, sizeof(int), &n1);
	ret = clSetKernelArg(kernel, 2, sizeof(cl_mem), &memObjects[0]);
	ret = clSetKernelArg(kernel, 3, sizeof(cl_mem), &memObjects[1]);
	ret = clSetKernelArg(kernel, 4, sizeof(cl_mem), &memObjects[2]);

	/*******************************************************
	* execute the kernel
	*******************************************************/

	// used to store the number of work-items
	size_t global, local;

	// set the number of work-items
	// here we set the number as the dimension of result vector
	global = (size_t) getNearest2Ex(m1);

	// local is given by the argument
	local = (size_t) atoi(argv[1]);

	// when the input cannot divide global size evenly
	// set the local size as the maximum
	if(local > 0 && global % local != 0)
	{
		// get the max size of work group
		size_t maxSize;
    	clGetDeviceInfo(device_id,
    		CL_DEVICE_MAX_WORK_GROUP_SIZE, sizeof(maxSize), &maxSize, NULL);
    	printf("The max size of work group is %d\n", maxSize);
		local = maxSize;
	}

	// I don't know what's this
	cl_event prof_event;

    printf("The number of local group items is %d\n", (int) local);

	// Timers
	struct timeval Tvalue;
	struct timezone dummy;

	double starttime, endtime;
	double runtime = 0.0;

	for(int i = 0; i < 10; i++)
	{
		gettimeofday(&Tvalue, &dummy);
		starttime = (double)Tvalue.tv_sec + 1.0e-6*((double)Tvalue.tv_usec);

		// execute the kernel
		if(local == 0)
			ret = clEnqueueNDRangeKernel(command_queue, kernel, 1, NULL, 
		    	&global, NULL, 0, NULL, &prof_event);	
		else
			ret = clEnqueueNDRangeKernel(command_queue, kernel, 1, NULL, 
				&global, &local, 0, NULL, &prof_event);

		// Wait for calculations to be finished
		clWaitForEvents(1, &prof_event);

		gettimeofday(&Tvalue, &dummy);
		endtime = (double) Tvalue.tv_sec + 1.0e-6 * ((double) Tvalue.tv_usec);
		// printf("This run took up %.3lf seconds\n", endtime - starttime);
		runtime += (endtime - starttime) / (double)1.0;

		/* Copy results from the memory buffer */
		/* Here we copy the third array back */
		ret = clEnqueueReadBuffer(command_queue, memObjects[2], CL_TRUE, 0,
		sizeof(float) * m1 * n2, resultC, 0, NULL, NULL);
	}

	// print the result
	for(int i = 0; i < m1; i++)
		printf("%.2f\n", resultC[i]);

	printf("Multiplication took up %lf seconds\n", runtime);

	/*******************************************************
	* given by the instructions
	* I think it's better not to modify it
	*******************************************************/

	/* Finalization */
	ret = clFlush(command_queue);
	ret = clFinish(command_queue);
	ret = clReleaseKernel(kernel);
	ret = clReleaseProgram(program);
	// ret = clReleaseMemObject(memobj);
	ret = clReleaseMemObject(memObjects[0]);
	ret = clReleaseMemObject(memObjects[1]);
	ret = clReleaseMemObject(memObjects[2]);
	ret = clReleaseCommandQueue(command_queue);
	ret = clReleaseContext(context);

	free(source_str);

	return 0;
}