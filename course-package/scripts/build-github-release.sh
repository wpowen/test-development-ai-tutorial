#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
factory="$root/../career-ai-course-factory"
target="${1:-$root/dist/github-release}"

mkdir -p "$target"
find "$target" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

cp "$root/github/README.md" "$target/README.md"
cp "$root/DISTRIBUTION.md" "$target/DISTRIBUTION.md"
cp "$root/validation-report.md" "$target/validation-report.md"

mkdir -p "$target/.github/workflows" "$target/courses" "$target/site" "$target/docs/research" "$target/skill" "$target/course-package"
cp "$root/.github/workflows/"*.yml "$target/.github/workflows/"
cp "$root/learning-architecture.md" "$target/docs/learning-architecture.md"
cp "$root/course-map.md" "$target/docs/course-map.md"
cp "$root/curriculum-gap-analysis.md" "$target/docs/curriculum-gap-analysis.md"
cp "$root/industry-framework.md" "$target/docs/industry-framework.md"
cp "$root/curriculum.json" "$target/docs/curriculum.json"
cp "$root/research/"* "$target/docs/research/"

rsync -a --exclude '__pycache__/' --exclude '*.pyc' "$factory/" "$target/skill/career-ai-course-factory/"

rsync -a \
  --exclude '.git/' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude '.next/' \
  --exclude '.wrangler/' \
  --exclude '.vinext/' \
  --exclude '.openai/' \
  --exclude 'db/' \
  --exclude 'drizzle/' \
  --exclude 'examples/' \
  "$root/site/" "$target/site/"

rsync -a \
  --exclude '.git/' \
  --exclude '.github/' \
  --exclude '.openai/' \
  --exclude 'dist/' \
  --exclude 'site/' \
  --exclude 'github/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  "$root/" "$target/course-package/"

rsync -a "$root/courses/td-ai-006-rag-eval-ci/" "$target/courses/td-ai-006-rag-eval-ci/"

credential_hits="$(rg -n --pcre2 --hidden --glob '!package-lock.json' '(?<![A-Za-z0-9])(sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gho_[A-Za-z0-9]{20,}|art_v1_[A-Za-z0-9]{20,})' "$target" | rg -v 'sk-live-demo-secret' || true)"
if [[ -n "$credential_hits" ]]; then
  printf '%s\n' "$credential_hits"
  echo "release contains a credential-like token" >&2
  exit 1
fi

python3 "$factory/scripts/validate_career_package.py" "$target/course-package"

source_commit="$(git -C "$root/site" rev-parse HEAD 2>/dev/null || echo unknown)"
file_count="$(find "$target" -type f ! -path '*/.git/*' | wc -l | tr -d ' ')"
jq -n \
  --arg source_commit "$source_commit" \
  --argjson page_count 52 \
  --argjson delivered_page_count 26 \
  --argjson file_count "$file_count" \
  '{schema_version:"1.0", source_commit:$source_commit, page_count:$page_count, delivered_page_count:$delivered_page_count, file_count:$file_count, evidence_level:"fixture-tested; desk-researched; not production-validated"}' \
  > "$target/RELEASE-MANIFEST.json"

echo "$target"
