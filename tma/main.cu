#include "cutlass/util/command_line.h"

#include "scale_tma_kernel.h"
#include "tma_copy.h"
#include "tma_copy_multicast.h"

int main(int argc, char const **argv) {

  cutlass::CommandLine cmd(argc, argv);
  // Parses the command line

  int M, N, iterations;  
  cmd.get_cmd_line_argument("M", M, 16384);
  cmd.get_cmd_line_argument("N", N, 16384);
  cmd.get_cmd_line_argument("iterations", iterations, 10);
  cmd.get_cmd_line_argument("tile", tile, 128);

  std::cout << "(M, N): " << M << ", " << N << std::endl;


  // initial profiling
  copy_host_tma_load_and_store_kernel<128, 128>(M, N, iterations);
  copy_host_tma_load_and_store_kernel_multicast<true, 2, 128, 128>(M, N, iterations);
  copy_host_tma_load_and_store_kernel_multicast<true, 4, 128, 128>(M, N, iterations);
  copy_host_tma_load_and_store_kernel_multicast<false, 2, 128, 128>(M, N, iterations);
  copy_host_tma_load_and_store_kernel_multicast<false, 4, 128, 128>(M, N, iterations);
  
 
  //copy_host_tma_load_and_store_kernel_multicast<true, 2, 128, 128>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel<256, 256>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel(M/2, N/2, iterations);
  //copy_host_tma_load_and_store_kernel(M/4, N/4, iterations);
  //scaleTmaKernelHost(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<true, 1>(M, N, iterations);
  
  

  //copy_host_tma_load_and_store_kernel_multicast<true, 2, 256, 256>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<true, 4, 256, 256>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 2, 256, 256>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 4, 256, 256>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 2>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 4>(M, N, iterations);
  
  //copy_host_tma_load_and_store_kernel_multicast<true, 4>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 4>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<true, 8>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 8>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<true, 16>(M, N, iterations);
  //copy_host_tma_load_and_store_kernel_multicast<false, 16>(M, N, iterations);
  return 0;
}
