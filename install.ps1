# CarVendors Video Studio — install / update on Windows (PowerShell). Safe to re-run.
#   powershell -ExecutionPolicy Bypass -File install.ps1          full install
#   powershell -ExecutionPolicy Bypass -File install.ps1 -SkillOnly   only copy the skill (used by update.ps1)
param([switch]$SkillOnly)
$ErrorActionPreference = "Stop"
$Here  = Split-Path -Parent $MyInvocation.MyCommand.Path
$Skill = Join-Path $env:USERPROFILE ".claude\skills\carvendors-studio"
$Venv  = Join-Path $env:USERPROFILE ".cache\carvendors-studio\venv"

function Copy-Skill {
  New-Item -ItemType Directory -Force -Path (Split-Path $Skill) | Out-Null
  if (Test-Path $Skill) { Remove-Item -Recurse -Force $Skill }
  Copy-Item -Recurse -Force (Join-Path $Here "skills\carvendors-studio") $Skill
  Write-Host "skill installed: $(Get-Content (Join-Path $Here 'VERSION'))"
}
if ($SkillOnly) { Copy-Skill; exit 0 }

Write-Host "== 1/5 tools (winget: ffmpeg, node, python, chrome)"
foreach ($id in @("Gyan.FFmpeg", "OpenJS.NodeJS.LTS", "Python.Python.3.12", "Google.Chrome", "Git.Git")) {
  winget list --id $id -e | Out-Null
  if ($LASTEXITCODE -ne 0) { winget install --id $id -e --accept-source-agreements --accept-package-agreements }
}
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "== 2/5 skill"
Copy-Skill

Write-Host "== 3/5 Python env for the skill (numpy + scipy)"
$Py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Py)) { py -3 -m venv $Venv }
& $Py -m pip install --quiet --upgrade pip numpy scipy

Write-Host "== 4/5 keys file + workspace"
$Cfg = Join-Path $env:USERPROFILE ".config\video-studio"
New-Item -ItemType Directory -Force -Path $Cfg | Out-Null
$EnvF = Join-Path $Cfg ".env"
if (-not (Test-Path $EnvF)) { "ELEVENLABS_API_KEY=your_api_key_here`nELEVENLABS_VOICE_EN=JBFqnCBsd6RMkjVDRZzb" | Set-Content -Encoding UTF8 $EnvF }
$Ws = Join-Path $env:USERPROFILE "Projects\videos"
New-Item -ItemType Directory -Force -Path $Ws | Out-Null
foreach ($f in @("AGENTS.md", "CLAUDE.md", "TEAM_GUIDE.md", "CARVENDORS_CONTEXT.md")) { Copy-Item -Force (Join-Path $Here "workspace\$f") (Join-Path $Ws $f) }
Push-Location $Ws; try { npx --yes hyperframes@latest --version | Out-Null } catch {}; Pop-Location

Write-Host "== 5/5 check"
& $Py (Join-Path $Skill "tools\doctor.py")
Write-Host ""
Write-Host "Done. Google Drive for desktop must be running. If Drive shows MISSING:"
Write-Host "  $Py $Skill\tools\paths.py drive `"G:\My Drive`""
Write-Host "Only for new voiceovers: put YOUR ElevenLabs key in $EnvF"
Write-Host "Open Claude Code in $Ws and say: plan videos 1-10  /  edit video 7"
