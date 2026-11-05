param(
    [string]$GaphorExe = 'C:\Program Files\Gaphor\gaphor.exe',
    [string]$PackageDirectory,
    [switch]$UnitOnly
)
$ErrorActionPreference = 'Stop'
$testOutput = Join-Path ([IO.Path]::GetTempPath()) ('gaphor-bpmn-tests-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $testOutput | Out-Null
$gaphorDirectory = Split-Path -Parent (Resolve-Path -LiteralPath $GaphorExe)
$originalEnv = @{}
foreach ($key in @('PATH', 'GI_TYPELIB_PATH', 'GAPHOR_BPMN_TEST_OUTPUT', 'GAPHOR_BPMN_TEST_PACKAGE', 'PYTHONDONTWRITEBYTECODE')) {
    $originalEnv[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
}
try {
    $env:GI_TYPELIB_PATH = Join-Path $gaphorDirectory '_internal\gi_typelibs'
    $env:PATH = "$(Join-Path $gaphorDirectory '_internal');$env:SystemRoot\System32;$env:SystemRoot"
    $env:GAPHOR_BPMN_TEST_OUTPUT = $testOutput
    $env:GAPHOR_BPMN_TEST_PACKAGE = if ($PackageDirectory) { (Resolve-Path -LiteralPath $PackageDirectory).Path } else { $null }
    $env:PYTHONDONTWRITEBYTECODE = '1'
    # GAPHOR_PLUGIN_PATH extends the search path; it does not hide user plugins.
    # The fixtures register source languages explicitly and use temporary models.
    $testScripts = @('run_in_gaphor.py')
    if (-not $UnitOnly) { $testScripts += 'integration.py' }
    foreach ($script in $testScripts) {
        $scriptPath = Join-Path $PSScriptRoot "tests\$script"
        $testProcess = Start-Process -FilePath $GaphorExe -WorkingDirectory $gaphorDirectory -ArgumentList @('exec', ('"' + $scriptPath + '"')) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $testOutput "$script-stdout.txt") -RedirectStandardError (Join-Path $testOutput "$script-stderr.txt")
        if (-not $testProcess.WaitForExit(60000)) {
            $testProcess.Kill()
            throw "La prueba excedió 60 segundos y se terminó su proceso. Registro: $testOutput"
        }
        $prefix = if ($script -eq 'run_in_gaphor.py') { '' } else { 'integration-' }
        $statusFile = Join-Path $testOutput ($prefix + 'status.txt')
        $reportFile = Join-Path $testOutput $(if ($prefix) { 'integration.txt' } else { 'results.txt' })
        if (Test-Path -LiteralPath $reportFile) { Get-Content -LiteralPath $reportFile }
        if (-not (Test-Path -LiteralPath $statusFile)) {
            Get-Content -LiteralPath (Join-Path $testOutput "$script-stderr.txt")
            throw "Gaphor terminó sin resultado ($($testProcess.ExitCode)). Registro: $testOutput"
        }
        if ((Get-Content -LiteralPath $statusFile) -ne 'PASS') { throw "Pruebas fallidas. Registro: $testOutput" }
    }
    Write-Output "Modelos temporales, capturas y resultados: $testOutput"
} finally {
    foreach ($key in $originalEnv.Keys) { [Environment]::SetEnvironmentVariable($key, $originalEnv[$key], 'Process') }
}
