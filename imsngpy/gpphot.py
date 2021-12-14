#%%
#	Path
path_table = '/home/paek/imsngpy/table'
path_config = '/home/paek/imsngpy/config'

prefix = 'gpphot'
path_param = f'{path_config}/{prefix}.param'
path_conv = f'{path_config}/{prefix}.conv'
path_nnw = f'{path_config}/{prefix}.nnw'
path_conf = f'{path_config}/{prefix}.sex'

#	Table
from astropy.io import ascii
ccdtbl = ascii.read(f'{path_table}/ccd.tsv') 

def file2dict(path_infile):
	out_dict = dict()
	f = open(path_infile)
	for line in f:
		key, val = line.split()
		out_dict[key] = val
	return out_dict

path_gphot = f'{path_config}/gphot.config'

import os
if os.path.exists(path_gphot) == True:
	gphot_dict = file2dict(path_gphot)
else:
	print('[NOTICE] There is no gphot.config. Use default configuration.')
	gphot_dict = {
		'imkey': 'Calib*com.fits',
		'photfraction': '0.75',
		'refcatname': 'PS1',
		'refqueryradius': '1',
		'refmaglower': '12',
		'refmagupper': '20',
		'refmagerupper': '0.05',
		'inmagerupper': '0.05',
		'flagcut': '0',
		'DETECT_MINAREA': '5',
		'DETECT_THRESH': '3.0',
		'DEBLEND_NTHRESH': '64',
		'DEBLEND_MINCONT': '0.0001',
		'BACK_SIZE': '64',
		'BACK_FILTERSIZE': '3',
		'BACKPHOTO_TYPE': 'LOCAL',
		'check': 'False'
		}

#	Test image
inim = '/data3/paek/factory/test/phot/Calib-LOAO-M99-20210421-063118-R-180.com.fits'
from astropy.io import fits
hdr = fits.getheader(inim)
if ('OBSERVAT' in hdr.keys()) & ('CCDNAME' in hdr.keys()):
	obs = hdr['OBSERVAT']
	ccd = hdr['CCDNAME']
else:
	#	observatory from filename
	obs = os.path.basename(inim).split('-')[1]
	if '_' not in obs:
		ccd = ''
	else:
		obs = obs.split('_')[0]
		ccd = obs.split('_')[1]

#------------------------------------------------------------
#	CCD INFO
import numpy as np
indx_ccd = np.where(
	(ccdtbl['obs']==obs) &
	(ccdtbl['ccd']==ccd)
)
print(f"""{'-'*60}\n#\tCCD INFO\n{'-'*60}""")
from astropy import units as u
gain = ccdtbl['gain'][indx_ccd][0]*(u.electron/u.adu)
rdnoise = ccdtbl['readnoise'][indx_ccd][0]*(u.electron)
pixscale = ccdtbl['pixelscale'][indx_ccd][0]*(u.arcsec/u.pixel)
fov = ccdtbl['foveff'][indx_ccd][0]*(u.arcmin)
print(f"""GAIN : {gain}\nREAD NOISE : {rdnoise}\nPIXEL SCALE : {pixscale}\nEffective FoV : {fov}""")
#------------------------------------------------------------
import sys
sys.path.append('/home/paek/imsngpy')
from misc import *


#	Single
if ('SEEING' in hdr.keys()) & ('PEEING' in hdr.keys()):
	seeing = hdr['SEEING']*u.arcsec
	peeing = hdr['PEEING']*u.pix
else:
	print('No seeing information on the header. Calculate ')
	prefix = 'simple'
	path_conf = f'{path_config}/{prefix}.sex'
	path_param = f'{path_config}/{prefix}.param'
	path_nnw = f'{path_config}/{prefix}.nnw'
	path_conv = f'{path_config}/{prefix}.conv'
	seeing, peeing = get_seeing(
		inim,
		gain, 
		pixscale, 
		fov, 
		path_conf, 
		path_param, 
		path_conv, 
		path_nnw, 
		seeing_assume=3*u.arcsec, 
		frac=0.68, 
		n_min_src=5
		)

aperture_dict = dict(
	MAG_AUTO=dict(
		errkey='MAGERR_AUTO',
		aperture=0.,
		comment='',
	),
	#	BEST SNR ASSUMING GAUSSIAN PROFILE
	MAG_APER_1=dict(
		errkey='MAGERR_APER_1',
		aperture=2*0.6731*peeing.value,
		comment='',
	),
)

apertures = peeing.value*np.arange(0.25, 8+0.25, 0.25)
apertures_input = ','.join([str(d) for d in apertures])
#%%
prefix = 'growthcurve'
path_param = f'{path_config}/{prefix}.param'
path_conv = f'{path_config}/{prefix}.conv'
path_nnw = f'{path_config}/{prefix}.nnw'
path_conf = f'{path_config}/{prefix}.sex'

outcat = f'{os.path.splitext(inim)[0]}.cat'
#	SE parameters
param_insex = dict(
	#------------------------------
	#	CATALOG
	#------------------------------
	CATALOG_NAME = outcat,
	#------------------------------
	#	CONFIG FILES
	#------------------------------
	CONF_NAME = path_conf,
	PARAMETERS_NAME = path_param,
	FILTER_NAME = path_conv,    
	STARNNW_NAME = path_nnw,
	#------------------------------
	#	PHOTOMETRY
	#------------------------------
	PHOT_APERTURES = apertures_input,
	GAIN = str(gain.value),
	PIXEL_SCALE = str(pixscale.value),
	#------------------------------
	#	STAR/GALAXY SEPARATION
	#------------------------------
	SEEING_FWHM = str(seeing.value),
	#------------------------------
	#	EXTRACTION
	#------------------------------
	DETECT_MINAREA = gphot_dict['DETECT_MINAREA'],
	DETECT_THRESH = gphot_dict['DETECT_THRESH'],
	DEBLEND_NTHRESH = gphot_dict['DEBLEND_NTHRESH'],
	DEBLEND_MINCONT = gphot_dict['DEBLEND_MINCONT'],
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
)
os.system(sexcom(inim, param_insex))
intbl = ascii.read(outcat)
gctbl = intbl[
	(intbl['FLAGS']==0) &
	(intbl['CLASS_STAR']>0.9)
	# (intbl[''])
]
gctbl['APER_OPT'] = 0.0
for n in range(len(apertures)):
	if n==0:
		gctbl[f'SNR'] = gctbl[f'FLUX_APER']/gctbl[f'FLUXERR_APER']
	else:
		gctbl[f'SNR_{n}'] = gctbl[f'FLUX_APER_{n}']/gctbl[f'FLUXERR_APER_{n}']
#%%
indx_col = np.where('SNR'==np.array(gctbl.keys()))
x=apertures*pixscale.value
for raw in range(len(gctbl)):
	y = np.array(list(gctbl[raw])[indx_col[0].item():])
	y[np.isnan(y)] = 0.0
	indx_peak = np.where(y==np.max(y))
	if len(y)-1 in indx_peak:
		x_opt=None
	else:
		x_opt=x[indx_peak].item()
		plt.plot(x, y, color='silver', alpha=0.125)
		plt.axvline(x=x_opt, ls='-', linewidth=0.5, color='dodgerblue', alpha=0.125)
		gctbl['APER_OPT'][raw] = x_opt
aper_opt = np.median(gctbl['APER_OPT'])
plt.axvline(x=aper_opt, ls='-', linewidth=2.0, color='tomato', alpha=0.5, label=f'OPT.APERTURE : {round(aper_opt, 3)}\"\n(SEEING*{round(aper_opt/seeing.value, 3)})')
plt.axvline(x=seeing.value, ls='-', linewidth=2.0, color='gold', alpha=0.5, label=f'SEEING : {round(seeing.value, 3)} \"')

plt.grid('both', ls='--', color='silver', alpha=0.5)
plt.xlabel('Aperture Diameter [arcsec]', fontsize=14)
plt.ylabel('SNR', fontsize=14)
plt.legend(fontsize=14, framealpha=0.0, loc='upper right')
# plt.yscale('log')
gcoutpng = f'{os.path.splitext(inim)[0]}.gc.png'
plt.savefig(gcoutpng, dpi=500, overwrite=True)
#%%


"""""




	inmagkeys = [
				'MAG_AUTO',
				'MAG_APER',
				'MAG_APER_1',
				'MAG_APER_2',
				'MAG_APER_3',
				'MAG_APER_4',
				'MAG_APER_5',
				]
	inmagerkeys = []
	for key in inmagkeys: inmagerkeys.append(key.replace('MAG_', 'MAGERR_'))
	aperkeys = []
	for key in inmagkeys: aperkeys.append(key.replace('MAG_', ''))
	aperlist = [0, optaper, 2*0.6731*peeing.value, peeing.value*2, peeing.value*3, (3*u.arcsecond/pixscale).value, (5*u.arcsecond/pixscale).value]	
	aperdiscription = ['MAG_AUTO DIAMETER [pix]', 'BEST APERTURE DIAMETER in SNR curve [pix]', 'BEST GAUSSIAN APERTURE DIAMETER [pix]', '2*SEEING APERTURE DIAMETER [pix]', '3*SEEING APERTURE DIAMETER [pix]', """FIXED 3" APERTURE DIAMETER [pix]""", """FIXED 5" APERTURE DIAMETER [pix]""",]


'''
if __name__ == '__main__':
	#	Seeing measurement
	print(f"""{'-'*60}\n#\tSEEING MEASUREMENT\n{'-'*60}""")
	with multiprocessing.Pool(processes=ncore) as pool:
		results = pool.starmap(
			get_seeing,
			zip(
					omtbl['now'],
					repeat(gain), 
					repeat(pixscale), 
					repeat(fov),
					repeat(path_conf), 
					repeat(path_param), 
					repeat(path_conv), 
					repeat(path_nnw), 
					repeat(3*u.arcsec),
					repeat(0.68),
					repeat(5),
			)
		)
		print('DONE')'''
# %%
"""""