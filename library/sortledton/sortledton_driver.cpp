//
// Created by per on 03.02.21.
//

#include "sortledton_driver.hpp"

#include <chrono>

#include "not_implemented.hpp"

#include "data_types.h"
#include "versioning/EdgeDoesNotExistsPrecondition.h"

namespace gfe::library {

    thread_local uint SortledtonDriver::thread_id = 0;

    SortledtonDriver::SortledtonDriver(bool is_graph_directed, bool sparse_graph, uint64_t max_num_vertices,
                                       int num_threads, int block_size) : tm(num_threads), m_is_directed(is_graph_directed) {
      if (is_graph_directed == true) {
        throw std::invalid_argument("Only undirected graphs are currently supported by the front-end");
      }
      if (sparse_graph == true) { throw std::invalid_argument("Only dense graphs are supported by the front-end."); }
      ds = new VersioningBlockedSkipListAdjacencyList(block_size, tm); // TODO add max_num_vertices as an option to my data structure
    }

    SortledtonDriver::~SortledtonDriver() {
      delete ds;
      ds = nullptr;
    }

    void SortledtonDriver::on_thread_init(int thread_id) {
      SortledtonDriver::thread_id = tm.register_thread();
    }

    void SortledtonDriver::on_thread_destroy(int thread_id) {
      // nop
    }

    void SortledtonDriver::dump_ostream(std::ostream &out) const {
      throw NotImplemented();
    }

    uint64_t SortledtonDriver::num_edges() const {
      SortledtonDriver* non_const_this = const_cast<SortledtonDriver*>(this);
      SnapshotTransaction tx = non_const_this->tm.getSnapshotTransaction(ds, thread_id);
      auto num_edges = 0;  // TODO need to add this method.
      non_const_this->tm.transactionCompleted(tx, thread_id);
      return num_edges;
    }

    uint64_t SortledtonDriver::num_vertices() const {
      SortledtonDriver* non_const_this = const_cast<SortledtonDriver*>(this);
      SnapshotTransaction tx = non_const_this->tm.getSnapshotTransaction(ds, thread_id);
      auto num_vertices = tx.vertex_count();
      non_const_this->tm.transactionCompleted(tx, thread_id);
      return num_vertices;
    }

/**
 * Returns true if the given vertex is present, false otherwise
 */
    bool SortledtonDriver::has_vertex(uint64_t vertex_id) const {
      return vertex_id < num_vertices();  // TODO rethink
    }

/**
 * Returns the weight of the given edge is the edge is present, or NaN otherwise
 */
    double SortledtonDriver::get_weight(uint64_t source, uint64_t destination) const {
      SortledtonDriver* non_const_this = const_cast<SortledtonDriver*>(this);
      SnapshotTransaction tx = non_const_this->tm.getSnapshotTransaction(ds, thread_id);  // TODO weights currently not supported
      auto has_edge = tx.has_edge({source, destination});
      non_const_this->tm.transactionCompleted(tx, thread_id);
      return has_edge ? 0.0 : nan("");
    }

/**
 * Check whether the graph is directed
 */
    bool SortledtonDriver::is_directed() const {
      return m_is_directed;
    }

/**
 * Impose a timeout on each graph computation. A computation that does not terminate by the given seconds will raise a TimeoutError.
 */
    void SortledtonDriver::set_timeout(uint64_t seconds) {
      m_timeout = chrono::seconds { seconds };
    }

/**
 * Add the given vertex to the graph
 * @return true if the vertex has been inserted, false otherwise (that is, the vertex already exists)
 */
    bool SortledtonDriver::add_vertex(uint64_t vertex_id) {
      throw NotImplemented();
    }

/**
 * Remove the mapping for a given vertex. The actual internal vertex is not removed from the adjacency list.
 * @param vertex_id the vertex to remove
 * @return true if a mapping for that vertex existed, false otherwise
 */
    bool SortledtonDriver::remove_vertex(uint64_t vertex_id) {
      throw NotImplemented();
    }

/**
 * Add the given edge in the graph. The implementation does not check whether this edge already exists,
 * adding a new edge always.
 * @return always true when both the source & the destination vertices already exist, false otherwise
 */
    bool SortledtonDriver::add_edge(gfe::graph::WeightedEdge e) {
      edge_t internal_edge{e.source(), e.destination()};
      // TODO need to add vertices.
      SnapshotTransaction tx = tm.getSnapshotTransaction(ds, thread_id);

      VertexExistsPrecondition pre_v1(internal_edge.src);  // TODO write this precondition
      tx.register_precondition(&pre_v1);
      VertexExistsPrecondition pre_v2(internal_edge.dst);
      tx.register_precondition(&pre_v2);
      EdgeDoesNotExistsPrecondition pre_e(internal_edge);
      tx.register_precondition(&pre_e);

      bool inserted = true;
      try {
        tx.insert_edge(internal_edge);
        tx.execute();
      } catch (EdgeExistsException& e) {
        inserted = false;
      }
      tm.transactionCompleted(tx, thread_id);
      return inserted;
    }

    bool SortledtonDriver::add_edge_v2(gfe::graph::WeightedEdge e) {
      edge_t internal_edge{e.source(), e.destination()};

      SnapshotTransaction tx = tm.getSnapshotTransaction(ds, thread_id);

      EdgeDoesNotExistsPrecondition p(internal_edge);
      tx.register_precondition(&p);

      bool inserted = true;
      try {
        // TODO inserting vertices is a nop currently.
        tx.insert_vertex(internal_edge.src);
        tx.insert_vertex(internal_edge.dst);
        tx.insert_edge(internal_edge);
        tx.execute();
      } catch (EdgeExistsException& e) {
        inserted = false;
      }
      tm.transactionCompleted(tx, thread_id);
      return inserted;
    }

    bool SortledtonDriver::remove_edge(gfe::graph::Edge e) {
      throw NotImplemented();
    }

    void SortledtonDriver::bfs(uint64_t source_vertex_id, const char *dump2file) {
      throw NotImplemented();
    }

    void SortledtonDriver::pagerank(uint64_t num_iterations, double damping_factor, const char *dump2file) {
      throw NotImplemented();
    }

    void SortledtonDriver::wcc(const char *dump2file) {
      throw NotImplemented();
    }

    void SortledtonDriver::cdlp(uint64_t max_iterations, const char *dump2file) {
      throw NotImplemented();
    }

    void SortledtonDriver::lcc(const char *dump2file) {
      throw NotImplemented();
    }

    void SortledtonDriver::sssp(uint64_t source_vertex_id, const char *dump2file) {
      throw NotImplemented();
    }
}