data "vsphere_host_thumbprint" "this" {
  address  = var.host_hostname
  insecure = true
}
