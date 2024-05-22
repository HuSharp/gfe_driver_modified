//
// Created by per on 29.09.21.
//

#include "mixed_workload.hpp"

#include <future>
#include <chrono>
#include <unistd.h>
#if defined(HAVE_OPENMP)
  #include "omp.h"
#endif

#include "graphalytics.hpp"
#include "aging2_experiment.hpp"
#include "mixed_workload_result.hpp"
#include "library/interface.hpp"

#include "common/timer.hpp"

namespace gfe::experiment {

    using namespace std;
    using clock = std::chrono::steady_clock;

    MixedWorkloadResult MixedWorkload::execute() {
      auto aging_result_future = std::async(std::launch::async, &Aging2Experiment::execute, &m_aging_experiment);
      clock::time_point m_tstart = clock::now();
      common::Timer timer; timer.start();
      chrono::seconds progress_check_interval( 1 );
      this_thread::sleep_for( progress_check_interval );  // Poor mans synchronization to ensure AgingExperiment was able to setup the master etc
      while (true) {
        if (m_aging_experiment.progress_so_far() > 0.1 || aging_result_future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) { // The graph reached its final size
          break;
        }
        this_thread::sleep_for( progress_check_interval ) ;
      }
      cout << "Graph reached final size, executing graphaltyics now" << endl;

      // TODO change this to also work for LCC, generally this solution is very ugly
#if defined(HAVE_OPENMP)
      if(m_read_threads != 0 ){
                        cout << "[driver] OpenMP, number of threads for the Graphalytics suite: " << m_read_threads << endl;
                        omp_set_num_threads(m_read_threads);
                    }
#endif
      int i=1; 
      

      clock::time_point m_t0 = clock::now(); 
       // start time
      (m_aging_experiment.m_library)->create_epoch(100+i);
          cout<<"Current epochs: "<<100+i++<<endl;
      
      auto lembda = [&](){
        clock::time_point m_t0 = clock::now();
        while(1){
          clock::time_point m_t1 = clock::now();
          auto seconds = std::chrono::duration_cast<std::chrono::seconds>(m_t1 - m_t0);
          long long dur = seconds.count();
          usleep(500000);
          (m_aging_experiment.m_library)->run_gc();
          if(dur > 310)
            break;
        }
      };
          // lembda();
          std::thread gcthread(lembda);

      while (m_aging_experiment.progress_so_far() < 0.9 && aging_result_future.wait_for(std::chrono::seconds(0)) != std::future_status::ready) {
          clock::time_point m_t1 = clock::now();
          auto seconds = std::chrono::duration_cast<std::chrono::seconds>(m_t1 - m_t0);
          long long dur = seconds.count();
          if(dur > 5){
            (m_aging_experiment.m_library)->create_epoch(100+i);
            cout<<"Current epochs: "<<100+i++<<endl;
            m_t0 = clock::now();
          }
          // // // cout<<"\n\n"<<dur<<endl<<endl;
          // sleep(1);
          // seconds = std::chrono::duration_cast<std::chrono::seconds>(m_t1 - m_tstart);
          // dur = seconds.count();
          // cout<<"time taken till now: "<<timer<<endl;
          m_graphalytics.execute();
          // (m_aging_experiment.m_library)->run_gc();
          // if(i>4) break;
      }

      cout << "Waiting for aging experiment to finish" << endl;
      aging_result_future.wait();
      cout << "Getting aging experiment results" << endl;
      auto aging_result = aging_result_future.get();
      // sleep(20);
      // (m_aging_experiment.m_library)->create_epoch(100+i+1);
      // m_graphalytics.execute();
      m_graphalytics.report(false);
      gcthread.join();
      return MixedWorkloadResult { aging_result, m_graphalytics };
      
    }

}