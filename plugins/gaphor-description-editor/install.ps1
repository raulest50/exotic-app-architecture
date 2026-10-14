param(
    [Parameter(Mandatory = $true)][string]$PythonExe,
    [string]$PluginDirectory = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.local\gaphor\plugins-2')
)
$ErrorActionPreference = 'Stop'
$metadata = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'pyproject.toml') -Raw
$pluginVersion = [regex]::Match($metadata, '(?m)^version\s*=\s*"([^"]+)"').Groups[1].Value
if (-not $pluginVersion) { throw 'No se encontró la versión del plugin.' }
& $PythonExe -m pip install --no-deps --no-build-isolation --no-compile --upgrade --target $PluginDirectory $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar el plugin.' }
$pluginRoot = (Resolve-Path -LiteralPath $PluginDirectory).Path.TrimEnd('\', '/')
$currentMetadata = "gaphor_description_editor-$pluginVersion.dist-info"
if (-not (Test-Path -LiteralPath (Join-Path $pluginRoot $currentMetadata))) {
    throw 'No se encontraron los metadatos de la versión instalada.'
}
# pip --target can retain metadata from the previous version, duplicating entry points.
foreach ($entry in Get-ChildItem -LiteralPath $pluginRoot -Directory -Filter 'gaphor_description_editor-*.dist-info') {
    if ($entry.Name -eq $currentMetadata) { continue }
    $resolvedMetadata = (Resolve-Path -LiteralPath $entry.FullName).Path
    if ([IO.Path]::GetDirectoryName($resolvedMetadata) -ne $pluginRoot -or
        ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Ruta de metadatos inesperada: $resolvedMetadata"
    }
    $distributionMetadata = Get-Content -LiteralPath (Join-Path $resolvedMetadata 'METADATA') -Raw
    if ($distributionMetadata -notmatch '(?m)^Name: gaphor-description-editor\r?$') {
        throw "Distribución inesperada: $resolvedMetadata"
    }
    Remove-Item -LiteralPath $resolvedMetadata -Recurse -Force
}
Write-Output "Plugin instalado en $PluginDirectory. Reinicia Gaphor para cargarlo."
