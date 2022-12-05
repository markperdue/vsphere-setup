from diagrams import Cluster, Diagram
from diagrams.generic.virtualization import Vmware
from diagrams.k8s.infra import Master, Node
# from diagrams.k8s.storage import StorageClass
from diagrams.onprem.ci import Jenkins
# from diagrams.oci.compute import Container
from diagrams.custom import Custom

no_margin = {
    "margin": "-2"
}

margin = {
    "margin": "8"
}

with Diagram("Homelab", graph_attr=no_margin, show=False, direction="TB"):
    with Cluster("ESXi - host: esxi-01.lab, ip: 192.168.2.10", graph_attr=margin):
        with Cluster("VM - host: c1-node3.lab, ip: 192.168.2.33", graph_attr=margin):
            with Cluster("Kubernetes node", graph_attr=margin):
                Node("c1-node3")

        with Cluster("VM - host: c1-node2.lab, ip: 192.168.2.32", graph_attr=margin):
            with Cluster("Kubernetes node", graph_attr=margin):
                Node("c1-node2")

        with Cluster("VM - host: c1-node1.lab, ip: 192.168.2.31", graph_attr=margin):
            with Cluster("Kubernetes node", graph_attr=margin):
                Node("c1-node1")

        with Cluster("VM - host: c1-cp1.lab, ip: 192.168.2.21", graph_attr=margin):
            with Cluster("Kubernetes node", graph_attr=margin):
                Master("c1-cp1")

        with Cluster("VM - host: vcsa-01.lab, ip: 192.168.2.12", graph_attr=margin):
            with Cluster("vCenter", graph_attr=margin):
                Vmware("vcsa-01")

with Diagram("Homelab Kubernetes Tools", graph_attr=no_margin, show=False, direction="TB", filename="homelab_tools"):
    with Cluster("", graph_attr=margin):
        Custom("Longhorn\nBlock\nStorage", "./diagram/longhorn.png")
        Custom("MetalLB", "./diagram/metallb.svg")
        Custom("Kubernetes\nDashboard", "./diagram/kubernetes.svg")
        Jenkins("Jenkins")


# More condensed layout. Issues with text alignment
# with Diagram("Homelab Alt", graph_attr=no_margin, show=False, direction="TB"):
#     with Cluster("ESXi\nhost: esxi-01.lab\nip: 192.168.2.10"):
#         with Cluster("VM\nhost: c1-node3.lab\nip: 192.168.2.33"):
#             with Cluster("Kubernetes node"):
#                 worker3b = [Node("c1-node3")]

#         with Cluster("VM\nhost: c1-node2.lab\nip: 192.168.2.32"):
#             with Cluster("Kubernetes node"):
#                 worker2b = [Node("c1-node2")]

#         with Cluster("VM\nhost: c1-node1.lab\nip: 192.168.2.31"):
#             with Cluster("Kubernetes node"):
#                 worker1b = [Node("c1-node1")]

#         with Cluster("VM\nhost: c1-cp1.lab\nip: 192.168.2.21"):
#             with Cluster("Kubernetes node"):
#                 controlplaneb = [Master("c1-cp1")]

#         with Cluster("VM\nhost: vcsa-01.lab\nip: 192.168.2.12"):
#             with Cluster("vCenter"):
#                 vsphereb = [Vmware("vcsa-01")]
