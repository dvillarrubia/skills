# Instala una skill de este repo en Claude Code y/o Google Antigravity (Windows PowerShell).
#
# Uso (pega en PowerShell, cambiando el nombre de la skill y el destino):
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/dvillarrubia/skills/main/install.ps1))) content-prioritization-ai-search all
#
# Destino: claude | antigravity | all (por defecto: all)
# Si la skill ya estaba instalada, se sustituye por la última versión.
param(
    [Parameter(Position = 0)][string]$Skill,
    [Parameter(Position = 1)][ValidateSet('claude', 'antigravity', 'all')][string]$Target = 'all'
)
$ErrorActionPreference = 'Stop'
$Repo = 'dvillarrubia/skills'
$Branch = 'main'

if (-not $Skill) {
    Write-Host "Uso: install.ps1 <skill> [claude|antigravity|all]"
    Write-Host "Skills disponibles: https://github.com/$Repo"
    return
}

$claude = Join-Path $HOME '.claude\skills'
$agCli  = Join-Path $HOME '.gemini\antigravity-cli\skills'
$agApp  = Join-Path $HOME '.gemini\config\skills'
switch ($Target) {
    'claude'      { $dests = @($claude) }
    'antigravity' { $dests = @($agCli, $agApp) }
    'all'         { $dests = @($claude, $agCli, $agApp) }
}

$tmp = Join-Path ([IO.Path]::GetTempPath()) ("skills-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    if ($env:SKILLS_SRC) {
        $srcRoot = $env:SKILLS_SRC   # para pruebas locales
    } else {
        Write-Host "Descargando $Repo..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $zip = Join-Path $tmp 'repo.zip'
        Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath $tmp
        $srcRoot = Join-Path $tmp "skills-$Branch"
    }

    $src = Join-Path $srcRoot $Skill
    if (-not (Test-Path (Join-Path $src 'SKILL.md'))) {
        Write-Host "No existe la skill '$Skill' en el repo. Disponibles:" -ForegroundColor Red
        Get-ChildItem $srcRoot -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
            ForEach-Object { Write-Host "  - $($_.Name)" }
        return
    }

    foreach ($dest in $dests) {
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        $skillDest = Join-Path $dest $Skill
        if (Test-Path $skillDest) { Remove-Item -Recurse -Force $skillDest }
        Copy-Item -Recurse -Path $src -Destination $skillDest
        Write-Host "Instalada en $skillDest" -ForegroundColor Green
    }

    if (Test-Path (Join-Path $src 'requirements.txt')) {
        Write-Host ""
        Write-Host "Esta skill usa Python. Instala sus dependencias con:"
        Write-Host "  py -3 -m pip install -r `"$(Join-Path $dests[0] $Skill)\requirements.txt`""
    }
    Write-Host ""
    Write-Host "Listo. Reinicia Claude Code / Antigravity para que detecte la skill."
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
