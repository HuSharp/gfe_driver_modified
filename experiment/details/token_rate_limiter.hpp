#include <algorithm>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <thread>

class TokenBucketRateLimiter
{
private:
    uint64_t m_target_rate;
    uint64_t m_bucket_capacity;

    std::atomic<double> m_tokens; // available tokens
    std::atomic<bool> m_running; // background thread running
    std::thread m_refill_thread;
    double m_ns_per_token;

    std::atomic<uint64_t> m_operations_count;
    std::atomic<uint64_t> m_wait_count;
    std::chrono::steady_clock::time_point m_stats_start_time;
    double m_current_rate;

    std::mutex m_mutex;
    std::condition_variable m_cv;


public:
    TokenBucketRateLimiter(uint64_t target_rate, uint64_t bucket_capacity = 0)
        : m_target_rate(target_rate)
        , m_bucket_capacity(bucket_capacity == 0 ? target_rate / 2 : bucket_capacity)
        , m_tokens(0)
        , m_running(false)
        , m_operations_count(0)
        , m_wait_count(0)
        , m_stats_start_time(std::chrono::steady_clock::now())
    {
        start();
    }

    ~TokenBucketRateLimiter() { stop(); }

    void start()
    {
        if (!m_running.exchange(true))
        {
            m_refill_thread = std::thread(&TokenBucketRateLimiter::refill_loop, this);
        }
    }

    void stop()
    {
        if (m_running.exchange(false))
        {
            m_cv.notify_all();
            if (m_refill_thread.joinable())
            {
                m_refill_thread.join();
            }
        }
    }

    void set_target_rate(uint64_t target_rate)
    {
        m_target_rate = target_rate;
        m_bucket_capacity = std::max(m_bucket_capacity, target_rate / 2);
    }

    struct Stats
    {
        uint64_t operations_count;
        uint64_t wait_count;
        double current_rate;
        double elapsed_seconds;
        double wait_ratio;
    };

    Stats get_stats()
    {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - m_stats_start_time).count();

        Stats stats;
        stats.operations_count = m_operations_count.load();
        stats.wait_count = m_wait_count.load();
        stats.elapsed_seconds = elapsed > 0 ? elapsed : 1.0;
        stats.current_rate = stats.operations_count / stats.elapsed_seconds;
        stats.wait_ratio
            = stats.operations_count > 0 ? static_cast<double>(stats.wait_count) / stats.operations_count : 0.0;

        return stats;
    }

    void acquire(uint64_t tokens = 1)
    {
        m_operations_count.fetch_add(1);

        // quick path
        double current = m_tokens.load();
        while (current >= tokens)
        {
            if (m_tokens.compare_exchange_weak(current, current - tokens))
            {
                return;
            }
        }

        m_wait_count.fetch_add(1);
        // slow path
        // wait for tokens to be available
        std::unique_lock<std::mutex> lock(m_mutex);
        m_cv.wait(lock, [this, tokens]() {
            if (!m_running.load())
                return true;

            double current = m_tokens.load();
            if (current >= tokens)
            {
                // try to acquire tokens
                while (current >= tokens)
                {
                    if (m_tokens.compare_exchange_weak(current, current - tokens))
                    {
                        return true;
                    }
                }
            }
            return false;
        });
    }

    void refill_loop()
    {
        // 10ms interval
        // 10ms = 10,000,000 ns
        constexpr uint64_t refill_interval_ns = 10000000;
        // 1s = 1,000,000,000 ns
        double tokens_per_interval = static_cast<double>(m_target_rate) * refill_interval_ns / 1000000000.0;

        while (m_running.load())
        {
            // load current tokens
            double current = m_tokens.load();
            double new_tokens = std::min(current + tokens_per_interval, static_cast<double>(m_bucket_capacity));
            // update tokens
            while (!m_tokens.compare_exchange_weak(current, new_tokens))
            {
                new_tokens = std::min(current + tokens_per_interval, static_cast<double>(m_bucket_capacity));
            }

            // notify waiting threads if we have more tokens
            if (new_tokens > current)
            {
                m_cv.notify_one();
            }

            std::this_thread::sleep_for(std::chrono::nanoseconds(refill_interval_ns));

            tokens_per_interval = static_cast<double>(m_target_rate) * refill_interval_ns / 1000000000.0;
        }
    }
};