#include "../Utils/data_types.hpp"

class Node {
public:
  std::vector<int> children_node_ids;
  char ext_type; // 'i' or 's'
  ItemID item_id;
  double WES;
  Node(char ext_type, ItemID item_id);
};

class USeqTrie {
public:
  std::vector<Node> nodes;
  USeqTrie();
};