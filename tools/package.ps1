param(
    [string]$GameRefsDir = $env:CESIUM_GAME_REFS,
    [string]$SdkDll = $env:CESIUM_SDK_DLL,
    [string]$DotNet = 'dotnet',
    [string]$InstallModsDir = ''
)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$projectFile = Join-Path $taskRoot 'src/PinnedRelicsMod.csproj'
$modVersion = (Get-Content -LiteralPath (Join-Path $taskRoot 'src/PinnedRelicsMod.json') -Raw | ConvertFrom-Json).version
& $DotNet build $projectFile -c Release "-p:GameRefsDir=$GameRefsDir" "-p:SdkDll=$SdkDll" -p:NuGetAudit=false
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
$outputRoot = Join-Path $taskRoot 'outputs'
$packageRoot = Join-Path $outputRoot "package-$modVersion"
$modRoot = Join-Path $packageRoot 'PinnedRelicsMod'
New-Item -ItemType Directory -Force -Path $modRoot | Out-Null
$buildRoot = Join-Path $taskRoot 'src/bin/Release/netstandard2.0'
foreach ($file in @('PinnedRelicsMod.dll', 'PinnedRelicsMod.pdb', 'PinnedRelicsMod.json', 'config.json')) {
    Copy-Item -LiteralPath (Join-Path $buildRoot $file) -Destination $modRoot -Force
}
foreach ($file in @('README.md', 'NOTICE.md', 'LICENSE', '支持的筹码.md')) {
    Copy-Item -LiteralPath (Join-Path $taskRoot $file) -Destination $modRoot -Force
}
$zipPath = Join-Path $outputRoot "PinnedRelicsMod-$modVersion.zip"
Compress-Archive -LiteralPath $modRoot -DestinationPath $zipPath -Force
if ($InstallModsDir) {
    $installRoot = Join-Path ([IO.Path]::GetFullPath($InstallModsDir)) 'PinnedRelicsMod'
    if (Test-Path -LiteralPath $installRoot) { throw "Refusing to overwrite an existing installation: $installRoot" }
    Copy-Item -LiteralPath $modRoot -Destination $installRoot -Recurse
    Write-Output "Installed: $installRoot"
}
Write-Output "Package: $zipPath"
