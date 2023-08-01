#include "USeqTrie.hpp"

class Node {
public:
  std::vector<int> children_node_ids;
  char ext_type;
  ItemID item_id;
  double WES;
  Node(char ext_type, ItemID item_id) : ext_type(ext_type), item_id(item_id) {
    assert(ext_type == 'i' or ext_type == 's');
    WES = 0;
  }
};

class USeqTrie {
public:
  std::vector<Node> nodes;
  USeqTrie() {
    nodes.emplace_back();
  }
};