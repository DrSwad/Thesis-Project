#include <is_subset.hpp>

template<typename T>
bool is_subset(const std::set<T> &superset, const std::set<T> &subset) {
  return includes(superset.begin(), superset.end(), subset.begin(), subset.end());
}