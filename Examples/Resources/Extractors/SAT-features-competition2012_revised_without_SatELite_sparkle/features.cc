#include "SATinstance.h"
#include <cstdlib>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <string.h>
#include "global.h"
using namespace std;


Stopwatch gSW;
int gTimeOut;
double preTime;
int  OrigNumVars, OrigNumClauses;
double myTime=0.0;
const char* mypath;

// int numFeats=64;
int getTimeOut(void)
{
  char * value = getenv("SATTIMEOUT");
  if (value == NULL)
    return(2419200); // -- 4 weeks

  return atoi(value);
}

int main(int argc, char** argv)
{
  if(argc < 2)
    {
      cerr << "Usage: features {  [-all] | [-base] |[-sp] [-Dia] [-Cl] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
      return 1;
    }

  bool doBase=false;
  bool doUnitProbe=false;
  bool doLSProbe=false;
  bool doCl=false;
  bool doDia=false;
  bool doSp=false;
  bool doLobjois = false;
  bool doLP = false;
  bool doComp=true;
  int nextParam=1;
 string fullPath(argv[0]);
    size_t lastSlashPos=fullPath.find_last_of('/');
    string myownpath=fullPath.substr(0,lastSlashPos);

    if (lastSlashPos==-1){
		myownpath=".";
      }
    mypath=myownpath.c_str();
  

  if(strcmp(argv[nextParam],"-all")==0)
    {
      doBase=true;
      doUnitProbe=true;
      doLSProbe=true;
      doLobjois=true;
      doCl=true;
      doDia=true;
      doSp=true;
      doLP=true;
      nextParam++;
      if(nextParam==argc)
	{
	  cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	  return 1;
	}
    }
  else {
    if(strcmp(argv[nextParam],"-base")==0)
      {
	doBase=true;
	nextParam++;
	if(nextParam==argc)
	  {
	    cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }


    if(strcmp(argv[nextParam],"-unit")==0)
      {
	doUnitProbe=true;
	nextParam++;
	if(nextParam==argc)
	  {
	   cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }
 if(strcmp(argv[nextParam],"-lp")==0)
      {
	doLP=true;
	nextParam++;
	if(nextParam==argc)
	  {
	   cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }

     if(strcmp(argv[nextParam],"-sp")==0)
      {
	doSp=true;
	nextParam++;
	if(nextParam==argc)
	  {
	   cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }


   if(strcmp(argv[nextParam],"-dia")==0)
      {
	doDia=true;
	nextParam++;
	if(nextParam==argc)
	  {
	    cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }


    if(strcmp(argv[nextParam],"-cl")==0)
      {
	doCl=true;
	nextParam++;
	if(nextParam==argc)
	  {
	    cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-LP] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }

    if(strcmp(argv[nextParam],"-ls")==0)
      {
	doLSProbe=true;
	nextParam++;
	if(nextParam==argc)
	  {
	   cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }

    if(strcmp(argv[nextParam],"-lobjois")==0)
      {
	doLobjois=true;
	nextParam++;
	if(nextParam==argc)
	  {
	  cerr << "Usage: features { [-all] | [-base] [-sp] [-dia] [-cl] [-lp] [-unit] [-ls] [-lobjois] } infile [outfile]" << endl;
	    return 1;
	  }
      }
  }
  bool letsgo=true;
  
  if( !( doBase || doSp || doCl || doDia || doLobjois ||doLP || doLSProbe || doUnitProbe) )
    doBase=true;


  char *filename;
  //char outfile[512];      
  char *outfile;
  filename=argv[nextParam++];
  
  outfile = argv[nextParam++];
  
  /* 
  //sprintf(outfile, "%s", "/tmp"); //ori
  sprintf(outfile, "%s", "TMP/tmp"); //luoc
  strcat(outfile, "/outputXXXXXX");
  mkstemp(outfile);
  */
  
  gTimeOut = getTimeOut();
  BuildSolvers("123456", filename);
  gSW.Start();

  // before doing anything, count number of variables and clauses
  ifstream infile(filename);
  if (!infile) {
    fprintf(stderr, "c Error: Could not read from input file %s.\n", filename);
    exit(1);
  }
  char chbuf;
  char strbuf[1024];
  infile.get(chbuf);
  while (chbuf != 'p') {
    infile.ignore(1000, '\n');
    infile.get(chbuf);
    if(!infile)
      {
    	fprintf(stderr, "c ERROR: Premature EOF reached in %s\n", filename);
	    exit(1);
      }
  }
  infile >> strbuf; // "cnf"
  infile >> OrigNumVars >> OrigNumClauses;
if (DEB)
  printf("c Orignal number of varibales is %d, number of clauses is %d \n", OrigNumVars, OrigNumClauses);
/*
if (DEB)
  printf("c run SatELite as pre-processor ... \n");
  int returnVal;
if (DEB)
  printf("c Input file is: %s. Output file is %s\n", filename, outfile);
  returnVal = SolverSatelite -> execute(filename, 1200);
  if (returnVal==10 || returnVal==20) {
if (DEB)
      printf("c This instance is solved by pre-processor with %d!\n", returnVal);
      doComp=false;
      }
*/ //Commented out by luo

  /*
  string filename_str = filename;
  string outfile_str = outfile;
  string command = "cp " + filename_str + " " + outfile_str;
  system(command.c_str());
  */

  SolverSatelite->cleanup();
 // SATinstance* sat = new SATinstance(outfile); 
  SATinstance* sat = new SATinstance(filename, doComp); 
  preTime=gSW.TotalLap()-myTime;
  myTime=gSW.TotalLap();
  if (DEB)
     printf("c Pre-process time is %f second\n", preTime);

  if(doBase && letsgo)
  { 
    sat->computeFeatures(doComp);
 //   cout <<sat->getNumVals()<<"  "<< sat->getNumClaus()<<endl;
    if (sat->getNumVals()==0 ||sat->getNumClaus()==0)
    {
        doComp=false;
if (DEB)
        cout <<"c Instance can be solved by unit propodation alone!!!\n";
        } 
}

  
 if (doDia && letsgo)
     sat->init_diameter(doComp);
    
 if (doCl && letsgo)
    sat->cl_prob(filename, doComp);
    
 if (doSp && letsgo)
    sat->sp(doComp);

 if (doUnitProbe && letsgo)
    sat->unitPropProbe(false, doComp);

 if(doLP && letsgo)
    sat->compute_lp(doComp);
  

  if (doLSProbe && letsgo){
    sat->localSearchProbeSaps(filename, doComp);
    sat->localSearchProbeGsat(filename, doComp);
    
}

  if (doLobjois && letsgo)
    sat->lobjoisProbe(false, doComp);

  if (letsgo)
  if(argc > nextParam )
    {
      sat->writeFeatNamesToFile(argv[nextParam]);
      sat->writeFeaturesToFile(argv[nextParam]);
    }
  else
    {
      sat->writeFeatNamesToFile(stdout);
      sat->writeFeaturesToFile(stdout);
    }
  
  delete sat;
  remove(outfile);
  
  return 0;
}
