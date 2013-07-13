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
    $ md5sum test.xt test2.txt
    fc264c65fb17b7db5237cf7ce1780769 test.txt
    fc264c65fb17b7db5237cf7ce1780769 test2.txt

