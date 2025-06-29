#!/usr/bin/env python3
"""
Fix structlog configuration to output to stderr instead of stdout.
MCP servers must only output JSON-RPC to stdout; all logging goes to stderr.
"""
import re
import sys
from pathlib import Path

def fix_logger_configuration():
    """Fix the logger configuration in mcp_hybrid_memory.py"""
    
    # Read the file
    file_path = Path("tool_combo_chains/mcp_hybrid_memory.py")
    if not file_path.exists():
        print(f"Error: {file_path} not found", file=sys.stderr)
        return False
    
    content = file_path.read_text()
    original_content = content
    
    # Pattern 1: Fix PrintLogger without file parameter
    content = re.sub(
        r'structlog\.PrintLogger\(\)',
        'structlog.PrintLogger(file=sys.stderr)',
        content
    )
    
    # Pattern 2: Fix PrintLoggerFactory without file parameter
    content = re.sub(
        r'structlog\.PrintLoggerFactory\(\)',
        'structlog.PrintLoggerFactory(file=sys.stderr)',
        content
    )
    
    # Pattern 3: Fix logger_factory in configure
    content = re.sub(
        r'logger_factory=structlog\.PrintLoggerFactory\(\)',
        'logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)',
        content
    )
    
    # Pattern 4: Add import sys if not present (needed for sys.stderr)
    if 'import sys' not in content and 'from sys import' not in content:
        # Add after other imports
        import_match = re.search(r'(import [^\n]+\n)+', content)
        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + 'import sys\n' + content[insert_pos:]
        else:
            # Add at the beginning after docstring
            content = 'import sys\n' + content
    
    # Pattern 5: Fix ConsoleRenderer to ensure it goes to stderr
    # Look for dev.ConsoleRenderer() and ensure the logger using it outputs to stderr
    if 'dev.ConsoleRenderer()' in content:
        # This is usually fine as long as the PrintLogger uses stderr
        pass
    
    # Check if we made any changes
    if content != original_content:
        # Write the fixed content
        file_path.write_text(content)
        print(f"✅ Fixed logger configuration in {file_path}", file=sys.stderr)
        print("Changes made:", file=sys.stderr)
        
        # Show what changed
        if 'structlog.PrintLogger()' in original_content:
            print("  - Changed structlog.PrintLogger() to structlog.PrintLogger(file=sys.stderr)", file=sys.stderr)
        if 'structlog.PrintLoggerFactory()' in original_content:
            print("  - Changed structlog.PrintLoggerFactory() to structlog.PrintLoggerFactory(file=sys.stderr)", file=sys.stderr)
        if 'import sys' not in original_content:
            print("  - Added 'import sys' for sys.stderr reference", file=sys.stderr)
        
        return True
    else:
        print(f"ℹ️ No changes needed - logger might already be configured correctly", file=sys.stderr)
        print("   Run the MCP server to test if the issue persists", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = fix_logger_configuration()
    sys.exit(0 if success else 1)
