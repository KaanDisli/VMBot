from pyVim import connect
from pyVmomi import vim
import threading
from datetime import datetime, timedelta
from pyVim.task import WaitForTask

class VMControl:
#Connecting to the vSphere 
#To be replaced with Simbrella Credentials and hos
    def __init__(self) -> None:
        self.service_instance = connect.SmartConnect(
            host='localhost:8989',
            user='root',
            pwd='root'
        )

        # Get the content
        self.content = self.service_instance.RetrieveContent()
        # Retrieve all virtual machines
        self.vm_list = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.VirtualMachine], True).view
        self.host_list = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.HostSystem], True).view
        self.host_vm_map = {host.name: [] for host in self.host_list}
        self.vm_map = {vm: (vm.runtime.powerState, "None", "undefined time interval") for vm in self.vm_list}
        self.update_host_vm_map()

    #Updates the current value of host_vm_map based on changes in status and whitelists
    def update_host_vm_map(self):
        self.content = self.service_instance.RetrieveContent()
        self.vm_list = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.VirtualMachine], True).view
        self.host_list = self.content.viewManager.CreateContainerView(self.content.rootFolder, [vim.HostSystem], True).view
        self.host_vm_map = {host.name: [] for host in self.host_list}
        self.vm_map = {vm: (vm.runtime.powerState, "None", "undefined time interval") for vm in self.vm_list}
        for vm in self.vm_list:
            if vm.runtime.host:
                host_name = vm.runtime.host.name
                if host_name in self.host_vm_map:
                        self.host_vm_map[host_name].append((vm,vm.runtime.powerState))
                        time_interval = self.get_time_interval(vm)
                        user = self.get_user(vm)
                        self.vm_map[vm] = (vm.runtime.powerState, user, time_interval)
    def get_vm_map(self):
        return self.vm_map                    



    def display_vm_by_machine(self):
        self.update_host_vm_map()
        str = ""
        for vm, status_user_timeinterval in self.vm_map.items():
            print(f"VM: {vm.name}")
            str = str + f"VM: {vm.name}\n"
            status, user, timeinterval = status_user_timeinterval
            guest_id = vm.config.guestId
            print(f"    OS: {guest_id}, Power: {status}, User:  {user} [{timeinterval}]\n")
            str = str + f"  OS: {guest_id}, Power: {status}, User:  {user} [{timeinterval}]\n"
        return str


    #Powers off a vm if on
    def powerOff_VM(self,vm):
        if vm:
            try:
            # Power off the VM
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    task = vm.PowerOffVM_Task()
                    WaitForTask(task)
                    print(f"VM '{vm.name}' powered off.")
                else:
                    print(f"VM '{vm.name}' is already powered off.")
            except:
                print(f"Problem turning off the vm.")
        self.update_host_vm_map()
    #Powers on a vm if off
    def powerOn_VM(self,vm):
        if vm:
            try:
            # Power on the VM
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    task = vm.PowerOnVM_Task()
                    WaitForTask(task)
                    print(f"VM '{vm.name}' powered on.")
                else:
                    print(f"VM '{vm.name}' is already powered on.")
            except:
                print(f"Problem turning on the vm.")
        self.update_host_vm_map()

    #Powers off after a certain delay for a virtual machine
    def power_off_vm_after_delay(self,vm, delay_seconds):
            print(f"Powering off after {delay_seconds} seconds")
            threading.Timer(delay_seconds, self.powerOff_VM, [vm]).start()

    #Changes name back to old name after whitelist time is done
    def whitelist_off_vm_after_delay(self, vm, old_name  ,delay_seconds):
            print(f"Whitelist off after {delay_seconds} seconds")
            threading.Timer(delay_seconds, self.change_vm_name, [vm, old_name]).start()
    def set_custom_attributes_none_after_delay(self,vm,delay_seconds):
        print(f"Custom attributes set to none after {delay_seconds} seconds")
        threading.Timer(delay_seconds, self.set_custom_attributes_none, [vm]).start()


    #function to change the name of a vm 
    def change_vm_name(self,vm,new_name):
        spec = vim.vm.ConfigSpec()
        spec.name = new_name
        if vm.name == new_name:
            print("Machine already whitelisted")
            return
        task = vm.ReconfigVM_Task(spec)
        try:
            WaitForTask(task)
            print("Machine name changed")
        except Exception as e:
            print(e) 
        self.update_host_vm_map()

    #making the white list function calls for a vm (powerOn is seperate)

    def set_time_interval(self,vm,duration):
        key="time_interval"
        current_time = datetime.now()
        duration_to_add = timedelta(seconds=duration)
        ending_time = current_time + duration_to_add
        formatted_datetime_start = current_time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_datetime_end = ending_time.strftime("%Y-%m-%d %H:%M:%S")
        value = f"[{formatted_datetime_start}] - [{formatted_datetime_end}]"
        self.set_custom_attribute(vm,key,value)

    def set_user(self,vm,user):
        key = "User"
        value = user
        self.set_custom_attribute(vm,key,value)

    def set_custom_attributes_none(self,vm):
        spec = vim.vm.ConfigSpec()
        for option in vm.config.extraConfig:
            spec.extraConfig.append(vim.option.OptionValue(key=option.key, value=None))
        task = vm.ReconfigVM_Task(spec)
        WaitForTask(task)



    def whitelist_vm(self,vm,duration):
        bool = self.check_vm_whitelisted(vm)
        if bool:    
            #Already whitelisted
            return False
            
        old_name = vm.name 
        new_name = "test_" + old_name
        self.change_vm_name(vm,new_name)
        self.powerOn_VM(vm)
        self.set_time_interval(vm,duration)
        user="Kaan" #For the moment it is like this will change later
        self.set_user(vm,user)
        self.whitelist_off_vm_after_delay(vm, old_name,duration)
        self.power_off_vm_after_delay(vm, duration)
        self.set_custom_attributes_none_after_delay(vm,duration)
        return True #whitelisting successfull
    
    
    def get_user(self,vm):
        keys_and_vals = vm.config.extraConfig
        for opts in keys_and_vals:
            if opts.key == "User":
                return opts.value
    def get_time_interval(self,vm):
        keys_and_vals = vm.config.extraConfig
        for opts in keys_and_vals:
            if opts.key == "time_interval":
                return opts.value


    def check_vm_whitelisted(self, vm):
        name = vm.name
        if name.startswith("test_") :
            return True
        else: 
            return False
    def is_linux(self, vm):
        linux_list = ["ubuntu","debian"]
        guest_id = vm.config.guestId
        for elem in linux_list:
            if guest_id.startswith("elem") :
                return True
            else: 
                return False
        

    def set_custom_attribute(self,vm,key,value):
     print("Setting custom attribute")
     try:
        spec = vim.vm.ConfigSpec()
        opt = vim.option.OptionValue() 
        spec.extraConfig = []
        opt.key = key
        opt.value = value
        spec.extraConfig.append(opt)
        task = vm.ReconfigVM_Task(spec)
        WaitForTask(task)
     except:
         print("Custom attribute already set")
    


    def unwhitelist_vm(self,vm):
        bool = self.check_vm_whitelisted(vm)
        if not bool:
            False #vm is not whitelisted so we cannot unwhitelist
        whitelisted_name = vm.name 
        if self.check_vm_whitelisted(vm):
            unwhitelisted_name = whitelisted_name[5:]
        else:
            unwhitelisted_name = whitelisted_name
        self.change_vm_name(vm,unwhitelisted_name)
        self.powerOff_VM(vm)
        self.set_custom_attributes_none_after_delay(vm,0)
        return True #unwhitelisting successfull
    

    def unwhitelist_vm_by_name(self,vm_name):
        for vm in self.vm_list:
            if vm.name == vm_name:
                bool =  self.unwhitelist_vm(vm)
                return bool
        self.update_host_vm_map()
        
        return -1 #vm doesn't exist

    def whitelist_vm_by_name(self,vm_name,duration):
        if int(duration) > 86400: #MAX DURATION OF 3 WEEKS
            return -2
        for vm in self.vm_list:
            if vm.name == vm_name:
                bool =  self.whitelist_vm(vm,int(duration))
                return bool
        self.update_host_vm_map()
        
        return -1 #vm doesn't exist
    #Whitelists every machine in a host
    """def whitelist_host(self,host_,duration):
        self.powerOn_host(host_,duration)
        for host, vms in self.host_vm_map.items():
            if host_.name == host:
                bool = self.check_host_whitelisted(host)
                if bool:    
                    if bool == -1:
                        return  -1
                    else:
                        return False
                
                for vm,status in vms:
                    self.whitelist_vm(vm,duration)
                return True"""
    #function that checks if the host is already whitelisted
    
    """def check_host_whitelisted(self, host):
        list_of_machines_and_status = self.host_vm_map[host]
        if list_of_machines_and_status == []:
            print("No machines on this host")
            return -1
        vm, status = list_of_machines_and_status[0]
        name = vm.name
        if name.startswith("test_") :
            return True
        else: 
            return False"""

    #Whitelists every machine in a host based on host name entered         
    # return value  False already whitelisted: 
    # return value -1 No machines on host
    # return value -2 Inappropriate duration
    # return value  True succesful


    """def whitelist_host_by_name(self,host_name,duration):
        if int(duration) > 3600:
            return -2
        for host in self.host_list:
            if host.name == host_name:
                bool = self.whitelist_host(host,duration)
        self.update_host_vm_map()
        return bool"""
    

        #Powers on every machine in a host
    """def powerOn_host(self,host_,duration):
        print(self.host_vm_map.items())
        for host, vms in self.host_vm_map.items():
            if host_.name == host:
                print(vms)
                for vm,status in vms:
                    print(vm)
                    self.powerOn_VM(vm)
                    self.power_off_vm_after_delay(vm, duration)"""


    """    def display_vm_by_host(self):
        #Displaying the VM's each host has
        
        # Print the host-VM mapping
        self.update_host_vm_map()
        str = ""
        for host, vms_and_status in self.host_vm_map.items():
            print(f"Host: {host}")
            str = str + f"Host: {host}\n"
            for vm,status in vms_and_status:
                guest_id = vm.config.guestId
                print(f"    VM: {vm.name}, OS: {guest_id}, Power: {status}")
                str = str + f"    VM: {vm.name}, OS: {guest_id} Power: {status} \n"
            if not vms_and_status :
                print(f"    No VMs on this host.")
                str = str + f"    No VMs on this host.\n"
        return str"""


    # Disconnect from vSphere server
    #connect.Disconnect(service_instance)
