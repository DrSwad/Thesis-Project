#include "USeqTrie.hpp"

Node::Node(char ext_type, ItemID item_id) : ext_type(ext_type), item_id(item_id) {
  assert(ext_type == 'i' or ext_type == 's');
  WES = 0;
}

USeqTrie::USeqTrie(int total_items) : total_items(total_items) {
  nodes.emplace_back(Node('s', -1));
}

int USeqTrie::getChildNode(int node_id, char ext_type, ItemID item_id) {
  int id = (ext_type == 's') * total_items + item_id;
  if (nodes[node_id].children_node_ids[id] == -1) {
    int child_id = nodes.size();
    nodes.emplace_back(ext_type, item_id);
    nodes[node_id].children_node_ids[id] = child_id;
  }
  return nodes[node_id].children_node_ids[id];
}