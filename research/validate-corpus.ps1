param(
  [switch]$RequireComplete
)

$ErrorActionPreference = 'Stop'

$expectedIds = @(
  'FND-01','FND-02','FND-03','SL-01','SL-02','CT-01','CT-02',
  'NFR-01','NFR-02','NFR-03','NFR-04','NFR-05','SR-01','SR-02',
  'AI-01','AI-02','GOV-01','GOV-02','GOV-03'
)
$allowedTypes = @('ACM','IEEE','ISO','University_Courseware','Formal_Standard')
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$rows = [System.Collections.Generic.List[object]]::new()

foreach ($id in $expectedIds) {
  $path = Join-Path $PSScriptRoot ($id + '.json')
  if (-not (Test-Path -LiteralPath $path)) {
    if ($RequireComplete) { $errors.Add("Missing deliverable: $id") }
    continue
  }

  try {
    $document = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
  } catch {
    $errors.Add("$id is not valid JSON: $($_.Exception.Message)")
    continue
  }

  foreach ($property in @(
    'subject_id','subject_title','theoretical_foundations',
    'practical_architecture_and_implementation','primary_evidence',
    'failure_modes_and_antipatterns','maturity_matrix'
  )) {
    if ($null -eq $document.$property) { $errors.Add("$id missing property: $property") }
  }

  if ($document.subject_id -ne $id) { $errors.Add("$id subject_id mismatch: $($document.subject_id)") }
  if (@($document.primary_evidence).Count -lt 8) { $errors.Add("$id has fewer than 8 evidence entries") }
  if (@($document.failure_modes_and_antipatterns).Count -eq 0) { $errors.Add("$id has no evaluated failure modes") }
  foreach ($level in @('foundational','advanced','expert_2026')) {
    if ([string]::IsNullOrWhiteSpace([string]$document.maturity_matrix.$level)) {
      $errors.Add("$id missing maturity level: $level")
    }
  }

  $tierOneCount = 0
  for ($index = 0; $index -lt @($document.primary_evidence).Count; $index++) {
    $entry = $document.primary_evidence[$index]
    $label = '{0}-{1}' -f $id, ($index + 1)
    foreach ($property in @('source_title','authors_or_institution','year','source_type','doi_or_url','verbatim_excerpt','analytical_interpretation')) {
      if ($null -eq $entry.$property -or [string]::IsNullOrWhiteSpace([string]$entry.$property)) {
        $errors.Add("$label missing evidence property: $property")
      }
    }
    if ($entry.source_type -notin $allowedTypes) { $errors.Add("$label invalid source_type: $($entry.source_type)") }
    if ([int]$entry.year -lt 1900 -or [int]$entry.year -gt 2026) { $errors.Add("$label implausible year: $($entry.year)") }
    if ([string]$entry.doi_or_url -notmatch '^https://') { $errors.Add("$label does not use an HTTPS primary link") }
    $wordCount = @(([string]$entry.verbatim_excerpt -split '\s+') | Where-Object { $_ }).Count
    if ($wordCount -gt 20) { $errors.Add("$label quotation has $wordCount words (maximum 20)") }
    if ($entry.source_type -in @('ACM','IEEE','ISO','University_Courseware')) { $tierOneCount++ }
    if ($entry.source_type -eq 'Formal_Standard' -and [string]$entry.doi_or_url -match 'nist\.gov|doi\.org/10\.6028') { $tierOneCount++ }
  }
  if ($tierOneCount -lt 5) { $warnings.Add("$id has only $tierOneCount mechanically recognizable Tier-1 entries") }

  $rows.Add([pscustomobject]@{
    Subject = $id
    Evidence = @($document.primary_evidence).Count
    Tier1Recognized = $tierOneCount
    FailureModes = @($document.failure_modes_and_antipatterns).Count
  })
}

$rows | Format-Table -AutoSize
if ($warnings.Count -gt 0) {
  Write-Output ''
  Write-Output 'Warnings:'
  $warnings | ForEach-Object { Write-Output "- $_" }
}
if ($errors.Count -gt 0) {
  Write-Output ''
  Write-Output 'Errors:'
  $errors | ForEach-Object { Write-Output "- $_" }
  throw "Corpus validation failed with $($errors.Count) error(s)."
}

Write-Output ''
Write-Output "Corpus validation passed for $($rows.Count) deliverable(s)."
