#ifndef DATA_TYPES_INCLUDED
#define DATA_TYPES_INCLUDED

#include <utility>
#include <set>
#include <vector>
#include <map>

typedef int ItemID;
typedef double ItemProbability;
typedef double ItemWeight;

typedef ItemID Item;
typedef std::pair<ItemID, ItemProbability> UItem;

typedef std::set<Item> Itemset;
typedef std::map<ItemID, ItemProbability> UItemset;

typedef std::vector<Itemset> Sequence;
typedef std::vector<UItemset> USequence;

typedef std::vector<USequence> UDatabase;
typedef std::pair<UDatabase, std::vector<ItemWeight>> WUDatabase;

#endif