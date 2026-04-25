Param(
  [int]$LatestN = 6,
  [string]$Out = "lol_patch_notes.json",
  [int]$DetalleChars = 800
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$LogDir = Join-Path $ScriptDir "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir ("fetch_patchnotes_v33b_{0}.log" -f $ts)
$Transcript = Join-Path $LogDir ("fetch_patchnotes_v33b_transcript_{0}.txt" -f $ts)

function Log([string]$m){
  try{
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Add-Content -Path $LogFile -Value $line
  } catch {}
  Write-Host $m
}

# HTTP setup
$UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
$Headers = @{
  "User-Agent" = $UA
  "Accept-Language" = "es-ES,es;q=0.9,en;q=0.8"
}

function Get-Page([string]$url){
  Log ("GET " + $url)
  try {
    return Invoke-WebRequest -Uri $url -UseBasicParsing -Headers $Headers -MaximumRedirection 5 -ErrorAction Stop
  } catch {
    Log ("HTTP ERROR: " + $_.Exception.Message)
    throw
  }
}

# Sources to scan
function Get-TagPages {
  @(
    "https://www.leagueoflegends.com/es-es/news/tags/patch-notes/",
    "https://www.leagueoflegends.com/es-mx/news/tags/patch-notes/",
    "https://www.leagueoflegends.com/en-us/news/tags/patch-notes/"
  )
}
function Get-UpdatesPages {
  @(
    "https://www.leagueoflegends.com/es-es/news/game-updates/",
    "https://www.leagueoflegends.com/es-mx/news/game-updates/",
    "https://www.leagueoflegends.com/en-us/news/game-updates/"
  )
}

# Match absolute/relative links, with or without trailing slash.
$LinkRx = [Regex]@'
(?is)href="(?<link>(?:https?://[^"']+)?/(?:es-es|es-mx|en-us)/news/game-updates/patch-[0-9\-]+-notes/?)"
'@
function VersionFromLink([string]$path){
  $m = [Regex]::Match($path, 'patch-([0-9]{2})-([0-9]{2})-notes', 'IgnoreCase')
  if($m.Success){ return ("{0}.{1}" -f $m.Groups[1].Value, $m.Groups[2].Value) }
  return $null
}

function CollectFrom([string[]]$pages,[int]$need){
  $found = New-Object System.Collections.Generic.List[object]
  foreach($url in $pages){
    try {
      $resp = Get-Page -url $url
      $html = $resp.Content
      $matches = $LinkRx.Matches($html)
      Log ("Links encontrados en " + $url + ": " + $matches.Count)

      foreach($m in $matches){
        $path = $m.Groups['link'].Value
        if ($path -notmatch '^https?://') { $path = "https://www.leagueoflegends.com" + $path }
        $ver = VersionFromLink $path
        if ($ver){ $found.Add([PSCustomObject]@{ version=$ver; url=$path }) }
      }
      if ($found.Count -ge $need) { break }
    } catch {
      Log ("Fallo al leer " + $url + ": " + $_.Exception.Message)
    }
  }
  return $found
}

function HtmlToText([string]$frag){
  return ($frag -replace '<script.*?</script>',' ' -replace '<style.*?</style>',' ' -replace '<[^>]+>',' ' -replace '&nbsp;',' ' -replace '&amp;','&' -replace '\s+',' ').Trim()
}

function Format-FechaCorta([string]$iso){
  if(-not $iso){ return "" }
  try { return ([datetime]::Parse($iso)).ToString('dd/MM/yy') } catch { return $iso }
}

function Get-LatestPatchPosts([int]$n) {
  $cand = CollectFrom (Get-TagPages) $n
  if ($cand.Count -lt $n) {
    Log ("Fallback a /news/game-updates/")
    $more = CollectFrom (Get-UpdatesPages) $n
    $cand.AddRange($more)
  }
  if ($cand.Count -eq 0) { throw "No se encontraron enlaces a notas de parche." }

  $seen = New-Object System.Collections.Generic.HashSet[string]
  $uniq = foreach($e in $cand){ if($seen.Add($e.url)){ $e } }

  $ordered = $uniq | Sort-Object @{Expression={ [int]($_.version.Split('.')[0]) }; Descending=$true },
                                  @{Expression={ [int]($_.version.Split('.')[1]) }; Descending=$true }
  $take = $ordered | Select-Object -First $n
  $versionsList = (($take | ForEach-Object { $_.version }) -join ", ")
  Log ("Parches detectados: " + $versionsList)
  return $take
}

function Parse-PatchPage([string]$url,[int]$clip){
  $resp = Get-Page -url $url
  $html = $resp.Content

  $title = ""
  $m = [Regex]::Match($html, "(?is)<h1[^>]*>(.*?)</h1>")
  if($m.Success){ $title = HtmlToText $m.Groups[1].Value }

  $published = ""
  $m2 = [Regex]::Match($html, "(?i)([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:\.]+Z)")
  if($m2.Success){ $published = Format-FechaCorta $m2.Groups[1].Value }

  $h2rx = [Regex]'(?is)<h2[^>]*>(?<h>.*?)</h2>'
  $h3rx = [Regex]'(?is)<h3[^>]*>(?<h>.*?)</h3>'

  $sections = New-Object System.Collections.Generic.List[object]
  $h2m = $h2rx.Matches($html)
  foreach($m in $h2m){
    $labelRaw = $m.Groups['h'].Value
    $label = (HtmlToText $labelRaw)
    $labelNorm = $label.ToLowerInvariant()
    $idxStart = $m.Index + $m.Length
    $sections.Add([PSCustomObject]@{ label=$label; labelNorm=$labelNorm; start=$idxStart })
  }

  # calcular end sin operador ternario (PS 5.1)
  $docLen = $html.Length
  for($i=0; $i -lt $sections.Count; $i++){
    $nextStart = $null
    if ($i -lt ($sections.Count - 1)) {
      $nextStart = $sections[$i+1].start
    } else {
      $nextStart = $docLen
    }
    $sections[$i] | Add-Member -NotePropertyName end -NotePropertyValue $nextStart -Force
  }

  # Construir estructura general de secciones (con subsecciones por h3)
  $seccionesOut = New-Object System.Collections.Generic.List[object]
  foreach($sec in $sections){
    $frag = $html.Substring($sec.start, $sec.end - $sec.start)
    $h3 = $h3rx.Matches($frag)
    $subs = @()
    if($h3.Count -gt 0){
      for($i=0; $i -lt $h3.Count; $i++){
        $titulo = HtmlToText $h3[$i].Groups['h'].Value
        $bstart = $h3[$i].Index + $h3[$i].Length
        $bend = if($i -lt ($h3.Count-1)) { $h3[$i+1].Index } else { $frag.Length }
        $len = [Math]::Max(0, $bend - $bstart)
        $texto = if($len -gt 0) { HtmlToText ($frag.Substring($bstart, $len)) } else { '' }
        if($titulo){ $subs += [PSCustomObject]@{ titulo=$titulo; texto=$texto } }
      }
      $seccionesOut.Add([PSCustomObject]@{ nombre=$sec.label; nombre_norm=$sec.labelNorm; subsecciones=$subs })
    } else {
      $seccionesOut.Add([PSCustomObject]@{ nombre=$sec.label; nombre_norm=$sec.labelNorm; texto=(HtmlToText $frag) })
    }
  }

  # campeones (conveniencia, derivado de secciones)
  $champions = @()
  $champWin = $sections | Where-Object { $_.labelNorm -match 'campeon|champion' } | Select-Object -First 1
  if ($champWin){
    $frag = $html.Substring($champWin.start, $champWin.end - $champWin.start)
    $h3 = $h3rx.Matches($frag)
    for($i=0; $i -lt $h3.Count; $i++){
      $nm = HtmlToText $h3[$i].Groups['h'].Value
      $bstart = $h3[$i].Index + $h3[$i].Length
      $bend = $null
      if ($i -lt ($h3.Count - 1)) {
        $bend = $h3[$i+1].Index
      } else {
        $bend = $frag.Length
      }
      $len = [Math]::Max(0, $bend - $bstart)
      if ($len -gt 0) {
        $block = $frag.Substring($bstart, $len)
        $txt = HtmlToText $block
        if ($nm) {
          $champions += [PSCustomObject]@{
            campeon = $nm
            texto = ($txt.Substring(0, [Math]::Min($clip, $txt.Length)))
          }
        }
      }
    }
  }

  # objetos (conveniencia, derivado de secciones)
  $itemsText = ""
  $itemsWin = $sections | Where-Object { $_.labelNorm -match 'objeto|item' } | Select-Object -First 1
  if ($itemsWin){
    $frag = $html.Substring($itemsWin.start, $itemsWin.end - $itemsWin.start)
    $itemsText = HtmlToText $frag
  }

  return [PSCustomObject]@{
    titulo = $title
    url = $url
    publicado = $published
    secciones = $seccionesOut
    campeones = $champions
    objetos = $itemsText
  }
}

$Exit = 0
try {
  Start-Transcript -Path $Transcript -Append -ErrorAction SilentlyContinue | Out-Null
  Log ("Inicio V3.3b: N="+$LatestN+" Out="+$Out+" Dir="+$ScriptDir+" Clip="+$DetalleChars)
  $posts = Get-LatestPatchPosts -n $LatestN
  if (-not $posts -or $posts.Count -eq 0) { throw "No se encontraron posts de parches despues de fallbacks." }

  $patches = New-Object System.Collections.Generic.List[object]
  foreach($p in $posts){
    Log ("Procesando " + $p.version + " -> " + $p.url)
    $parsed = Parse-PatchPage -url $p.url -clip $DetalleChars
    $parsed | Add-Member -NotePropertyName version -NotePropertyValue $p.version -Force
    $patches.Add($parsed)
  }

  $root = [PSCustomObject]@{
    generado = (Get-Date).ToString("s")
    fuente = "tags+game-updates: es-es, es-mx, en-us"
    total = $patches.Count
    parches = $patches
  }

  $json = $root | ConvertTo-Json -Depth 6
  $outPath = Join-Path $ScriptDir $Out
  $json | Out-File -FilePath $outPath -Encoding utf8

  Log ("OK -> " + $outPath)
  Log ("Log: " + $LogFile)
  Write-Host ""
  Write-Host ("Completado. JSON: " + $outPath)
  Write-Host ("Log: " + $LogFile)
}
catch {
  $Exit = 1
  $msg = $_.Exception.Message
  Log ("ERROR: " + $msg)
  Write-Error $msg
}
finally {
  try { Stop-Transcript | Out-Null } catch {}
  exit $Exit
}
