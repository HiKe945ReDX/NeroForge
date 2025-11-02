#!/usr/bin/env bash
# 🔥 GUIDORA ULTRA SPLITTER v11.0
# Splits backend & frontend into 3 each. Avoids node_modules, __pycache__, .git, venvs, Python libs.
# Produces ~11 clean text files — fully self-contained collector.

set -euo pipefail
IFS=$'\n\t'
TS=$(date +%Y%m%d_%H%M%S)
echo "🚀 GUIDORA ULTRA SPLITTER v11.0"
echo "🕒 Timestamp: $TS"
echo ""

# OUTPUT FILES
TREE_FILE="guidora_repo_tree_${TS}.txt"
DOCKER_FILE="guidora_docker_logs_${TS}.txt"
GCP_FILE="guidora_gcp_logs_${TS}.txt"
SYSTEM_FILE="guidora_system_snapshot_${TS}.txt"
BACKEND_A="guidora_backend_partA_${TS}.txt"
BACKEND_B="guidora_backend_partB_${TS}.txt"
BACKEND_C="guidora_backend_partC_${TS}.txt"
FRONTEND_A="guidora_frontend_partA_${TS}.txt"
FRONTEND_B="guidora_frontend_partB_${TS}.txt"
FRONTEND_C="guidora_frontend_partC_${TS}.txt"
STATIC_MISC="guidora_static_misc_${TS}.txt"

# ---------- 1️⃣ REPO TREE ----------
echo "🌲 Generating repo tree..."
{
  echo "=== GUIDORA REPOSITORY TREE ==="
  echo "Generated: $(date)"
  echo ""
  if command -v tree >/dev/null 2>&1; then
    tree -a -I 'node_modules|__pycache__|.git|dist|build|.next|.venv|venv|env|site-packages|dist-packages|.turbo' -h --du .
  else
    find . \
      -path '*/node_modules' -prune -o \
      -path '*/__pycache__' -prune -o \
      -path './.git' -prune -o \
      -path '*/site-packages*' -prune -o \
      -path '*/dist-packages*' -prune -o \
      -print | sed 's|^./||' | sort
  fi
} > "$TREE_FILE"
echo "✅ Repo tree → $TREE_FILE"
echo ""

# ---------- 2️⃣ DOCKER LOGS ----------
echo "🐳 Collecting Docker logs..."
{
  echo "=== GUIDORA DOCKER LOGS ==="
  echo "Generated: $(date)"
  echo ""
  if command -v docker >/dev/null 2>&1; then
    echo "📦 docker ps -a:"
    docker ps -a
    echo ""
    docker-compose ps 2>/dev/null || echo "[No docker-compose file found]"
    echo ""
    docker ps --format '{{.Names}}' | while read -r cname; do
      [[ -z "$cname" ]] && continue
      echo "----- LOGS FOR: $cname -----"
      docker logs --tail=300 "$cname" 2>&1 || echo "[No logs for $cname]"
      echo ""
    done
  else
    echo "⚠️ Docker not installed."
  fi
} > "$DOCKER_FILE"
echo "✅ Docker logs → $DOCKER_FILE"
echo ""

# ---------- 3️⃣ GCP LOGS ----------
echo "☁️ Collecting GCP logs..."
{
  echo "=== GUIDORA GCP LOGS ==="
  echo "Generated: $(date)"
  echo ""
  if command -v gcloud >/dev/null 2>&1; then
    TIME_WINDOW="$(date -u -d '24 hour ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "�� Logs since: $TIME_WINDOW"
    echo ""
    gcloud logging read "timestamp >= \"$TIME_WINDOW\"" --limit 500 --format json 2>/dev/null || echo "[No GCP logs found]"
  else
    echo "⚠️ gcloud not found — skipped."
  fi
} > "$GCP_FILE"
echo "✅ GCP logs → $GCP_FILE"
echo ""

# ---------- 4️⃣ SYSTEM SNAPSHOT ----------
echo "🖥️ Collecting system snapshot..."
{
  echo "=== GUIDORA SYSTEM SNAPSHOT ==="
  echo "Generated: $(date)"
  echo ""
  uname -a 2>/dev/null || true
  echo ""
  df -h 2>/dev/null || true
  echo ""
  free -h 2>/dev/null || true
  echo ""
  docker --version 2>/dev/null || echo "[No Docker]"
  gcloud --version 2>/dev/null || echo "[No gcloud]"
  echo ""
  echo "Top 10 biggest directories:"
  du -sh * 2>/dev/null | sort -hr | head -n 10
} > "$SYSTEM_FILE"
echo "✅ System snapshot → $SYSTEM_FILE"
echo ""

# ---------- 5️⃣ BACKEND CODE (split into 3) ----------
echo "📦 Dumping backend code (3 splits)..."
files=($(find backend -type f \
  \( -name "*.py" -o -name "*.js" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/site-packages/*" \
  -not -path "*/dist-packages/*" \
  -not -path "*/venv/*" \
  -not -path "*/.venv/*" \
  -not -path "./.git/*" 2>/dev/null))
third=$(( ${#files[@]} / 3 ))

{
  echo "=== GUIDORA BACKEND CODE PART A ==="
  for ((i=0; i<third; i++)); do
    echo "----- FILE: ${files[$i]} -----"
    cat "${files[$i]}" 2>/dev/null || echo "[Skipped binary]"
    echo ""
  done
} > "$BACKEND_A"

{
  echo "=== GUIDORA BACKEND CODE PART B ==="
  for ((i=third; i<2*third; i++)); do
    echo "----- FILE: ${files[$i]} -----"
    cat "${files[$i]}" 2>/dev/null || echo "[Skipped binary]"
    echo ""
  done
} > "$BACKEND_B"

{
  echo "=== GUIDORA BACKEND CODE PART C ==="
  for ((i=2*third; i<${#files[@]}; i++)); do
    echo "----- FILE: ${files[$i]} -----"
    cat "${files[$i]}" 2>/dev/null || echo "[Skipped binary]"
    echo ""
  done
} > "$BACKEND_C"

echo "✅ Backend split → $BACKEND_A, $BACKEND_B, $BACKEND_C"
echo ""

# ---------- 6️⃣ FRONTEND CODE (split into 3) ----------
echo "🌐 Dumping frontend code (3 splits)..."
fefiles=($(find frontend -type f \
  \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.html" -o -name "*.css" -o -name "*.json" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/build/*" \
  -not -path "*/.next/*" \
  -not -path "*/dist/*" 2>/dev/null))
fthird=$(( ${#fefiles[@]} / 3 ))

{
  echo "=== GUIDORA FRONTEND CODE PART A ==="
  for ((i=0; i<fthird; i++)); do
    echo "----- FILE: ${fefiles[$i]} -----"
    cat "${fefiles[$i]}" 2>/dev/null || echo "[Skipped binary]"
    echo ""
  done
} > "$FRONTEND_A"

{
  echo "=== GUIDORA FRONTEND CODE PART B ==="
  for ((i=fthird; i<2*fthird; i++)); do
    echo "----- FILE: ${fefiles[$i]} -----"
    cat "${fefiles[$i]}" 2>/dev/null || echo "[Skipped binary]"
    echo ""
  done
} > "$FRONTEND_B"

{
  echo "=== GUIDORA FRONTEND CODE PART C ==="
  for ((i=2*fthird; i<${#fefiles[@]}; i++)); do
    echo "----- FILE: ${fefiles[$i]} -----"
    cat "${fefiles[$i]}" 2>/dev/null || echo "[Skipped binary]"
    echo ""
  done
} > "$FRONTEND_C"

echo "✅ Frontend split → $FRONTEND_A, $FRONTEND_B, $FRONTEND_C"
echo ""

# ---------- 7️⃣ STATIC / MISC ----------
echo "📚 Collecting static & misc..."
{
  echo "=== GUIDORA STATIC & MISC FILES ==="
  echo "Generated: $(date)"
  echo ""
  find . \
    \( -path "./guidora-static/*" -o -path "./scripts/*" -o -path "./config/*" -o -name "*.md" -o -name "*.sh" \) \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/site-packages/*" \
    -not -path "*/dist-packages/*" \
    -not -path "./.git/*" | while read -r f; do
      echo "----- FILE: $f -----"
      cat "$f" 2>/dev/null || echo "[Skipped binary]"
      echo ""
    done
} > "$STATIC_MISC"
echo "✅ Static & misc → $STATIC_MISC"
echo ""

# ---------- ✅ SUMMARY ----------
echo ""
echo "🎯 11 OUTPUTS GENERATED:"
for f in "$TREE_FILE" "$DOCKER_FILE" "$GCP_FILE" "$SYSTEM_FILE" \
         "$BACKEND_A" "$BACKEND_B" "$BACKEND_C" \
         "$FRONTEND_A" "$FRONTEND_B" "$FRONTEND_C" \
         "$STATIC_MISC"; do
  [[ -f "$f" ]] && echo "📄 $f"
done
echo ""
echo "🎉 DONE — GUIDORA ULTRA SPLITTER v11.0 COMPLETED SUCCESSFULLY."
