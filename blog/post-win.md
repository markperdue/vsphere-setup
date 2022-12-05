# Installing vSphere vCenter from Windows

1. Download [VMware-VCSA-all-8.0.0-20519528.iso](https://customerconnect.vmware.com/en/downloads/details?downloadGroup=VC800&productId=1345&rPId=97539) or desired VCSA file
1. Double click to mount the image
1. Launch `vcsa-ui-installer/win32/installer.exe`
1. Click `Install`
1. Click `Next`
1. Click to accept the license agreement and click `Next`
1. Enter the values of your ESXi host and click `Next`
1. Accept the certificate warning if it is shown
1. Enter desired values for the new vCenter Server VM and click `Next`
1. Select the desired deployment size and storage size and click `Next`
1. Select the desired datastore (and enable Thing Disk Mode) and click `Next`
1. Configure network settings and click `Next`
```
Network: VM Network
IP version: IPv4
IP assignment: static
FQDN: vcsa-01.lab
IP address: 192.168.2.12
Subnet mask or prefix length: 255.255.255.0
Default gateway: 192.168.2.1
DNS servers: 192.168.2.1,1.1.1.1
```
1. Review settings and click `Finish`
1. Once stage 1 installation is complete, click `Continue`
1. Click `Next` to start stage 2 installation
1. Configure `vCenter Server Configuration` screen and and click `Next`
```
Time synchronization mode: Synchronize time with the NTP servers
NTP servers: time.cloudflare.com
SSH access: Disabled
```
1. Configure SSO Configuration screen and click `Next`
```
Create a new SSO domain
Single Sign-On domain name: vsphere.local
Single Sign-On username: administrator
Single Sing-On password: changethisP455word!
Confirm password: changethisP455word!
```
1. Uncheck `Join the VMWare's CEIP` and click `Next`
1. Review settings and click `Finish`
1. Click `OK` to warning message
1. Click `Close` when the installation is complete

## Post install vSphere (ui)
1. Launch [vCenter UI](https://192.168.2.12)
1. Add a new `Datacenter`
1. Add a new `Cluster`
1. Add a new `Host` to the previously created `Datacenter`
