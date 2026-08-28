$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$manualPath = Join-Path $root 'Modern_Quality_Engineering_2026.md'
$editorialPath = Join-Path $PSScriptRoot 'editorial-appendices.md'
$generatedPath = Join-Path $PSScriptRoot 'generated-evidence-appendix.md'

foreach ($path in @($manualPath, $editorialPath, $generatedPath)) {
  if (-not (Test-Path -LiteralPath $path)) { throw "Missing compilation input: $path" }
}

$manual = Get-Content -Raw -LiteralPath $manualPath
$editorial = (Get-Content -Raw -LiteralPath $editorialPath).Trim()
$generated = (Get-Content -Raw -LiteralPath $generatedPath).Trim()
$compiled = "<!-- COMPILED_APPENDICES_BEGIN -->`n`n$editorial`n`n$generated`n`n<!-- COMPILED_APPENDICES_END -->"

if ($manual -match '<!-- COMPILED_APPENDICES_BEGIN -->') {
  $manual = [regex]::Replace(
    $manual,
    '(?s)<!-- COMPILED_APPENDICES_BEGIN -->.*?<!-- COMPILED_APPENDICES_END -->',
    [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $compiled }
  )
} elseif ($manual.Contains('<!-- RESEARCH_MODULES_END -->')) {
  $manual = $manual.Replace('<!-- RESEARCH_MODULES_END -->', $compiled)
} else {
  throw 'Manual has neither a compilation marker nor an existing compiled appendix block.'
}

$manual = $manual.Replace('status: "Editorial compilation in progress"', 'status: "Publication-ready research edition"')
[System.IO.File]::WriteAllText($manualPath, $manual, [System.Text.UTF8Encoding]::new($false))
Write-Output $manualPath
