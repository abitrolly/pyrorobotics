"""
pyplayer.py is a Player client written in/for python
"""
import socket
import thread
import time
from ppmessage import *


class player:
    """
    wrapper class for communication to a player server.
    """

    #--------------------------------------------------------------------------
    # functions for connection to Player server.
    #--------------------------------------------------------------------------

    def __init__(self, hostname='localhost', port=6665, auto=1, speed=20):
	"""
	connect to the specified player server, and request a player device.
	"""

	# debugging information will be inhibited
	self.debug = 0

	try:
	    # make a connection to the specified player server
	    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    self.__socket.connect((hostname, port))
	    pversion = self.__nrecv(32)		# version string
	    self.__socket.setblocking(0)

	    # create sensory data repository
	    self.power		= {}
	    self.gripper	= {}
	    self.position	= {}
	    self.sonar		= {}
	    self.laser		= {}
	    self.blobfinder	= {}
	    self.ptz		= {}
	    self.audio		= {}
	    self.fiducial	= {}
	    self.comms		= {}
	    #self.speech	= {}		# no data for this device
	    self.gps		= {}
	    self.bumper		= {}
	    self.truth		= {}
	    #self.idarturret	= {}		# not implemented yet
	    #self.idar		= {}		# not implemented yet
	    #self.descartes	= {}		# not exist anymore
	    self.mote		= {}
	    self.dio		= {}
	    self.aio		= {}
	    self.ir		= {}
	    self.wifi		= {}
	    self.waveform	= {}
	    self.localization	= {}
# Player 1.5
            self.mcom           = {}
            self.sound          = {}
            self.audiodsp       = {}
            self.audiomixer     = {}
            self.position3d     = {}
            self.simulation     = {}
            self.service_adv    = {}
            self.blinkenlight   = {}
            self.camera         = {}
# Player 1.5
	    #self.bps		= {}		# bps device is broken
	    # create automatic update thread
	    self.lock = thread.allocate_lock()
	    if auto: self.start_update(speed)
	    else: self.stop_update()

	except socket.error, errstr:
	    self.__socket = None
	    raise 'cannot create a socket: %s' % errstr

	except thread.error:
	    raise 'cannot run an update thread.'

	else:
# Player 1.5
            self.lastPosition = {}
	    self.lastPosition['xpos'] = 0
	    self.lastPosition['ypos'] = 0
	    self.lastPosition['yawspeed'] = 0
	    self.lastPosition['xspeed'] = 0
	    self.lastPosition['yspeed'] = 0
	    self.lastPosition['yawspeed'] = 0
# Player 1.5
	    # save the information of the connection
	    self.server = (hostname, port)
	    if self.debug: print '<connected to %s:%d>' % self.server + ' (%s)' % pversion


    def close(self):
	"""
	disconnect from the player server.
	"""
	# close the connection
	if self.__socket is not None:
	    try:
	        self.__update_flag = 0
	        self.__socket.shutdown(2)
		self.__socket.close()

	    except socket.error, errstr:
	        raise 'cannot close the socket: %s' % errstr

	    else:
		if self.debug: print '<connection to %s:%d is closed>' % self.server


    #--------------------------------------------------------------------------
    # functions for sensory information update.
    #--------------------------------------------------------------------------

    def __update_thread(self):
        """
	update sensory information (internal use only).
	"""
	if self.debug: print '<started a thread updating sensory information>'
	while self.__update_flag:
	    self.update()
	    time.sleep(1.0 / self.__update_speed)
	if self.debug: print '<stop the update thread>'


    def start_update(self, speed=20):
        """
	start to update sensory information continuously.
	"""
	self.__update_flag = 1
	self.__update_speed = speed
	thread.start_new_thread(self.__update_thread, ())


    def stop_update(self):
        """
	stop updating sensory information continuously.
	"""
	self.__update_flag = 0


    def update(self):
        """
	update sensory information.
	"""
	try:
	    # for synchronization with other functions
	    self.lock.acquire()

	    # update information
	    while 1:
	        # read a packet
	        packet = self.__recv_packet()
		if packet == None: break
		(type, device, index), payload = packet

		# synchronization packet is not used at all.
		if type == synchronization:
		    continue

		# update information
		if device == 0x0001:		# player
		    print '<unexpected packet (%s:%d)>' % (devicestr[device], index)
		elif device == 0x0002:		# power
		    self.power[index] = unpack_power_data(payload)
		elif device == 0x0003:		# gripper
		    self.gripper[index] = unpack_gripper_data(payload)
		elif device == 0x0004:		# position
		    self.position[index] = unpack_position_data(payload)
		elif device == 0x0005:		# sonar
		    self.sonar[index] = unpack_sonar_data(payload)
		elif device == 0x0006:		# laser
		    self.laser[index] = unpack_laser_data(payload)
		elif device == 0x0007:		# blobfinder
		    self.blobfinder[index] = unpack_blobfinder_data(payload)
		elif device == 0x0008:		# ptz
		    self.ptz[index] = unpack_ptz_data(payload)
		elif device == 0x0009:		# audio
		    self.audio[index] = unpack_audio_data(payload)
		elif device == 0x000A:		# fiducial
		    self.fiducial[index] = unpack_fiducial_data(payload)
		elif device == 0x000B:		# comms
		    self.comms[index] = unpack_comms_data(payload)[0]
		elif device == 0x000C:		# speech
		    print '<speech device is not supposed to send data back>'
		elif device == 0x000D:		# gps
		    self.gps[index] = unpack_gps_data(payload)
		elif device == 0x000E:		# bumper
		    self.bumper[index] = unpack_bumper_data(payload)
		elif device == 0x000F:		# truth
		    self.truth[index] = unpack_truth_data(payload)
		elif device == 0x0010:		# idarturret
		    print '<idarturret device has not been implemented>'
		    #self.idarturret[index] = unpack_idarturret_data(payload)
		elif device == 0x0011:		# idar
		    print '<idar device has not been implemented>'
		    #self.idar[index] = unpack_idar_data(payload)
		elif device == 0x0012:		# descartes
		    print '<descartes device does not exist anymore>'
		elif device == 0x0013:		# mote
		    self.mote[index] = unpack_mote_data(payload)
		elif device == 0x0014:		# dio
		    self.dio[index] = unpack_dio_data(payload)
		elif device == 0x0015:		# aio
		    self.aio[index] = unpack_aio_data(payload)
		elif device == 0x0016:		# ir
		    self.ir[index] = unpack_ir_data(payload)
		elif device == 0x0017:		# wifi
		    self.wifi[index] = unpack_wifi_data(payload)
		elif device == 0x0018:		# waveform
		    self.waveform[index] = unpack_waveform_data(payload)
		elif device == 0x0019:		# localization
		    self.localization[index] = unpack_localization_data(payload)
		elif device == 0x001A:		# bps
		    print 'bps device is broken in v1.3'
		#    self.bps[index] = unpack_bps_data(payload)
		else:				# unknown device
		    print '<unknown device (%d:%d:%d) packet>' % (type, device, index)

	except socket.error:
	    # for synchronization with other functions
	    self.lock.release()
	    raise 'network connection error: (%s, %d)' % (device, index)

	else:
	    # for synchronization with other functions
	    self.lock.release()


    #--------------------------------------------------------------------------
    # common functions for all devices (internal use only).
    #--------------------------------------------------------------------------

    def __repr__(self):
        """
	convert itself to a string.
	"""
	return 'player client connected to %s:%d' % self.server


    def __wait_recv(self, size):
        """
	receive the specified number of bytes from the server.
	if data is not available yet, wait forever.
	"""
	recv_str = ''
	while len(recv_str) < size:
	    try:
		recv_str += self.__socket.recv(size - len(recv_str))
	    except socket.error:
	        time.sleep(0.01)	# wait more data
	return recv_str


    def __wait_packet(self):
        """
	receive a packet, which is a minimal, meaningful data chunk.
	if a packet is not available yet, wait forever.
	"""
	# receive header
	header = self.__wait_recv(32)
	hdrinfo, t_time, ts_time, size = unpack_header(header)
	# receive payload
	payload = self.__wait_recv(size)
	# return only useful data
	return (hdrinfo, payload)


    def __wait_response(self, device):
        """
	wait a response from the player server.
	ignore all irrelevant packets until it gets response from the server.
	"""
	# wait the right response
	while 1:
	    header, payload = self.__wait_packet()
	    if (header[0]==acknowledgement or header[0]==nacknowledgement or header[0]==error) \
	            and header[1]==devicenum[device[0]] and header[2]==device[1]:
	        break
	# return the payload
	return (header[0], payload)


    def __nsend(self, data):
        """
	send the data string to the server.
	caller should catch exceptions for proper error handling,
	i.e. broken pipe.
	"""
        if self.debug: print "__nsend data: len =", len(data)
	sent = 0
	while sent < len(data):
	    sent += self.__socket.send(data[sent:])


    def __nrecv(self, size):
        """
	receive the specified number of bytes from the server.
	caller should catch exceptions for proper error handling
	"""
	recv_str = ''
	while len(recv_str) < size:
	    try:
		recv_str += self.__socket.recv(size - len(recv_str))
	    except socket.error, (errno, errstr):
	        if errno == 11 and recv_str == '':
		    return None	# network link is fine, but data is not ready
		else:
		    raise	# network link got broken
	return recv_str


    def __recv_packet(self):
        """
	receive a packet, which is a minimal, meaningful data chunk.
	caller should catch exceptions for proper error handling
	"""
	# receive header
	header = self.__nrecv(32)
	if header == None: return None		# no data is available yet
	hdrinfo, t_time, ts_time, size = unpack_header(header)
	# receive payload
	payload = self.__wait_recv(size)
	# return only useful data
	return (hdrinfo, payload)


    #--------------------------------------------------------------------------
    # functions for debugging.
    #--------------------------------------------------------------------------

    def turnon_debug(self):
        """
	show debugging information on the screen.
	"""
	self.debug = 1


    def turnoff_debug(self):
        """
	do not show debugging information on the screen.
	"""
	self.debug = None


    def dump_sensors(self): #--------------------------------------------------
        """
	print sensory information on the screen.
	"""
	print self.power
	print self.gripper	
	print self.position
	print self.sonar
	print self.laser
	print self.blobfinder
	print self.ptz
	print self.audio
	print self.fiducial
	print self.comms
	#print self.speech		# no data for speech device
	print self.gps
	print self.bumper
	print self.truth
	#print self.idarturret		# not implemented yet
	#print self.idar		# not implemented yet
	#print self.descartes		# not exist anymore
	print self.mote
	print self.dio
	print self.aio
	print self.ir
	print self.wifi
	print self.waveform
	print self.localization
	#print self.bps			# bps device is broken


    #--------------------------------------------------------------------------
    # interfaces for the 'player' device.
    #--------------------------------------------------------------------------

    def get_device_list(self):
        """
	get the list of available devices from the server.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=388)
	    payload = pack_player_devlist()
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    type, payload = self.__wait_response(('player', 0))
	    if self.debug: print '<received one round of data>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot retrieve the device list'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_player_devlist(payload)


    def get_driver_name(self, device, index=0, port=6665):
        """
	get the driver name for a particular device.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=72)
	    payload = pack_player_driverinfo(device, index, port)
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    type, payload = self.__wait_response(('player', 0))
	    if self.debug: print '<received one round of data>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot retrieve the driver name'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_player_driverinfo(payload)


    def start(self, device, index=0, access='a'):
        """
	send a request to access device.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=7)
	    payload = pack_player_request(device, index, access)
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    type, payload = self.__wait_response(('player', 0))
	    access, drivername = unpack_player_request(payload)
	    if access == 'e':
		raise 'device request error: (%s, %d)' % (device, index)
	    else:
	        if self.debug: print '<device %s:%d is enabled>' \
					% (device, index)

	    # insert default values
	    # otherwise, 'KeyError' excpetion is thrown sometimes
	    if device=='power': self.power[index] = 0
	    elif device=='gripper': self.gripper[index] = (0,0)
	    elif device=='position': self.position[index] = ((0,0,0),(0,0,0),0)
	    elif device=='sonar': self.sonar[index] = ()
	    elif device=='laser': self.laser[index] = ((0,0,0),(),())
	    elif device=='blobfinder': self.blobfinder[index] = \
	    		((),(),(),(),(),(),(),(),(),(),(),(),(),(),(),(),
			 (),(),(),(),(),(),(),(),(),(),(),(),(),(),(),())
	    elif device=='ptz': self.ptz[index] = (0,0,0,0,0) # Player 1.5
	    elif device=='audio': self.audio[index] = (0,0,0,0,0,0,0,0,0,0)
	    elif device=='fiducial': self.fiducial[index] = ()
	    elif device=='comms': self.comms[index] = ''
	    #elif device=='speech': self.speech[index]=		# no data
	    elif device=='gps': self.gps[index] = (0,0,0)
	    elif device=='bumper': self.bumper[index] = ()
	    elif device=='truth': self.truth[index] = (0,0,0)
	    #elif device=='idarturret': self.idarturret[index]=	# not implemented
	    #elif device=='idar': self.idar[index]=		# not implemented
	    #elif device=='descartes': self.descartes[index]= 	# not exist
	    elif device=='mote': self.mote[index] = ''
	    elif device=='dio': self.dio[index] = ()
	    elif device=='aio': self.aio[index] = ()
	    elif device=='ir': self.ir[index] = ((),())
	    elif device=='wifi': self.wifi[index] = ()
	    elif device=='waveform': self.waveform[index] = (0,0,0,'')
	    elif device=='localization':
	    	self.localization[index] = ((0,0,0),
					    ((1,0,0),
					     (0,1,0),
					     (0,0,1)),
					    0.0)
	    #elif device=='bps': self.bps[index]=		# broken

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise

	else:
	    # re-start the update thread
	    self.lock.release()
	    return drivername


    def stop(self, device, index=0):
        """
	send a request to close a device.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=7)
	    payload = pack_player_request(device, index, 'c')
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    type, payload = self.__wait_response(('player', 0))
	    access, drivername = unpack_player_request(payload)
	    if access == 'e':
	        raise 'cannot stop the device (%s, %d)' % (device, index)
	    else:
	        if self.debug: print '<device %s:%d is disabled>' % (device, index)

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'device close error: (%s, %d)' % (device, index)

	else:
	    # re-start the update thread
	    self.lock.release()


    def fetch_data(self):
        """
	request a single round of data when the server is in a pull mode.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=2)
	    payload = pack_player_data()
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    self.__wait_response(('player', 0))
	    if self.debug: print '<received one round of data>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot fetch data'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_mode(self, mode='push new'):
        """
	change a data mode.

	there are four different modes currently:

	    - 'push all' : at a fixed frequency, send data from every
	                   currently subscribed device.
	    - 'pull all' : on client request, send data from every
	                   currently subscribed device.
	    - 'push new' : at a fixed frequency, send data only from
	                   those currently subscribed devices that
			   have generated new data.
	    - 'pull new' : on client request, send data only from
	                   those currently subscribed devices that
			   have generated new data.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # decide the mode number
	    if mode == 'push all': mode_number = 0x00
	    elif mode == 'pull all': mode_number = 0x01
	    elif mode == 'push new': mode_number = 0x02
	    elif mode == 'pull new': mode_number = 0x03
	    else: raise 'error'

	    # send request
	    header = pack_header(request, 'player', size=3)
	    payload = pack_player_datamode(mode_number)
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    self.__wait_response(('player', 0))
	    if self.debug: print '<player is in "%s" mode>' % mode

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot change to the data mode (%s)' % mode

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_frequency(self, frequency):
        """
	change data feeding frequency.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=4)
	    payload = pack_player_datafreq(frequency)
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    self.__wait_response(('player', 0))
	    if self.debug: print '<data frequency is %dHz now>' % frequency

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set to the data frequency (%d)' % frequency

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_auth_key(self, key):
        """
	send a key string for authentication.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'player', size=2+len(key))
	    payload = pack_player_auth(key)
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    self.__wait_response(('player', 0))
	    if self.debug: print '<the authentication key has been sent>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot send the authentication key (%s)' % key

	else:
	    # re-start the update thread
	    self.lock.release()


    #--------------------------------------------------------------------------
    # interfaces for the 'power' device.
    #--------------------------------------------------------------------------

    def get_main_power(self):
        """
	request the power data.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'power', size=1)
	    payload = pack_power_main()
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    type, payload = self.__wait_response(('power', 0))
	    if self.debug: print '<the request of power config has been sent>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot send the request of power config'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_power_main(payload)


    #--------------------------------------------------------------------------
    # interfaces for the 'gripper' device.
    #--------------------------------------------------------------------------

    def __gripper_command(self, gripcommand, press=1, carry=1, gripindex=0):
	"""
	send a gripper command to the player server (internal use only).
	"""
	try:
	    # send the command
	    header = pack_header(command, 'gripper', gripindex, size=2)
	    if command == gripper_command['press']:
		payload = pack_gripper_command(gripcommand, press)
	    elif command == gripper_command['carry']:
		payload = pack_gripper_command(gripcommand, carry)
	    else:
		payload = pack_gripper_command(gripcommand, 0)
	    self.__nsend(header+payload)
	    # NO RESPONSE
	    if self.debug: print '<sent the command (%s)>' % gripcommand
	except:
	    raise 'cannot send the command (%s)' % gripcommand


    def gripper_open(self, index=0):
        """
	send the 'open' gripper command to the player server.
	"""
	self.__gripper_command('open', gripindex=index)


    def gripper_close(self, index=0):
        """
	send the 'close' gripper command to the player server.
	"""
	self.__gripper_command('close', gripindex=index)


    def gripper_stop(self, index=0):
        """
	send the 'stop' gripper command to the player server.
	"""
	self.__gripper_command('stop', gripindex=index)


    def gripper_up(self, index=0):
        """
	send the 'up' gripper command to the player server.
	"""
	self.__gripper_command('up', gripindex=index)


    def gripper_down(self, index=0):
        """
	send the 'down' gripper command to the player server.
	"""
	self.__gripper_command('down', gripindex=index)


    def gripper_stay(self, index=0):
        """
	send the 'stay' gripper command to the player server.
	"""
	self.__gripper_command('stay', gripindex=index)


    def gripper_store(self, index=0):
        """
	send the 'store' gripper command to the player server.
	"""
	self.__gripper_command('store', gripindex=index)


    def gripper_deploy(self, index=0):
        """
	send the 'deploy' gripper command to the player server.
	"""
	self.__gripper_command('deploy', gripindex=index)


    def gripper_halt(self, index=0):
        """
	send the 'halt' gripper command to the player server.
	"""
	self.__gripper_command('halt', gripindex=index)


    def gripper_press(self, press_time=1, index=0):
        """
	send the 'press' gripper command to the player server.
	"""
	self.__gripper_command('press', press=press_time, gripindex=index)


    def gripper_carry(self, carry_time=1, index=0):
        """
	send the 'carry' gripper command to the player server.
	"""
	self.__gripper_command('carry', carry=carry_time, gripindex=index)


    def is_paddles_open(self, index=0):
        """
	check if paddles are open.
	"""
	return self.gripper[index][0] & 0x01


    def is_paddles_closed(self, index=0):
        """
	check if paddles are closed.
	"""
	return self.gripper[index][0] & 0x02


    def is_paddles_moving(self, index=0):
        """
	check if paddles are moving.
	"""
	return self.gripper[index][0] & 0x04


    def is_paddles_error(self, index=0):
        """
	check if there is an error related to paddles.
	"""
	return self.gripper[index][0] & 0x08


    def is_lift_up(self, index=0):
        """
	check if a lift is in up position.
	"""
	return self.gripper[index][0] & 0x10


    def is_lift_down(self, index=0):
        """
	check if a lift is in down position.
	"""
	return self.gripper[index][0] & 0x20


    def is_lift_moving(self, index=0):
        """
	check if a lift is moving.
	"""
	return self.gripper[index][0] & 0x40


    def is_lift_error(self, index=0):
        """
	check if there is an error related to a lift.
	"""
	return self.gripper[index][0] & 0x80


    def is_glimit_reached(self, index=0):
        """
	check if the gripper limit is reached.
	"""
	return self.gripper[index][1] & 0x01


    def is_llimit_reached(self, index=0):
        """
	check if the gripper limit is reached.
	"""
	return self.gripper[index][1] & 0x02


    def is_obeam_obstructed(self, index=0):
        """
	check if the outer beam is obstructed.
	"""
	return self.gripper[index][1] & 0x04


    def is_ibeam_obstructed(self, index=0):
        """
	check if the inner beam is obstructed.
	"""
	return self.gripper[index][1] & 0x08


    def is_lpaddle_open(self, index=0):
        """
	check if the inner beam is obstructed.
	"""
	return self.gripper[index][1] & 0x10


    def is_rpaddle_open(self, index=0):
        """
	check if the inner beam is obstructed.
	"""
	return self.gripper[index][1] & 0x20


    #--------------------------------------------------------------------------
    # interfaces for the 'position' device.
    #--------------------------------------------------------------------------

    def set_position(self, xpos=None, ypos=None, yawpos=None,
    			   xspeed=None, yspeed=None, yawspeed=None, index=0):
        """
	set a new position and a new speed. If a new value is None, the current
	sensor value will be used.
	"""
	try:
	    # set proper position and speed
	    #if xpos is None: xpos = self.position[index][0][0]
	    #if ypos is None: ypos = self.position[index][0][1]
	    #if yawpos is None: yawpos = self.position[index][0][2]
	    #if xspeed is None: xspeed = self.position[index][1][0]
	    #if yspeed is None: yspeed = self.position[index][1][1]
	    #if yawspeed is None: yawspeed = self.position[index][1][2]
	    if xpos is None: xpos = self.lastPosition['xpos']
	    if ypos is None: ypos = self.lastPosition['ypos']
	    if yawpos is None: yawpos = self.lastPosition['yawspeed']
	    if xspeed is None: xspeed = self.lastPosition['xspeed']
	    if yspeed is None: yspeed = self.lastPosition['yspeed']
	    if yawspeed is None: yawspeed = self.lastPosition['yawspeed']
	    # send command
# Player 1.5
	    header = pack_header(command, 'position', index, size=26) #24
# Player 1.5
	    payload = pack_position_command(xpos, ypos, yawpos,
	    				    xspeed, yspeed, yawspeed)
            self.lastPosition['xpos'] = xpos
	    self.lastPosition['ypos'] = ypos
	    self.lastPosition['yawspeed'] = xspeed
	    self.lastPosition['xspeed'] = xspeed
	    self.lastPosition['yspeed'] = yspeed
	    self.lastPosition['yawspeed'] = yawspeed
	    self.__nsend(header+payload)
	    # NO RESPONSE
	    if self.debug: print '<set the position and speed to (%d,%d,%d) and (%d,%d,%d)>' \
			    % (xpos, ypos, yawpos, xspeed, yspeed, yawspeed)

	except:
	    raise 'cannot set a position and a speed'


    def set_speed(self, xspeed=None, yspeed=None, yawspeed=None,
    			xpos=None, ypos=None, yawpos=None, index=0):
	"""
	change the speed and the position. If a new value is None, the current
	sensor value will be used.
	"""
        if self.debug:
            print "set_speed", (xspeed, yspeed, yawspeed, xpos, ypos, yawpos)
            print "position[%d]" % index, self.position[index]
	try:
	    # set proper position and speed
	    #if xspeed is None: xspeed = self.position[index][1][0]
	    #if yspeed is None: yspeed = self.position[index][1][1]
	    #if yawspeed is None: yawspeed = self.position[index][1][2]
	    #if xpos is None: xpos = self.position[index][0][0]
	    #if ypos is None: ypos = self.position[index][0][1]
	    #if yawpos is None: yawpos = self.position[index][0][2]
	    if xpos is None: xpos = self.lastPosition['xpos']
	    if ypos is None: ypos = self.lastPosition['ypos']
	    if yawpos is None: yawpos = self.lastPosition['yawspeed']
	    if xspeed is None: xspeed = self.lastPosition['xspeed']
	    if yspeed is None: yspeed = self.lastPosition['yspeed']
	    if yawspeed is None: yawspeed = self.lastPosition['yawspeed']
	    # send command
# Player 1.5
	    header = pack_header(command, 'position', index, size=26) # 24
# Player 1.5
	    payload = pack_position_command(xpos, ypos, yawpos,
	    				    xspeed, yspeed, yawspeed)
            self.lastPosition['xpos'] = xpos
	    self.lastPosition['ypos'] = ypos
	    self.lastPosition['yawspeed'] = xspeed
	    self.lastPosition['xspeed'] = xspeed
	    self.lastPosition['yspeed'] = yspeed
	    self.lastPosition['yawspeed'] = yawspeed
	    if self.debug: print '<set the speed and position to (%d,%d,%d) and (%d,%d,%d)>' \
			    % (xspeed, yspeed, yawspeed, xpos, ypos, yawpos)
	    self.__nsend(header+payload)
	    # NO RESPONSE
	except:
	    raise 'robot/driver/player cannot set speed and/or position!'


    def get_position_geometry(self):
        """
	request robot geomery.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()

	    # send request
	    header = pack_header(request, 'position', size=11)
	    payload = pack_position_geom()
	    self.__nsend(header+payload)

	    # wait a respose from the player server
	    type, payload = self.__wait_response(('position', 0))
	    if self.debug: print '<the request of position geomery has been sent>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot send the request of position geomery'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_position_geom(payload)


    def turnon_motors(self):
        """
	turn motors on.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=2)
	    payload = pack_position_motorpower(1)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<turned on the motors>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot turn on the motors'

	else:
	    # re-start the update thread
	    self.lock.release()


    def turnoff_motors(self):
        """
	turn motors off.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=2)
	    payload = pack_position_motorpower(0)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<turned off the motors>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot turn off the motors'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_velocity_control(self, mode='default'):
        """
	set velocity control mode.

	there are four different modes currently:

	    - 'default'  : take the system default mode.
	                   ('separate' for P2OS and 'pd' for REB)
	    - 'direct'   : direct wheel control
	    - 'separate' : separate translational and rotational control
	    - 'pd'       : velocity-based heading PD control	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=2)
	    if mode=='default' or mode=='separate' or mode=='pd':
		vc = 1
	    elif mode=='direct':
		vc = 0
	    else:
	        raise 'invlalid control mode (%s)' % mode
	    payload = pack_position_velocitymode(vc)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<set the velocity control to "%s">' % mode

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the velocity control'

	else:
	    # re-start the update thread
	    self.lock.release()


    def reset_odometry(self): #------------------------------------------------
	"""
	reset odometry information to (0,0,0).
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=1)
	    payload = pack_position_reset()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<reset the odometry>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot reset the odometry'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_position_control(self, mode='velocity'):
        """
	set position control mode.

	there are two different modes currently:

	    - 'velocity' : receive velocity commands
	    - 'position' : receive position commands
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=2)
	    if mode=='velocity': pc = 0
	    elif mode=='position': pc = 1
	    else: raise 'invlalid control mode (%s)' % mode
	    payload = pack_position_positionmode(pc)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<set the position control to "%s">' % mode

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the position control'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_pid_velocity(self, kp, ki, kd):
        """
	set the PID parameters for velocity control.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=13)
	    payload = pack_position_speedpid(kp, ki, kd)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<set the PID parameters for velocity control>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the PID parameters for velocity control'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_pid_position(self, kp, ki, kd):
        """
	set the PID parameters for position control.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=13)
	    payload = pack_position_positionpid(kp, ki, kd)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<set the PID parameters for position control>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the PID parameters for position control'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_speed_profile(self, max_speed, max_acc):
        """
	set the maximum speed and acceleration.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'position', size=5)
	    payload = pack_position_speedprof(max_speed, max_acc)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<set the speed profile>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the speed profile'

	else:
	    # re-start the update thread
	    self.lock.release()


    def set_odometry(self, x, y, theta):
        """
	set the robot's odometry to a particular state.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
# Player 1.5
	    header = pack_header(request, 'position', size=13)
# Player 1.5
	    payload = pack_position_setodom(x, y, theta)
            if self.debug: print "set_odometry: payload len =", len(payload)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('position', 0))
	    if self.debug: print '<set the robot odometry>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the robot odometry'

	else:
	    # re-start the update thread
	    self.lock.release()


    #--------------------------------------------------------------------------
    # interfaces for the 'sonar' device.
    #--------------------------------------------------------------------------

    def get_sonar_geometry(self):
        """
	read the current geometry information of sonar sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'sonar', size=1)
	    payload = pack_sonar_geom()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('sonar', 0))
	    if self.debug: print '<read the sonar geometry>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the sonar geometry'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_sonar_geom(payload)


    def turnon_sonar(self):
        """
	turon on sonar transducers.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'sonar', size=2)
	    payload = pack_sonar_power(1)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('sonar', 0))
	    if self.debug: print '<turned on the sonar transducers>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot turn on the sonar transducers'

	else:
	    # re-start the update thread
	    self.lock.release()


    def turnoff_sonar(self):
        """
	turon off sonar transducers.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'sonar', size=2)
	    payload = pack_sonar_power(0)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('sonar', 0))
	    if self.debug: print '<turned off the sonar transducers>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot turn off the sonar transducers'

	else:
	    # re-start the update thread
	    self.lock.release()


    #--------------------------------------------------------------------------
    # interfaces for the 'laser' device.
    #--------------------------------------------------------------------------

    def get_laser_geometry(self):
        """
	read the geometry information of laser sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'laser', size=1)
	    payload = pack_laser_geom()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('laser', 0))
	    if self.debug: print '<read the laser configuration>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the laser configuration'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_laser_geom(payload)


    def set_laser_config(self, min=-90.0, max=90.0, resolution=0.5, intensity=1):
        """
	change the configuration of laser sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'laser', size=8)
	    payload = pack_laser_setconfig(min, max, resolution, intensity)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('laser', 0))
	    if self.debug: print '<changed the laser configuration>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot change the laser configuration'

	else:
	    # re-start the update thread
	    self.lock.release()


    def get_laser_config(self):
        """
	read the current configuration of laser sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'laser', size=1)
	    payload = pack_laser_getconfig()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('laser', 0))
	    if self.debug: print '<read the laser configuration>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the laser configuration'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_laser_getconfig(payload)


    #--------------------------------------------------------------------------
    # interfaces for the 'blobfinder' device.
    #--------------------------------------------------------------------------

    # no command or request in run-time for this sensor.


    #--------------------------------------------------------------------------
    # interfaces for the 'ptz' device.
    #--------------------------------------------------------------------------

    def set_ptz(self, pan, tilt, zoom, panspeed = 0, tiltspeed = 0):
        """
	move a camera.
	"""
	try:
	    # send command
	    header = pack_header(command, 'ptz', size=10)
	    payload = pack_ptz_command(pan, tilt, zoom, panspeed, tiltspeed)
	    self.__nsend(header+payload)
	    # NO RESPONSE
	    if self.debug: print '<sent a ptz command>'

	except:
	    raise 'cannot send a ptz command'


    #--------------------------------------------------------------------------
    # interfaces for the 'audio' device.
    #--------------------------------------------------------------------------

    def beep(self, frequency=1000, amplitude=300, duration=1):
        """
	play a beep sound.
	"""
	try:
	    # send command
	    header = pack_header(command, 'audio', size=6)
	    payload = pack_audio_command(frequency, amplitude, duration)
	    self.__nsend(header+payload)
	    # NO RESPONSE
	    if self.debug: print '<sent a beep command>'

	except:
	    raise 'cannot send a beep command'


    #--------------------------------------------------------------------------
    # interfaces for the 'fiducial' device.
    #--------------------------------------------------------------------------

    def get_fiducial_geometry(self):
        """
	read the geometry of fiducial sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'fiducial', size=1)
	    payload = pack_fiducial_getgeom()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('fiducial', 0))
	    if self.debug: print '<read the fiducial geometry>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the fiducial geometry'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_fiducial_getgeom(payload)


    #--------------------------------------------------------------------------
    # interfaces for the 'comms' device.
    #--------------------------------------------------------------------------

    def send_message(self, message): #-----------------------------------------
        """
	send a message over the wireless network.
	"""
	try:
	    # send request
	    header = pack_header(command, 'comms', size=len(message))
	    payload = pack_comms_command(message)
	    self.__nsend(header+payload)
	    # NO RESPONSE
	    if self.debug: print '<sent the message>'

	except:
	    raise 'cannot send the message'


    #--------------------------------------------------------------------------
    # interfaces for the 'speech' device.
    #--------------------------------------------------------------------------

    def speak(self, message): #------------------------------------------------
        """
	speak the message.
	"""
	try:
	    # send command
	    header = pack_header(command, 'speech', size=256)
	    payload = pack_speech_command(message)
	    self.__nsend(header+payload)
	    # NO RESPONSE
	    if self.debug: print '<sent a speech command>'

	except:
	    raise 'cannot send a speech command'


    #--------------------------------------------------------------------------
    # interfaces for the 'gps' device.
    #--------------------------------------------------------------------------

    # no command or request in run-time for this sensor.


    #--------------------------------------------------------------------------
    # interfaces for the 'bumper' device.
    #--------------------------------------------------------------------------

    def get_bumper_geometry(self):
        """
	read the geometry of bumper sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'bumper', size=1)
	    payload = pack_bumper_getgeom()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('bumper', 0))
	    if self.debug: print '<read the bumper geometry>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the bumper geometry'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_bumper_getgeom(payload)


    #--------------------------------------------------------------------------
    # interfaces for the 'truth' device.
    #--------------------------------------------------------------------------

    def get_truth_pose(self):
        """
	read the pose of truth sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'truth', size=1)
	    payload = pack_truth_getpose()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('truth', 0))
	    if self.debug: print '<read the truth pose>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the truth pose'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_truth_getpose(payload)


    def set_truth_pose(self, px, py, pa):
        """
	set the pose of truth sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'truth', size=13)
	    payload = pack_truth_setpose(px, py, pa)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('truth', 0))
	    if self.debug: print '<set the truth pose>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot set the truth pose'

	else:
	    # re-start the update thread
	    self.lock.release()


    #--------------------------------------------------------------------------
    # interfaces for the 'idarturret' device.
    #--------------------------------------------------------------------------

    # TODO: not supported yet.


    #--------------------------------------------------------------------------
    # interfaces for the 'idar' device.
    #--------------------------------------------------------------------------

    # TODO: not supported yet.


    #--------------------------------------------------------------------------
    # interfaces for the 'descartes' device.
    #--------------------------------------------------------------------------

    # This device does not exist anymore.


    #--------------------------------------------------------------------------
    # interfaces for the 'mote' device.
    #--------------------------------------------------------------------------

    def set_transmission_power(strength):
        """
	change the transmission power setting.
        """
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'mote', size=1)
	    payload = pack_mote_config(strength)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('mote', 0))
	    if self.debug: print '<changed the transmission power setting>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot change the transmission power setting'

	else:
	    # re-start the update thread
	    self.lock.release()


    #--------------------------------------------------------------------------
    # interfaces for the 'dio' device.
    #--------------------------------------------------------------------------

    # no command or request in run-time for this sensor.


    #--------------------------------------------------------------------------
    # interfaces for the 'aio' device.
    #--------------------------------------------------------------------------

    # no command or request in run-time for this sensor.


    #--------------------------------------------------------------------------
    # interfaces for the 'ir' device.
    #--------------------------------------------------------------------------

    def get_ir_pose(self):
        """
	read the current poses information of ir sensors.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'ir', size=1)
	    payload = pack_ir_getpose()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('ir', 0))
	    if self.debug: print '<read the ir poses>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the ir poses'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_ir_getpose(payload)


    def turnon_ir(self):
        """
	turon on ir sensors.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'ir', size=2)
	    payload = pack_ir_power(1)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('ir', 0))
	    if self.debug: print '<turned on the ir sensors>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot turn on the ir sensors'

	else:
	    # re-start the update thread
	    self.lock.release()


    def turnoff_ir(self):
        """
	turon off ir sensors.
	
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'ir', size=2)
	    payload = pack_ir_power(0)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('ir', 0))
	    if self.debug: print '<turned off the ir sensors>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot turn off the ir sensors'

	else:
	    # re-start the update thread
	    self.lock.release()


    #--------------------------------------------------------------------------
    # interfaces for the 'wifi' device.
    #--------------------------------------------------------------------------

    # no command or request in run-time for this sensor.


    #--------------------------------------------------------------------------
    # interfaces for the 'waveform' device.
    #--------------------------------------------------------------------------

    # no command or request in run-time for this sensor.


    #--------------------------------------------------------------------------
    # interfaces for the 'localization' device.
    #--------------------------------------------------------------------------

    def reset_localization(self):
        """
	re-initialize a localization algorithm.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'localization', size=1)
	    payload = pack_localization_reset()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('localization', 0))
	    if self.debug: print '<re-initialized a localization algorithm>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot re-initialize a localization algorithm'

	else:
	    # re-start the update thread
	    self.lock.release()


    def get_localization_config(self):
        """
	read the configuration of the localization device.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'localization', size=1)
	    payload = pack_localization_getconfig()
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('localization', 0))
	    if self.debug:
	        print '<read the configuration of a localization device>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the configuration of a localization device'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_localization_getconfig(payload)


    def set_localization_config(self, num_particles):
        """
	change the configuration of the localization device.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'localization', size=5)
	    payload = pack_localization_setconfig(num_particles)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    self.__wait_response(('localization', 0))
	    if self.debug:
	        print '<changed the configuration of a localization device>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot change the configuration of a localization device'

	else:
	    # re-start the update thread
	    self.lock.release()


    def get_map_size(self, scale=1):
        """
	read the size of the map being used by a localization device.
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'localization', size=2)
	    payload = pack_localization_getmaphdr(scale)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('localization', 0))
	    if self.debug:
	        print '<read the size of a map>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read the size of a map'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_localization_getmaphdr(payload)


    def __get_map_data(self, scale, row):
        """
	read particl map starting from the specified row.
	(internal use only)
	"""
	try:
	    # stop the update thread
	    self.lock.acquire()
	    # send request
	    header = pack_header(request, 'localization', size=4)
	    payload = pack_localization_getmapdata(scale, row)
	    self.__nsend(header+payload)
	    # wait a respose from the player server
	    type, payload = self.__wait_response(('localization', 0))
	    if self.debug:
	        print '<read particl map data>'

	except:
	    # re-start the update thread
	    self.lock.release()
	    raise 'cannot read partial map data'

	else:
	    # re-start the update thread
	    self.lock.release()
	    return unpack_localization_getmapdata(payload)


    def get_map_data(self, scale=1):
        """
	retrieve the scaled map data.
	"""
	#try:
	# retrieve the size information
	width, height, ppm = self.get_map_size(scale)
	# check if the scaled map is too big
	if width > 1020:		# 1020 = PLAYER_MAX_REQREP_SIZE-4
	    raise
	# compute the data amount we can retrieve once
	count = int(1020 / width)
	map_data = ''
	for row in range(0,height,count):
	    if row+count >= height: blocksize = width * (height - row)
	    else: blocksize = count * width
	    map_data += self.__get_map_data(scale,row)[:blocksize]

	#except:
	#    raise 'cannot retrieve map data'

	#else:
	return (width, height, map_data)


    #--------------------------------------------------------------------------
    # interfaces for the 'bps' device.
    #--------------------------------------------------------------------------

    # this device is broken in v1.3

#    def configure_bps(self):
#        """
#	change the configuration of BPS devices.
#	"""
#	print 'BPS configuration is not supported in Player v1.2 yet.'
#
#
#    def get_bps_configuration(self):
#        """
#	read the configuration of BPS devices.
#	"""
#	print 'BPS configuration is not supported in Player v1.2 yet.'
#
#
#    def add_laserbeacon(self, id, px, py, pa, ux, uy, ua):
#        """
#	add a piece of laserbeacon information.
#	"""
#	try:
#	    # stop the update thread
#	    self.lock.acquire()
#	    # send request
#	    header = pack_header(request, 'bps', size=26)
#	    payload = pack_bps_beacon(id, px, py, pa, ux, uy, ua)
#	    self.__nsend(header+payload)
#	    # wait a respose from the player server
#	    self.__wait_response(('bps', 0))
#	    if self.debug: print '<sent a bps laserbeacon request>'
#	except:
#	    # re-start the update thread
#	    self.lock.release()
#	    raise 'cannot send a bps laserbeacon request'
#	else:
#	    # re-start the update thread
#	    self.lock.release()
#
#
#    def get_bps_laserbeacon(self):
#        """
#	read the position of registered laserbeacons.
#	"""
#	print 'BPS query is not supported in Player v1.2 yet.'


    #--------------------------------------------------------------------------
    # utility functions for data retrieval.
    #--------------------------------------------------------------------------

    def __byte_to_reversed_tuple(self, byte):
        """
	convert a byte into a bit list (internal use only).
	"""
	result = []
	for idx in range(8):
	    result.append(byte & 0x01)
	    byte >>= 1
	return tuple(result)


    def get_power(self, index=0):
        """
	return the sensory value of a power device.
	"""
	return self.power[index]


    def get_gripper(self, index=0):
        """
	return the sensory value of a gripper device.
	"""
	state = self.__byte_to_reversed_tuple(self.gripper[index][0])
	beams = self.__byte_to_reversed_tuple(self.gripper[index][1])[:6]
	return (state, beams)


    def get_position(self, index=0):
        """
	return the sensory value of a position device.
	"""
	return self.position[index]


    def get_sonar(self, index=0):
        """
	return the sensory value of a sonar device.
	"""
	return self.sonar[index]


    def get_laser(self, index=0):
        """
	return the sensory value of a laser device.
	"""
	return self.laser[index]


    def get_blobfinder(self, index=0):
        """
	return the sensory value of a blobfinder device.
	"""
	return self.blobfinder[index]


    def get_ptz(self, index=0):
        """
	return the sensory value of a ptz device.
	"""
	return self.ptz[index]


    def get_audio(self, index=0):
        """
	return the sensory value of a audio device.
	"""
	return (self.audio[index][0:2], self.audio[index][2:4],
	        self.audio[index][4:6], self.audio[index][6:8],
	        self.audio[index][8:10])


    def get_fiducial(self, index=0):
        """
	return the sensory value of a fiducial device.
	"""
	return self.fiducial[index]


    def get_comms(self, index=0):
        """
	return the sensory value of a comms device.
	"""
	s = ''
	if self.comms[index] != '':
	    s = self.comms[index]
	    self.comms[index] = ''
	return s


    def get_gps(self, index=0):
        """
	return the sensory value of a gps device.
	"""
	return self.gps[index]


    def get_bumper(self, index=0):
        """
	return the sensory value of a bumper device.
	"""
	return self.bumper[index]


    def get_truth(self, index=0):
        """
	return the sensory value of a truth device.
	"""
	return self.truth[index]


    def get_idarturret(self, index=0):
        """
	return the sensory value of a idarturret device.
	"""
	print 'This device has not been implemented.'
	#return self.idarturret[index]


    def get_idar(self, index=0):
        """
	return the sensory value of a idar device.
	"""
	print 'This device has not been implemented.'
	#return self.idar[index]


    def get_descartes(self, index=0):
        """
	return the sensory value of a descartes device.
	"""
	print 'This device does not exist anymore.'


    def get_mote(self, index=0):
        """
	return the sensory value of a mote device.
	"""
	return self.mote[index]


    def get_dio(self, index=0):
        """
	return the sensory value of a dio device.
	"""
	return self.dio[index]


    def get_aio(self, index=0):
        """
	return the sensory value of a aio device.
	"""
	return self.aio[index]


    def get_ir(self, index=0):
        """
	return the sensory value of a ir device.
	"""
	return self.ir[index]


    def get_wifi(self, index=0):
        """
	return the sensory value of a wifi device.
	"""
	return self.wifi[index]


    def get_waveform(self, index=0):
        """
	return the sensory value of a waveform device.
	"""
	return self.waveform[index]


    def get_localization(self, index=0):
        """
	return the sensory value of a localization device.
	"""
	return self.localization[index]


    def get_bps(self, index=0):
        """
	return the sensory value of a bps device.
	"""
	print 'bps device is broken in v1.3'
#	return ( tuple(self.bps[index][0:3]),
#		 tuple(self.bps[index][3:6]),
#		 self.bps[index][6] )

