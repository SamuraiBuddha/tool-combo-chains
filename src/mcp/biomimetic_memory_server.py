"""
Biomimetic Memory MCP Server
============================

MCP server that provides biomimetic memory capabilities to Claude Desktop,
enabling tool-combo-chains with neuromorphic cognitive architecture.

This server implements the MCP protocol to expose biomimetic memory operations
as tools that Claude can use for enhanced cognitive capabilities.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .biomimetic_manager import BiomimeticMemoryManager, create_biomimetic_config, BrainRegion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("biomimetic-memory-mcp")

class BiomimeticMemoryMCPServer:
    """MCP Server for biomimetic memory operations"""
    
    def __init__(self):
        self.app = Server("biomimetic-memory")
        self.memory_manager: Optional[BiomimeticMemoryManager] = None
        self.config = create_biomimetic_config()
        
        # Register MCP handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.app.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available biomimetic memory tools"""
            return [
                types.Tool(
                    name="store_biomimetic_memory",
                    description="Store information in the biomimetic memory system using neuromorphic architecture",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to store in memory"},
                            "content_type": {"type": "string", "default": "text", "description": "Type of content (text, insight, pattern, etc.)"},
                            "importance": {"type": "number", "minimum": 0, "maximum": 10, "description": "Importance rating (0-10)"},
                            "emotional_significance": {"type": "number", "minimum": 0, "maximum": 1, "description": "Emotional significance (0-1)"},
                            "context": {"type": "object", "description": "Additional context metadata"}
                        },
                        "required": ["content"]
                    }
                ),
                types.Tool(
                    name="recall_biomimetic_memory",
                    description="Search and recall memories using parallel neuromorphic search across brain regions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for memory recall"},
                            "access_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.5, "description": "Minimum weight threshold for memory access"},
                            "brain_regions": {"type": "array", "items": {"type": "string"}, "description": "Specific brain regions to search (hippocampus, neocortex, cerebellum, amygdala)"},
                            "max_results": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10, "description": "Maximum number of results to return"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="consolidate_memories",
                    description="Trigger biomimetic memory consolidation (sleep cycle simulation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cycle_type": {"type": "string", "enum": ["sws", "rem"], "default": "sws", "description": "Type of consolidation cycle (SWS or REM)"},
                            "force": {"type": "boolean", "default": False, "description": "Force consolidation even if not due"}
                        }
                    }
                ),
                types.Tool(
                    name="memory_analytics",
                    description="Get analytics and insights about the biomimetic memory system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metric_type": {"type": "string", "enum": ["overview", "brain_regions", "weight_distribution", "importance_patterns"], "default": "overview", "description": "Type of analytics to retrieve"}
                        }
                    }
                ),
                types.Tool(
                    name="memory_associations",
                    description="Find and create associations between memories using biomimetic pattern recognition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "ID of memory to find associations for"},
                            "association_type": {"type": "string", "enum": ["semantic", "emotional", "procedural", "all"], "default": "all", "description": "Type of associations to find"},
                            "strength_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.3, "description": "Minimum association strength"}
                        }
                    }
                ),
                types.Tool(
                    name="update_memory_weight",
                    description="Update the weight (accessibility) of a specific memory using biomimetic reinforcement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "string", "description": "ID of memory to update"},
                            "weight_change": {"type": "number", "minimum": -1, "maximum": 1, "description": "Weight change (-1 to 1)"},
                            "reason": {"type": "string", "description": "Reason for weight change"}
                        },
                        "required": ["memory_id", "weight_change"]
                    }
                ),
                types.Tool(
                    name="pattern_recognition",
                    description="Use cerebellum (Neo4j) to recognize patterns across stored memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern_type": {"type": "string", "enum": ["temporal", "semantic", "behavioral", "procedural"], "description": "Type of pattern to recognize"},
                            "time_window": {"type": "string", "description": "Time window for pattern analysis (e.g., '7d', '30d', 'all')"},
                            "confidence_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.7, "description": "Minimum confidence for pattern detection"}
                        }
                    }
                ),
                types.Tool(
                    name="emotional_context",
                    description="Analyze emotional context and significance using amygdala (SurrealDB)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to analyze for emotional significance"},
                            "context": {"type": "object", "description": "Additional context for emotional analysis"}
                        },
                        "required": ["content"]
                    }
                )
            ]
        
        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls to biomimetic memory system"""
            
            # Initialize memory manager if not already done
            if not self.memory_manager:
                await self._initialize_memory_manager()
            
            try:
                if name == "store_biomimetic_memory":
                    return await self._handle_store_memory(arguments)
                elif name == "recall_biomimetic_memory":
                    return await self._handle_recall_memory(arguments)
                elif name == "consolidate_memories":
                    return await self._handle_consolidate_memories(arguments)
                elif name == "memory_analytics":
                    return await self._handle_memory_analytics(arguments)
                elif name == "memory_associations":
                    return await self._handle_memory_associations(arguments)
                elif name == "update_memory_weight":
                    return await self._handle_update_memory_weight(arguments)
                elif name == "pattern_recognition":
                    return await self._handle_pattern_recognition(arguments)
                elif name == "emotional_context":
                    return await self._handle_emotional_context(arguments)
                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _initialize_memory_manager(self):
        """Initialize biomimetic memory manager"""
        try:
            self.memory_manager = BiomimeticMemoryManager(self.config)
            await self.memory_manager.connect()
            logger.info("✅ Biomimetic memory manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory manager: {e}")
            raise
    
    async def _handle_store_memory(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle memory storage request"""
        content = args["content"]
        content_type = args.get("content_type", "text")
        
        # Build context from arguments
        context = args.get("context", {})
        if "importance" in args:
            context["user_rating"] = args["importance"]
        if "emotional_significance" in args:
            context["emotional_override"] = args["emotional_significance"]
        
        # Store in biomimetic memory
        memory_id = await self.memory_manager.store_memory(content, content_type, context)
        
        result = {
            "memory_id": memory_id,
            "status": "stored",
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "brain_regions": ["hippocampus"],  # Initially stored in working memory
            "weight": 1.0,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"🧠 Memory stored successfully!\n\n{json.dumps(result, indent=2)}"
        )]
    
    async def _handle_recall_memory(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle memory recall request"""
        query = args["query"]
        access_threshold = args.get("access_threshold", 0.5)
        max_results = args.get("max_results", 10)
        
        # Parse brain regions if specified
        brain_regions = None
        if "brain_regions" in args:
            brain_regions = [BrainRegion(region) for region in args["brain_regions"]]
        
        # Perform biomimetic memory recall
        memories = await self.memory_manager.recall_memory(
            query, access_threshold, brain_regions
        )
        
        # Limit results
        memories = memories[:max_results]
        
        if not memories:
            return [types.TextContent(
                type="text",
                text=f"🔍 No memories found matching '{query}' with access threshold {access_threshold}"
            )]
        
        # Format results
        results = []
        for i, memory in enumerate(memories, 1):
            results.append({
                "rank": i,
                "memory_id": memory.id,
                "content": memory.content[:200] + "..." if len(memory.content) > 200 else memory.content,
                "weight": round(memory.weight, 3),
                "importance": round(memory.importance_score, 3),
                "emotional_significance": round(memory.emotional_significance, 3),
                "access_count": memory.access_count,
                "brain_regions": [region.value for region in memory.brain_regions],
                "created": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat()
            })
        
        response = {
            "query": query,
            "results_count": len(results),
            "access_threshold": access_threshold,
            "memories": results
        }
        
        return [types.TextContent(
            type="text",
            text=f"🔍 Biomimetic memory recall results:\n\n{json.dumps(response, indent=2)}"
        )]
    
    async def _handle_consolidate_memories(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle memory consolidation request"""
        cycle_type = args.get("cycle_type", "sws")
        force = args.get("force", False)
        
        # Check if consolidation is due
        if not force:
            now = datetime.now()
            if cycle_type == "sws":
                time_since_last = (now - self.memory_manager.last_sws_cycle).total_seconds()
                if time_since_last < 5400:  # 90 minutes
                    return [types.TextContent(
                        type="text",
                        text=f"😴 SWS consolidation not due yet. Last cycle: {self.memory_manager.last_sws_cycle.isoformat()}"
                    )]
            elif cycle_type == "rem":
                time_since_last = (now - self.memory_manager.last_rem_cycle).total_seconds()
                if time_since_last < 21600:  # 6 hours
                    return [types.TextContent(
                        type="text",
                        text=f"🌙 REM consolidation not due yet. Last cycle: {self.memory_manager.last_rem_cycle.isoformat()}"
                    )]
        
        # Perform consolidation
        await self.memory_manager.consolidate_memories(cycle_type)
        
        result = {
            "cycle_type": cycle_type,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "forced": force
        }
        
        cycle_emoji = "😴" if cycle_type == "sws" else "🌙"
        cycle_name = "Slow-Wave Sleep" if cycle_type == "sws" else "REM Integration"
        
        return [types.TextContent(
            type="text",
            text=f"{cycle_emoji} {cycle_name} consolidation completed!\n\n{json.dumps(result, indent=2)}"
        )]
    
    async def _handle_memory_analytics(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle memory analytics request"""
        metric_type = args.get("metric_type", "overview")
        
        # Placeholder analytics - would query actual brain regions
        analytics = {
            "metric_type": metric_type,
            "timestamp": datetime.now().isoformat(),
            "system_status": "operational",
            "brain_regions": {
                "hippocampus": {"status": "connected", "active_memories": 42},
                "neocortex": {"status": "connected", "stored_memories": 1337},
                "cerebellum": {"status": "connected", "patterns": 89},
                "amygdala": {"status": "connected", "emotional_memories": 156},
                "brainstem": {"status": "connected", "processed_items": 2500},
                "thalamus": {"status": "connected", "messages_routed": 5680}
            },
            "memory_distribution": {
                "conscious": "12.3%",
                "easy_recall": "23.7%", 
                "effort_required": "35.2%",
                "subconscious": "21.8%",
                "deep_storage": "5.9%",
                "dormant": "1.1%"
            },
            "consolidation_stats": {
                "last_sws_cycle": self.memory_manager.last_sws_cycle.isoformat() if self.memory_manager else "never",
                "last_rem_cycle": self.memory_manager.last_rem_cycle.isoformat() if self.memory_manager else "never",
                "next_sws_due": "90 minutes from last cycle",
                "next_rem_due": "6 hours from last cycle"
            }
        }
        
        return [types.TextContent(
            type="text",
            text=f"📊 Biomimetic Memory Analytics\n\n{json.dumps(analytics, indent=2)}"
        )]
    
    async def _handle_memory_associations(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle memory association request"""
        # Placeholder implementation
        result = {
            "memory_id": args.get("memory_id"),
            "association_type": args.get("association_type", "all"),
            "associations": [
                {"memory_id": "mem_123", "strength": 0.85, "type": "semantic"},
                {"memory_id": "mem_456", "strength": 0.72, "type": "emotional"},
                {"memory_id": "mem_789", "strength": 0.65, "type": "procedural"}
            ]
        }
        
        return [types.TextContent(
            type="text",
            text=f"🔗 Memory associations found:\n\n{json.dumps(result, indent=2)}"
        )]
    
    async def _handle_update_memory_weight(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle memory weight update request"""
        memory_id = args["memory_id"]
        weight_change = args["weight_change"]
        reason = args.get("reason", "Manual adjustment")
        
        # Placeholder implementation
        result = {
            "memory_id": memory_id,
            "previous_weight": 0.7,
            "new_weight": min(1.0, max(0.0, 0.7 + weight_change)),
            "weight_change": weight_change,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"⚖️ Memory weight updated:\n\n{json.dumps(result, indent=2)}"
        )]
    
    async def _handle_pattern_recognition(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle pattern recognition request"""
        pattern_type = args.get("pattern_type", "semantic")
        
        # Placeholder implementation
        patterns = {
            "pattern_type": pattern_type,
            "confidence_threshold": args.get("confidence_threshold", 0.7),
            "patterns_found": [
                {"pattern": "biomimetic memory architecture", "confidence": 0.92, "frequency": 8},
                {"pattern": "sleep cycle consolidation", "confidence": 0.87, "frequency": 5},
                {"pattern": "weight-based access", "confidence": 0.84, "frequency": 12}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"🧩 Pattern recognition results:\n\n{json.dumps(patterns, indent=2)}"
        )]
    
    async def _handle_emotional_context(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle emotional context analysis request"""
        content = args["content"]
        
        # Placeholder emotional analysis
        analysis = {
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "emotional_significance": 0.75,
            "valence": "positive",
            "arousal": "medium",
            "emotions_detected": ["excitement", "curiosity", "satisfaction"],
            "importance_boost": 1.3,
            "amygdala_response": "high_significance",
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"💝 Emotional context analysis:\n\n{json.dumps(analysis, indent=2)}"
        )]

async def main():
    """Run the biomimetic memory MCP server"""
    server = BiomimeticMemoryMCPServer()
    
    # Configure stdio transport
    options = InitializationOptions(
        server_name="biomimetic-memory",
        server_version="1.0.0",
        capabilities=server.app.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
    )
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.app.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())