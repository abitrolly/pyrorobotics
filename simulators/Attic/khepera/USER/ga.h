#ifndef GA_H
#define GA_H

/* constants for GA */
#define MAXPOP 1000
#define MAXSTRING 200

/* new types for GA */
typedef float chromosome[MAXSTRING];

struct individual {
  chromosome geno;
  int birthgen;
  int parent1, parent2; 
  int xpoint;
  float fitness;
};

typedef struct individual Individual;
typedef Individual population[MAXPOP];

/* GA functions */
void ga_init();
void ga_quit();
void init_ga_data();
void initpop();
void ga_statistics();
void init_ga_report();
void ga_report();
void tournament_mutation(chromosome, chromosome);
void reportbest();

#endif
