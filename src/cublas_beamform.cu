#include <cublas_v2.h>
#include <cuda_runtime.h>
#include <stdio.h>

#include "cublas_beamform.cuh"

__constant__ float lut[16] = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, -8.0, -7.0, -6.0, -5.0, -4.0, -3.0, -2.0, -1.0};

// Transpose time x chan x pol x 4+4 bit to
// chan x pol x time x 32+32 bit float
__global__ void trans_4bit_to_float(unsigned char *in,
                                    float *out,
                                    int n_pol,
                                    int n_chan,
                                    int n_time
                                   ) {
  //long long int tid = blockDim.y*blockDim.x*blockIdx.y + blockDim.x*blockIdx.x + threadIdx.x;
  //int pol  = tid % n_pol;
  //int chan = (tid / n_pol) % n_chan;
  //int time = (tid / (n_pol * n_chan));
  int time = blockIdx.x;
  int chan = blockIdx.y;
  int pol = TRANSPOSE_POL_BLOCK_SIZE*threadIdx.x;
  unsigned char *in_off = in + time*n_chan*n_pol + chan*n_pol + pol; // 4+4 bit
  float *out_off = out + 2*( chan*n_pol*n_time + pol*n_time + time); // 32+32 bit
  //long long int old_index = time*n_chan*n_pol + chan*n_pol + pol;
  //long long int new_index = chan*n_pol*n_time + pol*n_time + time;
  float real, imag;
  unsigned char temp;
  #pragma unroll
  for (int i=0; i<TRANSPOSE_POL_BLOCK_SIZE; i++) {
    temp = *in_off++;
    //real = lut[in[old_index+i] >> 4];
    //imag = lut[in[old_index+i] & 0b1111];
    //out[2*(new_index+i)] = real;
    //out[2*(new_index+i)+1] = imag;
    real = lut[(temp >> 4) & 0b1111];
    imag = lut[temp & 0b1111];
    out_off[0] = real;
    out_off[1] = imag;
    out_off += 2*n_time;
  }
}

// Transpose chan x beam x pol x time x 32+32 float to
// beam x time[part-summed] x chan x [XX,YY,XY*_r,XY*_i] x 32 float
// Each thread deals with two pols of a beam, and sums over n_time_sum time samples
// n_beam is the _output_ number of beams. I.e., the number of dual-pol beams
__global__ void trans_output_and_sum(float *in,
                                    float *out,
                                    int n_chan,
                                    int n_beam,
                                    int n_time,
                                    int n_time_sum
                                   ) {
  int chan = blockIdx.x;
  int beam = blockIdx.y;
  int time = threadIdx.x;
  // n_beam here is a dual pol beam
  // input is: chan x beam x pol [2] x time x complexity
  long long int old_index = 2*(chan*n_beam*2*n_time + beam*2*n_time + time*n_time_sum); // start index for n_time/n_time_sum samples
  // output is: beam x time x chan x pol-products [4]
  long long int new_index = 4*(beam*(n_time / n_time_sum)*n_chan + time*n_chan + chan);
  float xx=0., yy=0., xy_r=0., xy_i=0.; // accumulator registers
  float x_r, x_i, y_r, y_i;
  int t;
  for (t=0; t<n_time_sum; t++) {
    x_r = in[old_index + 2*t];
    x_i = in[old_index + 2*t + 1];
    y_r = in[old_index + 2*(n_time + t)];
    y_i = in[old_index + 2*(n_time + t) + 1];
    xx = xx + x_r*x_r + x_i*x_i;
    yy = yy + y_r*y_r + y_i*y_i;
    xy_r = xy_r + x_r*y_r + x_i*y_i;
    xy_i = xy_i + x_i*y_r - x_r*y_i;
  }
  out[new_index] = xx;
  out[new_index+1] = yy;
  out[new_index+2] = xy_r;
  out[new_index+3] = xy_i;
}

// Take an input of order chan x beam x pol x time x 32+32 float and generate
// a single beam of time[part-summed] x chan x [XX,YY,XY*_r,XY*_i] x 32 float
// Each thread deals with two pols of a beam (beam_index and beam_index+1)
// and sums over n_time_sum time samples
__global__ void trans_output_and_sum_single_beam(float *in,
                                                 float *out,
                                                 int n_chan,
                                                 int n_beam,
                                                 int n_time,
                                                 int n_time_sum,
                                                 int beam_index
                                                ) {
  int chan = blockIdx.x;
  int beam = beam_index;
  int time = threadIdx.x;
  long long int old_index = chan*n_beam*n_time*2 + beam*n_time*2 + time*n_time_sum*2; // start index for n_time/n_time_sum samples
  long long int new_index = time*n_chan*4 + chan*4;
  float xx=0., yy=0., xy_r=0., xy_i=0.;
  float x_r, x_i, y_r, y_i;
  int t;
  for (t=0; t<n_time_sum; t++) {
    x_r = in[old_index + 2*t];
    x_i = in[old_index + 2*t + 1];
    y_r = in[old_index + 2*n_time + 2*t];
    y_i = in[old_index + 2*n_time + 2*t + 1];
    xx = xx + x_r*x_r + x_i*x_i;
    yy = yy + y_r*y_r + y_i*y_i;
    xy_r = xy_r + x_r*y_r + x_i*y_i;
    xy_i = xy_i + x_i*y_r - x_r*y_i;
  }
  out[new_index] = xx;
  out[new_index+1] = yy;
  out[new_index+2] = xy_r;
  out[new_index+3] = xy_i;
}

__global__ void complex2pow(float *in, float *out, int N) {
  int tid = blockDim.x * blockIdx.x + threadIdx.x;
  if (tid < N) {
    out[tid] = (in[2*tid]*in[2*tid] + in[2*tid + 1]*in[2*tid + 1]);
  }
}

#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line, bool abort=true)
{
   if (code != cudaSuccess) 
   {
      fprintf(stderr,"GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
      if (abort) exit(code);
   }
}

/* Error checking for cuBLAS */
void gpuBLASchk(int errval) {
	if (errval != CUBLAS_STATUS_SUCCESS) {
		fprintf(stderr, "Failed BLAS call, error code %d\n", errval);
	}
}

/*
Transa	CUDA_OP_N	Matrix A (Fourier coefficient matrix) is not transposed
Transb	CUDA_OP_N	Matrix B (input data) is not transposed
M	N_BEAMS	Number of rows of A/C
N	N_TIMESTEPS_PER_CALL	Number of columns of B/C
K	N_ANTENNAS	Number of columns of A, number of rows in B
Alpha	1.0/127	Fourier coefficients are 8-bit ints so must be normalized to 1
Atype	CUDA_C_8I	Data type of Fourier coefficient matrix (i.e. 8-bit + 8-bit integers)
Lda	N_BEAMS	Leading dimension of Fourier coefficient matrix
strideA	N_BEAMS*N_ANTENNAS	Stride between different frequencies in A
Btype	CUDA_C_8I	Data type of input data matrix
Ldb	N_ANTENNAS	Leading dimension of input matrix
StrideB	N_ANTENNAS*N_TIMESTEPS_PER_CALL	Stride between different frequencies in input matrix
Beta	0	Zero out the output data tensor
Ctype	CUDA_C_32F	Data type of output matrix
Ldc	N_BEAMS	Leading Dimension of output matrix
strideC	N_BEAMS*N_TIMESTEPS_PER_CALL	Stride between different frequencies in output matrix
batchCount	NCHANS	How many frequencies
computeType	CUDA_C_32F	Internal datatype
Algo	CUBLAS_GEMM_DEFAULT_TENSOR_OP	Use tensor operations
*/

struct beamform_context {
  int gpu_device;
  cublasHandle_t handle;
  cudaStream_t stream;
  // GPU buffers for intermediate data products
  float *in32_d; // Reordered [to inputs x chans x times x complexity], floatified 4-bit input data
  float *out_d;  // CUBLAS beamformer output [ntime x nchan x nbeam x complexity]
  float *weights_d; // Beamformer coefficients
  unsigned char *in4_d;     // 4-bit input data
  float *sum_out_d; // Time-summed output data, used only if ntimeblocks > 0
  int ninputs;   // Number of inputs (ants * pols)
  int npols;     // Number of polarizations per antenna
  int nchans;    // Number of channels input
  int ntimes;    // Number of time samples input
  int nbeams;    // Number of beams output
  int ntimeblocks; // Number of time samples to keep after summation
};

static struct beamform_context context;

void cublas_beamform_destroy(){
  cudaFree(context.in32_d);
  if (context.ntimeblocks > 0) {
    cudaFree(context.out_d);
  }
}

void cublas_beamform_init(int device, int ninputs, int nchans, int ntimes, int nbeams, int ntimeblocks) {
  context.gpu_device = device;
  gpuErrchk( cudaSetDevice(context.gpu_device) );
  gpuErrchk(cudaStreamCreate(&(context.stream)));
  gpuBLASchk(cublasCreate(&(context.handle)));
  gpuBLASchk(cublasSetStream(context.handle, context.stream));
  gpuBLASchk(cublasSetPointerMode(context.handle, CUBLAS_POINTER_MODE_HOST));
  //gpuBLASchk(cublasSetPointerMode(context.handle, CUBLAS_POINTER_MODE_DEVICE));
  gpuBLASchk(cublasSetMathMode(context.handle, CUBLAS_TENSOR_OP_MATH));

  context.ninputs = ninputs;
  context.nchans = nchans;
  context.ntimes = ntimes;
  context.nbeams = nbeams;
  context.ntimeblocks = ntimeblocks;

  // Internally allocate intermediate buffers
  gpuErrchk( cudaMalloc(&context.in32_d,  ninputs * nchans * ntimes * 2 * sizeof(float)) );
  //gpuErrchk( cudaMemcpy(context.in32_d, in32_h, ninputs * nchans * ntimes * 2 * sizeof(float), cudaMemcpyHostToDevice) );
  // If the context is initialized with ntimeblocks=0, then we do no summing so don't
  // need the intermediate buffer allocated internally.
  if (ntimeblocks > 0) {
    gpuErrchk( cudaMalloc(&context.out_d,   ntimes * nchans * nbeams * 2 * sizeof(float)) );
  }
}

void cublas_beamform(unsigned char *in4_d, float *out_d, float *weights_d) {
  // Transpose input data and promote to float.
  // CUBLAS doesn't support float coeffs with int8 data
  dim3 transBlockGrid(context.ntimes, context.nchans);
  dim3 transThreadGrid(context.ninputs / TRANSPOSE_POL_BLOCK_SIZE);
  trans_4bit_to_float<<<transBlockGrid, transThreadGrid, 0, context.stream>>>(
      in4_d,
      context.in32_d,
      context.ninputs,
      context.nchans,
      context.ntimes
  );
  cudaStreamSynchronize(context.stream);

  // If we are integrating beam powers, put the
  // GEM output in the internal intermediate
  // buffer. If not, then write beamformer output
  // to the address given by the user.
  float *gem_out_d;
  if (context.ntimeblocks > 0) {
    gem_out_d = context.out_d;
  } else {
    gem_out_d = out_d;
  }

  // Beamform using GEMM
  float alpha = 1.0;
  float beta = 0.0;
  // GEMM:
  // C <= alpha*AB + beta*C
  // alpha = 1.0
  // beta = 0.0
  // A matrix: beamforming coeffs (NBEAMS * NANTS)
  // B matrix: data matrix (NANTS * NTIMES)
    
  /*
  gpuBLASchk(cublasGemmStridedBatchedEx(
    context.handle,
    CUBLAS_OP_T, // transpose A?
    CUBLAS_OP_T, // transpose B?
    context.nbeams,      // m
    context.ntimes,      // n
    context.ninputs,     // k
    // Coeffs: [nchans x] nbeams x ninputs (m x k)
    &alpha,              // alpha
    weights_d,           // A
    CUDA_C_32F,          // A type
    context.ninputs,      // Lda
    context.nbeams*context.ninputs,// strideA : stride size
    // Data: [nchans x] ninputs x ntimes (k x n)
    context.in32_d,      // B
    CUDA_C_32F,          // B type
    context.ntimes,     // Ldb
    context.ninputs*context.ntimes,// strideB : stride size
    &beta,       // beta
    // Results
    gem_out_d,       // C
    CUDA_C_32F,          // Ctype 
    context.nbeams,      // Ldc
    context.nbeams*context.ntimes,// Stride C
    context.nchans,      // batchCount
    CUDA_C_32F,          // compute type
    CUBLAS_GEMM_DEFAULT_TENSOR_OP // algo
    ));
  */
  
  gpuBLASchk(cublasGemmStridedBatchedEx(
    context.handle,
    CUBLAS_OP_N, // transpose A?
    CUBLAS_OP_T, // transpose B?
    context.ntimes,      // n
    context.nbeams,      // m
    context.ninputs,     // k
    &alpha,              // alpha
    //
    // Data: [nchans x] ninputs x ntimes (k x n)
    context.in32_d,      // B
    CUDA_C_32F,          // B type
    context.ntimes,     // Ldb
    context.ninputs*context.ntimes,// strideB : stride size
    //
    // Coeffs: [nchans x] nbeams x ninputs (m x k)
    weights_d,           // A
    CUDA_C_32F,          // A type
    context.nbeams,      // Lda
    context.nbeams*context.ninputs,// strideA : stride size
    //
    &beta,       // beta
    // Results
    gem_out_d,       // C
    CUDA_C_32F,          // Ctype 
    context.ntimes,      // Ldc
    context.nbeams*context.ntimes,// Stride C
    context.nchans,      // batchCount
    CUDA_C_32F,          // compute type
    CUBLAS_GEMM_DEFAULT_TENSOR_OP // algo
    ));
  cudaStreamSynchronize(context.stream);

  // Optionally:
  if (context.ntimeblocks > 0) {
    // Create XX, YY, XY beam powers.
    // Sum over `ntimes_sum` samples
    // Write to the user-provided output buffer
    int ntimes_sum = context.ntimes / context.ntimeblocks;
    dim3 sumBlockGrid(context.nchans, context.nbeams/2);
    dim3 sumThreadGrid(context.ntimes / ntimes_sum);
    trans_output_and_sum<<<sumBlockGrid, sumThreadGrid, 0, context.stream>>>(
      gem_out_d,
      out_d,
      context.nchans,
      context.nbeams/2,
      context.ntimes,
      ntimes_sum
    );
    cudaStreamSynchronize(context.stream);
  }
}

/* Take input data of form
   nchan x nbeam x time x complex64 [i.e. the output of cublas_beamform],
   sum over ``ntimes_sum``, interpret beams `2n` and `2n+1` as a dual pol pair,
   and generate an output array of form
   nbeam x ntime / ntime_sum x nchan x nbeam / 2 x 4 x complex64.
   The last 4-element axis holds XX, YY, Re(XY), Im(XY
*/
void cublas_beamform_integrate(float *in_d, float *out_d, int ntimes_sum) {
  // Create XX, YY, XY beam powers.
  // Sum over `ntimes_sum` samples
  dim3 sumBlockGrid(context.nchans, context.nbeams/2);
  dim3 sumThreadGrid(context.ntimes / ntimes_sum);
  trans_output_and_sum<<<sumBlockGrid, sumThreadGrid>>>(
    in_d,
    out_d,
    context.nchans,
    context.nbeams/2,
    context.ntimes,
    ntimes_sum
  );
}

void cublas_beamform_integrate_single_beam(float *in_d, float *out_d, int ntimes_sum, int beam_index) {
  // Create XX, YY, XY beam powers.
  // Sum over `ntimes_sum` samples
  dim3 sumBlockGrid(context.nchans);
  dim3 sumThreadGrid(context.ntimes / ntimes_sum);
  trans_output_and_sum_single_beam<<<sumBlockGrid, sumThreadGrid>>>(
    in_d,
    out_d,
    context.nchans,
    context.nbeams/2,
    context.ntimes,
    ntimes_sum,
    beam_index
  );
}
