Walkthrough for getting VMWare vSphere ESXi 8 and vCenter 8 running on your homelab using the 60 day free evaluation license.

This is part 1 of a multi-part series.

# The goal of this series
This series is for you if you are interested in making management of your homelab something more turn-key. It is also for you if you are looking for something to help get hands-on experience to move from hobby tinkering to tools used in the workplace for managing infrastructure like Kubernetes clusters.

The series is an end-to-end walkthrough from installing ESXi on bare metal up to having homelab tools (Jenkins, Kubernetes dashboard) running in a Kubernenetes cluster using infrastructure as code practices to allow you to spin up and manage this whole setup through terraform and ansible.

The end-state Kubernetes cluster we will be creating will have some developer-focused tools deployed which will be described in more detail in part 4. All tools are deployed from code.
![homelab_tools-1](https://perdue.dev/content/images/2022/12/homelab_tools-1.png)


## Series Notes
To keep this series managable, I will skip over basics of why and how to use tools like terraform and ansible - this series will jump right in using the tools. If you are coming without a basic understanding of those tools, I would suggest running through some tutorials. There are fantastic write ups for those elsewhere.

This is a walkthrough that is meant to be adapted to your network design and hardware. It is best suited for those that have a single homelab machine where ESXi will be installed directly on the hardware and a vCenter instance will be started up within the ESXi host. Also, it should go without needing to say it, but this is not production grade - things like valid tls certificates are not included.

# This guide
At the end of this guide, we will have a vSphere install in our homelab that will be the foundation of everything else to come. For this guide, you will need to have an account created with vmware. A free account is all that is needed for this series. Create an account at [vmware.com](https://www.vmware.com)

This part of the series is probably the least of the set in regards to IaC since it deals with bootstrapping physical hardware and is also likely the least interesting of the series. At some point, I will come back and clean up the last few things to remove the manual cli steps relating to vCenter. Stick with the series and it should get a lot more interesting.


# Infrastructure Overview
## Homelab hardware
The hardware I am running on for this series is all consumer pc parts:
- CPU: AMD Ryzen 5 5700*
- Memory: 64GB DDR4*
- Storage: 1TB Samsung 970 nvme

*CPU - For a good experience, please have a cpu with at least 10 cpu threads/cores. With 4 Kubernetes nodes and vCenter running, anything less will be extremely cpu-constrained

*Memory - Less than 64GB is fine. The series should work as-is with 32GB. Anything less will require small tweaks to VM definitions for the amount of memory we allocate to the Kubernetes nodes in the second part of this series.

## Things we will be creating
The infrastructure that will be created as a result of this entire series is as follows:
![homelab-1](https://perdue.dev/content/images/2022/12/homelab-1.png)


# Guide
1. [Get companion code](#get-companion-code)
1. [(optional) Setup local DNS](#optional-setup-local-dns)
1. [Install ESXi 8](#install-esxi-8)
1. [Installing vCenter on an ESXi host](#installing-vcenter-on-an-esxi-host) or [Installing vCenter from Windows](https://github.com/markperdue/vsphere-setup/blob/main/blog/post-win.md)
1. [Finish settings up vCenter](#finish-settings-up-vcenter)
1. [Wrap Up](#wrap-up)


# Get companion code
The code this guide uses is available at [https://github.com/markperdue/vsphere-setup](https://github.com/markperdue/vsphere-setup). Clone the companion code repo to have the best experience following along. 


# (optional) Setup local DNS
Unless you really like memorizing ips, you should probably setup a basic dns server or something equivalent to handle our `.lab` domains. Skipping this step should have no technical impact on the operation of anything but will require you to replace a number of references in the config throughout this series. Essentially, any place you see any of the following values, you should replace the value with the ip
- `esxi-01.lab` values should be replaced with `192.168.2.10`
- `vcsa-01.lab` values should be replaced with `192.168.2.12`

A DNS record for ESXi and vCenter should be setup before running the installer. There are a number of ways to do this and it is up to the reader on how best to accomplish this but I will probably write this up in another guide. Currently, I run dnsmasq in a container with a very basic config file and it has been running great.

A previous method I used that I'll include here is for anyone using edgeos on a ubiquiti router and wishing to use static host mapping


### EdgeOS A record creation
1. SSH to router
1. Run the following commands:
    ```
    configure
    set system static-host-mapping host-name <hostname of ESXi host> inet <static ip of ESXi host>
    set system static-host-mapping host-name <hostname of vCenter host> inet <static ip of vCenter host>
    commit
    save
    exit
    ```

    Example:
    ```
    # sshed into edgerouter
    configure
    set system static-host-mapping host-name esxi-01.lab inet 192.168.2.10
    set system static-host-mapping host-name vcsa-01.lab inet 192.168.2.12
    commit
    save
    exit

    # on another machine
    ping vcsa-01.lab
    PING vcsa-01.lab (192.168.2.12) 56(84) bytes of data.
    64 bytes from vcsa-01.lab (192.168.2.12): icmp_seq=1 ttl=62 time=0.598 ms
    ```


# Install ESXi 8
Let's install ESXi directly on our hardware and use it as our hypervisor.

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
1. Boot homelab system from flash drive to start installer<br/>
    ![esxi-install-welcome](https://perdue.dev/content/images/2022/12/esxi-install-welcome.png)

1. Select the disk you would like to make available within ESXi as a VMFS datastore<br/>
    ![esxi-install-disk](https://perdue.dev/content/images/2022/12/esxi-install-disk.png)

1. Set a root password or use the example password we will use throughout this series `changethisp455word!`. If you use a custom password, be sure to update the config files in later steps<br/>
    ![esxi-install-root-password](https://perdue.dev/content/images/2022/12/esxi-install-root-password.png)

1. Confirm the install by hitting `F11` when prompted and wait for the install to complete<br/>
    ![esxi-install-progress](https://perdue.dev/content/images/2022/12/esxi-install-progress.png)

1. Remove the install media and hit `Enter` to reboot when prompted<br/>
    ![esxi-install-complete](https://perdue.dev/content/images/2022/12/esxi-install-complete.png)

1. After reboot, hit `F2` when ESXi has loaded to customize the system
1. Enter `root` as username and `changethisp455word!` as password
1. Select `Configure Management Network` and hit `Enter`
1. Select `IPv4 Configuration` and update the configuration to use a static address of `192.168.2.10` and hit `Enter` when done
1. Select `DNS Configuration` and update the DNS servers if neccessary. Set the hostname value to `esxi-01.lab` and hit `Enter` when done
1. Select `Custom DNS Suffixes` and type `lab` and hit `Enter`
1. Hit `Esc` and then hit `y` to apply the networking changes
1. Launch [https://esxi-01.lab](https://esxi-01.lab) on a different computer than the ESXi host and test a login with `root` and `changethisp455word!`<br/>
    ![esxi-ui-login](https://perdue.dev/content/images/2022/12/esxi-ui-login.png)
1. After logging in, you are greeted with your working ESXi instance
    ![esxi-ui-login-success](https://perdue.dev/content/images/2022/12/esxi-ui-login-success.png)


# Installing vCenter on an ESXi host
In part 2 of this series, we will be using the [vSphere terraform provider](https://registry.terraform.io/providers/hashicorp/vsphere/latest/docs) to manage our virtual machines so let's get vSphere vCenter installed. We will install vCenter as a server appliance within the ESXi host we created for our homelab. vCenter requires a lot of memory to run, 14GB by default, so if that is a concern based on your available homelab I have a tip - things seem to work for our terraform use case by setting the vCenter VM to use at least 4GB memory - albeit things start up much slower. If you have the memory to spare, keep things as they are by default.

For installing vCenter, we will focus on using their cli-based installer with a config file that would generally be placed into git for source control. This piece is one of the last pieces this series does not have automated, but until then, here are the manual steps.

1. Download the vCenter 8 iso image from wmware [[site](https://customerconnect.vmware.com/en/downloads/info/slug/datacenter_cloud_infrastructure/vmware_vsphere/8_0)]
1. Verify the sha256 checksum of the downloaded image against the stated checksum
    ```
    $ sha256sum VMware-VCSA-all-8.0.0-20519528.iso
    6f9a0691ee649f4e59fd961790d42367cad9bbbc0652070e893e209c95d969c5  VMware-VCSA-all-8.0.0-20519528.iso
    ```
1. Extract iso to disk and navigate to `vcsa-cli-installer/lin64`
1. Edit [examples/vsphere-cli.json](https://github.com/markperdue/vsphere-setup/blob/main/examples/vsphere-cli.json), if needed, with changes related to your network design and configuration
    ```
    # example file from companion code repo
    {
        "__version": "2.13.0",
        "new_vcsa": {
            "esxi": {
                "hostname": "esxi-01.lab",
                "username": "root",
                "password": "changethisp455word!",
                "deployment_network": "VM Network",
                "datastore": "datastore1"
            },
            "appliance": {
                "thin_disk_mode": true,
                "deployment_option": "tiny",
                "name": "vcsa-01.lab"
            },
            "network": {
                "ip_family": "ipv4",
                "mode": "static",
                "system_name": "vcsa-01.lab",
                "ip": "192.168.2.12",
                "prefix": "24",
                "gateway": "192.168.2.1",
                "dns_servers": [
                    "192.168.1.10",
                    "1.1.1.1"
                ]
            },
            "os": {
                "password": "changethisP455word!",
                "ntp_servers": "time.cloudflare.com",
                "ssh_enable": false
            },
            "sso": {
                "password": "changethisP455word!",
                "domain_name": "vsphere.local"
            }
        },
        "ceip": {
            "settings": {
                "ceip_enabled": false
            }
        }
    }
    ```
1. Run config validators and type `1` and then `Enter` to accept the untrusted SSL message since we do not have a signed certificate
    ```
    ./vcsa-deploy install --accept-eula --acknowledge-ceip --verify-template-only ./examples/vsphere-cli.json
    ./vcsa-deploy install --accept-eula --acknowledge-ceip --precheck-only ./examples/vsphere-cli.json
    ```
    <br/>![vsphere-cli-install-cert-check](https://perdue.dev/content/images/2022/12/vsphere-cli-install-cert-check.png)
    
1. If there were any error messages related to ovftool being not found, it is likely you need to install the dependencies mentioned below
    1. Install ovftool from https://customerconnect.vmware.com/downloads/get-download?downloadGroup=OVFTOOL443&download=true&fileId=43493035a4d43d3306fdb7c6ee61df29&uuId=edea95e1-2486-4298-afe6-28099de84bd6
    1. Install libcrypt `yay -S libxcrypt-compat`
1. Install vCenter
    ```
    ./vcsa-deploy install --accept-eula --acknowledge-ceip ./examples/vsphere-cli.json
    ```
    <br/>![vsphere-cli-install-start](https://perdue.dev/content/images/2022/12/vsphere-cli-install-start.png)
1. After 10 or 20 minutes, the installer should complete<br/>
    ![vcenter-cli-install-complete](https://perdue.dev/content/images/2022/12/vcenter-cli-install-complete.png)

1. Open [https://vcsa-01.lab](https://vcsa-01.lab) and click the button to `Launch vSphere Client` and login with `administrator@vsphere.local` and `changethisP455word!`<br/>
    ![vsphere-ui-login](https://perdue.dev/content/images/2022/12/vsphere-ui-login.png)
1. After login, we are greeted with our ready to use vCenter instance
    ![vsphere-login-success](https://perdue.dev/content/images/2022/12/vsphere-login-success.png)
1. Our [esxi-01 host](https://esxi-01.lab) can also be launched where we would see our vCenter server appliance running as a VM
    ![esxi-ui-vsphere-shown](https://perdue.dev/content/images/2022/12/esxi-ui-vsphere-shown.png)


# Finish settings up vCenter
Time to use terraform to manage a few vSphere objects using the vSphere terraform provider mentioned earlier.

Let's create a data center, cluster, and add our ESXi host to the cluster. See [main.tf](https://github.com/markperdue/vsphere-setup/blob/main/main.tf) for details.

1. In a terminal, navigate to where the [companion code repo](https://github.com/markperdue/vsphere-setup) was checked out to
2. Edit [examples/terraform.tfvars](https://github.com/markperdue/vsphere-setup/blob/main/examples/terraform.tfvars), if needed, with changes related to your network design and configuration
    ```
    # example file from companion code repo
    vsphere_user       = "administrator@vsphere.local"
    vsphere_password   = "changethisP455word!"
    vsphere_server     = "vcsa-01.lab"
    vsphere_datacenter = "Datacenter"
    vsphere_cluster    = "Cluster"
    host_hostname      = "esxi-01.lab"
    host_username      = "root"
    host_password      = "changethisp455word!"
    ```
1. Create a terraform workspace and init our plan
    ```
    terraform workspace new vsphere
    terraform init
    ```
    <br/>![terraform-vsphere-workspace-init-1](https://perdue.dev/content/images/2022/12/terraform-vsphere-workspace-init-1.png)
1. Looking at the companion code repo's [main.tf](https://github.com/markperdue/vsphere-setup/blob/main/main.tf) file we can see we are going to creates 3 resources using the vsphere terraform provider
    ```
    provider "vsphere" {
      user                 = var.vsphere_user
      password             = var.vsphere_password
      vsphere_server       = var.vsphere_server
      allow_unverified_ssl = true
    }

    resource "vsphere_datacenter" "vsphere_datacenter" {
      name = var.vsphere_datacenter
    }

    resource "vsphere_compute_cluster" "compute_cluster" {
      name          = var.vsphere_cluster
      datacenter_id = vsphere_datacenter.vsphere_datacenter.moid
      host_managed  = true
    }

    resource "vsphere_host" "esxi-01" {
      hostname   = var.host_hostname
      username   = var.host_username
      password   = var.host_password
      cluster    = vsphere_compute_cluster.compute_cluster.id
      thumbprint = data.vsphere_host_thumbprint.this.id
    }
    ```
1. Have terraform apply the plan with our `tfvars` configuration file
    ```
    terraform apply --var-file=examples/terraform.tfvars
    ```
    <br/>![terraform-vsphere-apply-1-1](https://perdue.dev/content/images/2022/12/terraform-vsphere-apply-1-1.png)
1. Terraform will detect our current infrastructure does not match our definition and that to match our definition, 3 resources - a datacenter, cluster, and host resources - need to be created. Type `yes` and hit `Enter` after confirming the displayed info
    ![terraform-vsphere-apply-2-1](https://perdue.dev/content/images/2022/12/terraform-vsphere-apply-2-1.png)
1. We can verify the terraform resources were created by visiting [https://vcsa-01.lab](https://vcsa-01.lab). The new resources should be visible in the datacenter panel
    ![vsphere-terraform-post-changes](https://perdue.dev/content/images/2022/12/vsphere-terraform-post-changes.png)


# Wrap Up
You should now have a working ESXi machine that is running an instance of vCenter. 

- ESXi host should be available by logging in at [https://esxi-01.lab](https://esxi-01.lab) with the example user `root` and password `changethisp455word!`
- vCenter host should be available by logging in at [https://vcsa-01.lab](https://vcsa-01.lab) with the example user `administrator@vsphere.local` and password `changethisP455word!`

Note - Certificate issues are expected for the above urls as we are using a .lab domain. A future update to the guide might improve this.

The next part of this series will continue with steps to create the virtual machines we will use for our Kubernetes cluster.
