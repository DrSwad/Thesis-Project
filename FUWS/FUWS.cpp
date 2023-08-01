#include "FUWS.hpp"
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
        itemset.insert(UItem(item_id, item_max_probability[item_id]));
      }
    }
  }

  return make_pair(pdb, wgt_sum / item_cnt);
}

std::vector<Sequence> FUWS(const WUDatabase &db, const ItemProbability min_sup, const ItemWeight wgt_fct) {
  auto [pdb, WAM] = preProcess(db);
  double minWES = min_sup * db.first.size() * WAM * wgt_fct;
  std::cerr << minWES << std::endl;

  return {};
}