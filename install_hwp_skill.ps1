param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$bundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceSkill = Join-Path $bundleRoot "hwp"

if (-not (Test-Path $sourceSkill)) {
    throw "Could not find bundled skill folder: $sourceSkill"
}

$destRoot = Join-Path $HOME ".codex\skills"
$destSkill = Join-Path $destRoot "hwp"

New-Item -ItemType Directory -Path $destRoot -Force | Out-Null

if (Test-Path $destSkill) {
    if (-not $Force) {
        throw "Skill already exists at $destSkill . Re-run with -Force to overwrite."
    }
    Remove-Item -LiteralPath $destSkill -Recurse -Force
}

Copy-Item -LiteralPath $sourceSkill -Destination $destSkill -Recurse -Force

Write-Host ""
Write-Host "Installed: $destSkill"
Write-Host "Restart Codex to pick up the new skill."
