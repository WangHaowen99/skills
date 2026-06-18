param(
    [string]$ProxyUrl = "",
    [switch]$FixWebRtcPolicies,
    [switch]$Json
)

$ErrorActionPreference = "Continue"

function Invoke-External {
    param(
        [string]$Label,
        [scriptblock]$Script
    )

    try {
        $global:LASTEXITCODE = $null
        $output = & $Script 2>&1
        [PSCustomObject]@{
            Label = $Label
            Ok = $global:LASTEXITCODE -eq 0 -or $null -eq $global:LASTEXITCODE
            Output = ($output | Out-String).Trim()
        }
    } catch {
        [PSCustomObject]@{
            Label = $Label
            Ok = $false
            Output = $_.Exception.Message
        }
    }
}

function Invoke-WebJson {
    param(
        [string]$Label,
        [string[]]$CurlArgs
    )

    try {
        $global:LASTEXITCODE = $null
        $output = & curl.exe @CurlArgs 2>&1
        [PSCustomObject]@{
            Label = $Label
            Ok = $global:LASTEXITCODE -eq 0
            Output = ($output | Out-String).Trim()
        }
    } catch {
        [PSCustomObject]@{
            Label = $Label
            Ok = $false
            Output = $_.Exception.Message
        }
    }
}

function Get-InternetSettings {
    try {
        $settings = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        [PSCustomObject]@{
            ProxyEnable = $settings.ProxyEnable
            ProxyServer = $settings.ProxyServer
            ProxyOverride = $settings.ProxyOverride
            AutoConfigURL = $settings.AutoConfigURL
            AutoDetect = $settings.AutoDetect
        }
    } catch {
        [PSCustomObject]@{ Error = $_.Exception.Message }
    }
}

function Get-BrowserPolicy {
    param(
        [string]$Path,
        [string]$Name
    )

    try {
        $item = Get-ItemProperty -Path $Path -ErrorAction Stop
        [PSCustomObject]@{
            Path = $Path
            Name = $Name
            Value = $item.$Name
            Present = $null -ne $item.$Name
        }
    } catch {
        [PSCustomObject]@{
            Path = $Path
            Name = $Name
            Value = $null
            Present = $false
        }
    }
}

function Set-BrowserWebRtcPolicies {
    New-Item -Path "HKLM:\Software\Policies\Google\Chrome" -Force | Out-Null
    New-ItemProperty -Path "HKLM:\Software\Policies\Google\Chrome" -Name "WebRtcIPHandling" -Value "disable_non_proxied_udp" -PropertyType String -Force | Out-Null

    New-Item -Path "HKLM:\Software\Policies\Microsoft\Edge" -Force | Out-Null
    New-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Edge" -Name "WebRtcLocalhostIpHandling" -Value "disable_non_proxied_udp" -PropertyType String -Force | Out-Null
}

if ([string]::IsNullOrWhiteSpace($ProxyUrl)) {
    $internetSettings = Get-InternetSettings
    if ($internetSettings.ProxyEnable -eq 1 -and -not [string]::IsNullOrWhiteSpace($internetSettings.ProxyServer)) {
        $server = ($internetSettings.ProxyServer -split ";")[0]
        if ($server -notmatch "^[a-zA-Z][a-zA-Z0-9+.-]*://") {
            $ProxyUrl = "http://$server"
        } else {
            $ProxyUrl = $server
        }
    }
}

if ($FixWebRtcPolicies) {
    Set-BrowserWebRtcPolicies
}

$directIpify = Invoke-WebJson -Label "direct_ipify_v4" -CurlArgs @("--noproxy", "*", "-4", "-s", "--max-time", "10", "https://api.ipify.org?format=json")
$directCloudflare = Invoke-WebJson -Label "direct_cloudflare_v4" -CurlArgs @("--noproxy", "*", "-4", "-s", "--max-time", "10", "https://cloudflare.com/cdn-cgi/trace")
$proxyIpify = $null
$proxyCloudflare = $null

if (-not [string]::IsNullOrWhiteSpace($ProxyUrl)) {
    $proxyIpify = Invoke-WebJson -Label "proxy_ipify_v4" -CurlArgs @("--proxy", $ProxyUrl, "-4", "-s", "--max-time", "10", "https://api.ipify.org?format=json")
    $proxyCloudflare = Invoke-WebJson -Label "proxy_cloudflare_v4" -CurlArgs @("--proxy", $ProxyUrl, "-4", "-s", "--max-time", "10", "https://cloudflare.com/cdn-cgi/trace")
}

$ipv6Ipify = Invoke-WebJson -Label "direct_ipify_v6" -CurlArgs @("--noproxy", "*", "-6", "-s", "--max-time", "10", "https://api6.ipify.org?format=json")

$dnsWhoamiAkamai = Invoke-External -Label "dns_whoami_akamai" -Script {
    Resolve-DnsName -Name "whoami.akamai.net" -Type A -ErrorAction Stop | Format-Table Name,Type,IPAddress,NameHost,QueryType -AutoSize
}

$dnsWhoamiGoogle = Invoke-External -Label "dns_whoami_google" -Script {
    nslookup -type=txt o-o.myaddr.l.google.com
}

$winHttpProxy = Invoke-External -Label "winhttp_proxy" -Script {
    netsh winhttp show proxy
}

$report = [PSCustomObject]@{
    GeneratedAt = (Get-Date).ToString("s")
    ProxyUrlUsed = $ProxyUrl
    FixedWebRtcPolicies = [bool]$FixWebRtcPolicies
    InternetSettings = Get-InternetSettings
    WinHttpProxy = $winHttpProxy.Output
    Adapters = @(Get-NetAdapter | Sort-Object ifIndex | Select-Object ifIndex,Name,InterfaceDescription,Status,LinkSpeed)
    DefaultRoutesV4 = @(Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object ifIndex,InterfaceAlias,DestinationPrefix,NextHop,RouteMetric,PolicyStore)
    DefaultRoutesV6 = @(Get-NetRoute -DestinationPrefix "::/0" -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object ifIndex,InterfaceAlias,DestinationPrefix,NextHop,RouteMetric,PolicyStore)
    DnsServers = @(Get-DnsClientServerAddress | Sort-Object InterfaceIndex,AddressFamily | Select-Object InterfaceIndex,InterfaceAlias,AddressFamily,ServerAddresses)
    IpAddresses = @(Get-NetIPAddress | Sort-Object InterfaceIndex,AddressFamily | Select-Object InterfaceIndex,InterfaceAlias,AddressFamily,IPAddress,PrefixOrigin,AddressState)
    BrowserPolicies = @(
        Get-BrowserPolicy -Path "HKLM:\Software\Policies\Google\Chrome" -Name "WebRtcIPHandling"
        Get-BrowserPolicy -Path "HKLM:\Software\Policies\Microsoft\Edge" -Name "WebRtcLocalhostIpHandling"
    )
    Probes = @(
        $directIpify
        $directCloudflare
        $proxyIpify
        $proxyCloudflare
        $ipv6Ipify
        $dnsWhoamiAkamai
        $dnsWhoamiGoogle
    ) | Where-Object { $null -ne $_ }
}

if ($Json) {
    $report | ConvertTo-Json -Depth 6
    exit
}

Write-Host "WebRTC/IP leak report"
Write-Host "Generated: $($report.GeneratedAt)"
Write-Host ""
Write-Host "Proxy URL used: $($report.ProxyUrlUsed)"
Write-Host "WebRTC policies fixed this run: $($report.FixedWebRtcPolicies)"
Write-Host ""

Write-Host "Browser policies:"
$report.BrowserPolicies | Format-Table Path,Name,Value,Present -AutoSize

Write-Host ""
Write-Host "Network adapters:"
$report.Adapters | Format-Table -AutoSize

Write-Host ""
Write-Host "IPv4 default routes:"
$report.DefaultRoutesV4 | Format-Table -AutoSize

Write-Host ""
Write-Host "IPv6 default routes:"
if ($report.DefaultRoutesV6.Count -gt 0) {
    $report.DefaultRoutesV6 | Format-Table -AutoSize
} else {
    Write-Host "None"
}

Write-Host ""
Write-Host "DNS servers:"
$report.DnsServers | Format-Table -AutoSize

Write-Host ""
Write-Host "Internet settings:"
$report.InternetSettings | Format-List

Write-Host ""
Write-Host "WinHTTP proxy:"
Write-Host $report.WinHttpProxy

Write-Host ""
Write-Host "External probes:"
foreach ($probe in $report.Probes) {
    Write-Host "[$($probe.Label)] ok=$($probe.Ok)"
    Write-Host $probe.Output
    Write-Host ""
}

Write-Host "Next: fully restart Chrome/Edge after policy changes, then verify WebRTC in a browser leak-test page."
