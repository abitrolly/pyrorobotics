/* som_devrobs.h
 * -------------
 * june 14, 2002
 * Daniel Sproul, sproul@sccs.swarthmore.edu
 * header for som_devrobs.c
 * ----------------------------------
 */



#ifndef SOM_DEVROBS_H
#define SOM_DEVROBS_H

#include "lvq_pak.h"



#define CYCLIC    0   // for train_fromdataset()
#define RAND      1   // for train_fromdataset()
#define LINEAR    0   // for construct_teach_params()
#define INVERSE_T 1   // for construct_teach_params()
#define NO_TRAIN  0   // for input_one()
#define TRAIN     1   // for input_one()

/* other relevant definitions:
 * lvq_pak.h:
 *   #define TOPOL_HEXA
 *   #define TOPOL_RECT
 *   #define NEIGH_BUBBLE
 *   #define NEIGH_GAUSSIAN
 */

/* other relevant functions:
 * datafile.h:
 *   struct entries *open_entries(char *name);
 *   void close_entries(struct entries *entries);
 *   int save_entries(struct entries *codes, char *out_code_file);
 *   int save_entries_wcomments(struct entries *codes,
 *                              char *out_code_file, char *comments);
 * somrout.h:
 *   struct entries *lininit_codes(struct entries *data, int topol, 
 *                                 int neigh, int xdim, int ydim);
 *   struct entries *randinit_codes(struct entries *data, int topol, 
 *                                  int neigh, int xdim, int ydim);
 */



int write_entries(struct entries *codes, char *out_code_file);
void set_globals(void);
eptr *get_eptr(void);


/* --------------------- data set manipulation functions ----------------- */

struct entries *init_dataset(int dim);
int addto_dataset(struct entries *data, struct data_entry *entry);
struct data_entry *make_data_entry_weighted_masked(float *points, 
			short weight, short *mask, int dim);
struct data_entry *make_data_entry(float *points);




/* ------------------ training session initialization functions ---------- */

struct teach_params *construct_teach_params(struct entries *codes,
					    short alpha_mode, 
					    short radius_mode);
int init_training_session(struct teach_params *params,
			  float alpha_0, float radius_0, long length,
			  long qerror_window);
int setup_snapshot(struct teach_params *params,
		   char *snapfile_prefix, long interval);



/* ------------------ training/mapping functions ---------------------- */

int *input_one(struct teach_params *teach,
	       struct data_entry *sample, short mode);
int *map_one(struct teach_params *teach, struct data_entry *sample);
int *train_one(struct teach_params *teach, struct data_entry *sample);

struct data_entry *train_fromdataset(struct teach_params *teach, 
		struct entries *data, short mode);



/* ------------------- training timing functions ---------------------- */

void timing_start(struct teach_params *teach);
void timing_stop(struct teach_params *teach);
int get_training_time(struct teach_params *teach);



/* -------------- functions for getting info about SOM state ---------- */

float get_error(struct teach_params *teach);
float *get_activation_levels(struct teach_params *teach,
			     int *coords, float radius, short mode);
float *get_levels_by_error(struct teach_params *teach,
								struct data_entry *sample, float *erange);
struct data_entry *get_model_vector(struct entries *codes, int *coords);
void print_dataset(struct entries *data);






#endif /* SOM_DEVROBS_H */
