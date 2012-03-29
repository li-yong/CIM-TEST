import sys, logging
sys.path.append('..\..\libs')
sys.path.append('..\..\libs\class')

import cim,baselib
import random
import unittest

import pywbem
import time


#class TestSequenceFunctions(unittest.TestCase):
class TestSample(cim.cimBase):
      

    def waitJobComplete(self,conn, job, msgSucc, msgFail):
            while True:
                    instJob=conn.GetInstance(job)
                    status = instJob.properties['Status'].value
                    if status == 'Success':
                            print msgSucc
                            break
                    elif status == 'Error':
                            print msgFail
                            break
                    else:
                            time.sleep(5)
    
    print '\n------------------'
    print 'Test begins.'
    print '------------------'	




    def setUp(self):
        self.sayHi()
        self.conn=pywbem.WBEMConnection('http://10.32.177.104:5988', ('admin', '#1Password'), 'root/emc')  
        self.checkStorCfgSvc()
        self.getInstanceNumber()
            
        instsPool=self.getInstanceNumber()
        
        if len(instsPool) < 1:
                print 'No such pool, will create.'                
        else:
                print 'The pool already existed'
                exit()
                
    def getInstanceNumber(self):
        instsPool=self.conn.ExecQuery('cql','select * from cim_storagepool where cim_storagepool.elementname=\'Pool_0\'')
        self.instsPool=instsPool
        return instsPool

    
    def checkStorCfgSvc(self):
        ### get instance of storage configuration service
        print '\nTrying to get storage configuration service...'
        self.instsStorCfgSvc=self.conn.EnumerateInstances('cim_storageconfigurationservice')
        if len(self.instsStorCfgSvc) != 1: 
                print 'storage configuration service nof found.'
                exit()
        print 'Got Storage Configuration Service.'        

    # The testcase must start with test_
    #@unittest.skip("reason")
    def test_sample(self): 
        ### create storage pool "Pool_0" with the minimal capacity of 1GB
        print '\nTrying to create pool...'
        retVal,outs=self.conn.InvokeMethod('CreateOrModifyStoragePool',
                                      self.instsStorCfgSvc[0].path,
                                      Size=pywbem.Uint64(1024),
                                      ElementName='Pool_00')
        ### wait job complete
        self.waitJobComplete(self.conn,
                        outs['Job'],
                        'Pool creation job completed successfully.',
                        'Pool creation job failed.')
        instsPool=self.getInstanceNumber()
        
        if len(instsPool) < 1:
                print 'Pool was not created'
                self.fail("create pool failed")
        else:
                print 'The pool is created' 
                            

    def tearDown(self):
        self.getInstanceNumber()
        if len(self.instsPool)<1:
            self.fail("No such pool")
        
        ### delete storage pool
        print '\nTrying to delete pool...'
        retVal,outs=self.conn.InvokeMethod('DeleteStoragePool', self.instsStorCfgSvc[0].path, Pool=self.instsPool[0].path)

        ### wait job complete
        self.waitJobComplete(conn,
                        outs['Job'],
                        'Pool deletion job completed successfully.',
                        'Pool deletion job failed.')        

        instsPool=self.getInstanceNumber()
        
        if len(instsPool) < 1:
                print 'Pool was removed'                
        else:
                print 'remove Pool failed'
        
        


if __name__ == '__main__':
    baselib.initLogger(__name__,'../../Report/att.log')
    unittest.main()