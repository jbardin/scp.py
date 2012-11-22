Readme
======
Python scp module for use with Paramiko

Changes
=======
+ fixed transerring of recursive dirs (dirlevel was sometimes miscalculated)
+ added support for fnmatch style transfers (filename wildcards)
+ fixed progress callback to initially trigger on byte 0 of file to make it easier to track file by file transfers

Usage
======


    class MYSSHClient(paramiko.SSHClient):    
        def open_scp(self,socket_timeout =None, progress = None):
            """
            Open SCP Connection
            progress = callback function (name,size,sent)
            socket_timeout = timeout float
            """
            t = self.get_transport()
            c = SCPClient(t,socket_timeout = socket_timeout, progress = progress)
            return c
    
    if __name__=="__main__":
        numfile=0
        def progress( filename, size, bytessent):
            global numfile
            if bytessent == 0:
              numfile+=1
              print numfile,size,filename
            
        sshc = MYSSHClient()
        sshc.set_ignore_missing_host_key_warning()
        sshc.connect('10.0.0.1', username='username', password='password')  
        scp = sshc.open_scp(progress=progress)
        #scp.get("/etc/bla-*",".")
        scp.put("c:\\_tmp\\test\\test\\n*.png",remote_path="/var/tmp/",recursive=False,)    #do not recurse dirs
        #scp.put("c:\\_tmp\\test\\test\\",remote_path="/var/tmp/",recursive=False,)
        print numfile
        print "done"
