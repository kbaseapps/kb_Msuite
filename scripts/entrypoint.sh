#!/usr/bin/env bash
set -euo pipefail

log() { echo "[$(date -Ins)] $*"; }

# --------- Config ---------
export CHECKM_DATA_PATH="${CHECKM_DATA_PATH:-/data/checkm_data}"
READY_FILE="/data/__READY__"
# You can override the DB URL via CHECKM_DB_URL if needed
DB_URL="${CHECKM_DB_URL:-https://data.ace.uq.edu.au/public/CheckM_databases/checkm_data_2015_01_16.tar.gz}"
DB_TGZ="$(basename "$DB_URL")"
# --------------------------

log "Initialize module"

# Sanity: ensure checkm is on PATH
if ! command -v checkm >/dev/null 2>&1; then
  log "ERROR: 'checkm' not found on PATH."
  exit 1
fi

# Write DATA_CONFIG into the live checkm package location (version-agnostic)
log "Configuring CheckM DATA_CONFIG -> ${CHECKM_DATA_PATH}"
mkdir -p "${CHECKM_DATA_PATH}"
python3 - <<'PY'
import importlib, pathlib, os, sys
try:
    pkg = importlib.import_module('checkm')
except Exception as e:
    print("ERROR: cannot import 'checkm':", e, file=sys.stderr)
    sys.exit(1)
cfg = pathlib.Path(pkg.__file__).parent / 'DATA_CONFIG'
root = os.environ.get('CHECKM_DATA_PATH', '/data/checkm_data').rstrip('/') + '\n'
cfg.write_text(root)
print("Set", cfg, "->", root.strip())
PY

# Helper: downloader (wget or curl)
downloader() {
  local out="$1" url="$2"
  if command -v wget >/dev/null 2>&1; then
    wget -nv -O "$out" "$url"
  elif command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "$out" "$url"
  else
    return 2
  fi
}

# If already initialized, skip heavy work
if [[ -f "${READY_FILE}" ]]; then
  log "Reference data already initialized (${READY_FILE} present)."
else
  log "Reference data initialization"
  if [[ -d "${CHECKM_DATA_PATH}" ]] && [[ -n "$(ls -A "${CHECKM_DATA_PATH}" 2>/dev/null || true)" ]]; then
    log "Existing content found in ${CHECKM_DATA_PATH}; registering with CheckM."
    checkm data setRoot "${CHECKM_DATA_PATH}" || true
    touch "${READY_FILE}"
  else
    log "No DB found. Downloading: ${DB_URL}"
    tmp="/tmp/${DB_TGZ}"
    if downloader "${tmp}" "${DB_URL}"; then
      log "Extracting DB into /data"
      mkdir -p /data
      tar -xzf "${tmp}" -C /data
      rm -f "${tmp}"

      # If tar created /data/checkm_data and our root differs, move contents
      if [[ "${CHECKM_DATA_PATH}" != "/data/checkm_data" ]] && [[ -d "/data/checkm_data" ]]; then
        log "Relocating DB to ${CHECKM_DATA_PATH}"
        mkdir -p "${CHECKM_DATA_PATH}"
        shopt -s dotglob
        mv /data/checkm_data/* "${CHECKM_DATA_PATH}/" || true
        rmdir /data/checkm_data || true
      fi

      checkm data setRoot "${CHECKM_DATA_PATH}" || true
      touch "${READY_FILE}"
    else
      log "WARNING: Could not download DB (wget/curl missing or network blocked)."
      # Register an empty root so the app can still start if your workflow doesn’t need the DB immediately.
      checkm data setRoot "${CHECKM_DATA_PATH}" || true
      # Do NOT create READY if we truly didn’t fetch data:
      # uncomment the next line to allow boot without DB:
      # touch "${READY_FILE}"
    fi
  fi
fi

if [[ ! -f "${READY_FILE}" ]]; then
  log "ERROR: __READY__ file is not detected. Reference data initialization wasn't done correctly."
  exit 1
fi

log "Init complete."
exec "$@"
