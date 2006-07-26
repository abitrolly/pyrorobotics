/*	 	IntelliBrainBot Control Code
 *	 	    built @ SUNY Potsdam
 *		James Snow & Dr. Timothy Fossum 
 *		Version 1.4 , July 19th 2006
 */

import com.ridgesoft.intellibrain.*;
import javax.comm.SerialPort;
import java.io.*;
import com.ridgesoft.io.*;
import com.ridgesoft.robotics.*;
import com.ridgesoft.robotics.sensors.SharpGP2D12;

public class IBB {
       public static float leftPreDist = 40;
       public static float rightPreDist = 40;
       public static final int H_MAX_POWER = 9;
       public static void writeCRLF(OutputStream out, String str) {
		try {
			char [] ary = str.toCharArray();
			int len = ary.length;
			for (int i=0 ; i<len ; i++)
				out.write((int)ary[i]);
			out.write('\r'); //CR
			out.write('\n'); //LF
		} 
		catch (Exception e) {
			e.printStackTrace();
		}		int leftPwr;
		int rightPwr;

	}

	public static void getVersion(OutputStream out, byte [] buf, int len) {
		writeCRLF(out, "b,RoboJDE v1.4.0r1");
	}

	public static void setSpeed(OutputStream out, byte [] buf, int len) {

		Motor leftMotor = new ContinuousRotationServo(IntelliBrain.getServo(1), false, 14);
		Motor rightMotor = new ContinuousRotationServo(IntelliBrain.getServo(2), true, 14);
		
		int leftSign = 1;
		int rightSign = 1;
		int p = 2;

		if (buf[p] == '-') {	//if input is '-', move right one place  
			leftSign = -1;
			p++;
		}
		int leftPwr = 0;
		while ('0' <= buf[p] && buf[p] <= '9')
			leftPwr =  leftPwr*10 + (buf[p++] - '0'); //accumulate the decimal value
		if (leftPwr > H_MAX_POWER)
			leftPwr = H_MAX_POWER; // stay in range
		leftPwr = leftSign*leftPwr;
		
		// assert(buf[p] == ',');
		p++;

		if (buf[p] == '-') {
			rightSign = -1;
			p++;
		}
		int rightPwr = 0;
		while ('0' <= buf[p] && buf[p] <= '9')
			rightPwr = rightPwr*10 + (buf[p++] - '0');
		if (rightPwr > H_MAX_POWER)
			rightPwr = H_MAX_POWER; // stay in range
		rightPwr = rightSign * rightPwr;

		// assert(buf[p] == 0); // the buffer is null-terminated
		p++;
		
		leftMotor.setPower((leftPwr*16)/H_MAX_POWER);
		rightMotor.setPower((rightPwr*16)/H_MAX_POWER);
		writeCRLF(out, "d");
}
	
	public static void sysBeep(OutputStream out, byte [] buf, int len) {

		if (buf[2] == '1') {
        	Speaker buzzer = IntelliBrain.getBuzzer();
       	 	buzzer.beep();
		}
		writeCRLF(out, "h");	
		
    }
	 
	
	public static void setLedState(OutputStream out, byte [] buf, int len) {
		
			LED statusLED = IntelliBrain.getStatusLed();
            LED faultLED = IntelliBrain.getFaultLed();

			if (buf[2] == '1') 
			    statusLED.on();
			else 
				statusLED.off();

			if (buf[4] == '1')
				faultLED.on();
			else
				faultLED.off();

		writeCRLF(out, "l");

    }
	//Distance Sensors on front of bot
	public static void readProximitySensors(OutputStream out, byte [] buf, int len) {
			
			try {

			RangeFinder leftRangeFinder = new SharpGP2D12(IntelliBrain.getAnalogInput(1), null);
			RangeFinder rightRangeFinder = new SharpGP2D12(IntelliBrain.getAnalogInput(2), null);

			leftRangeFinder.ping();											// Tell the sensor to test the left range sensor
				float leftDistance = leftRangeFinder.getDistanceCm();		// Read the distance measured by the left range sensor
			rightRangeFinder.ping();										// Tell the sensor to test the right range sensor
				float rightDistance = rightRangeFinder.getDistanceCm();		// Read the distance measured by the right range sensor
			
				if (leftDistance < 0.0f) 
					leftDistance = leftPreDist;
					
				else
					leftPreDist = leftDistance;
	
				int leftVal = (int)leftDistance;	

				if (rightDistance < 0.0f)	//out of range (too far or too close)
					rightDistance = rightPreDist;

				else
					rightPreDist = rightDistance;

				int rightVal = (int)rightDistance;

				writeCRLF(out, "n, " + rightVal + ", " + leftVal);
			}
		catch (Throwable t) {
			t.printStackTrace();
		}
	}	
	//Ground Sensors *Used in Line Follower* Bottom of Bot
	public static void readLightSensors(OutputStream out, byte [] buf, int len) {

			try {

				AnalogInput leftLightSensor = IntelliBrain.getAnalogInput(6);
            	AnalogInput rightLightSensor = IntelliBrain.getAnalogInput(7);			 
			
				int leftLightDetection = leftLightSensor.sample();
        	    int rightLightDetection = rightLightSensor.sample();

				//Convert the 10bit numbers to 8 bit
				int groundRight = (rightLightDetection >> 2);
				int groundLeft = (leftLightDetection >> 2);

				writeCRLF(out, "o, " + groundRight + ", " + groundLeft);
			}
			catch (Throwable t) {
            t.printStackTrace();
        	}
	}

	public static void motorsOff(OutputStream out, byte [] buf, int len) {
	
		Motor leftMotor = new ContinuousRotationServo(IntelliBrain.getServo(1), false, 14);
		Motor rightMotor = new ContinuousRotationServo(IntelliBrain.getServo(2), true, 14);

		leftMotor.setPower(0);
		rightMotor.setPower(0);
		
		writeCRLF(out, "z");
	}

	
	public static int readLine(InputStream in, OutputStream out, Display display, boolean echo, byte [] buf, int maxLen) {
		// get a line from the input stream into the buffer buf, of max length maxLen
		// line is terminated with a return character;
		// echo back to output stream
		// also write to line 0 of the display, up to 16 characters
		try {		int data;
		int len = 0;
		maxLen--; // make room for a null byte
        while ((data = in.read()) != -1) {
			if (data == 0)
				continue;
			if(data == '\n')
				continue;
			if (echo)
				out.write(data); // echo it back
			byte ch = (byte) data;

			if (ch == '\r') {
				if (echo)
					out.write('\n');
				int dlen = len; // LCD panel display length 
				if (dlen > 16)
					dlen = 16;
				byte [] screenBuf = new byte [dlen];
				for (int i=0 ; i<dlen ; i++)
					screenBuf[i] = buf[i];
				display.print(0, screenBuf);  // echo it to the display
				buf[len] = 0;
				return len;
			} else if(len < maxLen) {
				buf[len++] = ch;
			}
		}
		} catch (Exception e) {
			display.print(0, "oops!");
		}
		return -1;
	}

    public static void main(String args[]) {

		Display display = IntelliBrain.getLcdDisplay();

        try {
            // uncomment one line to choose a COM port
            SerialPort comPort = IntelliBrain.getCom1();

			//Serial Parameters
            comPort.setSerialPortParams(38400,
										SerialPort.DATABITS_8,		
                    					SerialPort.STOPBITS_1,
										SerialPort.PARITY_NONE);

            InputStream inputStream = comPort.getInputStream();
            OutputStream outputStream = comPort.getOutputStream();

			// clear screen
			display.print(0, "");
			display.print(1, "");
			
			// test the readLine routine			
			byte [] buf = new byte[128];

			

			while(true) {
				int len = readLine(inputStream, outputStream, display, true, buf, 128);

				if(len == 0) continue;
			
				switch (buf[0]) {
			
					case 'B' : getVersion(outputStream, buf, len); break;
					case 'D' : setSpeed(outputStream, buf, len); break;
					case 'H' : sysBeep(outputStream, buf, len); break;
					case 'L' : setLedState(outputStream, buf, len); break;
					case 'N' : readProximitySensors(outputStream, buf, len); break;
					case 'O' : readLightSensors(outputStream, buf, len); break;
					case 'Z' : motorsOff(outputStream, buf, len); break;
				}
			}
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }
}