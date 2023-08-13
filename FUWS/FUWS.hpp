#include "../Utils/data_types.hpp"
#include "../USeqTrie/USeqTrie.hpp"
#include "../WESCalc/WESCalc.hpp"

#ifndef FUWS_INCLUDED
#define FUWS_INCLUDED

std::pair<WUDatabase, ItemWeight> preProcess(const WUDatabase &db);
std::tuple<std::vector<ItemProbability>, std::vector<ItemProbability>, ItemWeight> determineExtensions(const WUDatabase &db);
std::vector<Sequence> FUWS(const WUDatabase &db, const ItemProbability min_sup, const ItemWeight wgt_fct);

#endif