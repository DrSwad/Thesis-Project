#include "../Utils/data_types.hpp"
#include "../Utils/is_subset.hpp"
#include "../USeqTrie/USeqTrie.hpp"

void WESCalc(const WUDatabase &db, USeqTrie &candidate_trie);

void TrieTraverse(USeqTrie &candidate_trie, const std::vector<ItemWeight> &weights, const USequence &seq, const Itemset &cur_itemset, const int &cur_node_id, const std::vector<ItemProbability> &max_support_dp, const ItemWeight wgt_sum, const int item_cnt);