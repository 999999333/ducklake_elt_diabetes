<#
  run_pipeline.ps1
  ---------------------------------------------------------------------------
  • Ensures uv is installed
  • uv sync → creates/updates .venv
  • uv run  → raw_download.py, ingest_dwh.py
  • Activates .venv
  • cd transformation\ → dbt run / docs / build     (plain dbt, inside venv)
  • ALWAYS: deactivate venv + return to original dir, then wait for ENTER
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# -------- tracking flags & paths --------------------------------------------
$StartPath       = Get-Location          # where the script began
$VenvActivated   = $false                # toggled after successful activation
$OverallError    = $null                 # set in outer catch

# -------- convenience helpers ------------------------------------------------
function Run-Step {
    param(
        [Parameter(Mandatory)][string] $Desc,
        [Parameter(Mandatory)][string] $Cmd,
        [string] $Hint = ""
    )
    Write-Host "`n➤ $Desc" -ForegroundColor Cyan
    try {
        & cmd /c "$Cmd"
        if ($LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
    } catch {
        Write-Host "✗ $Desc failed ($_)." -ForegroundColor Red
        if ($Hint) { Write-Host "  Possible fix → $Hint" -ForegroundColor Yellow }
        if (Should-Continue) {
            Write-Host "…continuing" -ForegroundColor Cyan
        } else {
            throw     # abort the pipeline → outer try/catch handles cleanup
        }
    }
}

# For activation we need a tiny variant that runs *in* PowerShell
function Run-PS {
    param(
        [Parameter(Mandatory)][string] $Desc,
        [Parameter(Mandatory)][ScriptBlock] $Block,
        [string] $Hint = ""
    )
    Write-Host "`n➤ $Desc" -ForegroundColor Cyan
    try {
        & $Block
    } catch {
        Write-Host "✗ $Desc failed ($_)." -ForegroundColor Red
        if ($Hint) { Write-Host "  Possible fix → $Hint" -ForegroundColor Yellow }
        throw
    }
}

# -------- hints --------------------------------------------------------------
$H = @{
    install_uv     = "Install/upgrade pip first:  py -m pip install -U pip"
    uv_sync        = "Check pyproject.toml / requirements.* and required Python version."
    duckdb_setup   = "Try rerunning. Check if python script can correctly reference .duckdb/*.json file"
    duckdb_ui      = "Try manually running 'duckdb -ui' in terminal and then killing it. There is big chance that your last session doesn't properly closed connection to db."
    py_raw         = "Add missing libs to pyproject & rerun 'uv sync'."
    py_ingest      = "Verify DB credentials in environment variables."
    venv_activate  = "Run  Set-ExecutionPolicy -Scope Process Bypass  if activation is blocked."
    dbt_run        = "Run '.venv\\Scripts\\dbt debug' to test the connection."
    dbt_docs       = "Did 'dbt run' succeed?  Inspect logs in transformation\\target\\."
    dbt_build      = "You can see that 'dbt build' failed. A few lines above you can see why → because data quality check wasn't succesfull and that is right (induced mistake to show capabilities of dbt's data testing :).Failing test (relationships_bridge_patient_visits_diagnosis__diagnosis_id___diagnosis_id__ref_dim_diagnosis) pinpoints what is failing, so we know that in this case we have to investigate referential integrity, between those 2 tables, because 12 rows breaks integrity expectation. "
}

function Should-Continue {
    param(
        [string]$Prompt = "Press ENTER to continue, or type X and ENTER to abort..."
    )
    $ans = Read-Host $Prompt
    return [string]::IsNullOrWhiteSpace($ans)   # TRUE => keep going
}

# ========== MAIN =============================================================
try {
    # 1) uv bootstrap ---------------------------------------------------------
    if (-not (Get-Command uv.exe -ErrorAction SilentlyContinue)) {
        Run-Step "Installing uv (user-level)" `
                 "python -m pip install --upgrade --user uv" `
                 $H.install_uv
    }

    # 2) sync dependencies ----------------------------------------------------
    Run-Step "uv sync" "uv sync" $H.uv_sync

    # 3) project’s Python scripts via uv run ----------------------------------
    Run-Step "setup_duckdb_ui.py"  "uv run ingestion/setup_duckdb_ui.py"  $H.duckdb_ui
    Run-Step "raw_download.py" "uv run ingestion/raw_download.py" $H.py_raw
    Run-Step "ingest_dwh.py"  "uv run ingestion/ingest_dwh.py"  $H.py_ingest

    # 4) Activate .venv for dbt ----------------------------------------------
    $Act = ".\.venv\Scripts\Activate.ps1"
    if (!(Test-Path $Act)) { throw ".venv not found – did 'uv sync' succeed?" }

    Run-PS "Activating .venv" { . $Act; $global:VenvActivated = $true } $H.venv_activate

    # 5) dbt block inside transformation/ -------------------------------------
    $Transform = "transformation"
    if (-not (Test-Path $Transform)) {
        throw "'$Transform' directory does not exist – adjust path in run_pipeline.ps1."
    }

    Set-Location $Transform          # (we'll jump back in the FINALLY block)

    Run-Step "dbt run"               "dbt run"                       $H.dbt_run
    Run-Step "dbt docs generate"     "dbt docs generate --static"    $H.dbt_docs
    Run-Step "Open docs"             "start .\target\static_index.html"
    Run-Step "dbt build"             "dbt build"                     $H.dbt_build
    Set-Location $StartPath
    Run-Step "duckdb -ui"            "duckdb -ui"                    $H.duckdb_ui



}
catch {
    $OverallError = $_              # remember for final report
}
finally {
    # ---- clean-up: always run ----------------------------------------------
    if ($VenvActivated) {
        try {
            if (Get-Command deactivate -ErrorAction SilentlyContinue) {
                deactivate
            } elseif (Test-Path ".\.venv\Scripts\Deactivate.ps1") {
                . .\.venv\Scripts\Deactivate.ps1
            }
        } catch {
            Write-Warning "Deactivation raised an error: $_"
        }
    }

    # return to the directory where we launched the script
    Set-Location $StartPath

    # final message
    Write-Host ""
    if ($OverallError) {
        Write-Host "✗ Pipeline aborted." -ForegroundColor Red
    } else {
        Write-Host "✓ All steps completed successfully." -ForegroundColor Green
    }

    Read-Host "Press ENTER to close..."
}
