/*
  XRCL: The Extensible Robot Control Language
  (c) 2000, Douglas S. Blank
  University of Arkansas, Roboticists Research Group
  http://ai.uark.edu/xrcl/
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
  02111-1307, USA.

  As a special exception, you have permission to link this program
  with the Qt library and distribute executables, as long as you
  follow the requirements of the GNU GPL in regard to all of the
  software in the executable aside from Qt.
*/

// B21R Camera Mover

#include "B21RCamMover.h"

B21RCamMover::B21RCamMover() : CamMover()
{
  fprintf(stderr, "Initializing B21RCamMover\n");
  xpos = ypos = pos = 0;
  
  xpmin = -3050;
  ypmin = -900;
  xpmax = 3050;
  ypmax = 600;

  struct termios term_info;
  rocketport = open(ROCKETPORT, O_RDWR | O_SYNC);
  if (rocketport == -1) {
    fprintf(stderr, "ERROR: '%s' did not open!\n", ROCKETPORT);
  }
  
  if(tcgetattr(rocketport,&term_info) <0) {
    fprintf(stderr, "ERROR: can't get info on '%s'!\n", ROCKETPORT);
  }
  
  term_info.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
  term_info.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
  term_info.c_cflag &= ~(CSIZE | PARENB);
  term_info.c_cflag |= CS8;
  term_info.c_oflag &= ~(OPOST);
  term_info.c_cc[VTIME] = 0;
  term_info.c_cc[VMIN] = 0;
  if(tcsetattr(rocketport,TCSAFLUSH,&term_info) <0) {
    fprintf(stderr, "ERROR: can't flush on '%s'!\n", ROCKETPORT);
  }
}

B21RCamMover::~B21RCamMover()
{
  close(rocketport);
}

int B21RCamMover::num_chars()
{
  long available=0;
  
  if (ioctl(rocketport, FIONREAD, &available) == 0)
    return available;
  else
    return -1;
}

int B21RCamMover::Read() 
{
  int pos;
  int size,get_size;
  int read_index;
  char AxisBuf[80];
  char read_buffer[128];

   // Read the buffer until it is empty.
   read_index = 0;
   get_size = num_chars();

   // Read as much of the buffer as you can, up to 127 characters.
   while((get_size > 0) && (read_index < 127) &&
	 (read_buffer[read_index-1] != '\r') &&
	 (read_buffer[read_index-1] != ' ') &&
	 (read_buffer[read_index-1] != '\n'))
     {
       if ((int)(sizeof(read_buffer) - read_index) < get_size)
	 get_size = sizeof(read_buffer) - read_index;

       size = read(rocketport, (unsigned char *)&(read_buffer[read_index]),
		   get_size);
      
       read_index += size;

       get_size = num_chars(); // Check for more again on next read.
     }

   // Read until the end of the response this time.

   // Put on a NULL terminator on the whole response we've read.
   read_buffer[read_index] = '\0';

   // Now process the buffer to extract update information:
   
      if ( sscanf(read_buffer," * Current %s position is %d ",
              AxisBuf,&pos) > 0)
        {
          if (AxisBuf[0] == 'T')
            { 
	      fprintf(stderr, "CAM TILT: %f\n", (float) pos);
	      /*
	      m_oldDriveData.position[0] = m_rawDriveData.position[0];
              m_rawDriveData.position[0] = (float) pos * m_tiltscale;

	      m_rawDriveData.velocity[0] = m_rawDriveData.position[0] -
		m_oldDriveData.position[0];
	      */
            }
          else if (AxisBuf[0] == 'P')
            { 
	      fprintf(stderr, "CAM PAN: %f\n", (float) pos);
	      /*
	      m_oldDriveData.position[1] = m_rawDriveData.position[1];
              m_rawDriveData.position[1] = (float) pos * m_panscale;

	      m_rawDriveData.velocity[1] = m_rawDriveData.position[1] -
		m_oldDriveData.position[1];

	      update_io_state(); // Send out the new information.
	      */
            }
        }
      else
	fprintf(stderr,"Pantilt Response: [%d] {%s}\n",read_index,read_buffer);

      /*
      char cmdbuf[20];
      // Send commands to cause PanTilt to generate position responses
      // Get current state.
      sprintf(cmdbuf,"PP\rTP\r");
      write(rocketport, (unsigned char *)cmdbuf,strlen(cmdbuf));
      */

      return 0;
}

void B21RCamMover::Init() {
  // Set echo mode.-- no command echo.
  sprintf(buffer,"ED\r");
  write(rocketport, (unsigned char *)buffer,strlen(buffer));
  sleep(1);
  Read();

  // Enable position limits.
  sprintf(buffer,"LE\r");
  write(rocketport, (unsigned char *)buffer,strlen(buffer));
  sleep(1);
  Read();

  // Query Model of pan-tilt.
  sprintf(buffer,"V\r");
  write(rocketport, (unsigned char *)buffer,strlen(buffer));
  sleep(1);
  Read();

  // Set immediate command mode.
  sprintf(buffer,"I\r");
  write(rocketport, (unsigned char *)buffer,strlen(buffer));
  sleep(1);
  Read();

  
  // Initial request for  current state.
  sprintf(buffer,"PP\rTP\r");
  write(rocketport, (unsigned char *)buffer,strlen(buffer));
  sleep(1);
  Read();

  Center();
  fprintf(stderr, "Pan-Tilt Unit initialized.\n");
}

void B21RCamMover::Center ()
{
  sprintf ( buffer, "TP0\rPP0\r");
  ypos = 0;
  xpos = 0;
  PanAngle = 0.0;
  TiltAngle = 0.0;
  ZoomAmount = 0.0;
  write(rocketport, buffer, strlen(buffer)); 
}

void B21RCamMover::Pan(int degrees) {
  static double DEG2TICKS = 19.444444444; // 1750 / 90
  static double TICKS2DEG = 0.051428571; // 90 / 1750
  xpos = (int) (-degrees * DEG2TICKS);
  if ( xpos > xpmax )
    xpos = xpmax;
  if ( xpos < xpmin )
    xpos = xpmin;
  PanAngle = xpos * TICKS2DEG;
  sprintf ( buffer, "PP%d\r", xpos);
  write(rocketport, buffer, strlen(buffer)); 
}

void B21RCamMover::Tilt(int degrees) {
  static double DEG2TICKS = 19.444444444; // 1750 / 90
  static double TICKS2DEG = 0.051428571; // 90 / 1750
  ypos = (int) (degrees * DEG2TICKS);
  if ( ypos < ypmin )
    ypos = ypmin;
  if ( ypos > ypmax )
    ypos = ypmax;
  TiltAngle = ypos * TICKS2DEG;
  sprintf ( buffer, "TP%d\r", ypos);
  write(rocketport, buffer, strlen(buffer)); 
}

void B21RCamMover::PanTilt(int pdegrees, int tdegrees) {
  Pan(pdegrees);
  Tilt(tdegrees);
}

void B21RCamMover::Zoom(int amount) {
  // nothing here, no zoom
  fprintf(stderr, "ERROR: B21RCamMover has no zoom\n");
}

int B21RCamMover::Up ()
{
  ypos += 250;
  if ( ypos > ypmax )
    {
      ypos = ypmax;
      return -1;  // return -1 if can't move in this direction again.
    }
  sprintf ( buffer, "TP%d\r", ypos );
  write(rocketport, buffer, strlen(buffer)); 
  //  fwrite( buffer, 1, strlen(buffer), rocketport );
  return 0;
}

int B21RCamMover::Down ()
{
  ypos-= 250;
  if ( ypos < ypmin )
    {
      ypos = ypmin;
      return -1;  // return -1 if can't move in this direction again.
    }
  sprintf ( buffer, "TP%d\r", ypos);
  write(rocketport, buffer, strlen(buffer)); 
  //  fwrite( buffer, 1, strlen(buffer), rocketport );
  return 0;
}

int B21RCamMover::Left ()
{
  xpos+= 250;
  if ( xpos > xpmax )
    {
      xpos = xpmax;
      return -1;  // return -1 if can't move in this direction again.
    }
  sprintf ( buffer, "PP%d\r", xpos);
  write(rocketport, buffer, strlen(buffer)); 
  //  fwrite( buffer, 1, strlen(buffer), rocketport );
  return 0;
}

int B21RCamMover::Right ()
{
  xpos-= 250;
  if ( xpos < xpmin )
    {
      xpos = xpmin;
      return -1;  // return -1 if can't move in this direction again.
    }
  sprintf ( buffer, "PP%d\r", xpos);
  write(rocketport, buffer, strlen(buffer)); 
  //  fwrite( buffer, 1, strlen(buffer), rocketport );
  return 0;
}
