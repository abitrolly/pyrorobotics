/*****************************************************************************/
/* File:        sim.c (Khepera Simulator)                                    */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Thu Sep 21 14:39:05 1995                                     */
/* Description: main program                                                 */
/*                                                                           */
/* Copyright (c) 1995                                                        */
/* Olivier MICHEL                                                            */
/* MAGE team, i3S laboratory,                                                */
/* CNRS, University of Nice - Sophia Antipolis, FRANCE                       */
/*                                                                           */
/* Permission is hereby granted to copy this package for free distribution.  */
/* The author's name and this copyright notice must be included in any copy. */
/* Commercial use is forbidden.                                              */
/*****************************************************************************/

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ipc.h>
#include <sys/shm.h>

#include "header.h"
#include "sim.h"
#include "world.h"
#include "graphics.h"
#include "robot.h"

struct Context *context;

/* this function returns a random value between 0 and x-1 */
long int Rnd(int x)
{
  return(((long)(rand() & 0x7fff)*(long)(x))/(long)(0x8000));
}

void OpenProgram()
{
  struct Button  *but;
  FILE           *file;

  file = fopen("WORLD/avoid.world","r");
  if (file)
  {
    context->World = (struct World *)malloc(sizeof(struct World));
    context->World->Objects = NULL;
    CreateEmptyWorld(context);
    ReadWorldFromFile(context->World,file);
    strcpy(context->World->Name,"avoid");
    fclose(file);
  }
  else
  {
    perror("unable to find avoid.world in WORLD directory");
    exit(0);
  }

  CreateDefaultRobot(context);

  strcpy(context->TextInput,"");
  context->Info           = INFO_ABOUT;

  but= context->Buttons = CreateButton(NEW_WORLD,"new",WINDOW_W/4,4);
  but= but->Next=CreateButton(REDRAW_WORLD,"redraw",WINDOW_W/4+30,4);
  but= but->Next=CreateButton(LOAD_WORLD,"load",WINDOW_W/4,23);
  but= but->Next=CreateButton(SAVE_WORLD,"save",WINDOW_W/4+37,23);
	
  but= but->Next=CreateButton(SET_ROBOT,"set robot",WINDOW_W/2,4);
  but= but->Next=CreateButton(SET_ANGLE,"set angle",WINDOW_W/2,23);

  but= but->Next=CreateButton(ADD_OBJECT,"add",WINDOW_W*3/4,4);
  but= but->Next=CreateButton(TURN_OBJECT,"turn",WINDOW_W*3/4+30,4);
  but= but->Next=CreateButton(REMOVE_OBJECT,"remove",WINDOW_W*3/4,23);
  but= but->Next=CreateButton(OBJECT_PLUS,"+",WINDOW_W*3/4+70,5);
  but= but->Next=CreateButton(OBJECT_MINUS,"-",WINDOW_W*3/4+70,22);

  but= but->Next=CreateButton(SENSORS_BUTTON,">",280,PLATE1_H+52);
  but= but->Next=CreateButton(MOTORS_BUTTON,">",280,PLATE1_H+72);
	
  but= but->Next=CreateButton(RUN_ROBOT,"run",5,PLATE1_H+168);
	but= but->Next=CreateButton(STEP_ROBOT,"step",35,PLATE1_H+168);

  but= but->Next=CreateButton(TEST,"test",WINDOW_W/2-38,PLATE1_H+168);
  but= but->Next=CreateButton(RESET_ROBOT,"reset",WINDOW_W/2,PLATE1_H+168);
  but= but->Next=CreateButton(QUIT,"quit",WINDOW_W-40,PLATE1_H+168);

	//but= but->Next=CreateButton(COMMAND,"command",73,PLATE1_H+168);
  //but= but->Next=CreateButton(KHEPERA_BUTTON,">",WINDOW_W/2+220,40);
  //but= but->Next=CreateButton(NEW_ROBOT,"new",WINDOW_W/2+48,WINDOW_W/2-34);
  //but= but->Next=CreateButton(LOAD_ROBOT,"load",WINDOW_W/2+92,WINDOW_W/2-34);
  //but= but->Next=CreateButton(SAVE_ROBOT,"save",WINDOW_W/2+140,WINDOW_W/2-34);
  //context->UserInfo = SetUserInfo();
  OpenGraphics(context);
  InitSensors(context);
}

void CloseProgram()
{
  UserClose(context->Robot);
  FreeRobot(context);
  FreeWorld(context);
  FreeButtons(context);
  free(context);
  CloseGraphics();
}

boolean ExistOption(char *opt,int argc,char *argv[])
{
  int     i;
  boolean ans = FALSE;

  for(i=1;i<argc;i++) if (argv[i][0]=='-')
   if (strcmp(&(argv[i][1]),opt)==0) ans = TRUE;
  return(ans);
}

void ReadConfigFile()
{
  char    text[TEXT_BUF_SIZE];
  boolean ok;
  FILE    *file;

  file = fopen(".simrc","r");

  if (file)
  {
    while(fscanf(file,"%s\n",text)!=EOF)
    {
      if (strcmp(text,"MONODISPLAY:")==0)
      {
        fscanf(file,"%s\n",text);
        if (strcmp(text,"TRUE")==0) context->MonoDisplay = TRUE;
        else context->MonoDisplay = FALSE;  
      }
      if (strcmp(text,"KHEPERA_AVAILABLE:")==0)
      {
        fscanf(file,"%s\n",text);
        if (strcmp(text,"TRUE")==0) context->KheperaAvailable = TRUE;
        else context->KheperaAvailable = FALSE;
      }
      if (strcmp(text,"SERIAL_PORT:")==0)
      {
        fscanf(file,"%s\n",text);
        InitKheperaSerial(text);
      }
    }
    fclose(file);
  }
  else
  {
    perror("unable to find .simrc in current directory");
    exit(0);
  }
}

int main(int argc,char *argv[]) {
  char              text[TEXT_BUF_SIZE],name[TEXT_BUF_SIZE],
                    file_name[TEXT_BUF_SIZE];
	char *rmsg;
  boolean           quit=FALSE,ok,queryflag=FALSE;
  struct World      *world;
  struct Robot      *robot,saved_robot;
  XPoint            *point;
  struct Button     *button;
  struct Object     *object,*obj;
  double            val0;
  long int          i,j;
  int               angle;
  FILE              *ffile;
  int               sim_serial_in,sim_serial_out,f;
	char *shm_in, *shm_out;
	int shmid_in, shmid_out;

	if((shmid_in = shmget(SHM_KEY_IN, SHM_BUF_SIZE, IPC_CREAT | SHM_PERM)) < 0) {
		perror("shmget");
		exit(1);
	}
	if((shmid_out = shmget(SHM_KEY_OUT, SHM_BUF_SIZE, IPC_CREAT | SHM_PERM)) < 0){
		perror("shmget");
		exit(1);
	}
	if((shm_in = shmat(shmid_in, NULL, 0)) == (char *) -1) {
		perror("shmat");
		exit(1);
	}
	if((shm_out = shmat(shmid_out, NULL, 0)) == (char *) -1) {
		perror("shmat");
		exit(1);
	}

	shm_in[0] = '\0';
	shm_out[0] = '\0';


  context = (struct Context *)malloc(sizeof(struct Context));
	
	context->KheperaAvailable = FALSE;
	context->Pipe = FALSE;
	context->MonoDisplay = FALSE;
	
  OpenProgram();
  world = context->World;
  robot = context->Robot;
  UserInit(robot);

  while(quit == FALSE)
  {
    button=PressButton(context);
    switch(button->Value)
    {
      case QUIT:
       DisplayComment(context,"bye !");
       quit = TRUE;
       break;

      case NEW_WORLD:
       DisplayComment(context,"creating new world");
       CreateDefaultWorld(context);
       strcpy(world->Name,"new");
       DrawWorld(context);
       DisplayComment(context,"new world created");
       break;

      case LOAD_WORLD:
       strcpy(name,ReadText(context,FILE_NAME_TEXT,button));
       if (name[0]!='\0')
       {
         sprintf(text,"loading %s.world",name);
         DisplayComment(context,text);
         strcpy(text,name);
         strcat(name,".world");
         strcpy(file_name,"WORLD/");
         strcat(file_name,name);
         ffile = fopen(file_name,"r");
         if (ffile)
         {
           WaitCursor();
           CreateEmptyWorld(context);
           ReadWorldFromFile(world,ffile);
           strcpy(world->Name,text);
           fclose(ffile);
           DrawWorld(context);
           if (!(robot->State & REAL_ROBOT_FLAG)) InitSensors(context);
           DrawRobotIRSensors(robot);
           sprintf(text,"%s loaded",name);
           PointerCursor();
         }
         else sprintf(text,"unable to find %s in WORLD directory",name);
         DisplayComment(context,text);
       }
       else DisplayComment(context,"nothing done");
       break;

      case SAVE_WORLD:
       strcpy(name,ReadText(context,FILE_NAME_TEXT,button));
       if (name[0]!='\0')
       {
         WaitCursor();
         strcpy(world->Name,name);
         strcat(name,".world");
         sprintf(text,"saving %s",name);
         strcpy(file_name,"WORLD/");
         strcat(file_name,name);
         DrawWorld(context);
         DisplayComment(context,text);
         ffile = fopen(file_name,"w");
         WriteWorldToFile(world,ffile);
         fclose(ffile);
         sprintf(text,"%s saved",name);
         PointerCursor();
         DisplayComment(context,text);
       }
       else DisplayComment(context,"nothing done");
       break;

      case SET_ROBOT:
        DisplayComment(context,"click in the world to set the robot");
        ok = FALSE;
        while(ok == FALSE)
        {
          point = ClickInWorld(context,button);
          if (point->x != -1)
          {
            robot->X = point->x;
            robot->Y = point->y;
            DrawWorld(context);
            if (!(robot->State & REAL_ROBOT_FLAG)) InitSensors(context);
             DrawRobotIRSensors(robot);
            ok = TRUE;
          }
          else ok = TRUE;
        }
        UndisplayComment(context);
       break;

      case REDRAW_WORLD:
       DrawObstacles(context);
       DrawWorld(context);
       if (!(robot->State & REAL_ROBOT_FLAG)) InitSensors(context);
        DrawRobotIRSensors(robot);
       break;

      case REMOVE_OBJECT:
       DisplayComment(context,"click in the world to remove objects");
       ok = FALSE;
       while(ok == FALSE)
       {
         point = ClickInWorld(context,button);
         if (point->x != -1)
         {
           object = FindObject(world,point->x,point->y);
           if (object)
           {
             sprintf(text,"%s removed at (%d,%d)",
                     world->ObjectName[object->Type],object->X,object->Y);
             RemoveObject(world,object);
             DrawWorld(context);
             DisplayComment(context,text);
           }
           else DisplayComment(context,"oops");
         }
         else ok = TRUE;
       }
       UndisplayComment(context);
       break;

      case ADD_OBJECT:
       DisplayComment(context,"click in the world to put objects");
       ok = FALSE;
       while(ok == FALSE)
       {
         obj = AddObjectInWorld(context,button);
         if (obj)
         {
           object = CreateObject(obj->Type,obj->X,obj->Y,obj->Alpha);
           AddObject(world,object);
           DrawObject(object);
           sprintf(text,"%s added at (%d,%d)",
                   world->ObjectName[obj->Type],obj->X,obj->Y);
           DisplayComment(context,text);
         }
         else ok = TRUE;
       }
       UndisplayComment(context);
       break;

      case TURN_OBJECT:
        world->ObjectAlpha[world->ObjectType] += 15;
        if (world->ObjectAlpha[world->ObjectType] >= 360) 
         world->ObjectAlpha[world->ObjectType] -= 360;
        DrawConsObject(world);
        sprintf(text,"turning %s",
                world->ObjectName[world->ObjectType]);
        DisplayComment(context,text);
        break;

      case OBJECT_PLUS:
        if (world->ObjectType == N_OBJECTS-1) 
         world->ObjectType= 0;
        else world->ObjectType++;
        DrawConsObject(world);
        sprintf(text,"%s selected",
                world->ObjectName[world->ObjectType]);
        DisplayComment(context,text);
        break;

      case OBJECT_MINUS:
        if (world->ObjectType == 0) 
         world->ObjectType = N_OBJECTS-1;
        else world->ObjectType--;
        DrawConsObject(world);
        sprintf(text,"%s selected",
                world->ObjectName[world->ObjectType]);
        DisplayComment(context,text);
        break;

      case STEP_ROBOT:
			 if(!queryflag && (shm_in[0] != '\0')) {
					 queryflag = TRUE;
					 MessageRobotDeal(context, shm_in, shm_out);
					 DisplayComment(context, shm_out);
			 }
			 MessageRobotRun(context);
			 if(queryflag && (shm_in[0] == '\0')) {
					 queryflag = FALSE;
					 shm_out[0] = '\0';
			 }
			 RunRobotStop(robot);
			 break;

      case RUN_ROBOT:
       //DisplayComment(context,"running Khepera");
       CancelCursor();
       DisplayComment(context,"running simulated Khepera");
			 while (UnpressButton(context,button)==FALSE) {
				 if(!queryflag && (shm_in[0] != '\0')) {
					 queryflag = TRUE;
					 MessageRobotDeal(context, shm_in, shm_out);
					 //DisplayComment(context, shm_out);
				 }
				 MessageRobotRun(context);
				 if(queryflag && (shm_in[0] == '\0')) {
					 queryflag = FALSE;
					 shm_out[0] = '\0';
				 }
			 }
			 RunRobotStop(robot);
			 DisplayComment(context,"simulated Khepera stopped");
			 PointerCursor();
			 break;

      case RESET_ROBOT:
       InitRobot(context);
       DrawRobotIRSensors(robot);
       DrawRobotEffectors(robot);
       DisplayComment(context,"Khepera reset");
       break;

      case SET_ANGLE:
       strcpy(name,ReadText(context,ANGLE_TEXT,button));
       if (name[0]!='\0')
       {
         UndisplayComment(context);
         CancelCursor();
         if (sscanf(name,"%d",&angle)==1)
         {
           robot->Alpha = (angle*M_PI)/180.0;
           DrawLittleRobot(robot,robot);
				 } else {
					 DisplayComment(context,"invalid angle");
				 }
         PointerCursor();
       }
       else DisplayComment(context,"nothing done");
       break;


      case TEST:
       if (robot->State & REAL_ROBOT_FLAG)
       {
         DisplayComment(context,"testing real Khepera");
         while (UnpressButton(context,button)==FALSE)
	 {
           InitKheperaSensors(context);
           DrawRobotIRSensors(robot);
         }
       }
       else
       {
         DisplayComment(context,"testing simulated Khepera");
         while (UnpressButton(context,button)==FALSE)
	 {
           InitSensors(context);
           DrawRobotIRSensors(robot);
         }
       }
       DisplayComment(context,"done");
       break;

       case SENSORS_BUTTON:    if (robot->State & DISTANCE_SENSOR_FLAG)
	                       {
                                 robot->State ^= DISTANCE_SENSOR_FLAG;
                                 robot->State ^= LIGHT_SENSOR_FLAG;
			       }
                               else if (robot->State & LIGHT_SENSOR_FLAG)
                                robot->State ^= LIGHT_SENSOR_FLAG;
                               else robot->State ^= DISTANCE_SENSOR_FLAG;
                               DrawRobotToggleButtons(robot);
                               DrawRobotIRSensors(robot);
                               UndisplayComment(context);
                               break;
       case MOTORS_BUTTON:     robot->State ^= MOTOR_VALUES_FLAG;
                               DrawRobotToggleButtons(robot);
                               DrawRobotEffectors(robot);
                               UndisplayComment(context);
                               break;
    }
    button->State = PLATE_UP;
    DrawButton(button);
  }
  CloseProgram();
}

