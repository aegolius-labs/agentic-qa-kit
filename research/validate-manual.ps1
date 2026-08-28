param(
  [string]$ManualPath = (Join-Path (Split-Path $PSScriptRoot -Parent) 'Modern_Quality_Engineering_2026.md')
)

$ErrorActionPreference = 'Stop'
$errors = [System.Collections.Generic.List[string]]::new()
$text = Get-Content -Raw -LiteralPath $ManualPath

if ($text -match '(?i)<!--[^>]*PENDING[^>]*-->|<!-- RESEARCH_MODULES_END -->') { $errors.Add('Unresolved editorial marker remains.') }
$fenceCount = ([regex]::Matches($text, '(?m)^```')).Count
if (($fenceCount % 2) -ne 0) { $errors.Add("Unbalanced fenced code blocks: $fenceCount fence lines") }

$chapterMatches = [regex]::Matches($text, '(?m)^## ([0-9]+)\. ')
$chapterNumbers = @($chapterMatches | ForEach-Object { [int]$_.Groups[1].Value })
if (($chapterNumbers -join ',') -ne ((1..19) -join ',')) {
  $errors.Add("Chapter sequence is not exactly 1–19: $($chapterNumbers -join ',')")
}

foreach ($appendix in 'A','B','C','D','E') {
  if ($text -notmatch "(?m)^# Appendix $appendix ") { $errors.Add("Missing Appendix $appendix") }
}

$expectedLabels = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.json' |
  Where-Object { $_.Name -match '^[A-Z]+-[0-9]{2}\.json$' } |
  ForEach-Object {
    $document = Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json
    for ($index = 0; $index -lt @($document.primary_evidence).Count; $index++) {
      [void]$expectedLabels.Add(('{0}-{1}' -f $document.subject_id.Replace('-', ''), ($index + 1)))
    }
  }

$usedLabels = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($match in [regex]::Matches($text, '(?<![A-Z0-9])([A-Z]{2,5}[0-9]{2}-[0-9]+)(?![A-Z0-9])')) {
  [void]$usedLabels.Add($match.Groups[1].Value)
}
foreach ($label in $usedLabels) {
  if (-not $expectedLabels.Contains($label)) { $errors.Add("Citation label has no corpus entry: $label") }
}

$wordCount = @(($text -split '\s+') | Where-Object { $_ }).Count
$report = [pscustomobject]@{
  Lines = ($text -split "`n").Count
  Words = $wordCount
  Chapters = $chapterNumbers.Count
  Appendices = @('A','B','C','D','E' | Where-Object { $text -match "(?m)^# Appendix $_ " }).Count
  CodeFences = $fenceCount
  CitationLabelsUsed = $usedLabels.Count
  CorpusLabels = $expectedLabels.Count
}
$report | Format-List

if ($errors.Count -gt 0) {
  Write-Output 'Errors:'
  $errors | ForEach-Object { Write-Output "- $_" }
  throw "Manual validation failed with $($errors.Count) error(s)."
}

Write-Output 'Manual validation passed.'
