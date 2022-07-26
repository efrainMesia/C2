 Param(
   [Parameter(Mandatory=$true)]
   [string]$serverip

) #end param

$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$runningAsAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if($runningAsAdmin){
  Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
  pip install -r requirements.txt
  $serverip_key = "--serverip=$serverip"
  python client.py $serverip_key
}
else{
  Write-Host "Please run this script as Administrator"
}


