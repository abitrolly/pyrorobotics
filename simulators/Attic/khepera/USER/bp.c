#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "bp.h"

int NUNITS, NINPUT, NHIDDEN, NCONTEXT, NOUTPUT;
float *netinput, *activation, *bias, *output;
float *weight[MAX_SIZE];

char termch;
int answer;

void compute_output()
{
   int i,j;

   for (i=first_unit_in('h'); i<NUNITS; i++) {
      netinput[i] = bias[i];
      for (j=first_weight_to(i); j<=last_weight_to(i); j++)
	 netinput[i] += activation[j] * weight[i][j];
      activation[i] = logistic(netinput[i]);
      }
   for (i=first_unit_in('o'), j=0; i<NUNITS; i++, j++) {
     output[j] = activation[i];
   }
}

void assign_weights(float vals[], int start, int stop)
{
   int i;

   for (i=start; i<=stop; i++)
      vals[i] = rand_weight();
}

void net_arch() {
  int i;

  printf("*** Initialize the network architecture ***\n");
  printf("Enter number of input, hidden, and output units> ");
  scanf("%d%d%d%c", &NINPUT, &NHIDDEN, &NOUTPUT, &termch);
  printf("Create an Elman network (1=yes,0=no)? ");
  scanf("%d%c", &answer, &termch);
  if (answer) {
    NCONTEXT = NHIDDEN;
    printf("ARCHITECTURE IS AN ELMAN NETWORK\n");
  }
  else {
    NCONTEXT = 0;
    printf("ARCHITECTURE IS A FEED-FORWARD NETWORK\n");
  }
  NUNITS = NINPUT + NHIDDEN + NOUTPUT + NCONTEXT;
  printf("NINPUT=%d NHIDDEN=%d NCONTEXT=%d NOUTPUT=%d\n",
	 NINPUT, NHIDDEN, NCONTEXT, NOUTPUT);
  printf("TOTAL NUMBER OF UNITS: %d\n", NUNITS);
  if (NUNITS > MAX_SIZE) {
    printf("Requested size exceeds limit of %d\n", MAX_SIZE);
    exit(1);
  }

  for (i=0; i<NUNITS; i++) {
    weight[i] = (float *)malloc(NUNITS*sizeof(float));
  }
  
  netinput = (float *)malloc(NUNITS*sizeof(float));
  activation = (float *)malloc(NUNITS*sizeof(float));
  bias = (float *)malloc(NUNITS*sizeof(float));
  output = (float *)malloc(NOUTPUT*sizeof(float));

  if (is_elman())
    init_hidden();
}

int is_elman() 
{
  if (NCONTEXT > 0)
    return 1;
  else
    return 0;
}

void init_hidden()
{
   int i;

   for (i=first_unit_in('h'); i<=last_unit_in('h'); i++)
      activation[i] = 0.5;
}

void copy_hidden()
{
   int i, j;

   for (i=first_unit_in('c'), j=first_unit_in('h'); i<=last_unit_in('c');
	i++, j++)
      activation[i] = activation[j];
}

void save_hidden(FILE *hid, int step)
{
  int i, start, end;

  start = first_unit_in('h');
  end = last_unit_in('h');
  for (i=start; i<=end; i++)
    fprintf(hid,"%f ",activation[i]);
  fprintf(hid,"\n");
}

void save_weights(char name[])
{
  int i,j;
  FILE *weight_out;
  
  weight_out = openfile(NULL,name,"wts","w");
  
  for (i=0; i<NUNITS; i++)
    for (j=0; j<NUNITS; j++)
      fprintf(weight_out, "%f ", weight[i][j]);
  
  fprintf(weight_out, "\n\n");
  for (i=0; i<NUNITS; i++)
    fprintf(weight_out, "%f ", bias[i]);

  fclose(weight_out);
}

void retrieve_weights(FILE *msg)
{
  int i,j;
  FILE *weight_in;
  char wtsfile[30];

  zero_weights_biases();
  weight_in = openfile("Enter filename (with no ext) of stored weights> ",
		       wtsfile,"wts","r");
  if (msg)
    fprintf(msg, "Retrieving weights from file %s.wts\n", wtsfile);
  printf("FILE NAME IS %s\n", wtsfile);
  for (i=0; i<NUNITS; i++)
    for (j=0; j<NUNITS; j++)
      fscanf(weight_in, "%f ", &weight[i][j]);
  for (i=0; i<NUNITS; i++)
    fscanf(weight_in, "%f ", &bias[i]);

  fclose(weight_in);
}

void print_activation() {
  int i;

  printf("ACTIVA ");
  for (i=0; i<NUNITS; i++) {
    printf("%d:%.3f ", i, activation[i]);
  }
  printf("\n");
}

void print_output() {
  int i;

  printf("OUTPUT ");
  for (i=0; i<NOUTPUT; i++) {
    printf("%d:%f ", i, output[i]);
  }
  printf("\n");
}

FILE *openfile(char *prompt, char *basename, char *ext, char *mode)
{
  FILE *result;
  char fullname[50];

  while(1) {
    if (prompt != NULL) {
      printf(prompt);
      scanf("%s%c", basename, &termch);
    }
    strcpy(fullname, basename);
    if (ext != NULL) {
      strcat(fullname, ".");
      strcat(fullname, ext);
    }
    result = fopen(fullname, mode);
    if (result != NULL)
      return result;
    else
      printf("Cannot open the file \"%s\". Please try again.\n", fullname);
  }
}

int first_unit_in(char layer)
{
  switch(layer) {
     case 'i': return(0);
     case 'c': return(NINPUT);
     case 'h': return(NINPUT+NCONTEXT);
     case 'o': return(NINPUT+NCONTEXT+NHIDDEN);
     default:  return(-1);
     }
}

int last_unit_in(char layer)
{
   switch(layer) {
      case 'i': return(NINPUT-1);
      case 'c': return(NINPUT+NCONTEXT-1);
      case 'h': return(NINPUT+NCONTEXT+NHIDDEN-1);
      case 'o': return(NUNITS-1);
      default:  return(-1);
      }
}

int first_weight_to(int node)
{
   if (node >= NINPUT+NCONTEXT && node < NINPUT+NCONTEXT+NHIDDEN)
      return(0);
   else if (node >= NUNITS-NOUTPUT && node < NUNITS)
      return(NINPUT+NCONTEXT);
   else {
     printf("Error in first_weight_to: invalid node %d\n", node);
     exit(1);
     }
}

int last_weight_to(int node)
{
   if (node >= NINPUT+NCONTEXT && node < NINPUT+NCONTEXT+NHIDDEN)
      return(NINPUT+NCONTEXT-1);
   else if (node >= NUNITS-NOUTPUT && node < NUNITS)
      return(NINPUT+NCONTEXT+NHIDDEN-1);
   else {
     printf("Error in last_weight_to: invalid node %d\n", node);
     exit(1);
     }
}

/**********************************************************************
Numeric help functions
***********************************************************************/
/* Return a real number between 0 and high. */
float real_rand(float high)
{
  float f;

  f = (float) rand() / ((float) RAND_MAX + 1);
  return(f * high);
}

int int_rand(int high) {
  return (int)real_rand(high);
}

float rand_weight()
{
  float val;

  val = real_rand(MAX_WEIGHT);
  if (int_rand(2) == 0)
     return(-val);
  else
     return(val);
}

float logistic(float net)
{
   return(1/(1+exp(-net)));
}

void get_input(float sensor[])
{
  int i;
  
  for (i=0; i<NUMSENSORS; i++) {
    activation[i] = sensor[i];
  }
}

void zero_weights_biases()
{
  int i,j;

  for (i=0; i<NUNITS; i++) {
    bias[i] = 0.0;
    for (j=0; j<NUNITS; j++)
      weight[i][j] = 0.0;
  }
}

void show_round(FILE *msg, float v[], int start, int stop)
{
   int i;

   for (i=start; i<=stop; i++) {
      if (v[i] == 1)
	 fprintf(msg, "X");
      else if (v[i] > 0.9)
	 fprintf(msg, "9");
      else if (v[i] > 0.8)
	 fprintf(msg, "8");
      else if (v[i] > 0.7)
	 fprintf(msg, "7");
      else if (v[i] > 0.6)
	 fprintf(msg, "6");
      else if (v[i] > 0.5)
	 fprintf(msg, "5");
      else if (v[i] > 0.4)
	 fprintf(msg, "4");
      else if (v[i] > 0.3)
	 fprintf(msg, "3");
      else if (v[i] > 0.2)
	 fprintf(msg, "2");
      else if (v[i] > 0.1)
	 fprintf(msg, "1");
      else if (v[i] > 0)
	 fprintf(msg, "+");
      else if (v[i] == 0)
	 fprintf(msg, "0");
      else fprintf(msg, "-");
      fprintf(msg," ");
      }
   fprintf(msg,"\n");
}

void show(FILE *msg)
{
   fprintf(msg, "input:\n");
   show_round(msg, activation, first_unit_in('i'), last_unit_in('i'));
   if (NCONTEXT > 0) {
     fprintf(msg, "context:\n");
     show_round(msg, activation, first_unit_in('c'), last_unit_in('c'));
   }
   fprintf(msg, "hidden:\n");
   show_round(msg, activation, first_unit_in('h'), last_unit_in('h'));
   fprintf(msg, "output:\n");
   show_round(msg, activation, first_unit_in('o'), last_unit_in('o'));
}

void wts_to_chrom(float c[])
{
  int i,j,k=0;

  /* transfer input to hidden wts and hidden biases */
  for (i=first_unit_in('h'); i<=last_unit_in('h'); i++, k++) {
    for (j=first_unit_in('i'); j<=last_unit_in('c'); j++, k++)
      c[k] = weight[i][j];
    c[k] = bias[i];
  }

  /* transfer hidden to output wts and output biases */
  for (i=first_unit_in('o'); i<=last_unit_in('o'); i++, k++) {
    for (j=first_unit_in('h'); j<=last_unit_in('h'); j++, k++)
      c[k] = weight[i][j];
    c[k] = bias[i];
  }
}

void chrom_to_wts(float c[])
{
  int i,j,k=0;

  /* NOTE: weight[i][j] is the weight FROM j TO i */
  zero_weights_biases();

  /* init weights from input layer to hidden layer and biases */
  for (i=first_unit_in('h'); i<=last_unit_in('h'); i++) {
    for (j=first_unit_in('i'); j<=last_unit_in('c'); j++, k++)
      weight[i][j] = c[k];
    bias[i] = c[k];
    k++;
  }

  /* init weights from hidden layer to output layer and biases */
  for (i=first_unit_in('o'); i<=last_unit_in('o'); i++) {
    for (j=first_unit_in('h'); j<=last_unit_in('h'); j++, k++)
      weight[i][j] = c[k];
    bias[i] = c[k];
    k++;
  }
}

/* 
   Determine how long the GA chromosome should be.
*/
int chrom_length()
{
  return(((NINPUT+NCONTEXT)*NHIDDEN)+ /*input to hidden weights */
	 (NHIDDEN*NOUTPUT)+           /*hidden to output weights */
	 NHIDDEN+NOUTPUT);            /*hidden and output biases */
}

/* 
  Consider each unit's incoming weights and bias as a building block. 
  So there are NHIDDEN+NOUPUT building blocks in a GA chromosome.  Do
  crossover so that each block is treated as a indivisable unit.  This
  function randomly picks a cross point from 1 to #BB.  Then it 
  converts this into the appropriate genome location.
*/
int cross_point()
{
  int block;

  block = int_rand((NHIDDEN+NOUTPUT-1)) + 1;
  if (block <= NHIDDEN)
    return(block*(NINPUT+NCONTEXT+1));
  else
    return((NHIDDEN*(NINPUT+NCONTEXT+1)) + 
	   ((block-NHIDDEN)*(NHIDDEN+1)));
}




