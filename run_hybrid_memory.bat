@echo off
REM Wrapper to suppress Python warnings and run hybrid memory MCP
python -u -W ignore -m tool_combo_chains.mcp_hybrid_memory %*
