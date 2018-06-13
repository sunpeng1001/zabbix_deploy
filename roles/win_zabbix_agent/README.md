* this role use for install&config zabbix_agent for windows

* the following steps are essential for using ansible on windows

# 1, config ansible server(linux):
apt-get update
apt-get intall ansible
pip install pywinrm

## 1.1 update /etc/ansible/hosts
$  vim /etc/ansible/hosts
[windows]
192.168.1.105 ansible_ssh_user="Administrator" ansible_ssh_pass="123456" ansible_ssh_port=5985 ansible_connection="winrm" ansible_winrm_server_cert_validation=ignore

# 2, config ansible client(windows):

## 2.1 config powershell

### 2.1.1 config powershell to remotesigned:
PS C:\Windows\system32>  set-executionpolicy remotesigned

### 2.1.2 upgrading PowerShell:
> the following step under PowerShell(must use admin open)(windows7必须是SP1)
> If running on Server 2008, then SP2 must be installed. If running on Server 2008 R2 or Windows 7, then SP1 must be installed.
> Windows Server 2008 can only install PowerShell 3.0; specifying a newer version will result in the script failing.
> http://docs.ansible.com/ansible/latest/user_guide/windows_setup.html#host-requirements

$url = "https://raw.githubusercontent.com/jborean93/ansible-windows/master/scripts/Upgrade-PowerShell.ps1"
$file = "C:\Users\yangkai\work_d\yunwei\ansible-windows\Upgrade-PowerShell.ps1"

$username = "yangkai"
$password = "yangkai"

(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force

&$file -Version 5.1 -Username $username -Password $password -Verbose

## 2.2 WinRM Setup

### 2.2.1 basic set up:
$url = "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"
$file = "$env:temp\ConfigureRemotingForAnsible.ps1"

(New-Object -TypeName System.Net.WebClient).DownloadFile($url, $file)

powershell.exe -ExecutionPolicy ByPass -File $file

### 2.2.3 WinRM Listener:
winrm enumerate winrm/config/Listener

### 2.2.4 Setup WinRM Listener:
winrm quickconfig

### 2.2.5 config the auth:
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'

# 3, test on linux:
  ansible windows -m win_ping
or
  ansible windows -m win_copy -a 'src=/etc/passwd dest=C:\Users\yangkai\tmp yyy'
or
  ansible windows -m win_file -a "path=C:\users\yangkai\passwd state=absent"

## 3.1 the playbook grammar is:
---
- name: windows module example
  hosts: windows
  tasks:
     - name: Move file on remote Windows Server from one location to another
       win_file: src=/etc/passwd dest=C:\Users\yangkai\


# 4, Reference:
http://docs.ansible.com/ansible/latest/user_guide/windows_setup.html#host-requirements
https://www.cnblogs.com/wuxie1989/p/8269564.html












