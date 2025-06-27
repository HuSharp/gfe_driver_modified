#ifndef GFE_DRIVER_MIXED_WORKLOAD_H
#define GFE_DRIVER_MIXED_WORKLOAD_H

namespace gfe::experiment
{
class Aging2Experiment;
}
namespace gfe::experiment
{
class GraphalyticsSequential;
}
namespace gfe::experiment
{
class MixedWorkloadResult;
}

namespace gfe::experiment
{

class MixedWorkload
{
public:
    MixedWorkload(
        Aging2Experiment & aging_experiment,
        GraphalyticsSequential & graphalytics,
        GraphalyticsSequential & graphalytics2,
        int read_threads)
        : m_aging_experiment(aging_experiment)
        , m_graphalytics(graphalytics)
        , m_graphalytics2(graphalytics2)
        , m_read_threads(read_threads)
    {}

    MixedWorkloadResult execute();

private:
    Aging2Experiment & m_aging_experiment;
    GraphalyticsSequential & m_graphalytics;
    GraphalyticsSequential & m_graphalytics2;

    int m_read_threads = 0;
};

} // namespace gfe::experiment

#endif //GFE_DRIVER_MIXED_WORKLOAD_H
