from dreampy3.onemm.plots import OnemmTotPowerPlot
import numpy as np

def gaussian2d ((x,y), c0, c1, x0,y0, sx, sy, theta):
	x = np.array(x)
	y = np.array(y)
	xp = (x-x0)*np.cos(theta) - (y-y0)*np.sin(theta)
	yp = (x-x0)*np.sin(theta) + (y-y0)*np.cos(theta)
	expn = (xp/sx)**2.0 + (yp/sy)**2.0
	ff = c0 + c1*np.exp(-0.5*expn)
	return ff

def fitgaussian2d (data, x,y):
	import scipy.optimize as opt
	
	xx, yy = np.meshgrid(x,y)
	sigma = np.sqrt(xx**2.0+yy**2.0)
	iguess = [0.0, np.median(data), 0.0, 0.0, 14.0, 14.0, 0.0]
	popt, pcov = opt.curve_fit(gaussian2d,(xx.ravel(),yy.ravel()), data.rave
l(), p0 = iguess, sigma=sigma.ravel())

	return popt

def getM2Off (nc):
	x = nc.hdu.header['M2']['XReq'][0]
	y = nc.hdu.header['M2']['YReq'][0]
	z = nc.hdu.header['M2']['ZReq'][0]

	return [x,y,z]

def getZernike (x,y, doplot = True):
    x = np.array(x)
    y = np.array(y)
    pfit = np.polyfit (x,y,2)
    xfit = np.arange(x.min(), x.max(), 0.01)
    yfit = np.polyval(pfit, xfit)
    w = np.where (yfit == yfit.max())
    leg = "Focus solution = %6.3f mm" % xfit[w]
    print leg
    if doplot:
	    pl = OnemmTotPowerPlot()
	    pl.plot (xfit,yfit)
	    pl.plot (x,y, '*')
	    #pl.title (leg)
	    #pl.axvline(xfit[w], ls=':')
	    pl.show()

def plotMap (nc):
	bmap = nc.hdu.BeamMap['BPower']
	xi = nc.hdu.xi
	yi = nc.hdu.yi

	pl = OnemmTotPowerPlot()
	pl.imshow(bmap, extent =[xi[0],xi[-1],yi[0], yi[-1]])
	pl.colorbar()
	pl.grid (color = 'white')
	pl.set_xlabel('Az Offset [arcsec]')
	pl.set_ylabel('El Offset [arcsec]')
	pl.set_title ('Map %d ' % nc.hdu.header['Dcs']['ObsNum'].getValue()[0])

	return pl
