param(
  [string]$OutputPath = (Join-Path $PSScriptRoot 'generated-evidence-appendix.md')
)

$ErrorActionPreference = 'Stop'

$subjectOrder = @(
  'FND-01','FND-02','FND-03','SL-01','SL-02','CT-01','CT-02',
  'NFR-01','NFR-02','NFR-03','NFR-04','NFR-05','SR-01','SR-02',
  'AI-01','AI-02','GOV-01','GOV-02','GOV-03'
)

function Escape-MarkdownCell([object]$Value) {
  if ($null -eq $Value) { return '' }
  return ([string]$Value).Replace('|', '\|').Replace("`r", '').Replace("`n", '<br>')
}

function Evidence-Label([string]$SubjectId, [int]$Index) {
  return ('{0}-{1}' -f $SubjectId.Replace('-', ''), $Index)
}

$documentsById = @{}
Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.json' |
  Where-Object { $_.Name -match '^[A-Z]+-[0-9]{2}\.json$' } |
  ForEach-Object {
    $document = Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json
    $documentsById[$document.subject_id] = $document
  }

$documents = foreach ($subjectId in $subjectOrder) {
  if ($documentsById.ContainsKey($subjectId)) { $documentsById[$subjectId] }
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# Appendix C — Consolidated Maturity Matrix')
$lines.Add('')
$lines.Add('| Subject | Foundational | Advanced | Expert 2026 |')
$lines.Add('|---|---|---|---|')
foreach ($document in $documents) {
  $subject = Escape-MarkdownCell ("{0} — {1}" -f $document.subject_id, $document.subject_title)
  $foundational = Escape-MarkdownCell $document.maturity_matrix.foundational
  $advanced = Escape-MarkdownCell $document.maturity_matrix.advanced
  $expert = Escape-MarkdownCell $document.maturity_matrix.expert_2026
  $lines.Add("| $subject | $foundational | $advanced | $expert |")
}

$lines.Add('')
$lines.Add('# Appendix D — Taxonomy and Isolated-Research Dispatch Record')
$lines.Add('')
$lines.Add('## D.1 Master taxonomy')
$lines.Add('')
$readmePath = Join-Path $PSScriptRoot 'README.md'
$readmeText = Get-Content -Raw -LiteralPath $readmePath
$taxonomyMatch = [regex]::Match($readmeText, '(?s)## Master taxonomy\s*(.*?)\s*## Taxonomy construction evidence\s*(.*?)\s*## Dispatch protocol')
if ($taxonomyMatch.Success) {
  foreach ($line in ($taxonomyMatch.Groups[1].Value.Trim() -split "`r?`n")) { $lines.Add($line) }
  $lines.Add('')
  $lines.Add('## D.2 Taxonomy construction evidence')
  $lines.Add('')
  foreach ($line in ($taxonomyMatch.Groups[2].Value.Trim() -split "`r?`n")) { $lines.Add($line) }
}

$lines.Add('')
$lines.Add('## D.3 Exact prompt protocol and subject substitutions')
$lines.Add('')
$lines.Add('The following record is copied into the compiled manual from `research/dispatch-prompts.md`. It preserves the model/inference settings, context isolation, exact common prompt text, subject-specific substitutions, output paths, and the two editorially distinct but criteria-equivalent suffixes actually dispatched.')
$lines.Add('')
$dispatchPath = Join-Path $PSScriptRoot 'dispatch-prompts.md'
$dispatchLines = Get-Content -LiteralPath $dispatchPath
foreach ($line in $dispatchLines) {
  if ($line -eq '# Exact Isolated-Research Prompt Protocol') { continue }
  $lines.Add($line)
}

$evidenceEntries = [System.Collections.Generic.List[object]]::new()
foreach ($document in $documents) {
  for ($index = 0; $index -lt $document.primary_evidence.Count; $index++) {
    $evidence = $document.primary_evidence[$index]
    $label = Evidence-Label $document.subject_id ($index + 1)
    $evidenceEntries.Add([pscustomobject]@{
      Label = $label
      SubjectId = $document.subject_id
      SubjectTitle = $document.subject_title
      SourceTitle = [string]$evidence.source_title
      Authors = [string]$evidence.authors_or_institution
      Year = [int]$evidence.year
      SourceType = [string]$evidence.source_type
      Url = [string]$evidence.doi_or_url
      Excerpt = [string]$evidence.verbatim_excerpt
    })
  }
}

$lines.Add('')
$lines.Add('# Appendix E — Academic Bibliography and Quotation Index')
$lines.Add('')
$lines.Add('## E.1 Bibliography')
$lines.Add('')
$uniqueSources = $evidenceEntries | Group-Object { $_.Url.Trim().ToLowerInvariant() } | Sort-Object { $_.Group[0].Authors }, { $_.Group[0].Year }, { $_.Group[0].SourceTitle }
foreach ($group in $uniqueSources) {
  $source = $group.Group[0]
  $labels = ($group.Group | ForEach-Object { $_.Label }) -join '; '
  $lines.Add("- **[$labels]** $($source.Authors) ($($source.Year)). *$($source.SourceTitle).* $($source.SourceType). [$($source.Url)]($($source.Url))")
}

$lines.Add('')
$lines.Add('## E.2 Verified short-quotation index')
$lines.Add('')
$lines.Add('Each excerpt is retained exactly as supplied by the isolated researcher and is limited to at most 20 words per source in this corpus. The bibliography above provides the authoritative source link.')
foreach ($document in $documents) {
  $lines.Add('')
  $lines.Add("### $($document.subject_id) — $($document.subject_title)")
  $lines.Add('')
  for ($index = 0; $index -lt $document.primary_evidence.Count; $index++) {
    $evidence = $document.primary_evidence[$index]
    $label = Evidence-Label $document.subject_id ($index + 1)
    $excerpt = ([string]$evidence.verbatim_excerpt).Replace("`r", ' ').Replace("`n", ' ')
    $title = ([string]$evidence.source_title).Replace("`r", ' ').Replace("`n", ' ')
    $lines.Add(('- **[{0}]** “{1}” — *{2}*.' -f $label, $excerpt, $title))
  }
}

$lines.Add('')
$lines.Add('## E.3 Corpus audit summary')
$lines.Add('')
$lines.Add("- Subject deliverables present: $($documents.Count) of $($subjectOrder.Count).")
$lines.Add("- Evidence entries: $($evidenceEntries.Count).")
$lines.Add("- Unique DOI/URL records: $($uniqueSources.Count).")
$lines.Add("- Peer-reviewed ACM/IEEE entries: $(($evidenceEntries | Where-Object { $_.SourceType -in @('ACM','IEEE') }).Count).")
$lines.Add("- ISO/formal-standard entries: $(($evidenceEntries | Where-Object { $_.SourceType -in @('ISO','Formal_Standard') }).Count).")
$lines.Add("- University-courseware entries: $(($evidenceEntries | Where-Object { $_.SourceType -eq 'University_Courseware' }).Count).")

[System.IO.File]::WriteAllLines($OutputPath, $lines, [System.Text.UTF8Encoding]::new($false))
Write-Output $OutputPath
