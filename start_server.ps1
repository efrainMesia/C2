$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$runningAsAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if($runningAsAdmin){
  Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
  pip install -r requirements.txt
  python server.py
}
else{
  Write-Host "Please run this script as Administrator"
  $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
}


