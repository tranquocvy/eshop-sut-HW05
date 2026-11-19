[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$ResultsDir,
    [Parameter(Mandatory)][string]$JavaExe,
    [Parameter(Mandatory)][string]$JMeterJar,
    [hashtable]$Properties = @{},
    [ValidateRange(1024, 65535)][int]$ShutdownPort = 4445
)

$ErrorActionPreference = 'Stop'
$planPath = (Resolve-Path -LiteralPath $Plan).Path
$javaPath = (Resolve-Path -LiteralPath $JavaExe).Path
$jarPath = (Resolve-Path -LiteralPath $JMeterJar).Path
$destination = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ResultsDir)

$overrides = foreach ($key in ($Properties.Keys | Sort-Object)) {
    if ($key -cnotmatch '^hw05\.[a-zA-Z0-9_.]+$') {
        throw "Invalid HW05 plan property: $key"
    }
    "-J$key=$($Properties[$key])"
}

if (Test-Path -LiteralPath $destination) {
    throw "Use a new result directory to preserve existing runs: $destination"
}
[System.IO.Directory]::CreateDirectory($destination) | Out-Null

$jtl = Join-Path $destination 'run.jtl'
$log = Join-Path $destination 'jmeter.log'
$dashboard = Join-Path $destination 'dashboard'
$javaVersion = & $javaPath -version 2>&1 | ForEach-Object { $_.ToString() }
if ($LASTEXITCODE -ne 0 -or ($javaVersion -join "`n") -notmatch 'version "17[."]' -or
    ($javaVersion -join "`n") -notmatch 'Temurin') {
    throw "Choose the Temurin Java 17 executable. Detected: $javaVersion"
}
$javaVersion
$jmeterVersion = & $javaPath -Xmx384m -jar $jarPath -v -j $log 2>&1
if ($LASTEXITCODE -ne 0 -or ($jmeterVersion -join "`n") -notmatch '\b5\.6\.3\b') {
    throw "Choose Apache JMeter 5.6.3. Detected: $jmeterVersion"
}
Write-Output 'Apache JMeter 5.6.3'

$arguments = @(
    '-n', '-t', $planPath, '-l', $jtl, '-j', $log,
    "-Jjmeterengine.nongui.port=$ShutdownPort",
    "-Jjmeterengine.nongui.maxport=$ShutdownPort",
    '-Jjmeter.save.saveservice.autoflush=true',
    '-Jjmeter.save.saveservice.output_format=csv',
    '-Jjmeter.save.saveservice.print_field_names=true',
    '-Jjmeter.save.saveservice.timestamp_format=ms',
    '-Jsampleresult.timestamp.start=true',
    '-Jjmeter.save.saveservice.thread_counts=true',
    '-Jjmeter.save.saveservice.response_data=false',
    '-Jjmeter.save.saveservice.response_data.on_error=false',
    '-Jjmeter.save.saveservice.requestHeaders=false',
    '-Jjmeter.save.saveservice.responseHeaders=false',
    '-Jjmeter.save.saveservice.samplerData=false',
    '-Jsample_variables=fixture_product_id,authenticated_user_id,order_id'
) + $overrides

$arguments | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $destination 'jmeter-arguments.json') -Encoding utf8
& $javaPath -Xmx384m -jar $jarPath @arguments
if ($LASTEXITCODE -ne 0) {
    throw "JMeter run failed with exit code $LASTEXITCODE. See $log"
}

if (-not (Test-Path -LiteralPath $jtl)) {
    throw "JMeter exited with zero HTTP samples. See $log"
}
$sample = Import-Csv -LiteralPath $jtl | Select-Object -First 1
if (-not $sample -or -not $sample.label -or -not $sample.responseCode) {
    throw "JMeter exited without a valid HTTP sample. See $log"
}

$dashboardLog = Join-Path $destination 'dashboard.log'
& $javaPath -Xmx384m -jar $jarPath -g $jtl -o $dashboard -j $dashboardLog
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $dashboard 'index.html'))) {
    throw "Dashboard generation failed. See $dashboardLog"
}
Write-Output "JTL: $jtl"
Write-Output "Dashboard: $(Join-Path $dashboard 'index.html')"
