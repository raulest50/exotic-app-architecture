param(
    [string]$GaphorExe = 'C:\Program Files\Gaphor\gaphor.exe',
    [switch]$Installed
)
$ErrorActionPreference = 'Stop'
$testOutput = Join-Path ([IO.Path]::GetTempPath()) ('gaphor-orthogonal-tests-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $testOutput | Out-Null
$emptyPlugins = Join-Path $testOutput 'empty-plugins'
New-Item -ItemType Directory -Path $emptyPlugins | Out-Null
$gaphorDirectory = Split-Path -Parent (Resolve-Path -LiteralPath $GaphorExe)
$originalEnv = @{}
foreach ($key in @('PATH', 'GI_TYPELIB_PATH', 'GAPHOR_PLUGIN_PATH', 'GAPHOR_ORTHOGONAL_TEST_OUTPUT')) {
    $originalEnv[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
}
try {
    $env:GI_TYPELIB_PATH = Join-Path $gaphorDirectory '_internal\gi_typelibs'
    $env:PATH = "$(Join-Path $gaphorDirectory '_internal');$env:SystemRoot\System32;$env:SystemRoot"
    $env:GAPHOR_PLUGIN_PATH = $emptyPlugins
    $env:GAPHOR_ORTHOGONAL_TEST_OUTPUT = $testOutput
    $scripts = @('run_in_gaphor.py', 'integration.py', 'without_plugin.py')
    if ($Installed) { $scripts += 'installed_plugin.py' }
    foreach ($script in $scripts) {
        if ($script -eq 'installed_plugin.py') {
            [Environment]::SetEnvironmentVariable('GAPHOR_PLUGIN_PATH', $originalEnv['GAPHOR_PLUGIN_PATH'], 'Process')
        }
        $scriptPath = Join-Path $PSScriptRoot "tests\$script"
        $process = Start-Process -FilePath $GaphorExe -WorkingDirectory $gaphorDirectory -ArgumentList @('exec', ('"' + $scriptPath + '"')) -WindowStyle Hidden -PassThru
        if (-not $process.WaitForExit(45000)) { throw "Gaphor no terminó. PID: $($process.Id). Registro: $testOutput" }
        $stem = switch ($script) {
            'run_in_gaphor.py' { '' }
            'integration.py' { 'integration-' }
            'without_plugin.py' { 'without-plugin-' }
            'installed_plugin.py' { 'installed-plugin-' }
        }
        Get-Content -LiteralPath (Join-Path $testOutput ($stem + 'results.txt'))
        if ((Get-Content -LiteralPath (Join-Path $testOutput ($stem + 'status.txt'))) -ne 'PASS') { throw "Pruebas fallidas. Registro: $testOutput" }
    }
    Write-Output "Modelos temporales y resultados: $testOutput"
} finally {
    foreach ($key in $originalEnv.Keys) { [Environment]::SetEnvironmentVariable($key, $originalEnv[$key], 'Process') }
}
