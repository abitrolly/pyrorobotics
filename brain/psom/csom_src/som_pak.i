/* som_devrobs.h
 * -------------
 * june 14, 2002
 * Daniel Sproul, sproul@sccs.swarthmore.edu
 * header for som_devrobs.c
 * ----------------------------------
 */

%module csom

%{
#include "som_devrobs.h"
#include "som_rout.h"
#include "datafile.h"
%}


%include pointer.i


#define CYCLIC    0   // for train_fromdataset()
#define RAND      1   // for train_fromdataset()
#define LINEAR    0   // for construct_teach_params()
#define INVERSE_T 1   // for construct_teach_params()
#define NO_TRAIN  0   // for input_one()
#define TRAIN     1   // for input_one()

#define TOPOL_HEXA 3
#define TOPOL_RECT 4
#define NEIGH_BUBBLE   1
#define NEIGH_GAUSSIAN 2




/* --------------- some data structures --------------------------- */

struct data_entry {
    float  *points;
    union {
      int  *label_array;
      int  label;
    } lab;
    short  num_labs;
    short  weight;
    struct data_entry *next;
    char   *mask;  
    struct fixpoint *fixed;
  };

struct entries {
  short dimension;      /* dimension of the entry */
  short topol;          /* topology type */
  short neigh;          /* neighbourhood */
  short xdim, ydim;     /* dimensions of the map */
  struct data_entry *current;  /* current entry */
  struct data_entry *entries;  /* pointer to entries */
  long num_loaded;      /* number of lines loaded in entries list */
  long num_entries;     /* number of entries in the data set if known */
  struct {
    unsigned int loadmode;
   	unsigned int totlen_known;
    unsigned int random_order; 
    unsigned int skip_empty; 
    unsigned int labels_needed; 
  } flags;
  int lap;               /* how many times have all samples been used */
  struct file_info *fi;  /* file info for file if needed */
  long buffer;           /* how many lines to read from file at one time */
};

struct teach_params {
  short topol;
  short neigh;
  short alpha_type;
  MAPDIST_FUNCTION *mapdist;  /* calculates distance between two units */
  DIST_FUNCTION *dist;        /* calculates distance between two vectors */
  NEIGH_ADAPT *neigh_adapt;   /* adapts weights */
  VECTOR_ADAPT *vector_adapt; /* adapt one vector */
  WINNER_FUNCTION *winner;    /* function to find winner */
  ALPHA_FUNC *alpha_func;
  ALPHA_FUNC *radius_func;  // used for devrobs hacks
  float radius;               /* initial radius (for SOM) */
  float alpha;                /* initial alpha value */
  long length;                /* length of training */
  long count;  // current training iteration, used by devrobs modifications
  double qerror;       // devrobs error tracking
  float error_factor;  // ditto
  int knn;                    /* nearest neighbours */
  struct entries *codes;
  struct entries *data;
  struct snapshot_info *snapshot;
  time_t start_time, end_time;
};







/* ------------------- from datafile.h: ------------------------------ */
/* ------------------------------------------------------------------- */

extern struct entries *open_entries(char *name);
extern void close_entries(struct entries *entries);
extern struct data_entry *rewind_entries(struct entries *entries, eptr *p);
extern struct data_entry *next_entry(eptr *p);

/* ------------------- from som_rout.h: ------------------------------ */
/* ------------------------------------------------------------------- */

extern struct entries *lininit_codes(struct entries *data, int topol,
                                  int neigh, int xdim, int ydim);
extern struct entries *randinit_codes(struct entries *data, int topol, 
                                   int neigh, int xdim, int ydim);




/* ------------------- from som_devrobs.h: --------------------------- */
/* ------------------------------------------------------------------- */

extern int write_entries(struct entries *codes, char *out_code_file);
extern void set_globals(void);
extern eptr *get_eptr(void);


/* --------------------- data set manipulation functions ----------------- */

extern struct entries *init_dataset(int dim);
extern int addto_dataset(struct entries *data, struct data_entry *entry);
extern struct data_entry *make_data_entry_weighted_masked(float *points, 
                                           short weight, short *mask, int dim);
extern struct data_entry *make_data_entry(float *points);




/* ------------------ training session initialization functions ---------- */

extern struct teach_params *construct_teach_params(struct entries *codes,
                                            short alpha_mode, 
                                            short radius_mode);
extern int init_training_session(struct teach_params *params,
                          float alpha_0, float radius_0, long length,
                          long qerror_window);
extern int setup_snapshot(struct teach_params *params,
                   char *snapfile_prefix, long interval);



/* ------------------ training/mapping functions ---------------------- */

extern int *input_one(struct teach_params *teach,
               struct data_entry *sample, short mode);

extern int *map_one(struct teach_params *teach, struct data_entry *sample);
extern int *train_one(struct teach_params *teach, struct data_entry *sample);

extern struct data_entry* train_fromdataset(struct teach_params *teach, 
							struct entries *data, short mode);



/* ------------------- training timing functions ---------------------- */

extern void timing_start(struct teach_params *teach);
extern void timing_stop(struct teach_params *teach);
extern int get_training_time(struct teach_params *teach);



/* -------------- functions for getting info about SOM state ---------- */

extern float get_error(struct teach_params *teach);
extern float *get_activation_levels(struct teach_params *teach,
                             int *coords, float radius, short mode);
extern float *get_levels_by_error(struct teach_params *teach,
                struct data_entry *sample, float tolerance);
extern struct data_entry *get_model_vector(struct entries *codes, int *coords);
extern void print_dataset(struct entries *data);


