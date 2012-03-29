import sys
sys.path.append('.\libs')
sys.path.append('.\class')
import cim
import baselib
import re
import ConfigParser

from configobj import ConfigObj


class tcParser:
   
    def __init__(self,cfgtxt):
        config = ConfigObj(cfgtxt)
        self.cfgtxt=cfgtxt
        config = ConfigParser.SafeConfigParser()
        config.read(self.cfgtxt)
        self.config=config
        self.tc={}
        
      
        
    def getSection(self):
        for i in self.config.sections():
            self.tc[i]={}
            self.getItems(i)
            
        
    def getItems(self,section):
        for i in self.config.items(section):
            (n,v)=i
            self.tc[section][n]=v
            
            
    def parseTest(self):
        self.getSection()
        return self

        
if __name__ == '__main__':
    tcConf="C:/cim_test/testcase/simple/testInstance_C4CB_HostService.conf"
    #tcConf="C:/cim_test/testcase/simple/testInvokeMethod.conf"
    #tcConf="C:/cim_test/testcase/simple/del.conf"
    x=tcParser(tcConf)
    x.parseTest()
    print 'hi'