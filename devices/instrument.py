# Basic visa instrument class.  Includes resoruce manager startup, basic query and write methods, id and reset methods
import visa

#Try to use NI-VISA
#If this fails, revert to using pyvisa-py
def makeRM():
    try:
        global_rs = visa.ResourceManager('@ni')
        print('Global NI ResourceManager created')
        return global_rs,'@ni'
    except:
        global_rs = visa.ResourceManager('@py') #Create resource manager using NI backend
        print('Global pyvisa-py ResourceManager created')
        return global_rs,'@py'
    


class instrument:
    global_rs, rstype = makeRM()  #Static resource manager for all instruments.  rstype is '@ni' for NI backend and '@py' for pyvisa-py
    def __init__(self,addr,reset=False,verb=True,**kwargs):
#        self.rs = visa.ResourceManager('@py')
#        self.dev = self.rs.open_resource(addr)

        #To correct serial resource naming depending on backend...  @py uses ASRLCOM1 and @ni uses ASRL1
        if 'ASRL' in addr:
            if self.rstype == '@py':
                if 'ASRLCOM' not in addr:
                    idx = addr.find('ASRL')+4
                    addr = addr[:idx] + 'COM' + addr[idx:]
            if self.rstype == '@ni':
                if 'ASRLCOM' in addr:
                    idx = addr.find('ASRL')+4
                    addr = addr[:idx] + addr[idx+3:]        

        #I have found that all our socket TCPIP devices need a \r\n line termination to work...  Add it if not overridden
        read_termination = None
        if 'SOCKET' in addr:
            read_termination = '\r\n'
        if 'read_termination' not in kwargs:
            kwargs['read_termination'] = read_termination
        self.dev = self.global_rs.open_resource(addr,**kwargs)
        self.verb = verb  #Whether to print commands on screen
        if reset:
            self.reset()
    def write(self,mystr):
        if self.verb:
            print(mystr)
        self.dev.write(mystr)
    def query(self,mystr):
        if self.verb:
            print(mystr)
        out = self.dev.query(mystr)
        return out
    def read(self):
        out = self.dev.read()
        return out
    def id(self):
        out = self.query('*IDN?')
        print(out)
        return out
    def reset(self):
        out = self.write('*RST')
        return out
    def setverbose(self,verb=True):
        self.verb = verb
    def close(self):
        self.dev.close()
        return
