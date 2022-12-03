# Overview
Walkthrough for getting VMWare vSphere ESXi 8 and vCenter 8 running on your homelab.

This guide is part of a series that focuses on using infrastructure as code practices to handle as much configuration as possible. This part of the series is probably the least of the set in regards to IaC since it deals with bootstrapping physical hardware. The main goal of this series surrounds spinning up a multi-node Kubernetes cluster that runs a Jenkins instance for development purposes.

For this guide, you will need to have an account created with vmware. A free account is all that is needed for this series. Create an account at [wmware.com](https://www.vmware.com)


# Note
This is a walkthrough that is meant to be adapted to your network design and hardware. It is best suited for those that have a single homelab machine where ESXi will be installed directly on the hardware and a vCenter instance will be started up within the ESXi host. The ESXi host is set to a static ip of 192.168.2.10 with the hostname esxi-01.lab. The vCenter instance is set to static ip 192.168.2.12 and hostname vcsa-01.lab


# Guide
1. [Install ESXi 8](#install-esxi-8)
1. [Setup before vCenter](#setup-before-vcenter)
2. [Installing vCenter on an ESXi host](#installing-vcenter-on-an-esxi-host) or [Installing vCenter from Windows](README-win.md)
4. [Finish settings up vCenter](#finish-settings-up-vcenter)


# Install ESXi 8
1. Download the ESXi 8 iso image from wmware [[site](https://customerconnect.vmware.com/en/downloads/info/slug/datacenter_cloud_infrastructure/vmware_vsphere/8_0)]
1. Verify the sha256 checksum of the downloaded image against the stated checksum
    ```
    $ sha256sum VMware-VMvisor-Installer-8.0-20513097.x86_64.iso
    78b8ee5613019f8d92da2b74fae674707679379803cb7b01b526747a849138c1  VMware-VMvisor-Installer-8.0-20513097.x86_64.iso
    ```
1. Write ESXi iso to a flash drive (take care with replacing /dev/sda device with your device as this command is potentially data destructive)
    ```
    $ sudo dd bs=4M if=VMware-VMvisor-Installer-8.0-20513097.x86_64.iso of=/dev/sda conv=fdatasync
    ```
1. Boot homelab system from flash drive to start installer
1. Follow prompts to complete setup (plenty of walkthroughs out there for this part)


# Setup before vCenter
A DNS record for vCenter should be setup before running the installer. There are a number of ways to do this and it's up to the reader on how best to accomplish this. I run dnsmasq in a container with a very basic config file and it has been running great.

A previous method I used that I'll include here is for anyone using an edgerouter and wishing to use static host mapping

### EdgeOS A record creation
1. SSH to router
2. Run the following commands:
    ```
    configure
    set system static-host-mapping host-name <hostname of vSphere> inet <static ip of vSphere>
    commit
    save
    exit
    ```

    Example:
    ```
    # sshed into edgerouter
    configure
    set system static-host-mapping host-name vcsa-01.lab inet 192.168.2.12
    commit
    save
    exit

    # on another machine
    ping vcsa-01.lab
    PING vcsa-01.lab (192.168.2.12) 56(84) bytes of data.
    64 bytes from vcsa-01.lab (192.168.2.12): icmp_seq=1 ttl=62 time=0.598 ms
    ```

# Installing vCenter on an ESXi host
1. Download the vCenter 8 iso image from wmware [[site](https://customerconnect.vmware.com/en/downloads/info/slug/datacenter_cloud_infrastructure/vmware_vsphere/8_0)]
1. Verify the sha256 checksum of the downloaded image against the stated checksum
    ```
    $ sha256sum VMware-VCSA-all-8.0.0-20519528.iso
    6f9a0691ee649f4e59fd961790d42367cad9bbbc0652070e893e209c95d969c5  VMware-VCSA-all-8.0.0-20519528.iso
    ```
1. Extract iso to disk and navigate to `vcsa-cli-installer/lin64`
1. Chmod the installer to executable
    ```
    chmod +x vcsa-deploy
    ```
1. Run config validators (with replacement of your config json file based off of examples/vsphere-cli.json)
    ```
    ./vcsa-deploy install --accept-eula --acknowledge-ceip --verify-template-only ./examples/vsphere-cli.json
    ./vcsa-deploy install --accept-eula --acknowledge-ceip --precheck-only ./examples/vsphere-cli.json
    ```
1. If there were any error messages related to ovftool being not found, it is likely you need to install the dependencies mentioned below
    1. Install ovftool from https://customerconnect.vmware.com/downloads/get-download?downloadGroup=OVFTOOL443&download=true&fileId=43493035a4d43d3306fdb7c6ee61df29&uuId=edea95e1-2486-4298-afe6-28099de84bd6
    1. Install libcrypt `yay -S libxcrypt-compat`
1. Install vCenter (with replacement of your config json file based off of examples/vsphere-cli.json)
    ```
    ./vcsa-deploy install --accept-eula --acknowledge-ceip ./examples/vsphere-cli.json
    ```

# Finish settings up vCenter
Time to use terraform to manage a few vSphere objects.

Let's create a data center, cluster, and add our ESXi host to the cluster.See [main.tf](main.tf) for details.

1. Edit [examples/terraform.tfvars](examples/terraform.tfvars) with your vSphere settings
2. Create a terraform workspace and apply the changes
    ```
    terraform workspace new vsphere
    terraform workspace select vsphere
    terraform init
    terraform apply --var-file=local/terraform.tfvars
    ```


# Wrap Up
You should have have a working ESXi machine that is running an instance of vCenter. The next part of this series will continue with steps to create the virtual machines we will use for our Kubernetes cluster.
