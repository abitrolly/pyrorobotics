#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "../SRC/include.h"
#include "bp.h"
#include "ga.h"

/*
  Definition of new types (see the file ga.h):
    chromosome   an array of floats representing a neural network
    individual   a structure containing a chromsome and other information
    population   an array of individuals

  This Genetic Algorithm (GA) code is intended to evolve the weights and 
  biases of a fixed architecture neural network.  The chromosome is
  simply a one dimensional array of floats partitioned into blocks.  The
  first block contains all the weights from the input layer to the first
  hidden node plus the bias of that node.  The second block contains all 
  the weights from the input layer to the second hidden node plus the bias
  of that node.  And so on through the hidden layer and then the output 
  layer.

  In the tournament style, there is a single population where losing
  individuals are gradually replaced by mutations of winning
  individuals and a generation is considered to be complete when the
  number of tournaments equals the popsize.
*/

int popsize;                      /* size of the population */
int lchrom;                       /* length of the chromosome */
int gen;                          /* current generation */
int maxgen;                       /* maximum number of generations */
float pcross=0;                   /* probability of crossover */
float pmutation=0;                /* probability of mutation */
int ncross;                       /* number of crossovers done in generation */
int nmutation;                    /* number of mutations done in generation */
int mutations_per_genome=2;       /* used with tournament selection */
int fitness_steps;                /* max fitness_steps in fitness test */

/* The following varaiables are set by ga_statistics() */
Individual bestindiv;             /* current best individual overall */
float avg;                        /* average fitness of the population */
float max;                        /* maximum fitness of the population */
float min;                        /* minimum fitness of the population */
float sumfitness;                 /* total fitness of the population */
int   goodenough=FALSE;           /* flag to indicate criterion met */
int   bestchanged=FALSE;

FILE *GAmsg=NULL;                 /* file for general GA messages */
FILE *GAavg=NULL;                 /* file for average fitness by generation */
FILE *GAbest=NULL;                /* file for best fitness by generation */
char filename[30];                /* filename string without extension */
char termch;                      /* terminating char in scanfs */

population pop;

void ga_init()
{  
  gen=0;
  /* define the network's architecture */
  net_arch(); 
  init_ga_data();
  initpop();
  init_ga_report();
}

void ga_quit() {  
  reportbest();
  fclose(GAmsg);
  fclose(GAavg);
  fclose(GAbest);
}

void init_ga_data()
{
  printf("*** Initialization for the Genetic Algorithm ***\n");
  GAmsg = openfile("Enter filename (with no ext) for this run> ",
		   filename, "GAmsg", "w");
  GAavg = openfile(NULL, filename, "GAavg", "w");
  GAbest = openfile(NULL, filename, "GAbest", "w"); 
  printf("Tournament style generations\n");
  printf("Enter population size> ");
  scanf("%d%c",&popsize, &termch);
  printf("POPSIZE=%d\n", popsize);
  lchrom = chrom_length();
  printf("LCHROM=%d\n", lchrom);
  printf("Enter maximum number of generations> ");
  scanf("%d%c", &maxgen, &termch);
  printf("MAXGEN=%d\n", maxgen);

  /* tournament ga */
  mutations_per_genome = lchrom;
  printf("MUTATIONS_PER_GENOME=%d\n", mutations_per_genome);
  nmutation = 0;
  ncross = 0;
}

void initpop()
{
  int i, j;
  float weight, delta;
  int ans;
  
  printf("Seed initial population (1=yes/0=no)? ");
  scanf("%d%c", &ans, &termch);
  if (ans == 1) {
    fprintf(GAmsg, "Seeding initial population\n");
    printf("Seeding initial population\n");
    retrieve_weights(GAmsg);
    wts_to_chrom(pop[0].geno);
    for (i=1; i<popsize; i++) {
      for (j=0; j<lchrom; j++) {
	delta = real_rand(1.0);
	if (int_rand(2))
	  delta *= -1;
	pop[i].geno[j] = pop[0].geno[j] + delta;
      }
    }
  }
  else {
    fprintf(GAmsg, "Randomizing initial population\n");
    printf("Randomizing initial population\n");
    for (i=0; i<popsize; i++) {
      for (j=0; j<lchrom; j++) {
	weight = real_rand(1.0);
	if (int_rand(2))
	  weight *= -1;
	pop[i].geno[j] = weight;
      }
    }
  }
  pop[i].birthgen = 0;
  pop[i].fitness = 0;
  bestindiv = pop[0];
  printf("Initial population completed.\n");
}

void init_ga_report()
{
  extern int NUNITS;
  extern int NINPUT;
  extern int NHIDDEN;
  extern int NCONTEXT;
  extern int NOUTPUT;

  fprintf(GAmsg,
	  "-----------------------------------------------------------\n");
  fprintf(GAmsg,"Neural Network Parameters\n");
  fprintf(GAmsg,
	  "-----------------------------------------------------------\n");
  fprintf(GAmsg,"          input units %d\n", NINPUT);
  fprintf(GAmsg,"         hidden units %d\n", NHIDDEN);
  fprintf(GAmsg,"        context units %d\n", NCONTEXT);
  fprintf(GAmsg,"         output units %d\n", NOUTPUT);
  fprintf(GAmsg,"Total number of units %d\n", NUNITS);
  fprintf(GAmsg,
	  "-----------------------------------------------------------\n");
  fprintf(GAmsg,"Genentic Algorithm Parameters\n");
  fprintf(GAmsg,
	  "-----------------------------------------------------------\n");
  fprintf(GAmsg,"Using tournament selection with steady state\n");
  fprintf(GAmsg,"number of mutations per genome %d\n", mutations_per_genome);
  fprintf(GAmsg,"population size %d\n", popsize);
  fprintf(GAmsg,"chromosome length %d\n", lchrom);
  fprintf(GAmsg,"max number of generations %d\n", maxgen);
  fprintf(GAmsg,"number of fitness_steps per evaluation %d\n", 
	  fitness_steps);
  fprintf(GAmsg,
	  "-----------------------------------------------------------\n");
  fflush(GAmsg);
}

/* 
   Calculate statistics for the current population and update the bestidiv
   of the run.
*/
void ga_statistics()
{
  int i, maxloc=0;

  sumfitness = min = max = pop[0].fitness;
  for (i=1; i<popsize; i++) {
    sumfitness += pop[i].fitness;
    if (pop[i].fitness > max) {
      max = pop[i].fitness;
      maxloc = i;
    }
    if (pop[i].fitness < min)
      min = pop[i].fitness;
  }
  if (max > bestindiv.fitness) {
    bestindiv = pop[maxloc];
    bestchanged=TRUE;
  }
  else
    bestchanged=FALSE;
  avg = sumfitness/popsize;
  fprintf(GAavg,"%d %f\n", gen, avg);
  fprintf(GAbest,"%d %g\n", gen, bestindiv.fitness);
  fflush(GAavg);
  fflush(GAbest);
}

void reportbest()
{
  fprintf(GAmsg,"---------------------------\n");
  fprintf(GAmsg,"Best individual of run\n");
  fprintf(GAmsg,"---------------------------\n");
  fprintf(GAmsg,"%d %g\n", 
	  bestindiv.birthgen, bestindiv.fitness);
  /* save weights of best individual */
  chrom_to_wts(bestindiv.geno);
  strcat(filename,"best");
  save_weights(filename);
}

void ga_report()
{
  int i;
  char weightsfile[50];
  char genstr[15];

  fprintf(GAmsg,"---------------------------\n");
  fprintf(GAmsg,"Generation %d\n", gen);
  fprintf(GAmsg,"---------------------------\n");
  for (i=0; i<popsize; i++) {
    fprintf(GAmsg,"%3d ", i);
    fprintf(GAmsg,"%d %d %d %d %f\n", 
	    pop[i].birthgen, pop[i].xpoint, pop[i].parent1, 
	    pop[i].parent2, pop[i].fitness);
  }
  fprintf(GAmsg,"\nmax=%f min=%f avg=%f sum=%f\n",
	  max, min, avg, sumfitness);
  /* in case system goes down, save best weights each generation */
  if (bestchanged) {
    chrom_to_wts(bestindiv.geno);
    strcpy(weightsfile, filename);
    if (gen < 10)
      sprintf(genstr, "-gen00%d", gen);
    else if (gen < 100)
      sprintf(genstr, "-gen0%d", gen);
    else
      sprintf(genstr, "-gen%d", gen);
    strcat(weightsfile,genstr);
    save_weights(weightsfile);
  }

  fflush(GAmsg);
}

/* Mutate just a few genes in every genome */
void tournament_mutation(chromosome old, chromosome new)
{
  int i;
  float delta;

  for (i=0; i<lchrom; i++) 
    new[i] = old[i];
  if (mutations_per_genome == lchrom)
    for (i=0; i<lchrom; i++) {
      delta = real_rand(1.0);
      if (int_rand(2)) 
	delta = -1 * delta;
      new[i] += delta;
    }
  else
    for (i=0; i<mutations_per_genome; i++) {
      delta = real_rand(1.0);
      if (int_rand(2)) 
	delta = -1 * delta;
      new[int_rand(lchrom)] += delta;
    }
}

