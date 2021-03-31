//  Created by Pieter Leyman on 10/03/2020.
//  Copyright (c) 2020 Pieter Leyman. All rights reserved.
//  Own implementation VRP_heuristic from Christiaens and Vanden Berghe (2020) 
//  Christiaens, J. and Vanden Berghe, G. (2020). Slack induction by string removals for vehicle routing problems. Transportation Science, 54:417-433.

#include <cmath>
#include <math.h>
#include <ctime>
#include <cstdlib> //for srand() and rand()
#include <iostream>
#include <stdio.h>
#include <random>
#include <string>
#include <cstring>
#include <sstream> 
#include <inttypes.h>

#define VERYSMALL -100000000
#define VERYLARGE 100000000
#define epsilon 0.0001

#define MAX(A,B) ((A)>(B)?(A):(B))
#define MIN(A,B) ((A)>(B)?(B):(A))

//To adjust (if needed, based on data used)
#define maxNode 1001
#define maxProb 100
#define maxFileNameLength 15

//following 2 lines are for mersene twister
std::random_device rd;
std::mt19937 generator(rd());
std::uniform_real_distribution<double> unifRealDistr(0.0, 1.0);

#define maxParam 15
#define maxParamNameLength 30
//parameters
int numberItLSConstant = 30000;//300000, multiply with #customers/nodes
//SA
double startTemp = 100.0;//100.0
std::string startTempString = "-startTemp";
double endTemp = 1.0;//1.0
std::string endTempString = "-endTemp";
double tempConst;//should include numberNodes!! = pow(endTemp / startTemp, 1.0 / (double)numberItLSConstant);
//ruin
int avRemovedCust = 10;//10, c^-
std::string avRemovedCustString = "-avRemovedCust";
int lengthRemovedStrings = 10;//10, L^max
std::string lengthRemovedStringsString = "-lengthRemovedStrings";
int numberOfStringsConstant = 4;//4
std::string numberOfStringsConstantString = "-numberOfStringsConstant";
double alpha = 0.01;//0.01, beta (new name published version)
std:: string alphaString = "-alpha";
double probSplitString = 0.5;//0.5, alpha
std::string probSplitStringString = "-probSplitString";
//recreate
double blinkRate = 0.01;//0.01, gamma
std::string blinkRateString = "-blinkRate";
int sortRandom = 4;//4
std::string sortRandomString = "-sortRandom";
int sortDemandLarge = 4;//4
std::string sortDemandLargeString = "-sortDemandLarge";
int sortDistDepotLarge = 2;//2
std::string sortDistDepotLargeString = "-sortDistDepotLarge";
int sortDistDepotSmall = 1;//1
std::string sortDistDepotSmallString = "-sortDistDepotSmall";
int copyRemovedNodeRandom[maxNode];
double weightNodeRandom[maxNode];
int copyRemovedNodeDemand[maxNode];
int weightNodeDemand[maxNode];
int copyRemovedNodeDistLarge[maxNode];
int weightNodeDistLarge[maxNode];
int copyRemovedNodeDistSmall[maxNode];
int weightNodeDistSmall[maxNode];
int totalSort;
double probRandom;
double probDemandLarge;
double probDistLarge;

//input
FILE *infile;
int numberNodes;
int nodeDemand[maxNode];
int position[maxNode][2];//coordinates of each nodes/job
int distance[maxNode][maxNode];//distances between nodes, calculated based on position
int vehicleCap;
int nodeDistList[maxNode][maxNode];//contains the node number of all other nodes, given a node number, in increasing order of distance to the given node (compute in advance)

double cutoff;

//output
FILE *outfile;
int solutionsDistBest;

struct solution
{
	int totalDist;
	int numberTours;
	int tours[maxNode][maxNode];//first index: #tours, second index: nodes in tour
	int numberNodesInTour[maxNode];//does not include depot
	int capacityUsageTour[maxNode];
	int numberAbsentNodes;
	int absentNodes[maxNode];
	int tourPerNode[maxNode];//contains the number of each node's tour (-1 if not in any route)
}bestSol, currentSol, SISRsSol;

long double twoPow32;
uint32_t w, x, y, z;

uint32_t xorshift128(void)
{
	uint32_t t = x;
	t ^= t << 11U;//U:unsigned
	t ^= t >> 8U;
	x = y; y = z; z = w;
	w ^= w >> 19U;
	w ^= t;
	return w;
}

//sorting algorithms
int partitionDecrInt(int start, int end, int valList[], int countList[], int thirdList[])
{
	int pivot = valList[end];
	while (start<end)
	{
		while (valList[start]>pivot)
			start++;
		while (valList[end]<pivot)
			end--;
		if (valList[start] == valList[end])
			start++;
		else if (start<end)
		{
			int temp = valList[start];
			valList[start] = valList[end];
			valList[end] = temp;
			int temp2 = countList[start];
			countList[start] = countList[end];
			countList[end] = temp2;
			int temp3 = thirdList[start];
			thirdList[start] = thirdList[end];
			thirdList[end] = temp3;
		}
	}
	return end;
}

void quicksortDecrInt(int start, int end, int valList[], int countList[], int thirdList[])
{
	if (start<end)
	{
		int pivot = partitionDecrInt(start, end, valList, countList, thirdList);
		quicksortDecrInt(start, pivot - 1, valList, countList, thirdList);
		quicksortDecrInt(pivot + 1, end, valList, countList, thirdList);
	}
}

int partitionDecrInt(int start, int end, int valList[], int countList[])
{
	int pivot = valList[end];
	while (start<end)
	{
		while (valList[start]>pivot)
			start++;
		while (valList[end]<pivot)
			end--;
		if (valList[start] == valList[end])
			start++;
		else if (start<end)
		{
			int temp = valList[start];
			valList[start] = valList[end];
			valList[end] = temp;
			int temp2 = countList[start];
			countList[start] = countList[end];
			countList[end] = temp2;
		}
	}
	return end;
}

void quicksortDecrInt(int start, int end, int valList[], int countList[])
{
	if (start<end)
	{
		int pivot = partitionDecrInt(start, end, valList, countList);
		quicksortDecrInt(start, pivot - 1, valList, countList);
		quicksortDecrInt(pivot + 1, end, valList, countList);
	}
}

int partitionIncrInt(int start, int end, int valList[], int countList[])
{
	int pivot = valList[end];
	while (start<end)
	{
		while (valList[start]<pivot)
			start++;
		while (valList[end]>pivot)
			end--;
		if (valList[start] == valList[end])
			start++;
		else if (start<end)
		{
			int temp = valList[start];
			valList[start] = valList[end];
			valList[end] = temp;
			int temp2 = countList[start];
			countList[start] = countList[end];
			countList[end] = temp2;
		}
	}
	return end;
}

void quicksortIncrInt(int start, int end, int valList[], int countList[])
{
	if (start<end)
	{
		int pivot = partitionIncrInt(start, end, valList, countList);
		quicksortIncrInt(start, pivot - 1, valList, countList);
		quicksortIncrInt(pivot + 1, end, valList, countList);
	}
}

int partitionIncrInt(int start, int end, int valList[], int countList[], int thirdList[])
{
	int pivot = valList[end];
	while (start<end)
	{
		while (valList[start]<pivot)
			start++;
		while (valList[end]>pivot)
			end--;
		if (valList[start] == valList[end])
			start++;
		else if (start<end)
		{
			int temp = valList[start];
			valList[start] = valList[end];
			valList[end] = temp;
			int temp2 = countList[start];
			countList[start] = countList[end];
			countList[end] = temp2;
			int temp3 = thirdList[start];
			thirdList[start] = thirdList[end];
			thirdList[end] = temp3;
		}
	}
	return end;
}

void quicksortIncrInt(int start, int end, int valList[], int countList[], int thirdList[])
{
	if (start<end)
	{
		int pivot = partitionIncrInt(start, end, valList, countList, thirdList);
		quicksortIncrInt(start, pivot - 1, valList, countList, thirdList);
		quicksortIncrInt(pivot + 1, end, valList, countList, thirdList);
	}
}

int partitionIncrDouble(int start, int end, double valList[], int countList[])
{
	double pivot = valList[end];
	while (start<end)
	{
		while (valList[start]<pivot)
			start++;
		while (valList[end]>pivot)
			end--;
		if (valList[start] == valList[end])
			start++;
		else if (start<end)
		{
			double temp = valList[start];
			valList[start] = valList[end];
			valList[end] = temp;
			int temp2 = countList[start];
			countList[start] = countList[end];
			countList[end] = temp2;
		}
	}
	return end;
}

void quicksortIncrDouble(int start, int end, double valList[], int countList[])
{
	if (start<end)
	{
		int pivot = partitionIncrDouble(start, end, valList, countList);
		quicksortIncrDouble(start, pivot - 1, valList, countList);
		quicksortIncrDouble(pivot + 1, end, valList, countList);
	}
}

int partitionDecrDouble(int start, int end, double valList[], int countList[])
{
	double pivot = valList[end];
	while (start<end)
	{
		while (valList[start]>pivot)
			start++;
		while (valList[end]<pivot)
			end--;
		if (valList[start] == valList[end])
			start++;
		else if (start<end)
		{
			double temp = valList[start];
			valList[start] = valList[end];
			valList[end] = temp;
			int temp2 = countList[start];
			countList[start] = countList[end];
			countList[end] = temp2;
		}
	}
	return end;
}

void quicksortDecrDouble(int start, int end, double valList[], int countList[])
{
	if (start<end)
	{
		int pivot = partitionDecrDouble(start, end, valList, countList);
		quicksortDecrDouble(start, pivot - 1, valList, countList);
		quicksortDecrDouble(pivot + 1, end, valList, countList);
	}
}

int writeResults()
{
	char name[100];
	strcpy(name, "Results.txt");
	outfile = fopen(name, "a");
	fprintf(outfile, "%d\n", solutionsDistBest);
	fclose(outfile);
	return 0;
}

int readInput(std::string fileName)
{
	infile = fopen(fileName.c_str(), "r");
	int trash = 0;
	//skip introduction trash 
	char str[100];
	while (true)//yes, I will have to use a break statement to get out of this later... (frack)
	{
		fscanf(infile, "%s", &str);
		if (strcmp(str, "DIMENSION") == 0)
		{
			fscanf(infile, "%s", &str);
			fscanf(infile, "%d", &numberNodes);
		}
		else if (strcmp(str, "CAPACITY") == 0)
		{
			fscanf(infile, "%s", &str);
			fscanf(infile, "%d", &vehicleCap);
		}
		else if (strcmp(str, "NODE_COORD_SECTION") == 0)
			break;
	}
	//read node coordinates
	for (int index1 = 0; index1 < numberNodes; index1++)
		fscanf(infile, "%d\t %d\t %d", &trash, &position[index1][0], &position[index1][1]);
	//calc distances
	for (int index1 = 0; index1 < numberNodes; index1++)
	{
		distance[index1][index1] = 0;
		for (int index2 = index1 + 1; index2 < numberNodes; index2++)
		{
			int diffX = position[index1][0] - position[index2][0];
			int squareX = diffX * diffX;
			int diffY = position[index1][1] - position[index2][1];
			int squareY = diffY * diffY;
			distance[index1][index2] = distance[index2][index1] = int(round(sqrt((double)(squareX + squareY))));
		}
	}
	for (int index1 = 1; index1 < numberNodes; index1++)
	{
		int nodeList[maxNode];
		int localDistList[maxNode];
		int countNodes = 0;
		for (int index2 = 1; index2 < numberNodes; index2++)
		{
			if (index2 != index1)
			{
				nodeList[countNodes] = index2 + 1;
				localDistList[countNodes++] = distance[index1][index2];
			}
		}
		quicksortIncrInt(0, numberNodes - 3, localDistList, nodeList);
		for (int index2 = 0; index2 < numberNodes - 2; index2++)
			nodeDistList[index1][index2] = nodeList[index2];
	}
	//skip DEMAND_SECTION header
	fscanf(infile, "%s", &str);
	//read node demands
	for (int index1 = 0; index1 < numberNodes; index1++)
		fscanf(infile, "%d %d", &trash, &nodeDemand[index1]);
	fclose(infile);
	return 0;
}

int copySISRsToCurrent()
{
	currentSol.totalDist = SISRsSol.totalDist;
	currentSol.numberTours = SISRsSol.numberTours;
	for (int index1 = 0; index1 < currentSol.numberTours; index1++)
	{
		currentSol.numberNodesInTour[index1] = SISRsSol.numberNodesInTour[index1];
		for (int index2 = 0; index2 < currentSol.numberNodesInTour[index1]; index2++)
			currentSol.tours[index1][index2] = SISRsSol.tours[index1][index2];
	}
	for (int index1 = 1; index1 < numberNodes; index1++)
		currentSol.tourPerNode[index1] = SISRsSol.tourPerNode[index1];
	return 0;
}

int copySISRsToBest()
{
	bestSol.totalDist = SISRsSol.totalDist;
	bestSol.numberTours = SISRsSol.numberTours;
	for (int index1 = 0; index1 < bestSol.numberTours; index1++)
	{
		bestSol.numberNodesInTour[index1] = SISRsSol.numberNodesInTour[index1];
		bestSol.capacityUsageTour[index1] = SISRsSol.capacityUsageTour[index1];
		for (int index2 = 0; index2 < bestSol.numberNodesInTour[index1]; index2++)
			bestSol.tours[index1][index2] = SISRsSol.tours[index1][index2];
	}
	return 0;
}

int copyCurrentToBest()
{
	bestSol.totalDist = currentSol.totalDist;
	bestSol.numberTours = currentSol.numberTours;
	for (int index1 = 0; index1 < bestSol.numberTours; index1++)
	{
		bestSol.numberNodesInTour[index1] = currentSol.numberNodesInTour[index1];
		bestSol.capacityUsageTour[index1] = currentSol.capacityUsageTour[index1];
		for (int index2 = 0; index2 < bestSol.numberNodesInTour[index1]; index2++)
			bestSol.tours[index1][index2] = currentSol.tours[index1][index2];
	}
	return 0;
}

int copyCurrentToSISRs()
{
	SISRsSol.totalDist = currentSol.totalDist;
	SISRsSol.numberTours = currentSol.numberTours;
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
	{
		SISRsSol.numberNodesInTour[index1] = currentSol.numberNodesInTour[index1];
		for (int index2 = 0; index2 <SISRsSol.numberNodesInTour[index1]; index2++)
			SISRsSol.tours[index1][index2] = currentSol.tours[index1][index2];
	}
	for (int index1 = 1; index1 < numberNodes; index1++)
		SISRsSol.tourPerNode[index1] = currentSol.tourPerNode[index1];
	return 0;
}

int startSol()
{
	twoPow32 = 2;
	for (int index1 = 1; index1 < 32; index1++)
		twoPow32 *= 2;
	//1 customer per tour, save in currentSol
	currentSol.numberTours = numberNodes - 1;
	currentSol.totalDist = 0;
	for (int index1 = 0; index1 < currentSol.numberTours; index1++)
	{
		currentSol.numberNodesInTour[index1] = 1;
		currentSol.tours[index1][0] = index1 + 2;
		currentSol.capacityUsageTour[index1] = nodeDemand[index1 + 1];//first tour corresponds with node 2 and so on (node 1 is depot)
		currentSol.totalDist += (distance[0][index1 + 1] * 2);
	}
	currentSol.numberAbsentNodes = 0;
	currentSol.tourPerNode[0] = -1;//depot
	for (int index1 = 1; index1 < numberNodes; index1++)
		currentSol.tourPerNode[index1] = index1;
	//how to sort removed nodes: 4 options
	for (int index1 = 1; index1 < numberNodes; index1++)
	{
		copyRemovedNodeRandom[index1] = index1 + 1;
		weightNodeRandom[index1] = (double)(xorshift128() / twoPow32);
		copyRemovedNodeDemand[index1] = index1 + 1;
		weightNodeDemand[index1] = nodeDemand[index1];
		copyRemovedNodeDistLarge[index1] = index1 + 1;
		weightNodeDistLarge[index1] = distance[index1][0];
		copyRemovedNodeDistSmall[index1] = index1 + 1;
		weightNodeDistSmall[index1] = distance[index1][0];
	}
	quicksortIncrDouble(1, numberNodes - 1, weightNodeRandom, copyRemovedNodeRandom);
	quicksortDecrInt(1, numberNodes - 1, weightNodeDemand, copyRemovedNodeDemand);
	quicksortDecrInt(1, numberNodes - 1, weightNodeDistLarge, copyRemovedNodeDistLarge);
	quicksortIncrInt(1, numberNodes - 1, weightNodeDistSmall, copyRemovedNodeDistSmall);
	//set probabilities
	totalSort = sortRandom + sortDemandLarge + sortDistDepotLarge + sortDistDepotSmall;
	probRandom = (double)sortRandom / (double)totalSort;
	probDemandLarge = (double)sortDemandLarge / (double)totalSort + probRandom;
	probDistLarge = (double)sortDistDepotLarge / (double)totalSort + probDemandLarge;
	return 0;
}

int ruinSplitString(int tourIndex, int lengthString, int startNodeIndex, bool nodeRemoved[])
{
	//step 0: find position of startNode in tour (startNode can be retained!!)
	int posStartNode = 0;
	int index10 = 0;
	bool found = false;
	while (!found && (index10 < SISRsSol.numberNodesInTour[tourIndex]))
	{
		if (SISRsSol.tours[tourIndex][index10] == startNodeIndex + 1)
		{
			posStartNode = index10;
			found = true;
		}
		index10++;
	}
	//step 0bis: determine number of preserved customers m
	int numberPreservedCust = 1;
	bool stopIncr = false;
	while (!stopIncr && (numberPreservedCust < SISRsSol.numberNodesInTour[tourIndex] - lengthString))
	{
		//update or not?
		double rand1 = xorshift128() / twoPow32;
		if (rand1 > alpha)
			numberPreservedCust++;
		else
			stopIncr = true;
	}
	//step 1: determine start of removal -> find substring with length lengthString+numberPreservedCust (l+m)
	int totalLength = lengthString + numberPreservedCust;
	int startRemoval = 0;
	if (totalLength > 1)
	{
		if (totalLength < SISRsSol.numberNodesInTour[tourIndex])
		{
			int options[maxNode];
			int countOptionsReal = 0;
			int countOptionsLoop = 0;
			int index10 = posStartNode;
			do
			{
				if ((index10 + totalLength - 1 < SISRsSol.numberNodesInTour[tourIndex]) && (index10 >= 0))
					options[countOptionsReal++] = index10;
				countOptionsLoop++;
				index10--;
			} while ((countOptionsLoop < totalLength) && (index10 >= 0));
			//options now contains possible start indices of current tour for substring removal
			int randomStart = (int)((xorshift128() / twoPow32)*countOptionsReal);
			startRemoval = options[randomStart];//index in current tour
		}
		else
			startRemoval = 0;//remove entire tour
	}
	else
		startRemoval = posStartNode;//1 option
	//step 1bis: determine start substring to retain
	int startRetain = startRemoval + 1;
	if (numberPreservedCust < totalLength - 2)
	{
		int options[maxNode];
		int countOptions = 0;
		int index10 = startRemoval + 1;
		do
		{
			options[countOptions++] = index10;
			index10++;
		} while ((index10 + numberPreservedCust - 1 < startRemoval + totalLength - 1) && (countOptions < totalLength - 2));
		int randomRetain = (int)((xorshift128() / twoPow32)*countOptions);
		startRetain = options[randomRetain];
	}
	//step 2: replace removed nodes with "-1" in tours, update absentNodes, numberAbsentNodes
	int copyNodes[maxNode];//holds copy of all nodes in current tour
	for (int index1 = 0; index1 < SISRsSol.numberNodesInTour[tourIndex]; index1++)
		copyNodes[index1] = SISRsSol.tours[tourIndex][index1];
	int countRemoved = 0;
	for (int index1 = startRemoval; index1 < startRetain; index1++)//part before retained substring
	{
		SISRsSol.absentNodes[SISRsSol.numberAbsentNodes++] = copyNodes[index1];
		SISRsSol.capacityUsageTour[tourIndex] -= nodeDemand[copyNodes[index1] - 1];
		SISRsSol.tourPerNode[copyNodes[index1] - 1] = -1;
		nodeRemoved[copyNodes[index1] - 1] = true;
		copyNodes[index1] = -1;
		countRemoved++;
	}
	for (int index1 = startRetain + numberPreservedCust; index1 < startRemoval + totalLength; index1++)//part after retained substring
	{
		SISRsSol.absentNodes[SISRsSol.numberAbsentNodes++] = copyNodes[index1];
		SISRsSol.capacityUsageTour[tourIndex] -= nodeDemand[copyNodes[index1] - 1];
		SISRsSol.tourPerNode[copyNodes[index1] - 1] = -1;
		nodeRemoved[copyNodes[index1] - 1] = true;
		copyNodes[index1] = -1;
		countRemoved++;
	}
	//step 3: reduce tours -> make tour only contain remaining nodes, if any
	int nodeIndex = 0;
	for (int index1 = 0; index1 < SISRsSol.numberNodesInTour[tourIndex]; index1++)
	{
		if (copyNodes[index1] != -1)
			SISRsSol.tours[tourIndex][nodeIndex++] = copyNodes[index1];
	}
	SISRsSol.numberNodesInTour[tourIndex] -= lengthString;
	return 0;
}

int ruinString(int tourIndex, int lengthString, int startNodeIndex, bool nodeRemoved[])
{
	//step 0: find position of startNode in tour
	int posStartNode = 0;
	int index10 = 0;
	bool found = false;
	while (!found && (index10 < SISRsSol.numberNodesInTour[tourIndex]))
	{
		if (SISRsSol.tours[tourIndex][index10] == startNodeIndex + 1)
		{
			posStartNode = index10;
			found = true;
		}
		index10++;
	}
	//step 1: determine start of removal
	int startRemoval = 0;
	if (lengthString > 1)
	{
		if (lengthString < SISRsSol.numberNodesInTour[tourIndex])
		{
			int options[maxNode];
			int countOptionsReal = 0;
			int countOptionsLoop = 0;
			int index10 = posStartNode;
			do
			{
				if ((index10 + lengthString - 1 < SISRsSol.numberNodesInTour[tourIndex]) && (index10 >= 0))
					options[countOptionsReal++] = index10;
				countOptionsLoop++;
				index10--;
			} while ((countOptionsLoop < lengthString) && (index10 >= 0));
			//options now contains possible start indices of current tour for substring removal
			int randomStart = (int)((xorshift128() / twoPow32)*countOptionsReal);
			startRemoval = options[randomStart];//index in current tour
		}
		else
			startRemoval = 0;//remove entire tour
	}
	else
		startRemoval = posStartNode;//1 option
	//step 2: replace removed nodes with "-1" in tours, update absentNodes, numberAbsentNodes
	int copyNodes[maxNode];//holds copy of all nodes in current tour
	for (int index1 = 0; index1 < SISRsSol.numberNodesInTour[tourIndex]; index1++)
		copyNodes[index1] = SISRsSol.tours[tourIndex][index1];
	for (int index1 = 0; index1 < lengthString; index1++)
	{
		SISRsSol.absentNodes[SISRsSol.numberAbsentNodes++] = copyNodes[startRemoval];
		SISRsSol.capacityUsageTour[tourIndex] -= nodeDemand[copyNodes[startRemoval] - 1];
		SISRsSol.tourPerNode[copyNodes[startRemoval] - 1] = -1;
		nodeRemoved[copyNodes[startRemoval] - 1] = true;
		copyNodes[startRemoval] = -1;
		startRemoval++;
	}
	//step 3: reduce tours -> make tour only contain remaining nodes, if any
	int nodeIndex = 0;
	SISRsSol.totalDist = 0;
	for (int index1 = 0; index1 < SISRsSol.numberNodesInTour[tourIndex]; index1++)
	{
		if (copyNodes[index1] != -1)
			SISRsSol.tours[tourIndex][nodeIndex++] = copyNodes[index1];
	}
	SISRsSol.numberNodesInTour[tourIndex] -= lengthString;
	return 0;
}

int ruin()//operates on SISRsSol
{
	//equations 5-7
	double tourCardinality = 0.0;//average tour cardinality
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
		tourCardinality += SISRsSol.numberNodesInTour[index1];
	tourCardinality = tourCardinality / (double)SISRsSol.numberTours;
	double maxStringCardinality = MIN(lengthRemovedStrings, tourCardinality);//l_s^max (eq5) -> how long is the removed string
	double maxStrings = ((double)numberOfStringsConstant*(double)avRemovedCust) / (1.0 + maxStringCardinality) - 1.0;//k_s^max (eq6) -> number of strings to remove
	int numberStringsToRemove = int(maxStrings* (xorshift128() / twoPow32) + 1.0);
	int randomSeedNodeIndex = (int)((numberNodes - 1)*(xorshift128() / twoPow32) + 1.0);
	int neighborIndex = 0;//refers to nodeIndexList
	int countRuinedTours = 0;
	bool ruinedTour[maxNode];//true if tour has been ruined, false otherwise
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
		ruinedTour[index1] = false;
	bool nodeRemoved[maxNode];//true if node has been removed, false otherwise
	for (int index1 = 0; index1 < numberNodes; index1++)
		nodeRemoved[index1] = false;
	double randProb = 0.0;
	SISRsSol.numberAbsentNodes = 0;
	while ((countRuinedTours < numberStringsToRemove) && (neighborIndex < numberNodes - 2))
	{
		int currentNodeIndex = nodeDistList[randomSeedNodeIndex][neighborIndex] - 1;//index of node to try to remove
		if ((!ruinedTour[SISRsSol.tourPerNode[currentNodeIndex] - 1]) && (!nodeRemoved[currentNodeIndex]))
		{
			ruinedTour[SISRsSol.tourPerNode[currentNodeIndex] - 1] = true;
			double localStringCardinality = MIN(SISRsSol.numberNodesInTour[SISRsSol.tourPerNode[currentNodeIndex] - 1], maxStringCardinality);
			int lengthStringToRemove = (int)(localStringCardinality*(xorshift128() / twoPow32) + 1.0);
			if ((SISRsSol.numberNodesInTour[SISRsSol.tourPerNode[currentNodeIndex] - 1] > 1)
				&& (SISRsSol.numberNodesInTour[SISRsSol.tourPerNode[currentNodeIndex] - 1] - lengthStringToRemove>0) && (lengthStringToRemove>1))
			{
				/*double*/ randProb = xorshift128() / twoPow32;
				if (randProb < probSplitString)
					ruinSplitString(SISRsSol.tourPerNode[currentNodeIndex] - 1, lengthStringToRemove, currentNodeIndex, nodeRemoved);
				else
					ruinString(SISRsSol.tourPerNode[currentNodeIndex] - 1, lengthStringToRemove, currentNodeIndex, nodeRemoved);
			}
			else
				ruinString(SISRsSol.tourPerNode[currentNodeIndex] - 1, lengthStringToRemove, currentNodeIndex, nodeRemoved);
			countRuinedTours++;
		}
		neighborIndex++;
	}
	//once all required nodes have been removed, check for empty tours
	int countEmptyTours = 0;
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
	{
		if (SISRsSol.numberNodesInTour[index1] == 0)
			countEmptyTours++;
	}
	int indexEmpty = countEmptyTours;
	int indexTours = SISRsSol.numberTours - 1;
	while ((indexEmpty >0) && (indexTours >= 0))
	{
		if (SISRsSol.numberNodesInTour[indexTours] == 0)
		{
			for (int index1 = indexTours; index1 < SISRsSol.numberTours - 1; index1++)
			{
				for (int index2 = 0; index2 < SISRsSol.numberNodesInTour[index1 + 1]; index2++)
					SISRsSol.tours[index1][index2] = SISRsSol.tours[index1 + 1][index2];
				SISRsSol.numberNodesInTour[index1] = SISRsSol.numberNodesInTour[index1 + 1];
			}
			SISRsSol.numberTours--;
			indexEmpty--;
		}
		indexTours--;
	}
	//calculate remaining used capacity per tour
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
	{
		SISRsSol.capacityUsageTour[index1] = 0;
		for (int index2 = 0; index2 < SISRsSol.numberNodesInTour[index1]; index2++)
			SISRsSol.capacityUsageTour[index1] += nodeDemand[SISRsSol.tours[index1][index2] - 1];
	}
	//set tourPerNode correctly
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
	{
		for (int index2 = 0; index2 < SISRsSol.numberNodesInTour[index1]; index2++)
		{
			SISRsSol.tourPerNode[SISRsSol.tours[index1][index2] - 1] = index1 + 1;
		}
	}
	return 0;
}

int recreate()//operates on SISRsSol
{
	//sort removed nodes according to 1 of 4 priorities (probabilities are parameters)
	double randProb = xorshift128() / twoPow32;
	int copyRemovedNode[maxNode];
	if (randProb < probRandom)
	{
		int count = 0;
		int index = 1;
		while ((count < SISRsSol.numberAbsentNodes) && (index < numberNodes))
		{
			if (SISRsSol.tourPerNode[copyRemovedNodeRandom[index] - 1] == -1)//node has been removed
				copyRemovedNode[count++] = copyRemovedNodeRandom[index];
			index++;
		}
	}
	else if (randProb < probDemandLarge)
	{
		int count = 0;
		int index = 1;
		while ((count < SISRsSol.numberAbsentNodes) && (index < numberNodes))
		{
			if (SISRsSol.tourPerNode[copyRemovedNodeDemand[index] - 1] == -1)//node has been removed
				copyRemovedNode[count++] = copyRemovedNodeDemand[index];
			index++;
		}
	}
	else if (randProb < probDistLarge)
	{
		int count = 0;
		int index = 1;
		while ((count < SISRsSol.numberAbsentNodes) && (index < numberNodes))
		{
			if (SISRsSol.tourPerNode[copyRemovedNodeDistLarge[index] - 1] == -1)//node has been removed
				copyRemovedNode[count++] = copyRemovedNodeDistLarge[index];
			index++;
		}
	}
	else
	{
		int count = 0;
		int index = 1;
		while ((count < SISRsSol.numberAbsentNodes) && (index < numberNodes))
		{
			if (SISRsSol.tourPerNode[copyRemovedNodeDistSmall[index] - 1] == -1)//node has been removed
				copyRemovedNode[count++] = copyRemovedNodeDistSmall[index];
			index++;
		}
	}
	int tourIndices[maxNode];
	double tourValues[maxNode];//for deciding order in which to go through existing tours
	for (int index2 = 0; index2 < SISRsSol.numberTours; index2++)
	{
		tourIndices[index2] = index2;
		tourValues[index2] = xorshift128() / twoPow32; 
	}
	quicksortDecrDouble(0, SISRsSol.numberTours - 1, tourValues, tourIndices);//in which order should tours be checked
	bool resort = false;
	for (int index1 = 0; index1 < SISRsSol.numberAbsentNodes; index1++)
	{
		int currentNodeIndex = copyRemovedNode[index1] - 1;//index of current node to reinsert
		int tempPos = -1;
		int tempTour = -1;
		int tempCost = VERYLARGE;
		for (int index2 = 0; index2 < SISRsSol.numberTours; index2++)
		{
			int currentTourIndex = tourIndices[index2];
			if (SISRsSol.capacityUsageTour[currentTourIndex] + nodeDemand[currentNodeIndex] <= vehicleCap)
			{
				//store current tour to avoid look-ups
				//evaluate position in tour for insertion
				for (int index3 = 0; index3 < SISRsSol.numberNodesInTour[currentTourIndex] + 1; index3++)
				{
					double randProb = xorshift128() / twoPow32;
					if (randProb < 1.0 - blinkRate)
					{//otherwise skip current position
						int currentCost = VERYLARGE;
						//option 1: index3=0 (start of tour)
						if (index3 == 0)
							currentCost = distance[0][currentNodeIndex] - distance[0][SISRsSol.tours[currentTourIndex][index3] - 1]
							+ distance[currentNodeIndex][SISRsSol.tours[currentTourIndex][index3] - 1];
						//option 2: index3=numberNodesInTour-1 (end position)
						else if (index3 == SISRsSol.numberNodesInTour[currentTourIndex])
							currentCost = distance[currentNodeIndex][0] - distance[SISRsSol.tours[currentTourIndex][index3 - 1] - 1][0]
							+ distance[SISRsSol.tours[currentTourIndex][index3 - 1] - 1][currentNodeIndex];
						//option 3: all others
						else
							currentCost = distance[SISRsSol.tours[currentTourIndex][index3 - 1] - 1][currentNodeIndex]
							- distance[SISRsSol.tours[currentTourIndex][index3 - 1] - 1][SISRsSol.tours[currentTourIndex][index3] - 1]
							+ distance[currentNodeIndex][SISRsSol.tours[currentTourIndex][index3] - 1];
						//has better position been found?
						if ((currentCost < tempCost) || (tempPos == -1))//second condition included to ensure that a first found position always gets accepted
						{
							tempTour = currentTourIndex;
							tempPos = index3;
							tempCost = currentCost;
						}
					}
				}
			}
		}
		if (tempPos == -1)
		{//no feasible position was found, add in new tour
			tourIndices[SISRsSol.numberTours] = SISRsSol.numberTours;//add new tour here as well
			tempTour = SISRsSol.numberTours++;
			SISRsSol.capacityUsageTour[tempTour] = 0;
			SISRsSol.numberNodesInTour[tempTour] = 0;
			tempPos = 0;
			tempCost = distance[0][currentNodeIndex] * 2;
		}
		//actually reinsert node
		SISRsSol.capacityUsageTour[tempTour] += nodeDemand[currentNodeIndex];
		SISRsSol.tourPerNode[currentNodeIndex] = tempTour + 1;
		//tours
		for (int index2 = SISRsSol.numberNodesInTour[tempTour]; index2 > tempPos; index2--)
			SISRsSol.tours[tempTour][index2] = SISRsSol.tours[tempTour][index2 - 1];
		SISRsSol.tours[tempTour][tempPos] = currentNodeIndex + 1;
		SISRsSol.numberNodesInTour[tempTour]++;
	}
	//all absentNodes should be included now, numberAbsentNodes=0
	SISRsSol.numberAbsentNodes = 0;
	return 0;
}

int SISRs()//operates on SISRsSol
{
	//copy currentCol to SISRsSol
	copyCurrentToSISRs();
	//call ruin
	ruin();
	recreate();
	//calculate totalDist
	SISRsSol.totalDist = 0;
	for (int index1 = 0; index1 < SISRsSol.numberTours; index1++)
	{
		if (SISRsSol.numberNodesInTour[index1] > 0)
		{
			for (int index2 = 0; index2 < SISRsSol.numberNodesInTour[index1] - 1; index2++)
				SISRsSol.totalDist += distance[SISRsSol.tours[index1][index2] - 1][SISRsSol.tours[index1][index2 + 1] - 1];
			//add distances from and to depot
			SISRsSol.totalDist += (distance[0][SISRsSol.tours[index1][0] - 1] + distance[SISRsSol.tours[index1][SISRsSol.numberNodesInTour[index1] - 1] - 1][0]);
		}
	}
	return 0;
}

int localSearchMH()
{
	//initial solution is currently stored in currentSol
	copyCurrentToBest();
	std::cout << bestSol.totalDist << std::endl;
	double currentTemp = startTemp;
	currentTemp = startTemp;
	for (int index1 = 0; index1 < numberItLSConstant*(numberNodes - 1); index1++)
	{
		SISRs();//starts from currentSol, result is stored in SISRsSol
		//acceptance criterion
		double randUniform = xorshift128() / twoPow32;
		if (SISRsSol.totalDist < currentSol.totalDist - currentTemp*log(randUniform))
			copySISRsToCurrent();
		if (SISRsSol.totalDist < bestSol.totalDist)
		{
			copySISRsToBest();
			std::cout << bestSol.totalDist << std::endl;
		}
		currentTemp *= tempConst;
	}
	return 0;
}

int main(int argc, char* argv[])
{
	uint32_t seed = 1000000000;
	std::string testInst;
	std::string instanceString = "-inst";
	std::string seedString = "-seed";

	for (int index1 = 1; index1 < argc; index1++)
	{
		if (std::strcmp(instanceString.c_str(), argv[index1]) == 0)
			testInst = argv[++index1];
		else if (std::strcmp(seedString.c_str(), argv[index1]) == 0)
			seed = strtoumax(argv[++index1], nullptr, 10);
		else if (std::strcmp(startTempString.c_str(), argv[index1]) == 0)
			startTemp = atof(argv[++index1]);
		else if (std::strcmp(endTempString.c_str(), argv[index1]) == 0)
			endTemp = atof(argv[++index1]);
		else if (std::strcmp(avRemovedCustString.c_str(), argv[index1]) == 0)
			avRemovedCust = atoi(argv[++index1]);
		else if (std::strcmp(lengthRemovedStringsString.c_str(), argv[index1]) == 0)
			lengthRemovedStrings = atoi(argv[++index1]);
		else if (std::strcmp(numberOfStringsConstantString.c_str(), argv[index1]) == 0)
			numberOfStringsConstant = atoi(argv[++index1]);
		else if (std::strcmp(alphaString.c_str(), argv[index1]) == 0)
			alpha = atof(argv[++index1]);
		else if (std::strcmp(probSplitStringString.c_str(), argv[index1]) == 0)
			probSplitString = atof(argv[++index1]);
		else if (std::strcmp(blinkRateString.c_str(), argv[index1]) == 0)
			blinkRate = atof(argv[++index1]);
		else if (std::strcmp(sortRandomString.c_str(), argv[index1]) == 0)
			sortRandom = atoi(argv[++index1]);
		else if (std::strcmp(sortDemandLargeString.c_str(), argv[index1]) == 0)
			sortDemandLarge = atoi(argv[++index1]);
		else if (std::strcmp(sortDistDepotLargeString.c_str(), argv[index1]) == 0)
			sortDistDepotLarge = atoi(argv[++index1]);
		else if (std::strcmp(sortDistDepotSmallString.c_str(), argv[index1]) == 0)
			sortDistDepotSmall = atoi(argv[++index1]);
	}
	w = unifRealDistr(generator) * seed;
	x = unifRealDistr(generator) * seed;
	y = unifRealDistr(generator) * seed;
	z = unifRealDistr(generator) * seed;
	readInput(testInst);
	tempConst = pow(endTemp / startTemp, 1.0 / (double)(numberItLSConstant*(numberNodes-1)));
	solutionsDistBest = VERYLARGE;
	startSol();
	localSearchMH();
	std::cout << bestSol.totalDist << std::endl;
	return 0;
}