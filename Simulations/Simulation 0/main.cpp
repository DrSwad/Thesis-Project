#include "../../Utils/data_types.hpp"
#include "../../FUWS/FUWS.hpp"
#include <fstream>
#include <sstream>
#include <cassert>

std::pair<std::map<std::string, int>, std::vector<ItemWeight>> read_item_weights(std::string directory) {
  std::string weight_file = directory + "/weights.txt";
  std::ifstream ifs(weight_file);

  std::map<std::string, int> item_id_map;
  std::vector<ItemWeight> item_weights;

  {
    std::map<std::string, ItemWeight> mp;
    std::string item;
    ItemWeight weight;
    while (ifs >> item >> weight) {
      mp[item] = weight;
    }

    for (auto [item, weight] : mp) {
      int item_id = item_weights.size();
      item_id_map[item] = item_id;
      item_weights.push_back(weight);
    }
  }

  ifs.close();

  return {item_id_map, item_weights};
}

UDatabase read_uncertain_database(std::string directory, std::map<std::string, int> &item_id_map) {
  std::string db_file = directory + "/db.txt";
  std::ifstream ifs(db_file);

  UDatabase db;
  std::string line;

  while (getline(ifs, line)) {
    USequence seq;
    std::stringstream ss(line);
    char c;
    while (ss >> c) {
      assert(c == '(');
      UItemset itemset;
      while (true) {
        std::string item; ss >> item; assert(item.back() == ':'); item.pop_back();
        ItemProbability probability; ss >> probability;
        itemset.insert(UItem(item_id_map[item], probability));

        ss >> c;
        if (c == ')') break;
        assert(c == ',');
      }
      seq.emplace_back(itemset);
    }

    db.emplace_back(seq);
  }

  ifs.close();

  return db;
}

int main() {
  WUDatabase db;

  auto [item_id_map, item_weights] = read_item_weights("Simulations/Simulation 0");
  db.second = item_weights;
  auto udb = read_uncertain_database("Simulations/Simulation 0", item_id_map);
  db.first = udb;

  const ItemProbability min_sup = 0.2;
  const ItemWeight wgt_fct = 1.0;
  FUWS(db, min_sup, wgt_fct);

  return 0;
}