#include "../../Utils/data_types.hpp"
#include "../../FUWS/FUWS.hpp"
#include <fstream>
#include <sstream>
#include <cassert>

int main() {
  WUDatabase db;

  std::ifstream ifs("weights.txt");
  std::map<std::string, int> item_id_map;
  {
    std::map<std::string, ItemWeight> mp;
    std::string item;
    ItemWeight weight;
    while (ifs >> item >> weight) {
      mp[item] = weight;
    }

    for (auto [item, weight] : mp) {
      int item_id = db.second.size();
      item_id_map[item] = item_id;
      db.second.push_back(weight);
    }
  }
  ifs.close();

  ifs.open("db.txt");
  {
    std::string line;
    while (getline(ifs, line)) {
      USequence seq;
      std::stringstream ss(line);
      char c;
      while (ss >> c) {
        assert(c == '(');
        UItemset itemset;
        while (true) {
          std::string item; ss >> item;  assert(item.back() == ':'); item.pop_back();
          ItemProbability probability; ss >> probability;
          itemset.insert(UItem(item_id_map[item], probability));

          ss >> c;
          if (c == ')') break;
          assert(c == ',');
        }
        seq.emplace_back(itemset);
      }

      db.first.emplace_back(seq);
    }
  }
  ifs.close();

  const ItemProbability min_sup = 0.2;
  const ItemWeight wgt_fct = 1.0;
  FUWS(db, min_sup, wgt_fct);

  return 0;
}