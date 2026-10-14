param(
    [string]$GaphorExe = 'C:\Program Files\Gaphor\gaphor.exe',
    [switch]$Installed
)
$ErrorActionPreference = 'Stop'
$testOutput = Join-Path ([IO.Path]::GetTempPath()) ('gaphor-folder-tests-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $testOutput | Out-Null
$emptyPlugins = Join-Path $testOutput 'empty-plugins'
New-Item -ItemType Directory -Path $emptyPlugins | Out-Null
$gaphorDirectory = Split-Path -Parent (Resolve-Path -LiteralPath $GaphorExe)
$originalEnv = @{}
foreach ($key in @('PATH', 'GI_TYPELIB_PATH', 'GAPHOR_PLUGIN_PATH', 'GAPHOR_FOLDER_TEST_OUTPUT')) {
    $originalEnv[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
}
try {
    $env:GI_TYPELIB_PATH = Join-Path $gaphorDirectory '_internal\gi_typelibs'
    $env:PATH = "$(Join-Path $gaphorDirectory '_internal');$env:SystemRoot\System32;$env:SystemRoot"
    $env:GAPHOR_PLUGIN_PATH = $emptyPlugins
    $env:GAPHOR_FOLDER_TEST_OUTPUT = $testOutput
    $testScripts = @('run_in_gaphor.py', 'without_plugin.py')
    if ($Installed) { $testScripts += 'installed_plugin.py' }
    foreach ($script in $testScripts) {
        if ($script -eq 'installed_plugin.py') {
            [Environment]::SetEnvironmentVariable('GAPHOR_PLUGIN_PATH', $originalEnv['GAPHOR_PLUGIN_PATH'], 'Process')
        }
        $scriptPath = Join-Path $PSScriptRoot "tests\$script"
        $testProcess = Start-Process -FilePath $GaphorExe -WorkingDirectory $gaphorDirectory -ArgumentList @('exec', ('"' + $scriptPath + '"')) -WindowStyle Hidden -PassThru
        if (-not $testProcess.WaitForExit(30000)) { throw "Gaphor no terminó la prueba. PID: $($testProcess.Id). Registro: $testOutput" }
        $statusName = switch ($script) {
            'run_in_gaphor.py' { 'status.txt' }
            'without_plugin.py' { 'without-plugin-status.txt' }
            'installed_plugin.py' { 'installed-plugin-status.txt' }
        }
        $reportName = switch ($script) {
            'run_in_gaphor.py' { 'results.txt' }
            'without_plugin.py' { 'without-plugin.txt' }
            'installed_plugin.py' { 'installed-plugin.txt' }
        }
        Get-Content -LiteralPath (Join-Path $testOutput $reportName)
        if ((Get-Content -LiteralPath (Join-Path $testOutput $statusName)) -ne 'PASS') { throw "Pruebas fallidas. Registro: $testOutput" }
    }
    Write-Output "Modelos temporales y resultados: $testOutput"
} finally {
    foreach ($key in $originalEnv.Keys) { [Environment]::SetEnvironmentVariable($key, $originalEnv[$key], 'Process') }
}

