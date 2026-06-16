# setup.ps1 - run from project root
$minMajor = 3; $minMinor = 8

# check python executable
if(-not (Get-Command python -ErrorAction SilentlyContinue)) { Write-Error "Python not found on PATH"; exit 1 }

$ver = (python --version 2>&1).Split(' ')[1]
$parts = $ver.Split('.')
[int]$maj = $parts[0]; [int]$min = $parts[1]
if($maj -lt $minMajor -or ($maj -eq $minMajor -and $min -lt $minMinor)){ Write-Error "Python $minMajor.$minMinor+ required (found $ver)"; exit 1 }

# install requirements
python -m pip install --user -r .\requirements.txt

# check environment vars for credentials
$required = @('GOOGLE_APPLICATION_CREDENTIALS','FIREBASE_SERVICE_ACCOUNT','GOOGLE_API_KEY')
$missing = $required | Where-Object { -not [string]::IsNullOrEmpty($env:$_) -eq $false }
if($missing.Count -gt 0){ Write-Host "WARNING: Missing one or more credential env vars:"; $required | ForEach-Object { if(-not $env:$_) { Write-Host " - $_ (set this to path or key)" } } }

# start server and smoke test
$proc = Start-Process -FilePath python -ArgumentList "app.py" -PassThru
$ok = $false
for($i=0;$i -lt 30;$i++){
  Start-Sleep -Seconds 1
  try{
    $r = Invoke-WebRequest -Uri http://localhost:5000 -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if($r.StatusCode -eq 200){ $ok = $true; break }
  } catch { }
}
if($ok){ Write-Host "Server responded at http://localhost:5000" } else { Write-Warning "Server did not respond within 30s" }

# stop server process
Try { Stop-Process -Id $proc.Id -ErrorAction SilentlyContinue } Catch {}
