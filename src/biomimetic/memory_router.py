"""
Biomimetic Memory Router (Thalamus)
Central coordinator for neuromorphic multi-database architecture
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

from .brain_regions.hippocampus import HippocampusMemory
from .brain_regions.neocortex import NeocortexMemory  
from .brain_regions.cerebellum import CerebellumMemory
from .brain_regions.amygdala import AmygdalaMemory
from .consolidation import ConsolidationEngine

logger = logging.getLogger(__name__)

@dataclass
class MemoryInput:
    """Input to the biomimetic memory system"""
    content: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    importance_hint: Optional[float] = None
    memory_type_hint: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class MemoryOutput:
    """Output from memory recall operations"""
    content: str
    confidence: float
    source_regions: List[str]
    related_memories: List[Dict[str, Any]]
    emotional_weight: float
    procedural_relevance: float
    timestamp: datetime
    synthesis_path: List[str]

class BiomimeticMemoryRouter:
    """
    Central coordinator implementing thalamus-like routing between specialized memory systems.
    
    This router orchestrates:
    - Memory encoding and storage routing
    - Cross-system memory recall and synthesis  
    - Consolidation between working and long-term memory
    - Connection weight updates (synaptic plasticity)
    - Temporal decay and forgetting processes
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.active_contexts = {}
        
        # Initialize brain regions
        self.hippocampus = HippocampusMemory(config.get('redis', {}))
        self.neocortex = NeocortexMemory(config.get('postgresql', {}))
        self.cerebellum = CerebellumMemory(config.get('neo4j', {}))
        self.amygdala = AmygdalaMemory(config.get('surrealdb', {}))
        
        # Consolidation engine for sleep-like processes
        self.consolidation = ConsolidationEngine(self)
        
        # Performance tracking
        self.stats = {
            'encoding_ops': 0,
            'recall_ops': 0,
            'consolidation_cycles': 0,
            'cross_system_syntheses': 0
        }
        
    async def initialize(self):
        """Initialize all brain region connections"""
        await asyncio.gather(
            self.hippocampus.initialize(),
            self.neocortex.initialize(),
            self.cerebellum.initialize(),
            self.amygdala.initialize()
        )
        
        # Start background consolidation process
        asyncio.create_task(self._consolidation_loop())
        
        logger.info(f"Biomimetic memory router initialized - Session: {self.session_id}")
    
    async def encode_memory(self, memory_input: MemoryInput) -> str:
        """
        Encode new memory using biomimetic process:
        1. Immediate storage in hippocampus (working memory)
        2. Parallel analysis by all regions
        3. Routing decisions based on content type and importance
        4. Cross-system relationship building
        """
        self.stats['encoding_ops'] += 1
        memory_id = str(uuid.uuid4())
        
        try:
            # Phase 1: Immediate working memory storage
            temp_id = await self.hippocampus.store_immediate(
                content=memory_input.content,
                context=memory_input.context,
                metadata=memory_input.metadata,
                ttl=30  # 30-second working memory
            )
            
            # Phase 2: Parallel analysis by specialized regions
            analysis_tasks = await asyncio.gather(
                self._semantic_analysis(memory_input),
                self._emotional_analysis(memory_input),
                self._procedural_analysis(memory_input),
                return_exceptions=True
            )
            
            semantic_features, emotional_weight, procedural_patterns = analysis_tasks
            
            # Phase 3: Consolidation routing decisions
            should_consolidate = await self._should_consolidate(
                emotional_weight, memory_input.importance_hint
            )
            
            if should_consolidate:
                # Route to appropriate long-term storage
                long_term_tasks = []
                
                if semantic_features['relevance'] > 0.7:
                    long_term_tasks.append(
                        self.neocortex.store_semantic(memory_input, semantic_features)
                    )
                
                if procedural_patterns['skill_relevance'] > 0.6:
                    long_term_tasks.append(
                        self.cerebellum.store_procedure(memory_input, procedural_patterns)
                    )
                
                if emotional_weight > 0.8:
                    long_term_tasks.append(
                        self.amygdala.store_priority(memory_input, emotional_weight)
                    )
                
                if long_term_tasks:
                    await asyncio.gather(*long_term_tasks, return_exceptions=True)
            
            # Phase 4: Cross-system relationship building
            await self._build_cross_system_relationships(memory_id, memory_input)
            
            logger.debug(f"Memory encoded: {memory_id} (emotional_weight: {emotional_weight})")
            return memory_id
            
        except Exception as e:
            logger.error(f"Memory encoding failed: {str(e)}")
            raise
    
    async def recall_memory(self, query: str, context: Dict[str, Any] = None) -> MemoryOutput:
        """
        Recall memory using spreading activation across all brain regions:
        1. Parallel search across all memory systems
        2. Cross-system synthesis and weighting
        3. Reconsolidation (memory changes when recalled)
        4. Context-dependent enhancement
        """
        self.stats['recall_ops'] += 1
        
        try:
            # Phase 1: Parallel search across all regions
            search_tasks = await asyncio.gather(
                self.hippocampus.search_working_memory(query, context),
                self.neocortex.semantic_search(query, context),
                self.cerebellum.search_procedures(query, context),
                self.amygdala.search_priorities(query, context),
                return_exceptions=True
            )
            
            working_results, semantic_results, procedural_results, priority_results = search_tasks
            
            # Phase 2: Cross-system synthesis
            synthesis = await self._synthesize_recall(
                working_results, semantic_results, 
                procedural_results, priority_results,
                query, context
            )
            
            # Phase 3: Reconsolidation - update connection weights
            await self._reconsolidate_memories(synthesis)
            
            # Phase 4: Build comprehensive output
            output = MemoryOutput(
                content=synthesis['primary_content'],
                confidence=synthesis['confidence'],
                source_regions=synthesis['active_regions'],
                related_memories=synthesis['related_memories'],
                emotional_weight=synthesis['emotional_weight'],
                procedural_relevance=synthesis['procedural_relevance'],
                timestamp=datetime.utcnow(),
                synthesis_path=synthesis['processing_path']
            )
            
            self.stats['cross_system_syntheses'] += 1
            return output
            
        except Exception as e:
            logger.error(f"Memory recall failed: {str(e)}")
            raise
    
    async def _semantic_analysis(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """Extract semantic features for neocortex storage decision"""
        # This would typically use embedding models
        return {
            'relevance': 0.8,  # Placeholder
            'embedding': None,  # Would generate actual embedding
            'concepts': [],
            'relationships': []
        }
    
    async def _emotional_analysis(self, memory_input: MemoryInput) -> float:
        """Analyze emotional weight for amygdala routing"""
        # This would analyze content for emotional significance
        importance = memory_input.importance_hint or 0.5
        
        # Boost based on keywords that indicate high importance
        boost_keywords = ['critical', 'urgent', 'error', 'success', 'failure']
        content_lower = memory_input.content.lower()
        
        for keyword in boost_keywords:
            if keyword in content_lower:
                importance = min(1.0, importance + 0.2)
        
        return importance
    
    async def _procedural_analysis(self, memory_input: MemoryInput) -> Dict[str, Any]:
        """Analyze procedural patterns for cerebellum routing"""
        # This would detect skill/procedure patterns
        return {
            'skill_relevance': 0.4,  # Placeholder
            'procedures': [],
            'skill_chains': [],
            'automation_potential': 0.3
        }
    
    async def _should_consolidate(self, emotional_weight: float, importance_hint: Optional[float]) -> bool:
        """Decide whether memory should be consolidated to long-term storage"""
        # Biomimetic consolidation threshold
        base_threshold = 0.6
        
        if importance_hint and importance_hint > 0.8:
            return True
        
        if emotional_weight > base_threshold:
            return True
            
        # Could add more sophisticated criteria here
        return False
    
    async def _build_cross_system_relationships(self, memory_id: str, memory_input: MemoryInput):
        """Build relationships between memory systems"""
        # This would create cross-system links for spreading activation
        pass
    
    async def _synthesize_recall(self, working_results, semantic_results, 
                               procedural_results, priority_results,
                               query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from all memory systems into coherent output"""
        
        # Weight results based on confidence and recency
        all_results = []
        active_regions = []
        
        if working_results and len(working_results) > 0:
            all_results.extend(working_results)
            active_regions.append('hippocampus')
            
        if semantic_results and len(semantic_results) > 0:
            all_results.extend(semantic_results)
            active_regions.append('neocortex')
            
        if procedural_results and len(procedural_results) > 0:
            all_results.extend(procedural_results)
            active_regions.append('cerebellum')
            
        if priority_results and len(priority_results) > 0:
            all_results.extend(priority_results)
            active_regions.append('amygdala')
        
        if not all_results:
            return {
                'primary_content': '',
                'confidence': 0.0,
                'active_regions': [],
                'related_memories': [],
                'emotional_weight': 0.0,
                'procedural_relevance': 0.0,
                'processing_path': ['no_results']
            }
        
        # Find best match and synthesize
        best_result = max(all_results, key=lambda x: x.get('confidence', 0))
        
        return {
            'primary_content': best_result.get('content', ''),
            'confidence': best_result.get('confidence', 0.0),
            'active_regions': active_regions,
            'related_memories': all_results[:5],  # Top 5 related
            'emotional_weight': sum(r.get('emotional_weight', 0) for r in all_results) / len(all_results),
            'procedural_relevance': sum(r.get('procedural_relevance', 0) for r in all_results) / len(all_results),
            'processing_path': ['search', 'synthesis', 'weighting', 'selection']
        }
    
    async def _reconsolidate_memories(self, synthesis: Dict[str, Any]):
        """Update connection weights based on memory access (reconsolidation)"""
        # This implements synaptic plasticity - memories change when recalled
        pass
    
    async def _consolidation_loop(self):
        """Background consolidation process (sleep-like memory transfer)"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.consolidation.run_consolidation_cycle()
                self.stats['consolidation_cycles'] += 1
                
            except Exception as e:
                logger.error(f"Consolidation cycle failed: {str(e)}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get performance and usage statistics"""
        region_stats = await asyncio.gather(
            self.hippocampus.get_stats(),
            self.neocortex.get_stats(),
            self.cerebellum.get_stats(),
            self.amygdala.get_stats(),
            return_exceptions=True
        )
        
        return {
            'router_stats': self.stats,
            'session_id': self.session_id,
            'hippocampus': region_stats[0] if not isinstance(region_stats[0], Exception) else {},
            'neocortex': region_stats[1] if not isinstance(region_stats[1], Exception) else {},
            'cerebellum': region_stats[2] if not isinstance(region_stats[2], Exception) else {},
            'amygdala': region_stats[3] if not isinstance(region_stats[3], Exception) else {}
        }
    
    async def shutdown(self):
        """Gracefully shutdown all brain regions"""
        await asyncio.gather(
            self.hippocampus.shutdown(),
            self.neocortex.shutdown(),
            self.cerebellum.shutdown(),
            self.amygdala.shutdown(),
            return_exceptions=True
        )
        
        logger.info(f"Biomimetic memory router shutdown - Session: {self.session_id}")

# Tool combo integration helpers
async def create_biomimetic_memory(config: Dict[str, Any]) -> BiomimeticMemoryRouter:
    """Factory function for creating and initializing biomimetic memory"""
    router = BiomimeticMemoryRouter(config)
    await router.initialize()
    return router

def biomimetic_memory_decorator(memory_router: BiomimeticMemoryRouter):
    """Decorator to add biomimetic memory to tool combo functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Store function context in working memory
            context = {
                'function': func.__name__,
                'args': str(args)[:200],  # Truncate for storage
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await memory_router.hippocampus.store_immediate(
                content=f"Executing {func.__name__}",
                context=context,
                metadata={'type': 'tool_execution'},
                ttl=60
            )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store successful execution
            if result:
                await memory_router.encode_memory(MemoryInput(
                    content=f"Successfully executed {func.__name__}",
                    context=context,
                    metadata={'type': 'tool_success', 'result_summary': str(result)[:500]},
                    importance_hint=0.7
                ))
            
            return result
        return wrapper
    return decorator
