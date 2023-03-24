import requests
import paramiko

esxi_host = 'your-esxi-hostname-or-ip'  # Give the host IP or hostname where you want VMs to be created
esxi_username = 'your-esxi-username'  # Create a user or assign user with write privilleges
esxi_password = 'your-esxi-password'  # assign password

ubuntu_iso_url = 'https://releases.ubuntu.com/20.04.3/ubuntu-20.04.3-live-server-amd64.iso'  # Replace URL with current URL
ubuntu_iso_filename = 'ubuntu.iso'  # Copy the name of file
ubuntu_iso_local_path = '/path/to/local/directory/' + ubuntu_iso_filename  # You can also assign local path

vm_base_name = 'ubuntu-vm'  # Hotsname of VM
vm_username = 'ubuntu'  # Username of Machine
vm_password = 'password'  # Default Password
vm_memory_gb = 2  # RAM Allocation
vm_disk_gb = 20  # Memory Allocation

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

response = requests.get(ubuntu_iso_url, stream=True)
with open(ubuntu_iso_local_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        f.write(chunk)

for i in range(1, 11):
    vm_name = vm_base_name + str(i)
    vm_network_label = 'VM Network'  # Change this to match your network label

    create_vm_command = f"vim-cmd vmsvc/createdummyvm {i} {vm_name}"
    ssh_client.connect(esxi_host, username=esxi_username, password=esxi_password)
    ssh_client.exec_command(create_vm_command)

    add_cdrom_command = f"vim-cmd vmsvc/device.connection {i} 4 0 /vmfs/volumes/datastore1/{ubuntu_iso_filename}"
    ssh_client.exec_command(add_cdrom_command)

    power_on_command = f"vim-cmd vmsvc/power.on {i}"
    ssh_client.exec_command(power_on_command)

    vm_ip = None
    while not vm_ip:
        get_vm_ip_command = f"vim-cmd vmsvc/get.guest {i} | grep ipAddress"
        stdin, stdout, stderr = ssh_client.exec_command(get_vm_ip_command)
        vm_ip_output = stdout.read().decode('utf-8')
        vm_ip = vm_ip_output.split('"')[1]