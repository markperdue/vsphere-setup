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
