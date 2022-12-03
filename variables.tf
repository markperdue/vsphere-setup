variable "vsphere_user" {
  description = "The username for vSphere API operations."
  type        = string
}

variable "vsphere_password" {
  description = "The password for vSphere API operations."
  type        = string
}

variable "vsphere_server" {
  description = "The vCenter server name for vSphere API operations."
  type        = string
}

variable "vsphere_datacenter" {
  description = "The name of the vSphere Datacenter into which resources will be created."
  type        = string
}

variable "vsphere_cluster" {
  description = "The name of the vSphere Cluster into which resources will be created."
  type        = string
}

variable "host_hostname" {
  description = "FQDN or IP address of the host to be added."
  type        = string
}

variable "host_username" {
  description = "Username that will be used by vSphere to authenticate to the host."
  type        = string
}

variable "host_password" {
  description = "Password that will be used by vSphere to authenticate to the host."
  type        = string
}
