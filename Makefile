useqtrie:
	g++ -std=c++17 USeqTrie/USeqTrie.cpp -c -o .object_files/USeqTrie

wescalc:
	g++ -std=c++17 WESCalc/WESCalc.cpp -c -o .object_files/WESCalc

fuws:
	g++ -std=c++17 FUWS/FUWS.cpp -c -o .object_files/FUWS

simulation0:
	g++ -std=c++17 USeqTrie/USeqTrie.cpp WESCalc/WESCalc.cpp FUWS/FUWS.cpp "Simulations/Simulation 0/main.cpp" -o "Simulations/Simulation 0/main"

simulation0_with_debug:
	g++ -std=c++17 USeqTrie/USeqTrie.cpp WESCalc/WESCalc.cpp FUWS/FUWS.cpp "Simulations/Simulation 0/main.cpp" /root/CP/Setup/include/debug.h -o "Simulations/Simulation 0/main"