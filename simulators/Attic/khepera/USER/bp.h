#ifndef BP_H
#define BP_H

#define MAX_SIZE 100
#define MAX_WEIGHT 0.4
#define NUMSENSORS 8

/* bp functions */
void compute_output();
void save_weights(char filename[20]);
void retrieve_weights(FILE *msg);
void init_hidden();
void copy_hidden();
void save_hidden(FILE *, int);
void assign_weights(float [], int, int);
void zero_weights_biases();
void net_arch();
int is_elman();

/* ga functions */
void chrom_to_wts(float []);
void wts_to_chrom(float []);
int chrom_length();
int cross_point();

/* array help functions */
void print_activation();
void print_output();
int first_unit_in(char);
int last_unit_in(char);
int first_weight_to(int);
int last_weight_to(int);
void show(FILE *);
void show_round(FILE *, float [], int, int);

/* numeric help functions */
float real_rand(float);
int int_rand(int);
float rand_weight();
float logistic(float);

/* input functions */
void get_input(float sensor[]);
FILE *openfile(char *prompt, char *filename, char *ext, char *mode);

#endif
