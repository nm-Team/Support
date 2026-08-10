param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    & uv run nmteam @Arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
