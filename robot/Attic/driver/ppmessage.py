"""
ppmessage.py defines constants and utility functions for data packet
"""
import struct


#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

# message type codes
data		  = 0x0001
command		  = 0x0002
request		  = 0x0003
acknowledgement	  = 0x0004
synchronization	  = 0x0005
nacknowledgement  = 0x0006
error		  = 0x0007

# conversion table from device number to device string
devicestr = { 0x0001 : 'player',
              0x0002 : 'power',
	      0x0003 : 'gripper',
	      0x0004 : 'position',
	      0x0005 : 'sonar',
	      0x0006 : 'laser',
	      0x0007 : 'blobfinder', 
	      0x0008 : 'ptz',
	      0x0009 : 'audio',
	      0x000A : 'fiducial',
	      0x000B : 'comms',
	      0x000C : 'speech',
	      0x000D : 'gps',
	      0x000E : 'bumper',
	      0x000F : 'truth',	
	      0x0010 : 'idarturret',
	      0x0011 : 'idar',
	      0x0012 : 'descartes',
	      0x0013 : 'mote',
	      0x0014 : 'dio',
	      0x0015 : 'aio',
	      0x0016 : 'ir',
	      0x0017 : 'wifi',
	      0x0018 : 'waveform',
	      0x0019 : 'localization',
#	      0x001A : 'bps',
}
    
# conversion table from device string to device number
devicenum = { 'player'		: 0x0001,
              'power'		: 0x0002,
              'gripper'		: 0x0003,
              'position'	: 0x0004,
              'sonar'		: 0x0005,
              'laser'		: 0x0006,
              'blobfinder'	: 0x0007,
              'ptz'		: 0x0008,
              'audio'		: 0x0009,
              'fiducial'	: 0x000A,
              'comms'		: 0x000B,
              'speech'		: 0x000C,
              'gps'		: 0x000D,
	      'bumper'		: 0x000E,
	      'truth'		: 0x000F,
	      'idarturret'	: 0x0010,
	      'idar'		: 0x0011,
	      'descartes'	: 0x0012,
	      'mote'		: 0x0013,
	      'dio'		: 0x0014,
	      'aio'		: 0x0015,
	      'ir'		: 0x0016,
	      'wifi'		: 0x0017,
	      'waveform'	: 0x0018,
	      'localization'	: 0x0019,
#	      'bps'		: 0x001A,
}

# gripper command table
gripper_command = { 'open'	: 1,
                    'close'	: 2,
		    'stop'	: 3,
		    'up'	: 4,
		    'down'	: 5,
		    'stay'	: 6,
		    'store'	: 7,
		    'deploy'	: 8,
		    'halt'	: 15,
		    'press'	: 16,
		    'carry'	: 17 }


#------------------------------------------------------------------------------
# Common functions for all devices.
#------------------------------------------------------------------------------

def pack_header(type, device, index=0, size=0):
    """
    encode header information into a binary string.
    """
    return struct.pack('!hhhhllllll',		# format string
                       0x5878,			# special symbol
		       type,			# message type
		       devicenum[device],	# device number
		       index,			# device index
		       0, 0, 0, 0,		# clients set them zero
		       0,			# reserved
		       size)			# the size of payload


def unpack_header(header):
    """
    decode header information.
    """
    try:
        stx, type, device, index, t_sec, t_usec, ts_sec, ts_usec, reserved, size \
             = struct.unpack('!hhhhllllll', header)
        return (type, device, index), (t_sec, t_usec), (ts_sec, ts_usec), size
    except:
        print "WARNING: error in unpack"
        return (0, 0, 0), (0, 0), (0, 0), 0


#------------------------------------------------------------------------------
# for 'player' device.
#------------------------------------------------------------------------------

def pack_player_devlist():
    """
    encode player get-device-list message in to a binary string.
    """
    return struct.pack('!H386x',
    		       0x01)			# PLAYER_PLAYER_DEVLIST_REQ


def unpack_player_devlist(payload):
    """
    decode player get-device-list message.
    """
    try:
        data = struct.unpack('!HH192H', payload)
    except:
        print "WARNING: error in unpack"
        data = [0] * 194
    list = []
    for idx in range(2, 2+3*data[1], 3):
        list.append((devicestr[data[idx]], data[idx+1], data[idx+2]))
    return tuple(list)


def pack_player_driverinfo(device, index, port):
    """
    encode player get-driver-info message in to a binary string.
    """
    return struct.pack('!HHHH64x',		# format string
    		       0x02,			# PLAYER_PLAYER_DRIVERINFO_REQ
    		       devicenum[device],	# device ID
		       index,			# device index
		       port)			# port number


def unpack_player_driverinfo(payload):
    """
    decode player get-driver-info message.
    """
    try:
        subtype, code, index, port, name = struct.unpack('!HHHH64s', payload)
        return name[0:name.find('\x00')]
    except:
        print "WARNING: error in unpack"
        return ""


def pack_player_request(device, index, access):
    """
    encode player request-device message into a binary string.
    """
    return struct.pack('!HHHc',			# format string
		       0x03,			# PLAYER_PLAYER_DEV_REQ
		       devicenum[device],	# device number
		       index,			# device index
		       access)			# access mode


def unpack_player_request(payload):
    """
    decode player request-device message.
    """
    try:
        subtype, device, index, access, name = struct.unpack('!HHHc64s', payload)
        return access, name[0:name.find('\x00')]
    except:
        print "WARNING: error in unpack"
        return 0, ""


def pack_player_data():
    """
    encode player request-data message into a binary string.
    """
    return struct.pack('!H',			# format string
                       0x04)			# PLAYER_PLAYER_DATA_REQ


def pack_player_datamode(mode):
    """
    encode player change-data-mode message into a binary string.
    """
    return struct.pack('!HB',			# format string
                       0x05,			# PLAYER_PLAYER_DATAMODE_REQ
                       mode)			# data mode


def pack_player_datafreq(frequency):
    """
    encode player data frequency change message into a binary string.
    """
    return struct.pack('!HH',			# format string
                       0x06,			# PLAYER_PLAYER_DATAFREQ_REQ
                       frequency)		# data frequency


def pack_player_auth(key):
    """
    encode player authentication key message into a binary string.
    """
    key_length = len(key)
    return struct.pack('!H%ds' % key_length,	# format string
    			0x07,			# PLAYER_PLAYER_AUTH_REQ
			key)			# authentication key


#------------------------------------------------------------------------------
# for 'power' device.
#------------------------------------------------------------------------------

def unpack_power_data(payload):
    """
    decode power device data.
    """
    try:
        return struct.unpack('!H', payload)[0] / 10.0
    except:
        print "WARNING: error in unpack"
        return 0.0

def pack_power_main():
    """
    encode power request-main-power message into a binary string.
    """
    return struct.pack('!B',		# format string
    		       0x0E)		# PLAYER_MAIN_POWER_REQ


def unpack_power_main(payload):
    """
    decode power request-main-power message.
    """
    try:
        return struct.unpack('!H', payload)[0] / 10.0
    except:
        print "WARNING: error in unpack"
        return 0.0


#------------------------------------------------------------------------------
# for 'gripper' device.
#------------------------------------------------------------------------------

def unpack_gripper_data(payload):
    """
    decode gripper device data.
    """
    try:
        return struct.unpack('!BB', payload)
    except:
        print "WARNING: error in unpack"
        return [0] * 2


def pack_gripper_command(command, argument):
    """
    encode a gripper command into a binary string.
    """
    return struct.pack('!BB',				# format string
                       gripper_command[command],	# command
		       argument)			# argument


#------------------------------------------------------------------------------
# for 'position' device.
#------------------------------------------------------------------------------

def unpack_position_data(payload):
    """
    decode position device data.
    """
    try:
        data = struct.unpack('!iiiiiiB', payload)
    except:
        print "WARNING: error in unpack"
        data = [0] * 7
    return (data[0:3], data[3:6], data[6])


def pack_position_command(xpos, ypos, yawpos, xspeed, yspeed, yawspeed):
    """
    encode position and speed command into a binary string.
    """
    return struct.pack('!iiiiii',	# format string
    		       xpos,		# X position
    		       ypos,		# Y position
    		       yawpos,		# heading
                       xspeed,		# X speed
		       yspeed,		# Y speed
		       yawspeed)	# turnrate


def pack_position_geom():
    """
    encode position request-geometry message into a binary string.
    """
    return struct.pack('!B10x',		# format string
    		       0x01)		# PLAYER_POSITION_GET_GEOM_REQ


def unpack_position_geom(payload):
    """
    decode position request-geometry message.
    """
    try:
        type, xpos, ypos, yawpos, xdim, ydim = struct.unpack('!B3H2H', payload)
        return ((xpos, ypos, yawpos), (xdim, ydim))
    except:
        print "WARNING: error in unpack"
        return ((0, 0, 0), (0, 0))


def pack_position_motorpower(on):
    """
    encode position motor-on/off message into a binary string.
    """
    return struct.pack('!BB',		# format string
                       0x02,		# PLAYER_POSITION_MOTOR_POWER_REQ
		       on)		# on/off


def pack_position_velocitymode(mode):
    """
    encode position velocity-control message into a binary string.
    """
    return struct.pack('!BB',		# format string
                       0x03,		# PLAYER_POSITION_VELOCITY_MODE_REQ
		       mode)		# velocity control mode


def pack_position_reset(): 
    """
    encode position odometry-reset message into a binary string.
    """
    return struct.pack('!B',		# format string
                       0x04)		# PLAYER_POSITION_RESET_ODOM_REQ


def pack_position_positionmode(mode):
    """
    encode position posiiton-control message into a binary string.
    """
    return struct.pack('!BB',		# format string
                       0x05,		# PLAYER_POSITION_POSITION_MODE_REQ
		       mode)		# position control mode


def pack_position_speedpid(kp, ki, kd): 
    """
    encode position speed-pid message into a binary string.
    """
    return struct.pack('!Biii',		# format string
                       0x06,		# PLAYER_POSITION_SPEED_PID_REQ
		       kp, kp, kd)	# PID parameters


def pack_position_positionpid(kp, ki, kd): 
    """
    encode position position-pid message into a binary string.
    """
    return struct.pack('!Biii',		# format string
                       0x07,		# PLAYER_POSITION_SPEED_PID_REQ
		       kp, kp, kd)	# PID parameters


def pack_position_speedprof(max_speed, max_acc):
    """
    encode position set-speed-profile message into a binary string.
    """
    return struct.pack('!Bhh',		# format string
    		       0x08,		# PLAYER_POSITION_POSITION_PID_REQ
		       max_speed,	# maximum speed
		       max_acc)		# maximum acceleration


def pack_position_setodom(x, y, theta):
    """
    encode position set-odometry message into a binary string.
    """
    return struct.pack('!BiiH',		# format string
    		       0x09,		# PLAYER_POSITION_SET_ODOM_REQ
		       x, y, theta)	# new pose


#------------------------------------------------------------------------------
# for 'sonar' device.
#------------------------------------------------------------------------------

def unpack_sonar_data(payload): 
    """
    decode sonar device data.
    """
    try:
        data = struct.unpack('!H32H', payload)
    except:
        print "WARNING: error in unpack"
        data = [0] * 33
    return data[1:data[0]+1]


def pack_sonar_geom(): 
    """
    encode sonar get-geometry message into a binary string.
    """
    return struct.pack('!B',		# format string
    		       0x01)		# PLAYER_SONAR_GET_GEOM_REQ


def unpack_sonar_geom(payload): 
    """
    decode sonar get-geometry message.
    """
    try:
        data = struct.unpack('!BH96h', payload)
    except:
        print "WARNING: error in unpack"
        data = [0] * 98
    geometry = []
    for idx in range(data[1]):
        geometry.append(tuple(data[2+idx*3:2+(idx+1)*3]))
    return tuple(geometry)


def pack_sonar_power(state): 
    """
    encode sonar set-power message into a binary string.
    """
    return struct.pack('!BB',		# format string
                       0x02,		# PLAYER_SONAR_POWER_REQ
		       state)		# on/off state


#------------------------------------------------------------------------------
# for 'laser' device.
#------------------------------------------------------------------------------

def unpack_laser_data(payload): 
    """
    decode laser device data.
    """
    try:
        data = struct.unpack('!hhHH401H401B', payload)
    except:
        print "WARNING: error in unpack"
        data = [0] * 806
    return ((data[0]/100.0, data[1]/100.0, data[2]/100.0),
    	    data[4:4+data[3]], data[405:405+data[3]])


def pack_laser_geom(): 
    """
    encode laser get-geometry message into a binary string.
    """
    return struct.pack('!B',			# format string
    		       0x01)			# PLAYER_LASER_GET_GEOM


def unpack_laser_geom(payload): 
    """
    decode laser get-geometry message.
    """
    try:
        type, xpos, ypos, yaw, xdim, ydim = struct.unpack('!B3h2h', payload)
        return ((xpos, ypos, yaw), (xdim, ydim))
    except:
        print "WARNING: error in unpack"
        return ((0, 0, 0), (0, 0))


def pack_laser_setconfig(min_angle, max_angle, resolution, intensity): 
    """
    encode laser set-config message into a binary string.
    """
    return struct.pack('!BhhHB',		# format string
    		       0x02,			# PLAYER_LASER_SET_CONFIG
                       int(min_angle*100),	# start angle for scanning
                       int(max_angle*100),	# end angle for scanning
                       int(resolution*100),	# angular resolution
		       intensity)		# refletive intensity ?


def pack_laser_getconfig(): 
    """
    encode laser get-config message into a binary string.
    """
    return struct.pack('!B',			# format string
    		       0x03)			# PLAYER_LASER_GET_CONFIG


def unpack_laser_getconfig(payload): 
    """
    decode laser get-config message.
    """
    try:
        type, min_angle, max_angle, resolution, intensity \
              = struct.unpack('!BhhHB', payload)
        return (min_angle/100.0, max_angle/100.0, resolution/100.0, intensity)
    except:
        print "WARNING: error in unpack"
        return (0, 0, 0, 0)


#------------------------------------------------------------------------------
# for 'blobfinder' device.
#------------------------------------------------------------------------------

def unpack_blobfinder_data(payload): 
    """
    decode blobfinder device data.
    """
    # parse header information
    try:
        width, height = struct.unpack('!HH', payload[:4])
    except:
        print "WARNING: error in unpack"
        width, height = 0, 0
    try:
        header = struct.unpack('!64H', payload[4:132])
    except:
        print "WARNING: error in unpack"
        header = [0] * 140
    num_blobs = range(32)
    index = range(32)
    for idx in range(0, 64, 2):
	index[idx/2] = header[idx]
        num_blobs[idx/2] = header[idx+1]
    # parse blob data
    blob_list = []
    for idx in range(32):
        if num_blobs[idx]:	# blobs found!
	    start = 132 + index[idx] * 22
	    blobs = []
	    for datum in range(start, start+num_blobs[idx]*22, 22):
                try:
                    blob = struct.unpack('!IIHHHHHHH', payload[datum:datum+22])
                except:
                    print "WARNING: error in unpack"
                    blob = [0] * 9
	        blobs.append(blob)
	    blob_list.append(tuple(blobs))
	else:			# no blob found in this channel
	    blob_list.append(())
    return ((width, height), tuple(blob_list))


#------------------------------------------------------------------------------
# for 'ptz' device.
#------------------------------------------------------------------------------

def unpack_ptz_data(payload): 
    """
    decode ptz device data.
    """
    return struct.unpack('!hhh', payload)


def pack_ptz_command(pan, tilt, zoom): 
    """
    encode ptz command data into a binary string.
    """
    return struct.pack('!hhh',			# format string
    		       pan,			# pan
		       tilt,			# tilt
		       zoom)			# zoom


#------------------------------------------------------------------------------
# for 'audio' device.
#------------------------------------------------------------------------------

def unpack_audio_data(payload): 
    """
    decode audio device data.
    """
    return struct.unpack('!10H', payload)


def pack_audio_command(frequency, amplitude, duration): 
    """
    encode audio command data into a binary string.
    """
    return struct.pack('!HHH',		# format string
                       frequency,	# frequency to play in Hz
                       amplitude,	# amplitude to play in dB
		       duration)	# duration of play in second


#------------------------------------------------------------------------------
# for 'fiducial' device.
#------------------------------------------------------------------------------

def unpack_fiducial_data(payload): 
    """
    decode fiducial device data.
    """
    data = struct.unpack('!H224h', payload)
    result = []
    for idx in range(data[0]):
    	result.append(tuple(data[1+idx*7:1+(idx+1)*7]))
    return tuple(result)


def pack_fiducial_getgeom(): 
    """
    encode fiducial get-geometry message into a binary string.
    """
    return struct.pack('!B',		# format string
		       0x01)		# PLAYER_FIDUCIAL_GET_GEOM


def unpack_fiducial_getgeom(payload): 
    """
    decode fiducial get-geometry message.
    """
    type, xpos, ypos, yaw, xdim, ydim, xsize, ysize \
    		= struct.unpack('!B3H2H2H', payload)
    return ((xpos, ypos, yaw), (xdim, ydim), (xsize, ysize))


#------------------------------------------------------------------------------
# for 'comms' device.
#------------------------------------------------------------------------------

def unpack_comms_data(payload): 
    """
    decode comms device data.
    """
    return struct.unpack('!%ds' % len(payload), payload)


def pack_comms_command(message): 
    """
    encode comms command into a binary string.
    """
    return struct.pack('!%ds' % len(message),	# format string
    		       message)			# message


#------------------------------------------------------------------------------
# for 'speech' device.
#------------------------------------------------------------------------------

def pack_speech_command(message): 
    """
    encode speech command into a binary string.
    """
    return struct.pack('!256s',			# format string
                       message)			# message


#------------------------------------------------------------------------------
# for 'gps' device.
#------------------------------------------------------------------------------

def unpack_gps_data(payload): 
    """
    decode gps device data.
    """
    return struct.unpack('!iii', payload)


#------------------------------------------------------------------------------
# for 'bumper' device.
#------------------------------------------------------------------------------

def unpack_bumper_data(payload): 
    """
    decode bumper device data.
    """
    data = struct.unpack('!B32B', payload)
    return data[1:data[0]+1]


def pack_bumper_getgeom():
    """
    encode bumper get-geometry message into a binary string.
    """
    return struct.pack('!B',			# format string
    		       0x01)			# PLAYER_BUMPER_GET_GEOM_REQ


def unpack_bumper_getgeom(payload):
    """
    decode bumper get-geometry message.
    """
    data = struct.unpack('!BH \
		  hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH \
		  hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH \
		  hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH \
		  hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH hhhHH', payload)
    result = []
    for idx in range(data[1]):
        result.append(data[2+idx*5:2+(idx+1)*5])
    return tuple(result)


#------------------------------------------------------------------------------
# for 'truth' device.
#------------------------------------------------------------------------------

def unpack_truth_data(payload): 
    """
    decode truth device data.
    """
    try:
        return struct.unpack('!iii', payload);
    except:
        print "WARNING: error in unpack"
        return [0] * 3


def pack_truth_getpose():
    """
    encode truth get-pose message into a binary string.
    """
    return struct.pack('!B',		# format string
    		       0x00)		# PLAYER_TRUTH_GET_POSE


def unpack_truth_getpose(payload):
    """
    decode truth get-pose message.
    """
    try:
        return struct.unpack('!Biii', payload)[1:]
    except:
        print "WARNING: error in unpack"
        return [0] * 2


def pack_truth_setpose(px, py, pa):
    """
    encode truth set-pose message into a binary string.
    """
    return struct.pack('!Biii',		# format string
    		       0x01,		# PLAYER_TRUTH_GET_POSE
		       px, py, pa)	# new pose


#------------------------------------------------------------------------------
# for 'idarturret' device.
#------------------------------------------------------------------------------

def unpack_idarturret_data(payload): 
    """
    decode idarturret device data.
    """
    pass



#------------------------------------------------------------------------------
# for 'idar' device.
#------------------------------------------------------------------------------

def unpack_idar_data(payload): 
    """
    decode idar device data.
    """
    pass


#------------------------------------------------------------------------------
# for 'descartes' device.
#------------------------------------------------------------------------------

# This device does not exist anymore.


#------------------------------------------------------------------------------
# for 'mote' device.
#------------------------------------------------------------------------------

def unpack_mote_data(payload): 
    """
    decode mote device data.
    """
    try:
        len = struct.unpack('!B', payload[0]);
    except:
        print "WARNING: error in unpack"
        len = 0
    return payload[1:len+1]


def pack_mote_config(strength):
    """
    encode mote set-config message into a binary string.
    """
    return struct.pack('!B',			# format string
    		       strength)		# transmission power


#------------------------------------------------------------------------------
# for 'dio' device.
#------------------------------------------------------------------------------

def unpack_dio_data(payload):
    """
    decode dio (digital IO) device data.
    """
    num, data = struct.unpack('!BI', payload)
    result = []
    filter = 0x80
    for idx in range(num):
        if data & filter: result.append(1)
	else: result.append(0)
	filter >>= 1
    return tuple(result)


#------------------------------------------------------------------------------
# for 'aio' device.
#------------------------------------------------------------------------------

def unpack_aio_data(payload):
    """
    decode aio (analog IO) device data.
    """
    data = struct.unpack('!B8i', payload)
    return data[1:data[0]+1]


#------------------------------------------------------------------------------
# for 'ir' device.
#------------------------------------------------------------------------------

def unpack_ir_data(payload):
    """
    decode ir device data.
    """
    data = struct.unpack('!H8H8H', payload)
    return (data[1:data[0]+1], data[9:data[0]+9])


def pack_ir_getpose(): 
    """
    encode ir get-pose message into a binary string.
    """
    return struct.pack('!B',		# format string
    		       0x01)		# PLAYER_IR_POSE_REQ


def unpack_ir_getpose(payload): 
    """
    decode ir get-pose message.
    """
    data = struct.unpack('!BH96h', payload)
    poses = []
    for idx in range(8):
        poses.append(tuple(data[1+idx*3:1+(idx+1)*3]))
    return tuple(poses)


def pack_ir_power(state): 
    """
    encode ir set-power message into a binary string.
    """
    return struct.pack('!BB',		# format string
                       0x02,		# PLAYER_IR_POWER_REQ
		       state)		# on/off state


#------------------------------------------------------------------------------
# for 'wifi' device.
#------------------------------------------------------------------------------

def unpack_wifi_data(payload):
    """
    decode wifi device data.
    """
    data = struct.unpack('!i 32s3H 32s3H 32s3H 32s3H \
    			     32s3H 32s3H 32s3H 32s3H \
    			     32s3H 32s3H 32s3H 32s3H \
    			     32s3H 32s3H 32s3H 32s3H ', payload)
    result = []
    for idx in range(data[0]):
        result.append(data[1+idx*4:1+(idx+1)*4])
    return tuple(result)


#------------------------------------------------------------------------------
# for 'waveform' device.
#------------------------------------------------------------------------------

def unpack_waveform_data(payload):
    """
    decode waveform device data.
    """
    rate, depth, samples = struct.unpack('!IHI', payload[0:10])
    return (rate, depth, sample, payload[10:])


#------------------------------------------------------------------------------
# for 'localization' device.
#------------------------------------------------------------------------------

def unpack_localization_data(payload):
    """
    decode localization device data.
    """
    data = struct.unpack('!I 3i9iI 3i9iI 3i9iI 3i9iI \
    			     3i9iI 3i9iI 3i9iI 3i9iI \
    			     3i9iI 3i9iI', payload)
    result = []
    for idx in range(10):
        result.append((data[1+idx*13:1+idx*13+3],	# mean
		       (data[1+idx*13+3:1+idx*13+6],
		        data[1+idx*13+6:1+idx*13+9],
		        data[1+idx*13+9:1+idx*13+12]),	# covariance matrix
		       data[1+idx*13+12]/1000000000.0))	# coefficient
    return tuple(result)


def pack_localization_reset():
    """
    encode localization reset message into a binary string.
    """
    return struct.pack('!B',		# format string
    		       0x01)		# PLAYER_LOCALIZATION_RESET_REQ


def pack_localization_getconfig():
    """
    encode localization get-config message into a binary string.
    """
    return struct.pack('!B',		# format string
    		       0x02)		# PLAYER_LOCALIZATION_GET_CONFIG_REQ


def unpack_localization_getconfig(payload):
    """
    decode localization get-config message.
    """
    return struct.unpack('!BI', payload)[1:]


def pack_localization_setconfig(num_particles):
    """
    encode localization get-config message into a binary string.
    """
    return struct.pack('!BI',		# format string
    		       0x03,		# PLAYER_LOCALIZATION_SET_CONFIG_REQ
		       num_particles)	# the number of particles


def pack_localization_getmaphdr(scale):
    """
    encode localization get-map-header message into a binary string.
    """
    return struct.pack('!BB',		# format string
    		       0x04,		# PLAYER_LOCALIZATION_GET_CONFIG_REQ
		       scale)		# the scale factor


def unpack_localization_getmaphdr(payload):
    """
    decode localization get-map-header message.
    """
    type, scale, width, height, ppkm = struct.unpack('!BBIII', payload)
    return (width, height, ppkm/1000.0)


def pack_localization_getmapdata(scale, row):
    """
    encode localization get-map-data message into a binary string.
    """
    return struct.pack('!BBH',		# format string
    		       0x05,		# PLAYER_LOCALIZATION_GET_CONFIG_REQ
		       scale,		# the scale factor
		       row)		# the starting row


def unpack_localization_getmapdata(payload):
    """
    decode localization get-map-header message.
    """
    return payload[4:]


#------------------------------------------------------------------------------
# for 'bps' device.
#------------------------------------------------------------------------------

# this device is broken in v1.3

#def unpack_bps(payload): 
#    """
#    decode bps device data.
#    """
#    return struct.unpack('!iiiiiii', payload)
#
#
#def pack_bps(): 
#    """
#    encode BPS configuration into a binary string.
#    """
#    pass
#
#
#def pack_bps_configuration(): 
#    """
#    encode query message for BPS configuration into a binary string.
#    """
#    pass
#
#
#def pack_bps_beacon(id, px, py, pa, ux, uy, ua): 
#    """
#    encode BPS beacon information into a binary string.
#    """
#    return struct.pack('!BBiiiiii',	# format string
#    		       0x03,		# request index
#		       id,		# laserbeacon ID
#                       px,		# x position in mm
#		       py,		# y position in mm
#		       pa,		# orientation in degree
#                       ux,		# x position uncertainty in mm
#		       uy,		# y position uncertainty in mm
#		       ua)		# orientation uncertainty in degree
#
#
#def pack_bps_beacon_configuration(): 
#    """
#    encode request mesage for BPS beacon information into a binary string.
#    """
#    return struct.pack('!B',	# format string
#    		       0x04)	# request message


