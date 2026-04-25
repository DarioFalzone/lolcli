Param(
  [string]$Lang = "es_AR",
  [string]$Out = "items_ddragon.csv",
  [string]$ImagesDir = "lolitems"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# ------------- logging ----------------
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$LogDir = Join-Path "." "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir ("ddragon_items_{0}.log" -f $ts)
$TranscriptFile = Join-Path $LogDir ("ddragon_items_transcript_{0}.txt" -f $ts)

function Write-Log([string]$msg) {
  $line = ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg)
  Add-Content -Path $LogFile -Value $line
}
function Log-Error($err) {
  try {
    $lines = @()
    $lines += "---- ERROR ----"
    $lines += ("Type: {0}" -f $err.Exception.GetType().FullName)
    $lines += ("Message: {0}" -f $err.Exception.Message)
    $lines += ("Category: {0}" -f $err.CategoryInfo)
    $lines += ("FQID: {0}" -f $err.FullyQualifiedErrorId)
    if ($err.InvocationInfo) {
      $lines += ("Script: {0}" -f $err.InvocationInfo.ScriptName)
      $lines += ("Line: {0}" -f $err.InvocationInfo.ScriptLineNumber)
      $lines += ("Position: {0}" -f $err.InvocationInfo.PositionMessage)
    }
    if ($err.ScriptStackTrace) { $lines += ("Stack: {0}" -f $err.ScriptStackTrace) }
    try {
      $resp = $err.Exception.Response
      if ($resp) {
        $lines += ("HTTP: {0} {1}" -f [int]$resp.StatusCode, $resp.StatusDescription)
        $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $body = $sr.ReadToEnd()
        if ($body) { $lines += ("HTTP Body: {0}" -f $body) }
      }
    } catch {}
    $lines += "--------------"
    foreach($l in $lines){ Write-Log $l }
  } catch {
    Write-Log ("Log-Error failed: {0}" -f $_.Exception.Message)
  }
}

try { Start-Transcript -Path $TranscriptFile -Append -ErrorAction SilentlyContinue | Out-Null } catch {}

# ------------- ASCII TUI (no special chars) -------------
$w = 100
try { $w = $Host.UI.RawUI.WindowSize.Width } catch {}
if ($w -lt 80) { $w = 80 }

function Draw-Header {
  Clear-Host
  $title = "LoL Data Dragon - Items Fetcher"
  $bar = ('-' * ($w-2))
  Write-Host ("+" + $bar + "+")
  $line = ("| {0} |" -f $title.PadRight($w-4))
  Write-Host $line
  Write-Host ("+" + $bar + "+")
}
function Draw-Line([string]$label, [string]$value) {
  $text = ("{0,-18} {1}" -f $label, $value)
  if ($text.Length -gt ($w-4)) { $text = $text.Substring(0, $w-7) + "..." }
  Write-Host ("| " + $text.PadRight($w-4) + " |")
}
function Draw-Separator { Write-Host ("+" + ('=' * ($w-2)) + "+") }
function Draw-Footer { Write-Host ("+" + ('-' * ($w-2)) + "+") }
function Draw-Progress([int]$pct,[string]$msg) {
  $width = [Math]::Max(20, $w-30)
  $fill = [Math]::Floor(($pct/100)*$width)
  $bar = ('#' * $fill) + ('-' * ($width - $fill))
  $line = ("{0,3}% {1}" -f $pct, $msg)
  $content = "| " + $bar + " " + $line.PadRight($w-($width+5)) + " |"
  Write-Host $content
}

# ------------- Data Dragon helpers -------------
function Get-Version {
  Write-Log "Fetching versions.json"
  return (Invoke-RestMethod -Uri "https://ddragon.leagueoflegends.com/api/versions.json")[0]
}
function Get-Items([string]$ver,[string[]]$langTry) {
  foreach($lg in $langTry) {
    try {
      $url = "https://ddragon.leagueoflegends.com/cdn/$ver/data/$lg/item.json"
      Write-Log ("Trying {0} -> {1}" -f $lg, $url)
      $tmp = Invoke-RestMethod -Uri $url
      $count = ($tmp.data.PSObject.Properties).Count
      Write-Log ("Items received ({0}): {1}" -f $lg, $count)
      if ($count -gt 0) { return ,@($lg,$tmp) }
    } catch {
      Log-Error $_
    }
  }
  throw ("Could not fetch item.json in languages: {0}" -f ($langTry -join ", "))
}
function Build-Rows($items,$ver) {
  $BASE = "https://ddragon.leagueoflegends.com/cdn"
  $rows = foreach($p in $items.data.PSObject.Properties) {
    $id = $p.Name; $it = $p.Value
    $name = $it.name
    $image_url = "$BASE/$ver/img/item/" + $it.image.full
    $teorica = $it.plaintext
    $stats = $it.stats
    $tecnica = ($stats.PSObject.Properties | Where-Object { $_.Value -ne 0 -and $_.Value -ne $null } |
      ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; '
    [PSCustomObject]@{
      id=$id; nombre=$name; imagen_url=$image_url;
      explicacion_teorica=$teorica; explicacion_tecnica=$tecnica
    }
  }
  return $rows
}

$ExitCode = 0
try {
  Write-Log "Start: Lang=$Lang Out=$Out ImagesDir=$ImagesDir"

  $ver = Get-Version
  $langs = @($Lang,'es_ES','en_US') | Select-Object -Unique
  $got = Get-Items -ver $ver -langTry $langs
  $langUsed = $got[0]; $items = $got[1]
  $rows = Build-Rows -items $items -ver $ver
  $rows | Export-Csv -Path $Out -Encoding UTF8 -NoTypeInformation
  Write-Log ("CSV exported: {0} rows={1}" -f $Out, $rows.Count)

  if (-not (Test-Path $ImagesDir)) { New-Item -ItemType Directory -Path $ImagesDir | Out-Null }
  $src = New-Object System.Collections.Generic.List[string]
  $dst = New-Object System.Collections.Generic.List[string]
  $already = 0
  foreach($r in $rows) {
    $fn = Join-Path $ImagesDir ([IO.Path]::GetFileName($r.imagen_url))
    if (Test-Path $fn) { $already++ } else { $src.Add($r.imagen_url); $dst.Add($fn) }
  }
  Write-Log ("Images existing={0} to_download={1}" -f $already, $src.Count)

  $useBits = $true
  $job = $null
  if ($src.Count -gt 0) {
    try {
      Import-Module BitsTransfer -ErrorAction Stop
      $job = Start-BitsTransfer -Source $src -Destination $dst -Asynchronous -DisplayName ("lolitems-{0}" -f $ts) -Description "DDragon images"
      Write-Log ("BITS job started: {0} totalFiles={1}" -f $job.Id, $job.FilesTotal)
    } catch {
      Log-Error $_
      $useBits = $false
      Write-Log "BITS not available, falling back to sequential downloads."
    }
  }

  if ($useBits -and $job -ne $null) {
    $done = $false
    while(-not $done) {
      Draw-Header
      Draw-Line "Version" $ver
      Draw-Line "Language" $langUsed
      Draw-Line "Items" ($rows.Count.ToString())
      Draw-Line "CSV" (Resolve-Path $Out).Path
      Draw-Line "Images" (Resolve-Path $ImagesDir).Path
      Draw-Separator

      try { $job = Get-BitsTransfer -Id $job.Id } catch {}
      $state = $job.JobState.ToString()
      $filesTotal = $job.FilesTotal + $already
      $filesDone = $job.FilesTransferred + $already
      $bt = [double]$job.BytesTransferred
      $btot = [double]$job.BytesTotal
      $pct = if ($btot -gt 0) { [math]::Round(($bt/$btot)*100) } else { [math]::Round((100.0 * $filesDone / [math]::Max(1,$filesTotal))) }

      Draw-Line "State" $state
      Draw-Progress $pct ("{0} / {1} files" -f $filesDone, $filesTotal)
      Draw-Separator
      Draw-Line "Keys" "[Q] Cancel"
      Draw-Footer

      if ([Console]::KeyAvailable) {
        $k = [Console]::ReadKey($true)
        if ($k.Key -eq 'Q') {
          Write-Log "User cancel requested"
          try { Remove-BitsTransfer -Id $job.Id -Confirm:$false } catch { Log-Error $_ }
          throw "Cancelled by user."
        }
      }

      switch ($state) {
        "Transferred" { Complete-BitsTransfer -Id $job.Id; Write-Log "BITS completed"; $done = $true }
        "Error" {
          $err = $job | Select-Object -ExpandProperty Error
          Log-Error $err
          throw "BITS failed."
        }
        default { Start-Sleep -Milliseconds 200 }
      }
    }
  }
  else {
    # sequential fallback
    $total = $src.Count
    $ok=0; $fail=0
    for ($i=0; $i -lt $total; $i++) {
      $url = $src[$i]
      $fn  = $dst[$i]
      try { Invoke-WebRequest -Uri $url -OutFile $fn -ErrorAction Stop; $ok++ }
      catch { Log-Error $_; $fail++ }
      $pct = [math]::Round(100.0 * ($i+1) / [math]::Max(1,$total))
      Draw-Header
      Draw-Line "Version" $ver
      Draw-Line "Language" $langUsed
      Draw-Line "Items" ($rows.Count.ToString())
      Draw-Line "CSV" (Resolve-Path $Out).Path
      Draw-Line "Images" (Resolve-Path $ImagesDir).Path
      Draw-Separator
      Draw-Line "State" ("Downloading {0}/{1}" -f ($i+1),$total)
      Draw-Progress $pct ("ok={0} fail={1}" -f $ok,$fail)
      Draw-Footer
    }
    Write-Log ("Downloads done. ok={0} fail={1}" -f $ok,$fail)
  }

  Draw-Header
  Draw-Line "Version" $ver
  Draw-Line "Language" $langUsed
  Draw-Line "Items" ($rows.Count.ToString())
  Draw-Line "CSV" (Resolve-Path $Out).Path
  Draw-Line "Images" (Resolve-Path $ImagesDir).Path
  Draw-Separator
  Draw-Line "Result" "OK - CSV and images ready"
  Draw-Progress 100 "Completed"
  Draw-Separator
  Draw-Line "Log" (Resolve-Path $LogFile).Path
  if (Test-Path $TranscriptFile) { Draw-Line "Transcript" (Resolve-Path $TranscriptFile).Path }
  Draw-Footer
  Write-Log "End OK"
}
catch {
  Log-Error $_
  try {
    Draw-Header
    Draw-Line "ERROR" "See log files below"
    Draw-Separator
    Draw-Line "Log" (Resolve-Path $LogFile).Path
    if (Test-Path $TranscriptFile) { Draw-Line "Transcript" (Resolve-Path $TranscriptFile).Path }
    Draw-Separator
    Draw-Line "Detail" ($_.Exception.Message)
    Draw-Footer
  } catch {}
  exit 1
}
finally {
  try { Stop-Transcript | Out-Null } catch {}
}
