# Overview
Companion code for getting VMWare vSphere ESXi 8 and vCenter 8 running on your homelab using the 60 day free evaluation license.

Please check out part 1 of the series at [Using VMWare ESXi 8 and vCenter 8 in your homelab for free](https://perdue.dev/using-vmware-esxi-8-and-vcenter-8-in-your-homelab-for-free/) which uses the code within this repo.

# Contents
1. [example configuration file](examples/vsphere-cli.json) used by guide to install vcenter through cli
1. [terraform plan](main.tf) with [example configuration](examples/terraform.tfvars) using vsphere provider for creating a datacenter, cluster, and host within vSphere instance
