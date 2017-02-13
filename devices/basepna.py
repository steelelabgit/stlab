from stlab.devices.instrument import instrument
from stlab.utils.stlabdict import stlabdict as stlabdict
import numpy as np

import abc


def numtostr(mystr):
    return '%20.15e' % mystr

class basepna(instrument):
    __metaclass__ = abc.ABCMeta

    def __init__(self,addr,reset=True,verb=True):
        super(basepna, self).__init__(addr,reset,verb)
        #Remove timeout so long measurements do not produce -420 "Unterminated Query"
        self.dev.timeout = None 
        self.id()
        if reset:
            self.SetContinuous(False) #Turn off continuous mode


##### ABSTRACT METHODS TO BE IMPLEMENTED ON A PER PNA BASIS #####################
    @abc.abstractmethod
    def SetContinuous(self,var=True):
        if var:
            self.write('INIT:CONT 1') #Turn on continuous mode
        elif not var:
            self.write('INIT:CONT 0') #Turn off continuous mode
        return

    @abc.abstractmethod
    def SetStart(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:STAR '+mystr
        self.write(mystr)
    @abc.abstractmethod
    def SetEnd(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:STOP '+mystr
        self.write(mystr)
    @abc.abstractmethod
    def SetCenter(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:CENT '+mystr
        self.write(mystr)
    @abc.abstractmethod
    def SetSpan(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:FREQ:SPAN '+mystr
        self.write(mystr)

    @abc.abstractmethod
    def GetStart(self):
        mystr = 'SENS:FREQ:STAR?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    @abc.abstractmethod
    def GetEnd(self):
        mystr = 'SENS:FREQ:STOP?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    @abc.abstractmethod
    def GetCenter(self):
        mystr = 'SENS:FREQ:CENT?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    @abc.abstractmethod
    def GetSpan(self):
        mystr = 'SENS:FREQ:SPAN?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp

    @abc.abstractmethod
    def SetIFBW(self,x):
        mystr = numtostr(x)
        mystr = 'SENS:BWID '+mystr
        self.write(mystr)
    @abc.abstractmethod
    def SetPower(self,x):
        mystr = numtostr(x)
        mystr = 'SOUR:POW '+mystr
        self.write(mystr)
    @abc.abstractmethod
    def GetPower(self):
        mystr = 'SOUR:POW?'
        pp = self.query(mystr)
        pp = float(pp)
        return pp
    @abc.abstractmethod
    def SetPoints(self,x):
        mystr = '%d' % x
        mystr = 'SENS:SWE:POIN '+mystr
        self.write(mystr)

    @abc.abstractmethod
    def Trigger(self):
        print((self.query('INIT;*OPC?')))
        return

    @abc.abstractmethod
    def GetFrequency(self):
        freq = self.query('CALC:X?')
        freq = np.asarray([float(xx) for xx in freq.split(',')])
        return freq

    @abc.abstractmethod
    def GetTraceNames(self):
        pars = self.query('CALC:PAR:CAT:EXT?')
        pars = pars.strip('\n').strip('"').split(',')
        parnames = pars[1::2] #parameter names
        pars = pars[::2] #parameter identifiers
        return pars,parnames
    @abc.abstractmethod
    def SetActiveTrace(self,mystr):
        self.write('CALC:PAR:SEL "%s"' % mystr)
    @abc.abstractmethod
    def GetTraceData(self):
        yy = self.query("CALC:DATA? SDATA")
        return yy

    @abc.abstractmethod
    def ClearAll(self): #Clears all traces and windows
        windows = self.query('DISP:CAT?')
        windows = windows.strip('\n')
        if windows != '"EMPTY"':
            windows = [int(x) for x in windows.strip('"').split(',')]
            for i in windows:
                self.write('DISP:WIND%d OFF' % i)
    @abc.abstractmethod
    def AutoScaleAll(self):
        self.write('DISP:WIND:TRAC:Y:COUP:METH WIND')
        windows = self.query('DISP:CAT?')
        windows = windows.strip('\n')
        if windows != '"EMPTY"':
            windows = [int(x) for x in windows.strip('"').split(',')]
            for i in windows:
                self.write('DISP:WIND%d:TRAC:Y:AUTO' % i)

    @abc.abstractmethod
    def AddTraces(self,trcs): #Function to add traces to measurement window.  trcs is a list of S parameters Sij.
        self.write('DISP:WIND1 ON')
        if type(trcs) is str:
            measnames = [trcs]
        else:
            measnames = trcs
        tracenames = ['CH1_%s' % x for x in measnames]
        for i,(meas,trc) in enumerate(zip(measnames,tracenames)):
            self.write("CALC:PAR:DEF:EXT '%s', '%s'" % (trc,meas))
            self.write("DISP:WIND:TRAC%d:FEED '%s'" % (i+1,trc))
    @abc.abstractmethod
    def LoadCal (self, calset):
        mystr = 'SENS:CORR:INT ON'
        self.write(mystr)
        mystr = 'SENS:CORR:CSET:ACT "%s",0' % calset
        self.write(mystr)
    @abc.abstractmethod
    def CalOn (self):
        mystr = "SENS:CORR ON"
        self.write(mystr)
    @abc.abstractmethod
    def CalOff (self):
        mystr = "SENS:CORR OFF"
        self.write(mystr)
    @abc.abstractmethod
    def GetCal(self):
        return bool(int(self.query('SENS:CORR?')))

##### FULLY IMPLEMENTED METHODS THAN DO NOT NEED TO BE REIMPLEMENTED (BUT CAN BE IF NECESSARY) #####################

    def SetRange(self,start,end):
        self.SetStart(start)
        self.SetEnd(end)
    def SetCenterSpan(self,center,span):
        self.SetCenter(center)
        self.SetSpan(span)

    def GetAllData(self):
        Cal = self.GetCal()
        pars,parnames = self.GetTraceNames()
        self.SetActiveTrace(pars[0])
        names = ['Frequency (Hz)']
        alltrc = [self.GetFrequency()]
        for pp in parnames:
            names.append('%sre ()' % pp)
            names.append('%sim ()' % pp)
            names.append('%sdB (dB)' % pp)
        if Cal:
            for pp in parnames:
                names.append('%sre unc ()' % pp)
                names.append('%sim unc ()' % pp)
                names.append('%sdB unc (dB)' % pp)
        for par in pars:
            self.SetActiveTrace(par)
            yy = self.GetTraceData()
            yy = np.asarray([float(xx) for xx in yy.split(',')])
            yyre = yy[::2]
            yyim = yy[1::2]
            alltrc.append(yyre)
            alltrc.append(yyim)
            yydb = 20.*np.log10( np.sqrt(np.power(yyre,2.)+np.power(yyim,2.)) )
            alltrc.append(yydb)
        if Cal:
            self.CalOff()
            for par in pars:
                self.SetActiveTrace(par)
                yy = self.GetTraceData()
                yy = np.asarray([float(xx) for xx in yy.split(',')])
                yyre = yy[::2]
                yyim = yy[1::2]
                alltrc.append(yyre)
                alltrc.append(yyim)
                yydb = 20.*np.log10( np.sqrt(np.power(yyre,2.)+np.power(yyim,2.)) )
                alltrc.append(yydb)
            self.CalOn()
        final = stlabdict()
        for name,data in zip(names,alltrc):
            final[name]=data
        return final

    def MeasureScreen(self):
        self.SetContinuous(False)
        print(self.Trigger()) #Trigger single sweep and wait for response
        return self.GetAllData()







