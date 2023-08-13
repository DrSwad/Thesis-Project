#include "WESCalc.hpp"
#include <cassert>
#include <algorithm>

template<typename T>
bool is_subset(const std::set<T> &superset, const std::set<T> &subset) {
  return includes(superset.begin(), superset.end(), subset.begin(), subset.end());
}

void WESCalc(const WUDatabase &db, USeqTrie &candidate_trie) {
  for (const USequence &seq : db.first) {
    std::vector<double> max_support_dp(seq.size() + 1, 1);
    int root_node_id = 0;
    double wgt_sum = 0;
    int item_cnt = 0;
    TrieTraverse(candidate_trie, db.second, seq, {}, root_node_id, max_support_dp, wgt_sum, item_cnt);
  }
}

void TrieTraverse(USeqTrie &candidate_trie, const std::vector<ItemWeight> &weights, const USequence &seq, const Itemset &cur_itemset, const int &cur_node_id, const std::vector<ItemProbability> &max_support_dp, const ItemWeight wgt_sum, const int item_cnt) {
  assert(cur_node_id < candidate_trie.nodes.size());
  for (const int child_node_id : candidate_trie.nodes[cur_node_id].children_node_ids) {
    Node &child_node = candidate_trie.nodes[child_node_id];
    const ItemID child_item_id = child_node.item_id;
    Itemset child_itemset;
    if (child_node.ext_type == 's') {
      child_itemset.insert(child_item_id);
    }
    else {
      child_itemset = cur_itemset;
      child_itemset.insert(child_item_id);
    }
    std::vector<ItemProbability> child_max_support_dp(seq.size() + 1);
    child_max_support_dp[0] = 0;
    for (int at_itemset = 0; at_itemset < seq.size(); at_itemset++) {
      Itemset seq_itemset;
      for (const UItem &item : seq[at_itemset]) {
        seq_itemset.insert(item.first);
      }
      if (is_subset(seq_itemset, child_itemset)) {
        ItemProbability child_edge_probability_in_seq = seq[at_itemset].at(child_item_id);

        if (child_node.ext_type == 's') {
          ItemProbability max_support = *std::max_element(max_support_dp.begin(), max_support_dp.begin() + at_itemset);
          child_max_support_dp[at_itemset + 1] = max_support * child_edge_probability_in_seq;
        }
        else {
          child_max_support_dp[at_itemset + 1] = max_support_dp[at_itemset + 1] * child_edge_probability_in_seq;
        }
      }
      else {
        child_max_support_dp[at_itemset + 1] = 0;
      }
    }

    double child_max_support = *std::max_element(child_max_support_dp.begin(), child_max_support_dp.end());
    double child_wgt_sum = wgt_sum + weights[child_item_id];
    int child_item_cnt = item_cnt + 1;
    child_node.WES += child_max_support * (child_wgt_sum / child_item_cnt);
    TrieTraverse(candidate_trie, weights, seq, child_itemset, child_node_id, child_max_support_dp, child_wgt_sum, child_item_cnt);
  }
}