#include "FUWS.hpp"
#include "debug.h"
#include <iostream>

std::pair<WUDatabase, ItemWeight> preProcess(const WUDatabase &db) {
  ItemWeight wgt_sum = 0;
  int item_cnt = 0;
  WUDatabase pdb = db;

  for (USequence &seq : pdb.first) {
    std::vector<ItemProbability> item_max_probability(pdb.second.size(), 0);

    for (auto it = seq.rbegin(); it != seq.rend(); it++) {
      UItemset &itemset = *it;
      std::vector<ItemID> item_ids;

      for (auto & [item_id, probability] : itemset) {
        wgt_sum += pdb.second[item_id];
        item_cnt++;
        item_max_probability[item_id] = std::max(item_max_probability[item_id], probability);
        item_ids.push_back(item_id);
      }

      for (ItemID item_id : item_ids) {
        itemset[item_id] = item_max_probability[item_id];
      }
    }
  }

  return make_pair(pdb, wgt_sum / item_cnt);
}

std::tuple<std::vector<ItemProbability>, std::vector<ItemProbability>, ItemWeight> determineExtensions(const WUDatabase &db) {
  const int total_items = db.second.size();
  std::vector<ItemProbability> max_prs(total_items, 0);
  std::vector<ItemProbability> exp_sups(total_items, 0);
  ItemWeight max_item_weight = 0;

  for (const USequence &seq : db.first) {
    std::vector<ItemProbability> seq_max_prs(total_items, 0);
    for (const UItemset &itemset : seq) {
      for (const auto [item, probability] : itemset) {
        max_prs[item] = std::max(max_prs[item], probability);
        seq_max_prs[item] = std::max(seq_max_prs[item], probability);
        max_item_weight = std::max(max_item_weight, db.second[item]);
      }
    }
    for (ItemID item = 0; item < total_items; item++) {
      exp_sups[item] += seq_max_prs[item];
    }
  }

  return {max_prs, exp_sups, max_item_weight};
}

WUDatabase projectedDatabase(const WUDatabase &db, ItemID item) {
  WUDatabase pdb;
  pdb.second = db.second;

  for (const USequence &seq : db.first) {
    pdb.first.push_back({});
    bool item_found = false;
    for (const UItemset &itemset : seq) {
      if (!item_found) {
        if (itemset.find(item) == itemset.end()) continue;
        item_found = true;
        UItemset new_itemset = itemset;
        while (!new_itemset.empty() and new_itemset.begin()->first <= item) {
          new_itemset.erase(new_itemset.begin());
        }
        pdb.first.back().emplace_back(new_itemset);
      }
      else {
        pdb.first.back().emplace_back(itemset);
      }
    }
  }

  return pdb;
}

void FUWSP(const double minWES, const WUDatabase &db, const ItemProbability seq_max_probs_product, const ItemWeight seq_max_item_weight, const ItemWeight sum_of_seq_item_weights, USeqTrie &candidateTrie, int cur_node_id) {
  // DB();
  // debug(minWES, db, seq_max_probs_product, seq_max_item_weight, sum_of_seq_item_weights, cur_node_id);

  auto [max_prs, exp_sups, max_item_weight] = determineExtensions(db);
  // debug(max_prs, exp_sups, max_item_weight);
  int total_items = db.second.size();
  for (ItemID item_id = 0; item_id < total_items; item_id++) {
    for (char ext_type : {'i', 's'}) {
      ItemProbability exp_sup_cap = seq_max_probs_product * exp_sups[item_id];
      ItemWeight weight_cap = std::max(seq_max_item_weight, max_item_weight);
      double w_exp_sup = exp_sup_cap * weight_cap;
      if (w_exp_sup >= minWES) {
        // debug(item_id, ext_type);
        int child_node_id = candidateTrie.getChildNode(cur_node_id, ext_type, item_id);
        FUWSP(minWES, projectedDatabase(db, item_id), seq_max_probs_product * max_prs[item_id], std::max(seq_max_item_weight, db.second[item_id]), sum_of_seq_item_weights + db.second[item_id], candidateTrie, child_node_id);
      }
    }
  }
}

void findFrequentSequencesFromTrie(int minWES, const USeqTrie &candidateTrie, int cur_node_id, Sequence &cur_seq, std::vector<Sequence> seqs) {
  if (candidateTrie.nodes[cur_node_id].WES < minWES) return;
  seqs.emplace_back(cur_seq);

  int total_items = candidateTrie.total_items;
  for (int item_id = 0, at = 0; item_id < total_items; item_id++, at++) {
    for (char ext_type : {'i', 's'}) {
      int child_node_id = candidateTrie.nodes[cur_node_id].children_node_ids[at];
      if (child_node_id != -1) {
        if (ext_type == 'i') cur_seq.back().insert(item_id);
        else cur_seq.push_back({item_id});
        findFrequentSequencesFromTrie(minWES, candidateTrie, child_node_id, cur_seq, seqs);
        if (ext_type == 'i') cur_seq.back().erase(item_id);
        else cur_seq.pop_back();
      }
    }
  }
}

std::vector<Sequence> FUWS(const WUDatabase &db, const ItemProbability min_sup, const ItemWeight wgt_fct) {
  auto [pdb, WAM] = preProcess(db);
  double minWES = min_sup * pdb.first.size() * WAM * wgt_fct;

  int total_items = pdb.second.size();
  USeqTrie candidateTrie(total_items);
  FUWSP(minWES, pdb, 1, 0, 0, candidateTrie, 0);
  // WESCalc(db, candidateTrie);

  std::vector<Sequence> seqs;
  Sequence seq;
  // findFrequentSequencesFromTrie(minWES, candidateTrie, 0, seq, seqs);

  return seqs;
}