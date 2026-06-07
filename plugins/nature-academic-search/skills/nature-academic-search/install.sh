#!/usr/bin/env bash
# Academic Search Skill + MCP Server Installer
# Supports: Claude Code, QoderWork (Qoder), and generic MCP clients
# Usage: bash install.sh [PUBMED_EMAIL]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBMED_EMAIL="${1:-user@example.com}"

# --- Platform detection ---
# Detect which AI coding assistant is running this script
if [ -d "${HOME}/.claude" ]; then
    PLATFORM="claude"
    PLATFORM_DIR="${HOME}/.claude"
    PLATFORM_NAME="Claude Code"
elif [ -d "${HOME}/.qoderwork" ]; then
    PLATFORM="qoderwork"
    PLATFORM_DIR="${HOME}/.qoderwork"
    PLATFORM_NAME="QoderWork"
elif [ -d "${HOME}/.qoder" ]; then
    PLATFORM="qoder"
    PLATFORM_DIR="${HOME}/.qoder"
    PLATFORM_NAME="Qoder"
else
    PLATFORM="generic"
    PLATFORM_DIR=""
    PLATFORM_NAME="Unknown"
fi

echo "=== Academic Search Installer ==="
echo "Detected platform: ${PLATFORM_NAME}"
echo "PubMed email: ${PUBMED_EMAIL}"
echo

# 1. Install Python dependencies
echo "[1/4] Installing Python dependencies..."
pip install --quiet mcp requests toml lxml 2>/dev/null || {
    echo "  pip failed, trying pip3..."
    pip3 install --quiet mcp requests toml lxml 2>/dev/null || {
        echo "  WARNING: Could not install Python deps. Install manually:"
        echo "    pip install mcp requests toml lxml"
    }
}

# 2. Install MCP server
echo "[2/4] Installing MCP server..."
if [ -n "${PLATFORM_DIR}" ]; then
    MCP_TARGET="${PLATFORM_DIR}/mcp_servers/academic-search"
    mkdir -p "${MCP_TARGET}"
    cp -r "${SCRIPT_DIR}/mcp-server/"* "${MCP_TARGET}/"
    echo "  Installed to: ${MCP_TARGET}/"
else
    echo "  No standard platform directory found."
    echo "  MCP server source: ${SCRIPT_DIR}/mcp-server/"
    echo "  Copy it manually to your MCP server directory."
fi

# 3. Install Skill files
echo "[3/4] Installing Skill files..."
if [ -n "${PLATFORM_DIR}" ]; then
    SKILL_TARGET="${PLATFORM_DIR}/skills/academic-search"
    mkdir -p "${SKILL_TARGET}"
    cp "${SCRIPT_DIR}/README.md" "${SKILL_TARGET}/" 2>/dev/null || true
    cp "${SCRIPT_DIR}/SKILL.md" "${SKILL_TARGET}/"
    cp -r "${SCRIPT_DIR}/references" "${SKILL_TARGET}/" 2>/dev/null || true
    cp -r "${SCRIPT_DIR}/scripts" "${SKILL_TARGET}/" 2>/dev/null || true
    cp -r "${SCRIPT_DIR}/config" "${SKILL_TARGET}/" 2>/dev/null || true
    echo "  Installed to: ${SKILL_TARGET}/"
else
    echo "  No standard platform directory found."
    echo "  Skill source: ${SCRIPT_DIR}/"
    echo "  Copy SKILL.md and references/ manually to your skill directory."
fi

# 4. Configure MCP server registration
echo "[4/4] Configuring MCP server..."

if [ "${PLATFORM}" = "claude" ]; then
    # Claude Code: .mcp.json + settings.json
    MCP_JSON="${PLATFORM_DIR}/.mcp.json"
    SETTINGS_JSON="${PLATFORM_DIR}/settings.json"

    if [ -f "${MCP_JSON}" ]; then
        if grep -q '"academic-search"' "${MCP_JSON}" 2>/dev/null; then
            echo "  academic-search already in .mcp.json, skipping."
        else
            python3 -c "
import json
with open('${MCP_JSON}', 'r') as f:
    cfg = json.load(f)
cfg.setdefault('mcpServers', {})['academic-search'] = {
    'command': 'python3',
    'args': ['${MCP_TARGET}/academic_search_server.py'],
    'env': {'PUBMED_EMAIL': '${PUBMED_EMAIL}'}
}
with open('${MCP_JSON}', 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
print('  Merged academic-search into .mcp.json')
"
        fi
    else
        cat > "${MCP_JSON}" <<MCPJSON
{
  "mcpServers": {
    "academic-search": {
      "command": "python3",
      "args": ["${MCP_TARGET}/academic_search_server.py"],
      "env": {
        "PUBMED_EMAIL": "${PUBMED_EMAIL}"
      }
    }
  }
}
MCPJSON
        echo "  Created .mcp.json"
    fi

    # Enable in settings.json
    if [ -f "${SETTINGS_JSON}" ]; then
        python3 -c "
import json
with open('${SETTINGS_JSON}', 'r') as f:
    cfg = json.load(f)
enabled = cfg.setdefault('enabledMcpjsonServers', [])
if 'academic-search' not in enabled:
    enabled.append('academic-search')
    with open('${SETTINGS_JSON}', 'w') as f:
        json.dump(cfg, f, indent=2)
        f.write('\n')
    print('  Enabled in settings.json')
else:
    print('  Already enabled in settings.json')
"
    else
        echo "  WARNING: settings.json not found. Manually enable 'academic-search'."
    fi

elif [ "${PLATFORM}" = "qoderwork" ] || [ "${PLATFORM}" = "qoder" ]; then
    # QoderWork/Qoder: use MCP config in platform directory
    MCP_CONFIG="${PLATFORM_DIR}/mcp.json"
    if [ -f "${MCP_CONFIG}" ]; then
        if grep -q '"academic-search"' "${MCP_CONFIG}" 2>/dev/null; then
            echo "  academic-search already configured."
        else
            python3 -c "
import json
with open('${MCP_CONFIG}', 'r') as f:
    cfg = json.load(f)
cfg.setdefault('mcpServers', {})['academic-search'] = {
    'command': 'python3',
    'args': ['${MCP_TARGET}/academic_search_server.py'],
    'env': {'PUBMED_EMAIL': '${PUBMED_EMAIL}'}
}
with open('${MCP_CONFIG}', 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
print('  Added academic-search to mcp.json')
"
        fi
    else
        cat > "${MCP_CONFIG}" <<MCPJSON
{
  "mcpServers": {
    "academic-search": {
      "command": "python3",
      "args": ["${MCP_TARGET}/academic_search_server.py"],
      "env": {
        "PUBMED_EMAIL": "${PUBMED_EMAIL}"
      }
    }
  }
}
MCPJSON
        echo "  Created mcp.json"
    fi
else
    echo "  Could not detect platform. Add the MCP server manually:"
    echo "    Command: python3"
    echo "    Args: [\"<path-to>/academic_search_server.py\"]"
    echo "    Env: {\"PUBMED_EMAIL\": \"${PUBMED_EMAIL}\"}"
fi

echo
echo "=== Done ==="
echo
echo "Installed:"
[ -n "${PLATFORM_DIR}" ] && echo "  MCP server : ${PLATFORM_DIR}/mcp_servers/academic-search/"
[ -n "${PLATFORM_DIR}" ] && echo "  Skill      : ${PLATFORM_DIR}/skills/academic-search/"
echo
echo "Next steps:"
echo "  1. Restart ${PLATFORM_NAME} (or reload MCP servers)"
echo "  2. Set your PubMed email in config.toml or PUBMED_EMAIL env var"
echo "  3. (Optional) Add NCBI_API_KEY for higher rate limits"
echo "  4. Test: ask 'search papers about CRISPR'"
