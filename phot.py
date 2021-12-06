def sexcom(inim, param_input, dualmode=False):
	'''
	
	'''
	param_sex = dict(
		CONF_NAME = 'default.sex',
		#------------------------------
		#	CATALOG
		#------------------------------
		CATALOG_NAME = 'test.cat',
		CATALOG_TYPE = 'ASCII_HEAD',
		PARAMETERS_NAME = 'default.param',
		#------------------------------
		#	EXTRACTION
		#------------------------------
		DETECT_TYPE = 'CCD',
		DETECT_MINAREA = '5',
		DETECT_MAXAREA = '0',
		DETECT_THRESH = '1.5',
		# ANALYSIS_THRESH = 'RELATIVE',
		ANALYSIS_THRESH = '1.5',						
		FILTER = 'Y',
		FILTER_NAME = 'default.conv',
		DEBLEND_NTHRESH = '64',
		DEBLEND_MINCONT = '0.0001',
		CLEAN = 'Y',
		CLEAN_PARAM = '1.0',
		MASK_TYPE = 'CORRECT',
		#------------------------------
		#	PHOTOMETRY
		#------------------------------
		# PHOT_APERTURES = '3',
		PHOT_AUTOPARAMS = '2.5,3.5',
		PHOT_PETROPARAMS = '2.0,3.5',
		SATUR_LEVEL  = '50000.0',
		SATUR_KEY = 'SQTURATE',
		MAG_ZEROPOINT = '0.0',
		MAG_GAMMA = '4.0',
		GAIN = '1.0',
		GAIN_KEY = 'GAIN',   
		PIXEL_SCALE = '1.0',
		#------------------------------
		#	STAR/GALAXY SEPARATION
		#------------------------------
		SEEING_FWHM = '3.0',
		STARNNW_NAME = 'default.nnw',
		#------------------------------
		#	BACKGROUND
		#------------------------------
		BACK_SIZE = '128',
		BACK_FILTERSIZE = '10',
		BACKPHOTO_TYPE = 'LOCAL',
		#------------------------------
		#	CHECK IMAGE
		#------------------------------
		CHECKIMAGE_TYPE = 'NONE',
		CHECKIMAGE_NAME = 'check.fits',
		#==============================
		#	MEMORY & MISCELLANEOUS
		#==============================
		MEMORY_OBJSTACK = '3000',
		MEMORY_PIXSTACK = '300000',
		MEMORY_BUFSIZE = '1024',
		VERBOSE_TYPE = 'NORMAL',
		HEADER_SUFFIX = '.head',
		WRITE_XML = 'N',
		XML_NAME = 'sex.xml'
	)

	for key in param_input.keys():
		param_sex[key] = param_input[key]

	sexcom_normal = f"sex -c {param_sex['CONF_NAME']} {inim} "
	# sexcom_dual = 'sex -c {} {} '.format(param_sex['CONF_NAME'], inim)
	for key in param_sex.keys():
		if key != 'CONF_NAME':
			sexcom_normal += f'-{key} {param_sex[key]} '

	return sexcom_normal
