import sys
import os
import math

import numpy as N
import pyfits
from pytools import testutil 
from pysynphot import units, locations, spectrum, observationmode
from pysynphot.obsbandpass import ObsBandpass
import pysynphot as S

## TO RUN IN A SINGLE TEST IN DEBUG MODE:
## import ui_test
## ui_test.FileTestCase('testwave').debug()


class FileTestCase(testutil.FPTestCase):
    def setUp(self):
        self.fname = os.path.join(locations.rootdir,'calspec','feige66_002.fits')
        self.sp = spectrum.TabularSourceSpectrum(self.fname)
        self.openfits = pyfits.open(self.fname)

    def testwave(self):
        "ui_test.FileTestCase('testwave'): r164 wave"
        fitswave=self.openfits[1].data.field('wavelength')
        self.assertEqualNumpy(self.sp.wave, fitswave)

    def testflux(self):
        "ui_test.FileTestCase('testflux'): r164 flux"
        fitsflux=self.openfits[1].data.field('flux')
        self.assertApproxNumpy(self.sp.flux, fitsflux)

    def testname(self):
        "ui_test.FileTestCase('testname'): Tests r163"
        self.assert_(str(self.sp) == self.fname)
        self.assert_(self.sp.filename == self.fname)

    def testresample(self):
        "ui_test.FileTestCase('testresample'): Tests #24"
        sp2=self.sp.resample(N.arange(10000,18000,2))
        self.failIf(sp2.fluxunits is None)
        #self.assertEqualNumpy(sp2.wave, N.arange(10000,18000,2))

    def testadd(self):
        "ui_test.FileTestCase('testadd'): Add two spectra"
        sp2=self.sp + self.sp
        sumflux = self.sp.flux + self.sp.flux
        self.assertEqualNumpy(sp2.flux,sumflux)
        
    def tearDown(self):
        self.openfits.close()

class TabTestCase(testutil.FPTestCase):
    def setUp(self):
        self.fname = os.path.join(locations.rootdir,'calspec','feige66_002.fits')
        self.old_sp = spectrum.TabularSourceSpectrum(self.fname)
        self.openfits = pyfits.open(self.fname)
        fdata=self.openfits[1].data
        self.new_sp = spectrum.NewTabularSpectrum(wave=fdata.field('wavelength'),
                                             flux=fdata.field('flux'),
                                             waveunits=self.openfits[1].header['tunit1'],
                                             fluxunits=self.openfits[1].header['tunit2'],
                                             name='table from feige66')


    def testwave(self):
        "ui_test.TabTestCase('testwave'): .wave equal"
        self.assertEqualNumpy(self.new_sp.wave, self.old_sp.wave)

    def testflux(self):
        "ui_test.TabTestCase('testflux'): .flux equal"
        self.assertEqualNumpy(self.new_sp.flux, self.old_sp.flux)

    def testwaveunits(self):
        "ui_test.TabTestCase('testwaveunits'): waveunits equal"
        self.assert_(type(self.new_sp.waveunits) == type(self.old_sp.waveunits))

    def testfluxunits(self):
        "ui_test.TabTestCase('testfluxunits'): fluxunits equal"
        self.assert_(type(self.new_sp.fluxunits) == type(self.old_sp.fluxunits))

    def testinternalwave(self):
        "ui_test.TabTetstCase('testinternalwave'): wavetabs equal"
        self.assertEqualNumpy(self.new_sp._wavetable, self.old_sp._wavetable)
        
    def testinternalflux(self):
        "ui_test.TabTestCase('testinternalflux)'): int. flux equal"
        self.assertEqualNumpy(self.new_sp._fluxtable, self.old_sp._fluxtable\
                                      )
                
    def testconvertflux(self):
        "ui_test.TabTestCase('testconvertflux'): convert the same way"
        self.old_sp.convert('vegamag')
        self.new_sp.convert('vegamag')
        self.assertEqualNumpy(self.new_sp.flux,self.old_sp.flux)

                            
    def tearDown(self):
        self.openfits.close()

class FSSTestCase(testutil.FPTestCase):
    "Test operations on a FileSourceSpectrum"
    def setUp(self):
        self.fname = os.path.join(locations.rootdir,'calspec','feige66_002.fits')
        self.old_sp = spectrum.TabularSourceSpectrum(self.fname)
        self.new_sp = spectrum.FileSourceSpectrum(self.fname)

    def testwave(self):
        "ui_test.FSSTestCase('testwave'): .wave equal"
        self.assertEqualNumpy(self.new_sp.wave, self.old_sp.wave)
        
    def testflux(self):
        "ui_test.FSSTestCase('testflux'): .flux equal"
        self.assertEqualNumpy(self.new_sp.flux, self.old_sp.flux)

    def testwaveunits(self):
        "ui_test.FSSTestCase('testwaveunits'): waveunits equal"
        self.assert_(type(self.new_sp.waveunits) == type(self.old_sp.waveunits))

    def testfluxunits(self):
        "ui_test.FSSTestCase('testfluxunits'): fluxunits equal"
        self.assert_(type(self.new_sp.fluxunits) == type(self.old_sp.fluxunits))

    def testinternalwave(self):
        "ui_test.FSSTestCase('testinternalwave'): waveteable equal"
        self.assertEqualNumpy(self.new_sp._wavetable, self.old_sp._wavetable)

    def testinternalflux(self):
        "ui_test.FSSTestCase('testinternalflux)'): int. flux equal"
        self.assertEqualNumpy(self.new_sp._fluxtable, self.old_sp._fluxtable)
        
    def testconvertflux(self):
        "ui_test.FSSTestCase('testconvertflux'): convert the same way"
        self.old_sp.convert('vegamag')
        self.new_sp.convert('vegamag')
        self.assertEqualNumpy(self.new_sp.flux,self.old_sp.flux)

                                                                        
class BandTestCase(testutil.FPTestCase):
    def setUp(self):
        cmptb_name=os.path.join('mtab','r1j2146sm_tmc.fits')
        observationmode.COMPTABLE = observationmode._refTable(cmptb_name)
        print "ui_Test.BandTests:"
        print "  Tests are being run with comptable",observationmode.COMPTABLE
        print "  Comparison results were computed with r1j2146sm_tmc.fits"
        
    def testomfail(self):
        "ui_test.BandTestCase('testomfail'): Tests #30"
        bp1=ObsBandpass('johnson,v')

    def testompass(self):
        "ui_test.BandTestCase('testompass'): Tests r172"
        bp1=ObsBandpass('acs,hrc,f555w')
        self.assert_(len(bp1) == 6)

class UnitTestCase(testutil.FPTestCase):
    def setUp(self):
        self.uspec=S.UnitSpectrum(1.0,fluxunits='flam')

    def testfnu(self):
        """Converted to fnu, it should not be flat.
        Can't test against 1.0 because there's computations & some
        numerical issues."""
        self.uspec.convert('fnu')
        self.failIf(self.uspec.flux.mean() == 1.0)

if __name__ == '__main__':
    if 'debug' in sys.argv:
        testutil.debug(__name__)
    else:
        testutil.testall(__name__)