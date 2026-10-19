# Get the latest version of the skill (keeps your keys, Drive paths and job folders untouched).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
git pull --ff-only
powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkillOnly
