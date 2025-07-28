#!/bin/bash

echo "🔧 Installing Git hooks..."

ln -sf ../../tools/git-hooks/pre-commit .git/hooks/pre-commit
ln -sf ../../tools/git-hooks/pre-push .git/hooks/pre-push

chmod +x .git/hooks/pre-commit .git/hooks/pre-push

echo "✅ Hooks installed!"
