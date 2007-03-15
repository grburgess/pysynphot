"""
Units class hierarchy: is used to manage both wavelength and flux
unit conversions

Warning: vegamag unit conversions import spectrum and locations => circular
imports.
"""

import math
import numpy as N

C = 2.99792458e18 # speed of light in Angstrom/sec
H = 6.62620E-27   # Planck's constant
HC = H * C
ABZERO = -48.60   # magnitude zero points
STZERO = -21.10

HSTAREA = 45238.93416  # cm^2


def Units(uname):
    """This needs to be a factory function in order to return an object
    of the correct subclass."""
    try:
        return factory(uname)
    except KeyError:
        raise ValueError("Unknown units %s"%uname)

#......................................................................
#Base classes

class BaseUnit(object):
    """ Base class for all units; defines UI"""
    def __init__(self,uname):
        self.Dispatch=None
        self.name=uname

    def __str__(self):
        return self.name

    def Convert(self,wave,flux,target_units):
        """This signature is appropriate for fluxes, not waves"""
        try:
            return self.Dispatch[target_units](wave,flux)
        except KeyError:
            raise KeyError("Target units %s unrecognized%(target_units)")

class WaveUnits(BaseUnit):
    """All WaveUnits know how to convert themselves to Angstroms"""
    def __init__(self):
        self.name=None
        self.isFlux = False
        self.Dispatch = {'angstrom' : self.ToAngstrom}

    def Convert(self,wave,target_units):
        try:
            return self.Dispatch[target_units](wave)
        except KeyError:
            raise KeyError("Target units %s unrecognized:"%target_units)

    def ToAngstrom(self,wave):
        raise NotImplementedError("Required method ToAngstrom not yet implemented")

class FluxUnits(BaseUnit):
    """All FluxUnits know how to convert themselves to Photlam"""
    def __init__(self):
        self.isFlux = True
        self.name=None
        self.Dispatch = {'photlam':self.ToPhotlam}
        
    def Convert(self,wave,flux,target_units):
        try:
            return self.Dispatch[target_units](wave,flux)
        except KeyError:
            raise KeyError("Target units %s unrecognized:%(target_units)")

    def ToPhotlam(self,wave,flux):
        raise NotImplementedError("Required method ToPhotlam not yet implemented")

#.............................................................
# Internal wavelength units are Angstroms, so it is smarter than the others
class Angstrom(WaveUnits):
    def __init__(self):
        WaveUnits.__init__(self)
        self.name = 'angstrom'
        self.Dispatch = {'angstrom' : self.ToAngstrom,
                         'nm': self.ToNm,
                         'micron': self.ToMicron,
                         'mm': self.ToMm,
                         'cm': self.ToCm,
                         'm': self.ToMeter,
                         'hz': self.ToHz}
        

    def ToAngstrom(self, wave):
        return wave
    
    def ToNm(self, wave):
        return wave / 10.0
    
    def ToMicron(self, wave):
        return wave * 1.0e-4
    
    def ToMm(self, wave):
        return wave * 1.0e-7
    
    def ToCm(self, wave):
        return wave * 1.0e-8
    
    def ToMeter(self, wave):
        return wave * 1.0e-10
    
    def ToHz(self, wave):
        return C / wave

#........................................................................
# Internal flux units = Photlam, so it is smarter than the others

class Photlam(FluxUnits):
    ''' photlam = photons cm^-2 s^-1 Ang^-1)'''
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'photlam'
        self.Dispatch = {'flam': self.ToFlam,
                         'fnu': self.ToFnu,
                         'photlam': self.ToPhotlam,
                         'photnu': self.ToPhotnu,
                         'jy':self.ToJy,
                         'mjy':self.TomJy,
                         'abmag':self.ToABMag,
                         'stmag':self.ToSTMag,
                         'obmag':self.ToOBMag,
                         'vegamag':self.ToVegaMag,
                         'counts':self.ToCounts}

    def ToFlam(self, wave, flux):
        return HC * flux / wave

    def ToFnu(self, wave, flux):
        return H * flux * wave

    def ToPhotlam(self, wave, flux):
        return flux.copy() # No conversion, just copy the array.

    def ToPhotnu(self, wave, flux):
        return flux * wave * wave / C

    def ToJy(self, wave, flux):
        return 1.0e+23 * H * flux * wave
    
    def TomJy(self, wave, flux):
        return 1.0e+26 * H * flux * wave
    
    def ToABMag(self, wave, flux):
        arg = H * flux * wave
        return -1.085736 * N.log(arg) + ABZERO
    
    def ToSTMag(self, wave, flux):
        arg = H * C* flux / wave
        return -1.085736 * N.log(arg) + STZERO
    
    def ToOBMag(self, wave, flux):
        dw = _getDeltaWave(wave)
        arg = flux * dw * HSTAREA
        return -1.085736 * N.log(arg)

    def ToVegaMag(self, wave, flux):
        import locations, spectrum #Circular import
        vegaspec = spectrum.TabularSourceSpectrum(locations.VegaFile)
        resampled = vegaspec.resample(wave)
        normalized = flux / resampled._fluxtable
        return -2.5 * N.log10(normalized)

    def ToCounts(self, wave, flux):
        return flux * _getDeltaWave(wave) * HSTAREA


#................................................................
#Other wavelength units

class Hz(WaveUnits):
    def __init__(self):
        WaveUnits.__init__(self)
        self.name='hz'

    def ToAngstrom(self, wave, dummy):
        return C / wave

class _MetricWavelength(WaveUnits):
    """ Encapsulates some easy unit-conversion machinery. Angstrom
    is not subclassed from here because it needs to be especially smart in
    other ways. (Although multiple inheritence might be possible.)"""
    def ToAngstrom(self,wave):
        return wave*self.factor

class Nm(_MetricWavelength):
    def __init__(self):
        _MetricWavelength.__init__(self)
        self.name = 'nm'
        self.factor = 10.0
    
class Micron(_MetricWavelength):
    def __init__(self):
        _MetricWavelength.__init__(self)
        self.name = 'micron'
        self.factor = 1.0e4

class Mm(_MetricWavelength):
    def __init__(self):
        _MetricWavelength.__init__(self)
        self.name = 'mm'
        self.factor = 1.0e7

class Cm(_MetricWavelength):
    def __init__(self):
        _MetricWavelength.__init__(self)
        self.name = 'cm'
        self.factor = 1.0e8

class Meter(_MetricWavelength):
    def __init__(self):
        _MetricWavelength.__init__(self)
        self.name = 'm'
        self.factor = 1.0e10


#................................................................
#Other flux units

class Flam(FluxUnits):
    ''' flam = erg cm^-2 s^-1 Ang^-1'''

    def __init__(self):
        FluxUnits.__init__(self)
        self.name='flam'
        self.Dispatch = {'photlam':self.ToPhotlam}
        
    def ToPhotlam(self, wave, flux):
        return flux * wave / HC

class Photnu(FluxUnits):
    ''' photnu = photon cm^-2 s^-1 Hz^-1'''
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'photnu'
    
    def ToPhotlam(self, wave, flux):
        return C * flux / (wave * wave)

class Fnu(FluxUnits):
    ''' fnu = erg cm^-2 s^-1 Hz^-1'''
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'fnu'
    
    def ToPhotlam(self, wave, flux):
        return flux /wave / H
class Jy(FluxUnits):
    ''' jy = 10^-23 erg cm^-2 s^-1 Hz^-1'''
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'jy'

    def ToPhotlam(self, wave, flux):
        return flux / wave * (1.0e-23 / H)

class mJy(FluxUnits):
    ''' mjy = 10^-26 erg cm^-2 s^-1 Hz^-1'''
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'mjy'

    def ToPhotlam(self, wave, flux):
        return flux / wave * (1.0e-26 / H)

class ABMag(FluxUnits):
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'abmag'
    
    def ToPhotlam(self, wave, flux):
        return 1.0 / (H * wave) * 10.0**(-0.4 * (flux - ABZERO))

class STMag(FluxUnits):
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'stmag'
    
    def ToPhotlam(self, wave, flux):
        return wave / H / C * 10.0**(-0.4 * (flux - STZERO))

class OBMag(FluxUnits):
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'obmag'
    
    def ToPhotlam(self, wave, flux):
        dw = _getDeltaWave(wave)
        return 10.0**(-0.4 * flux) / (dw * HSTAREA)

class VegaMag(FluxUnits):
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'vegamag'
    
    def ToPhotlam(self, wave, flux):
        vegaspec = spectrum.TabularSourceSpectrum(locations.VegaFile)
        resampled = vegaspec.resample(wave)
        return resampled.fluxtable * 10.0**(-0.4 * flux)

class Counts(FluxUnits):
    def __init__(self):
        FluxUnits.__init__(self)
        self.name = 'counts'
    
    def ToPhotlam(self, wave, flux):
        return flux / (_getDeltaWave(wave) * HSTAREA)

################   Factory for Units subclasses.   #####################


def factory(uname, *args, **kwargs):
    unitsClasses = {'flam'      : Flam,
                    'fnu'       : Fnu,
                    'photlam'   : Photlam,
                    'photnu'    : Photnu,
                    'jy'        : Jy,
                    'mjy'       : mJy,
                    'abmag'     : ABMag,
                    'stmag'     : STMag,
                    'obmag'     : OBMag,
                    'vegamag'   : VegaMag,
                    'counts'    : Counts,
                    'angstrom'  : Angstrom,
                    'angstroms' : Angstrom,
                    'nm'        : Nm,
                    'micron'    : Micron,
                    'um'        : Micron,
                    'mm'        : Mm,
                    'cm'        : Cm,
                    'm'         : Meter,
                    'meter'     : Meter,
                    'hz'        : Hz}

    key=uname.lower()
    ans= unitsClasses[key]()
    return ans

def _getDeltaWave(wave):
    """ Compute delta wavelngth for an array of wavelengths.
    If we had a WaveTable class, this function would be a method
    on that class: possible refactoring candidate. """
    
    last = wave.shape[0]-1

    hold1 = N.empty(shape=wave.shape, dtype=N.float64)
    hold2 = N.empty(shape=wave.shape, dtype=N.float64)

    hold1[1::] = wave[0:last]
    hold2[0:last] = wave[1::]

    delta = (hold2 - hold1) / 2.0

    delta[0] = wave[1] - wave[0]
    delta[last] = wave[last] - wave[last-1]

    return delta
