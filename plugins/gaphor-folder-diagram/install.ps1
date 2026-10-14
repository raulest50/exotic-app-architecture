param(
    [Parameter(Mandatory = $true)][string]$PythonExe,
    [string]$PluginDirectory = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.local\gaphor\plugins-2')
)
$ErrorActionPreference = 'Stop'
& $PythonExe -m pip install --no-deps --no-build-isolation --no-compile --upgrade --target $PluginDirectory $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar el plugin.' }
Write-Output "Plugin instalado en $PluginDirectory. Reinicia Gaphor para cargarlo."
