from pyVim import connect
from pyVmomi import vim
from pyVim.task import WaitForTask
import atexit
import time

#Connecting to the vSphere 
#To be replaced with Simbrella Credentials and host
service_instance = connect.SmartConnect(
    host='localhost:8989',
    user='root',
    pwd='root'
)
def change_vm_name(vm,new_name):
        spec = vim.vm.ConfigSpec()
        spec.name = new_name
        task = vm.ReconfigVM_Task(spec)
        WaitForTask(task)
        


# Get the content
content = service_instance.RetrieveContent()
# Retrieve all virtual machines
vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view
host_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True).view
h0_vm0 = vm_list[0]
h0_vm1 = vm_list[1]
h2_vm0 = vm_list[2]
h2_vm1 = vm_list[3]

change_vm_name(h0_vm0,"DC0_H0_VM0")
change_vm_name(h0_vm1,"DC0_H0_VM1")
change_vm_name(h2_vm0,"DC0_C0_RP0_VM0")
change_vm_name(h2_vm1,"DC0_C0_RP0_VM1")

def set_vm_os():
    #Set each host with 1 windows and 1 linux machine
    spec = vim.vm.ConfigSpec()
    
    h0_vm0 = vm_list[0]
    h0_vm1 = vm_list[1]
    h2_vm0 = vm_list[2]
    h2_vm1 = vm_list[3]

    spec.guestId = "windows2019Server64Guest"
    task0 = h0_vm0.ReconfigVM_Task(spec)
    spec.guestId = "ubuntuGuest"
    task1 = h0_vm1.ReconfigVM_Task(spec)
    spec.guestId = "windows2019Server64Guest"
    task2 = h2_vm0.ReconfigVM_Task(spec)
    spec.guestId = "ubuntuGuest"
    task3 = h2_vm1.ReconfigVM_Task(spec)

host_vm_map = {host.name: [] for host in host_list}
def display_vm_by_host():
    #Displaying the VM's each host has
    global host_vm_map
    
    for vm in vm_list:
        if vm.runtime.host:
            host_name = vm.runtime.host.name
            if host_name in host_vm_map:
                host_vm_map[host_name].append(vm.name)
    
    # Print the host-VM mapping
    for host, vms in host_vm_map.items():
        print(f"Host: {host}")
        for vm in vms:
            print(f"    VM: {vm}")
        if not vms:
            print(f"    No VMs on this host.")
    return host_vm_map



set_vm_os()
display_vm_by_host()
for vm in vm_list:
    guest_id = vm.config.guestId
    print(f"VM Name: {vm.name}, Guest ID: {guest_id}, Power: {vm.runtime.powerState}")
    
for host in host_list:
    print(f"Host Name: {host.name}")
# Disconnect from vSphere server
vm1 = vm_list[0]
vm2 = vm_list[1]
vm3 = vm_list[2]
vm4 = vm_list[3]

print(vm1.name)

try:           
    task = vm1.PowerOffVM_Task()
    WaitForTask(task)
except:
    print("already turned off")

try:           
    task = vm2.PowerOffVM_Task()
    WaitForTask(task)
except:
    print("already turned off")
try:           
    task = vm3.PowerOffVM_Task()
    WaitForTask(task)
except:
    print("already turned off")
try:           
    task = vm4.PowerOffVM_Task()
    WaitForTask(task)
except:
    print("already turned off")




connect.Disconnect(service_instance)
