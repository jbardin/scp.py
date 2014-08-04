# Pure python scp module
========================

The scp.py module uses a paramiko transport to send and recieve files via the
scp1 protocol. This is the protocol as referenced from the openssh scp program,
and has only been tested with this implementation.


## Example
==========

```python
from paramiko import SSHClient
from scp import SCPClient

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('example.com')

# SCPCLient takes a paramiko transport as its only argument
scp = SCPClient(ssh.get_transport())

scp.put('test.txt', 'test2.txt')
scp.get('test2.txt')
```
    $ md5sum test.txt test2.txt
    fc264c65fb17b7db5237cf7ce1780769 test.txt
    fc264c65fb17b7db5237cf7ce1780769 test2.txt


## Example for Fabric
=====================

Fabric does not support scp right now - see https://github.com/fabric/fabric/issues/945
so here is quick hack to use scp module with it:

```python
from fabric.api import env
from fabric.state import connections
from scp import SCPClient

def copy_file():
    client = SCPClient(connections[env.host_string]._transport)
    client.put('test.txt', 'test2.txt')
```
