# daniel sproul, june 24, 2002

# psom is a python interface to csom.so, which is itself in turn a low-level
# python interface to the som-pak c library.

# this file implements the following classes:
#		psom
#		vector
#		dataset
#		point
#		activations



import csom
csom.set_globals()  # neither worry about nor change this



class psom:
	"""
	this is the big one, your basic som object
	in general, construct a psom, then initialize it, then map to/train it,
	periodically doing something with the information it produces.
	the devil is in the details:
	---------------------------
	data members of interest to a user:
	self.xdim  (x dimension of map)
	self.ydim  (y dimension of map)
	self.dim   (length of vectors)
	self.topol ('rect' or 'hexa')
	"""
	def __init__(self, xdim='unset', ydim='unset', topol='hexa', 
									neigh='gaussian', alpha_mode='linear', radius_mode='linear',
									rmin=0.0, rmax=1.0, data='unset', file='unset'):
		"""
		to read a som from a .cod file (the same file format as used in som_pak):
		>>> mysom = psom(file=filename)
		to create a som with model vectors evenly distributed in the space of
		a pre-existing data set:
		>>> mysom = psom(xdim,ydim,data=mydataset)
		to randomly initialize (this doesn't actually work yet)
		>>> mysom = psom(xdim,ydim) ...
		"""

		if(alpha_mode=='inverse_t'):
			alpha_mode = csom.INVERSE_T
		else:
			alpha_mode = csom.LINEAR
		if(radius_mode=='inverse_t'):
			radius_mode = csom.INVERSE_T
		else:
			radius_mode = csom.LINEAR
		
		if(file!='unset'):
			codes = csom.open_entries(file)
			self.params = csom.construct_teach_params(codes, alpha_mode, radius_mode)
		else:
			if(xdim=='unset' or ydim=='unset'):
				raise "please specify x and y dimensions for the map"
			if(topol=='rect'):
				topol=csom.TOPOL_RECT
			else:
				topol=csom.TOPOL_HEXA
			if(neigh=='bubble'):
				neigh=csom.NEIGH_BUBBLE
			else:
				neigh=csom.NEIGH_GAUSSIAN
			if(data!='unset'):
				codes = csom.randinit_codes(data.data,topol,neigh,xdim,ydim)
				self.params = csom.construct_teach_params(codes,alpha_mode,radius_mode)
			else:
				raise "random initialization mode not yet implemented.  sorry"

		self.xdim = csom.entries_xdim_get(codes)
		self.ydim = csom.entries_ydim_get(codes)
		self.dim = csom.entries_dimension_get(codes)
		if(csom.teach_params_topol_get(self.params) == csom.TOPOL_RECT):
			self.topol = 'rect'
		else:
			self.topol = 'hexa'
		self.last = 'unset'


	def init_training(self,alpha_0,radius_0,runlen,errorwindow=1):
		csom.init_training_session(self.params,alpha_0,radius_0,runlen,
																	errorwindow)
		"""
		a few notes about init_training():
		   runlen is the number of training samples you expect to use in the
		current training session.  this affects the rate at which alpha and radius
		decay.  by default, the decay of these is linear, such that after running
		runlen samples, alpha is zero and radius is 1.0.  so it is kind of important
		to set runlen appropriately.  also, both radius and alpha can be set
		to decay with an inverse time function (alpha_mode='inverse_t'...),
		which can sometimes be less drastic because then your alpha never
		actually ends up at zero, even if you exceed the expected runlen number
		of training samples.  you can also reinitialize a training session
		whenever you like (currently alpha_mode and radius_mode are set in stone
		when the psom is created, however)
 		  errorwindow is sort of an ad-hoc way of making the error value returned
		by get_error() time dependent on the last 'errorwindow' number of
		training samples.  the default is 1, which should just return the error
		associated with the most recent training sample

		training examples:
		>>> mysom.init_training(initial_alpha,initial_radius,run_length)
		then either:
		>>> mysom.train_from_dataset(mydataset)
		or:
		>>> model1 = mysom.train(vec1)
		>>> model2 = mysom.train(vec2)
		>>> ...
		there are straightforward timing functions available if you like that
		sort of thing.
		map() acts a lot like train() but will not actually adjust any map
		weights (equivalent to training with zero alpha)
		"""

	def timing_start(self):
		csom.timing_start(self.params)
	def timing_stop(self):
		csom.timing_stop(self.params)
	def get_training_time(self):
		return csom.get_training_time(self.params)
	
	def map(self,vector):
		coords = csom.map_one(self.params,vector.entry)
		pt = point(csom.ptrvalue(coords,0),csom.ptrvalue(coords,1))
		self.last = vector
		self.last.point = pt
		return self.get_model_vector(pt)
	def train(self,vector):
		coords = csom.train_one(self.params,vector.entry)
		pt = point(csom.ptrvalue(coords,0),csom.ptrvalue(coords,1))
		self.last = vector
		self.last.point = pt
		return self.get_model_vector(pt)
	def train_from_dataset(self,dataset,mode='cyclic'):
		if(mode=='rand'):
			mode = csom.RAND
		else:
			mode = csom.CYCLIC
		entry = csom.train_fromdataset(self.params,dataset.data,mode)
		self.last = vector(entry=entry,dim=self.dim)
		coords = csom.map_one(self.params,self.last.entry)
		pt = point(csom.ptrvalue(coords,0),csom.ptrvalue(coords,1))
		self.last.point = pt
	def get_model_vector(self,point):
		codes = csom.teach_params_codes_get(self.params)
		entry = csom.get_model_vector(codes, point.asIntPtr())
		dim = csom.entries_dimension_get(codes)
		return vector(entry=entry,dim=dim,point=point)

	def get_activations(self,mode='bubble',radius=1.0,
																		emin='unset',emax='unset'):
		"""
		looking at SRN activation levels:
		after calling map(), train(), or train_from_dataset(),
		calling get_activation_levels() returns an activations class instance
		corresponding to the appropriate activation levels.
		This can either be done based on simple bubble or gaussian neighborhoods,
		or (as suggested by doug) by assigning activation weight according to
		error in mapping to each corresponding model vector.  this can either be
		done with a dynamically calculated error window, or a user-defined
		error window.
		some examples:
		>>> mysom.train(myvec)
		>>> myact = mysom.get_activations('bubble',2.0)
		>>> myact = mysom.get_activations('gaussian',3.0)
		>>> myact = mysom.get_activations('error')
		>>> myact = mysom.get_activations('error',emin=0.0,emax=1.0)
		note that error values are always >= 0.0
		"""

		if(self.last == 'unset'):
			raise "get_activations(): som has not yet been mapped to"
		if(mode == 'gaussian' or mode == 'bubble'):
			if(mode == 'gaussian'): mode = csom.NEIGH_GAUSSIAN
			else: mode = csom.NEIGH_BUBBLE
			float_levels = csom.get_activation_levels(self.params,
						self.last.point.asIntPtr(), radius, mode)
		elif(mode == 'error'):
			if(emin == 'unset'):
				fptr = "NULL"
			else:
				fptr = csom.ptrcreate("float",0.0,2)
				csom.ptrset(fptr,emin,0)
				csom.ptrset(fptr,emax,1)
			float_levels = csom.get_levels_by_error(self.params,self.last.entry,fptr)
		else:
			raise "mode " + mode + " not yet implemented.  sorry"
		levels = arr_to_list(float_levels,self.xdim*self.ydim)
		return activations(self.xdim,self.ydim,levels,self.topol)

	def save_to_file(self, file):
		codes = csom.teach_params_codes_get(self.params)
		csom.write_entries(codes,file)
	
	def display(self):
		codes = csom.teach_params_codes_get(self.params)
		csom.print_dataset(codes)






class vector:
	"""
	used both for data and model vectors
	get_elts() and get() can be used to access the actual values of the entries
	in the vector.  the point data member should remain 'unset' for data
	vectors, but for model vectors represents its coordinates in the SOM
	"""

	def __init__(self, elts='unset', weight=1, mask='NULL', entry='unset',
										dim='unset', point='unset'):
		"""
		everything is pretty self-explanatory, except the constructor.
		typically all a user need worry about is doing something like
		>>> mylist = [1.0, 2.0, 3.0, ...]
		>>> myvec = vector(mylist)
		if you want to use masking or weighting, you can do that too
		the other constructor parameters are primarily for internal use
		"""

		if(elts != 'unset'):
			points = list_to_arr(elts, "float")
			dim = len(elts)
			if(mask != 'NULL'):
				mask = list_to_arr(mask, "short")
			entry = csom.make_data_entry_weighted_masked( \
																					points, weight, mask, dim)
		self.dim = dim
		self.entry = entry
		self.point = point

	def get_elts(self):
		points = csom.data_entry_points_get(self.entry)
		return arr_to_list(points,self.dim)
	def __getitem__(self, key):
		mylist = self.get_elts()
		return mylist[key]
	def __len__(self):
		return len(self.get_elts())
	def get_weight(self):
		return csom.data_entry_weight_get(self.entry)
	def get_mask(self):
		raise "get_mask() has not yet been implemented.  sorry"
	def get_label(self):
		raise "get_label() has not yet been implemented.  sorry"	

	def display(self):
		mylist = self.get_elts();
		weight = self.get_weight();
		print "[",
		for elt in mylist:
			print "%.3f" % (elt),
		if(weight > 1):
			print "] weight:", weight
		else:
			print "]" 



class dataset:
	"""
	a python front-end to the c library's wacky linked-list data set
	implementation.  can read and write to .dat files (same file format
	as specified in the som_pak documentation)
	keeps a pointer to the current position in the list, so you can
	call next() until the end of the list is reached, at which point you
	need to call rewind().  there is also a get() method, but this will
	interfere with the previous pointer (so if you call get(6) and then
	next(), next() will return the 7th vector in the list)
	addvec() adds a vector to the list, and also causes wacky pointer
	behavior (bad idea to try to traverse the list and add things to it at
	the same time)
	"""

	def __init__(self, init_vector='NULL', dim='unset', file='unset'):
		"""
		ways to use the constructor:
		to read in a data set from a file:
		>>> mydataset = dataset(file=filename)
		to build a data set by hand, first initialize it, either by dimension or
		with an initial vector:
		>>> mydataset = dataset(dim=4)
		or
		>>> mydataset = dataset(initial_vector)
		then just add vectors to it
		>>> mydataset.addvec(vec1)
		>>> mydataset.addvec(vec2)
		"""

		self.p = csom.get_eptr()
		if(file!='unset'):
			self.data = csom.open_entries(file)
			self.dim = csom.entries_dimension_get(self.data)
		else:
			if(init_vector!='NULL'):
				dim = init_vector.dim	
			self.data = csom.init_dataset(dim)
			if(init_vector!='NULL'):
				self.addvec(init_vector)
			self.dim = dim

	# this was giving me problems with python2.2's garbage collection
	# no idea why, but if you are creating a whole lot of datasets
	# with this commented out you might end up with a memory leak
	#def __del__(self):
	#	csom.close_entries(self.data)

	def addvec(self, vec):
		csom.addto_dataset(self.data, vec.entry)

	def rewind(self):
		entry = csom.rewind_entries(self.data, self.p)
		return vector(entry=entry,dim=self.dim)
	def next(self):
		entry = csom.next_entry(self.p)
		return vector(entry=entry,dim=self.dim)
	def get(self, index):
		if(index >= self.n_vectors()):
			raise "dataset.get(): index out of bounds"
		vec = self.rewind()
		i = 0
		while(i < index):
			vec = self.next()
			i = i+1
		return vec

	def load_from_file(self,file):
		csom.close_entries(self.data)
		self.data = csom.open_entries(file)
		self.dim = csom.entries_dimension_get(self.data)
	def save_to_file(self,file):
		csom.write_entries(self.data)

	def n_vectors(self):
		return csom.entries_num_entries_get(self.data)

	def display(self):
		csom.print_dataset(self.data)			




class activations:
	"""
	really just an elaborate float array when you think about it...
	most of the real work is done in psom.get_activations()
	in any case, this class is used to communicate SRN-appropriate activation
	levels of the som after each mapping
	"""
	def __init__(self, xdim, ydim, levels=[], topol='hexa'):
		self.xdim=xdim
		self.ydim=ydim
		self.levels=levels
		if(levels == []):
			for i in range(0,xdim*ydim):
				self.levels.append(0.0)
		self.topol=topol

	def get(self, x, y):
		index = x + y * self.xdim
		return levels[index]
	def __getitem__(self, key):
		return levels[key]
	def __len__(self):
		return len(levels)
	
	def display(self):
		for j in range(0,self.ydim):
			if(j % 2 == 1 and self.topol=='hexa'):
				print "  ",
			for i in range(0,self.xdim):
				index = i + j * self.xdim
				print "%.2f" % (self.levels[index]),
			print ""



class point:
	"""
	simple x,y coordinate holder
	"""
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def asIntPtr(self):
		ptr = csom.ptrcreate("int",0,2)
		csom.ptrset(ptr,self.x,0)
		csom.ptrset(ptr,self.y,1)
		return ptr
	def display(self):
		print "(%d,%d)" % (self.x,self.y)





def list_to_arr(mylist,type):
	"""
	functions to convert between python lists and c arrays/pointers
	users should not ever use these functions
	"""
	nitems = len(mylist)
	myarr = csom.ptrcreate(type,0,nitems)
	i = 0
	for item in mylist:
		csom.ptrset(myarr,item,i)
		i = i+1
	return myarr

def arr_to_list(myarr,nitems):
	"""
	functions to convert between python lists and c arrays/pointers
	users should not ever use these functions
	"""
	mylist = []
	for i in range(0,nitems):
		mylist.append(csom.ptrvalue(myarr,i))
	return mylist





"""
main function for testing purposes
these tests closely follow the tests implemented for csom.so (test_csom.py)
and for som_pak-dev (test_devrobs.c)
"""

if(__name__ == '__main__'):
	print "test 1: som from file, data from file, train from dataset"
	print "---------------------------------------------------------"
	mysom = psom(file='ex.cod')
	mydataset = dataset(file='ex.dat')
	mysom.init_training(0.02,4.0,5000)
	mysom.timing_start()
	mysom.train_from_dataset(mydataset)
	mysom.timing_stop()
	ttime = mysom.get_training_time()
	mysom.save_to_file("test1.cod")
	print "training session completed in", ttime, "seconds"
	print "output written to file \"test1.cod\""
	print "for verification, compare to test_csom.py output \"test1.cod\""
	print "  and to test_devrobs output \"test1_verify.cod\""
	print "test 1 successfully completed"

	print ""

	print "test 2: dataset from file, som randinit from data, train from dataset"
	print "---------------------------------------------------------------------"
	mysom = psom(12,8,data=mydataset)
	mysom.init_training(0.02,4.0,5000)
	mysom.timing_start()
	mysom.train_from_dataset(mydataset)
	mysom.timing_stop()
	ttime = mysom.get_training_time()
	mysom.save_to_file("test2.cod")
	print "training session completed in", ttime, "seconds"
	print "last vector produces the following gaussian SRN activations:"
	myact = mysom.get_activations('gaussian',2.0)
	myact.display()
	print "last vector produces the following error-based SRN activations:"
	myact = mysom.get_activations('error')
	myact.display()
	print "output written to file \"test2.cod\""
	print "test 2 successfully completed"

	print ""

	print "test 3: data/training dynamic, view SRN levels"
	print "----------------------------------------------"
	mysom = psom(file='ex.cod')
	mysom.init_training(0.02,2.0,5000)
	vecs = []
	vecs.append(vector([13.57, 12.61, -1.38, -1.99, 399.77]))
	vecs.append(vector([19.58, 13.08, -1.17, -0.84, 400.03]))
	vecs.append(vector([29.36, 38.69, -1.10, -0.87, 405.21], 
																					weight=3, mask=[1,0,0,1,0]))
	vecs.append(vector([19.82, 27.08, -2.35, -3.70, 404.86]))
	mydataset = dataset(vecs[0])
	for i in range(1,4):
		mydataset.addvec(vecs[i])
	mydataset.display()

	for v in vecs:
		m = mysom.train(v)
		print "input vector",
		v.display()
		print "maps to model vector",
		m.display()
		print "at point",
		m.point.display()

	print "last mapping produces the following bubble srn activations:"
	myact = mysom.get_activations()
	myact.display()
	print "last mapping produces the following gaussian srn activations:"
	myact = mysom.get_activations('gaussian',2.0)
	myact.display()
	print "fixed-window error-based srn activations:"
	myact = mysom.get_activations('error',emin=5.0,emax=25.0)
	myact.display()
	print "dynamic error-based srn activations:"
	myact = mysom.get_activations('error')
	myact.display()

	mysom.save_to_file("test3.cod")
	print "output written to \"test3.cod\""
