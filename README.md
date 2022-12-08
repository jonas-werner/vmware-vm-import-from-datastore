# vmware-vm-import-from-datastore
Companion code for this blog post: 
--
https://jonamiki.com/?p=1966 

This script will scan an on-prem NetApp ONTAP datastore in vCenter and record the VMs to be migrated to FSxN and VMC using SnapMirror. Then it will ask for the destination folder, etc. and finally add the VMs to the vCenter registry
