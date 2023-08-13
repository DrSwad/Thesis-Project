#include "../Utils/data_types.hpp"
#include <cassert>

#ifndef USEQTRIE_INCLUDED
#define USEQTRIE_INCLUDED

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
  int total_items;
  std::vector<Node> nodes;
  USeqTrie(int total_items);
  int getChildNode(int node_id, char ext_type, ItemID item_id);
};

#endif