"""
Amygdala Brain Region - SurrealDB Implementation
Biomimetic Neuromorphic Architecture - Emotional Memory & Priority Scoring

Function: Importance scoring, emotional context, threat/opportunity detection
Database: SurrealDB for real-time priority assessment and multi-model flexibility
"""

import asyncio
from surrealdb import Surreal
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
import json
import logging
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class EmotionalValence(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

class ThreatLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class OpportunityLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXCEPTIONAL = 4

@dataclass
class EmotionalMemory:
    id: str
    content: str
    emotional_weight: float
    valence: EmotionalValence
    arousal: float
    threat_level: ThreatLevel
    opportunity_level: OpportunityLevel
    priority_score: float
    context: Dict[str, Any]
    triggers: List[str]
    created_at: datetime

class AmygdalaProcessor:
    """
    Amygdala - Emotional Memory & Priority Scoring Processor
    
    Biological Functions Implemented:
    - Real-time emotional assessment and priority scoring
    - Threat and opportunity detection
    - Emotional memory consolidation
    - Context-dependent emotional responses
    - Fight/flight/freeze response simulation
    - Memory importance weighting based on emotional significance
    """
    
    def __init__(self, surrealdb_url: str, namespace: str = "biomimetic", database: str = "amygdala"):
        self.surrealdb_url = surrealdb_url
        self.namespace = namespace
        self.database = database
        self.db = None
        
    async def initialize(self):
        """Initialize SurrealDB connection and create schema"""
        self.db = Surreal()
        await self.db.connect(self.surrealdb_url)
        await self.db.use(self.namespace, self.database)
        
        await self._create_schema()
        await self._create_live_queries()
        logger.info("Amygdala initialized with SurrealDB")
        
    async def _create_schema(self):
        """Create SurrealDB tables and schema definitions"""
        
        # Emotional memories table
        await self.db.query("""
            DEFINE TABLE emotional_memories SCHEMAFULL;
            
            DEFINE FIELD id ON TABLE emotional_memories TYPE record<emotional_memories>;
            DEFINE FIELD content ON TABLE emotional_memories TYPE string;
            DEFINE FIELD emotional_weight ON TABLE emotional_memories TYPE number;
            DEFINE FIELD valence ON TABLE emotional_memories TYPE number;
            DEFINE FIELD arousal ON TABLE emotional_memories TYPE number;
            DEFINE FIELD threat_level ON TABLE emotional_memories TYPE number;
            DEFINE FIELD opportunity_level ON TABLE emotional_memories TYPE number;
            DEFINE FIELD priority_score ON TABLE emotional_memories TYPE number;
            DEFINE FIELD context ON TABLE emotional_memories TYPE object;
            DEFINE FIELD triggers ON TABLE emotional_memories TYPE array<string>;
            DEFINE FIELD source_memory_id ON TABLE emotional_memories TYPE string;
            DEFINE FIELD created_at ON TABLE emotional_memories TYPE datetime;
            DEFINE FIELD last_triggered ON TABLE emotional_memories TYPE datetime;
            DEFINE FIELD trigger_count ON TABLE emotional_memories TYPE number DEFAULT 0;
            
            DEFINE INDEX priority_idx ON TABLE emotional_memories COLUMNS priority_score;
            DEFINE INDEX threat_idx ON TABLE emotional_memories COLUMNS threat_level;
            DEFINE INDEX opportunity_idx ON TABLE emotional_memories COLUMNS opportunity_level;
            DEFINE INDEX emotional_weight_idx ON TABLE emotional_memories COLUMNS emotional_weight;
        """)
        
        # Emotional triggers table for pattern recognition
        await self.db.query("""
            DEFINE TABLE emotional_triggers SCHEMAFULL;
            
            DEFINE FIELD id ON TABLE emotional_triggers TYPE record<emotional_triggers>;
            DEFINE FIELD trigger_pattern ON TABLE emotional_triggers TYPE string;
            DEFINE FIELD emotional_response ON TABLE emotional_triggers TYPE object;
            DEFINE FIELD strength ON TABLE emotional_triggers TYPE number;
            DEFINE FIELD learned_from ON TABLE emotional_triggers TYPE array<string>;
            DEFINE FIELD activation_count ON TABLE emotional_triggers TYPE number DEFAULT 0;
            DEFINE FIELD created_at ON TABLE emotional_triggers TYPE datetime;
            DEFINE FIELD last_activated ON TABLE emotional_triggers TYPE datetime;
        """)
        
        # Real-time threat/opportunity assessment table
        await self.db.query("""
            DEFINE TABLE threat_assessments SCHEMAFULL;
            
            DEFINE FIELD id ON TABLE threat_assessments TYPE record<threat_assessments>;
            DEFINE FIELD content ON TABLE threat_assessments TYPE string;
            DEFINE FIELD threat_indicators ON TABLE threat_assessments TYPE array<string>;
            DEFINE FIELD threat_score ON TABLE threat_assessments TYPE number;
            DEFINE FIELD opportunity_indicators ON TABLE threat_assessments TYPE array<string>;
            DEFINE FIELD opportunity_score ON TABLE threat_assessments TYPE number;
            DEFINE FIELD recommended_action ON TABLE threat_assessments TYPE string;
            DEFINE FIELD urgency_level ON TABLE threat_assessments TYPE number;
            DEFINE FIELD assessed_at ON TABLE threat_assessments TYPE datetime;
            DEFINE FIELD context ON TABLE threat_assessments TYPE object;
        """)
        
    async def _create_live_queries(self):
        """Create live queries for real-time emotional processing"""
        
        # Live query for high-priority threats
        await self.db.query("""
            LIVE SELECT * FROM threat_assessments WHERE threat_score > 0.8;
        """)
        
        # Live query for exceptional opportunities  
        await self.db.query("""
            LIVE SELECT * FROM threat_assessments WHERE opportunity_score > 0.9;
        """)
        
    async def assess_emotional_content(
        self, 
        content: str, 
        context: Dict[str, Any] = None,
        source_memory_id: str = None
    ) -> Dict[str, Any]:
        """
        Perform real-time emotional assessment of content
        
        Biological Process: Amygdala's rapid emotional evaluation
        """
        context = context or {}
        
        # Emotional analysis (simplified - would use ML models in production)
        emotional_indicators = await self._extract_emotional_indicators(content)
        threat_indicators = await self._detect_threats(content, context)
        opportunity_indicators = await self._detect_opportunities(content, context)
        
        # Calculate emotional metrics
        emotional_weight = self._calculate_emotional_weight(emotional_indicators)
        valence = self._calculate_valence(emotional_indicators)
        arousal = self._calculate_arousal(emotional_indicators)
        threat_level = self._calculate_threat_level(threat_indicators)
        opportunity_level = self._calculate_opportunity_level(opportunity_indicators)
        
        # Priority scoring (Jordan's insight: importance determines consolidation)
        priority_score = self._calculate_priority_score(
            emotional_weight, threat_level, opportunity_level, arousal
        )
        
        # Store emotional memory
        memory_id = await self._store_emotional_memory(
            content=content,
            emotional_weight=emotional_weight,
            valence=valence,
            arousal=arousal,
            threat_level=threat_level,
            opportunity_level=opportunity_level,
            priority_score=priority_score,
            context=context,
            triggers=emotional_indicators.get('triggers', []),
            source_memory_id=source_memory_id
        )
        
        # Real-time threat/opportunity assessment
        assessment = await self._create_threat_opportunity_assessment(
            content=content,
            threat_indicators=threat_indicators,
            threat_score=threat_level / 4.0,  # Normalize to 0-1
            opportunity_indicators=opportunity_indicators,
            opportunity_score=opportunity_level / 4.0,  # Normalize to 0-1
            context=context
        )
        
        result = {
            'memory_id': memory_id,
            'emotional_weight': emotional_weight,
            'valence': valence.value,
            'arousal': arousal,
            'threat_level': threat_level.value,
            'opportunity_level': opportunity_level.value,
            'priority_score': priority_score,
            'assessment': assessment,
            'triggers': emotional_indicators.get('triggers', [])
        }
        
        logger.info(f"Assessed emotional content, priority: {priority_score:.2f}")
        return result
    
    async def _extract_emotional_indicators(self, content: str) -> Dict[str, Any]:
        """Extract emotional indicators from content (simplified implementation)"""
        # In production, this would use advanced NLP/ML models
        
        positive_keywords = [
            'breakthrough', 'success', 'amazing', 'excellent', 'revolutionary',
            'discover', 'achieve', 'opportunity', 'progress', 'innovation'
        ]
        
        negative_keywords = [
            'error', 'failure', 'problem', 'issue', 'limitation', 'concern',
            'threat', 'risk', 'danger', 'warning', 'critical'
        ]
        
        urgency_keywords = [
            'urgent', 'immediate', 'critical', 'asap', 'emergency', 'now',
            'deadline', 'time-sensitive', 'priority'
        ]
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in content_lower)
        negative_count = sum(1 for word in negative_keywords if word in content_lower)
        urgency_count = sum(1 for word in urgency_keywords if word in content_lower)
        
        triggers = []
        if positive_count > 0:
            triggers.extend(['positive_sentiment', 'achievement'])
        if negative_count > 0:
            triggers.extend(['negative_sentiment', 'problem_detection'])
        if urgency_count > 0:
            triggers.extend(['urgency', 'time_pressure'])
        
        return {
            'positive_score': positive_count / len(positive_keywords),
            'negative_score': negative_count / len(negative_keywords),
            'urgency_score': urgency_count / len(urgency_keywords),
            'triggers': triggers
        }
    
    async def _detect_threats(self, content: str, context: Dict[str, Any]) -> List[str]:
        """Detect potential threats in content"""
        threats = []
        content_lower = content.lower()
        
        # System threats
        if any(word in content_lower for word in ['error', 'failure', 'crash', 'bug']):
            threats.append('system_failure')
        
        # Performance threats
        if any(word in content_lower for word in ['slow', 'timeout', 'bottleneck']):
            threats.append('performance_degradation')
        
        # Security threats
        if any(word in content_lower for word in ['breach', 'vulnerability', 'attack']):
            threats.append('security_risk')
        
        # Data threats
        if any(word in content_lower for word in ['loss', 'corruption', 'delete']):
            threats.append('data_integrity')
        
        return threats
    
    async def _detect_opportunities(self, content: str, context: Dict[str, Any]) -> List[str]:
        """Detect potential opportunities in content"""
        opportunities = []
        content_lower = content.lower()
        
        # Innovation opportunities
        if any(word in content_lower for word in ['breakthrough', 'discovery', 'innovation']):
            opportunities.append('innovation_potential')
        
        # Performance opportunities
        if any(word in content_lower for word in ['optimize', 'improve', 'enhance', 'amplify']):
            opportunities.append('performance_improvement')
        
        # Learning opportunities
        if any(word in content_lower for word in ['learn', 'pattern', 'insight', 'knowledge']):
            opportunities.append('learning_opportunity')
        
        # Efficiency opportunities
        if any(word in content_lower for word in ['automate', 'streamline', 'efficiency']):
            opportunities.append('efficiency_gain')
        
        return opportunities
    
    def _calculate_emotional_weight(self, indicators: Dict[str, Any]) -> float:
        """Calculate overall emotional weight (0-1 scale)"""
        positive = indicators.get('positive_score', 0)
        negative = indicators.get('negative_score', 0)
        urgency = indicators.get('urgency_score', 0)
        
        # Higher emotional weight for more intense emotions
        weight = max(positive, negative) + (urgency * 0.5)
        return min(1.0, weight)
    
    def _calculate_valence(self, indicators: Dict[str, Any]) -> EmotionalValence:
        """Calculate emotional valence (positive/negative)"""
        positive = indicators.get('positive_score', 0)
        negative = indicators.get('negative_score', 0)
        
        net_valence = positive - negative
        
        if net_valence > 0.3:
            return EmotionalValence.VERY_POSITIVE
        elif net_valence > 0.1:
            return EmotionalValence.POSITIVE
        elif net_valence < -0.3:
            return EmotionalValence.VERY_NEGATIVE
        elif net_valence < -0.1:
            return EmotionalValence.NEGATIVE
        else:
            return EmotionalValence.NEUTRAL
    
    def _calculate_arousal(self, indicators: Dict[str, Any]) -> float:
        """Calculate emotional arousal (intensity)"""
        urgency = indicators.get('urgency_score', 0)
        emotional_intensity = max(
            indicators.get('positive_score', 0),
            indicators.get('negative_score', 0)
        )
        
        return min(1.0, urgency + emotional_intensity)
    
    def _calculate_threat_level(self, threat_indicators: List[str]) -> ThreatLevel:
        """Calculate threat level based on indicators"""
        if not threat_indicators:
            return ThreatLevel.NONE
        
        critical_threats = ['system_failure', 'security_risk', 'data_integrity']
        
        if any(threat in critical_threats for threat in threat_indicators):
            return ThreatLevel.CRITICAL if len(threat_indicators) > 2 else ThreatLevel.HIGH
        elif len(threat_indicators) >= 2:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_opportunity_level(self, opportunity_indicators: List[str]) -> OpportunityLevel:
        """Calculate opportunity level based on indicators"""
        if not opportunity_indicators:
            return OpportunityLevel.NONE
        
        exceptional_opportunities = ['innovation_potential', 'performance_improvement']
        
        if any(opp in exceptional_opportunities for opp in opportunity_indicators):
            return OpportunityLevel.EXCEPTIONAL if len(opportunity_indicators) > 2 else OpportunityLevel.HIGH
        elif len(opportunity_indicators) >= 2:
            return OpportunityLevel.MEDIUM
        else:
            return OpportunityLevel.LOW
    
    def _calculate_priority_score(
        self, 
        emotional_weight: float,
        threat_level: ThreatLevel,
        opportunity_level: OpportunityLevel,
        arousal: float
    ) -> float:
        """
        Calculate priority score for memory consolidation
        
        Jordan's Insight: Priority determines what gets consolidated to long-term memory
        """
        base_priority = emotional_weight * 0.4
        threat_boost = (threat_level.value / 4.0) * 0.3
        opportunity_boost = (opportunity_level.value / 4.0) * 0.2
        arousal_boost = arousal * 0.1
        
        priority = base_priority + threat_boost + opportunity_boost + arousal_boost
        return min(1.0, priority)
    
    async def _store_emotional_memory(
        self,
        content: str,
        emotional_weight: float,
        valence: EmotionalValence,
        arousal: float,
        threat_level: ThreatLevel,
        opportunity_level: OpportunityLevel,
        priority_score: float,
        context: Dict[str, Any],
        triggers: List[str],
        source_memory_id: str = None
    ) -> str:
        """Store emotional memory in SurrealDB"""
        
        memory_data = {
            'content': content,
            'emotional_weight': emotional_weight,
            'valence': valence.value,
            'arousal': arousal,
            'threat_level': threat_level.value,
            'opportunity_level': opportunity_level.value,
            'priority_score': priority_score,
            'context': context,
            'triggers': triggers,
            'source_memory_id': source_memory_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_triggered': datetime.now(timezone.utc).isoformat(),
            'trigger_count': 0
        }
        
        result = await self.db.create('emotional_memories', memory_data)
        return str(result[0]['id'])
    
    async def _create_threat_opportunity_assessment(
        self,
        content: str,
        threat_indicators: List[str],
        threat_score: float,
        opportunity_indicators: List[str],
        opportunity_score: float,
        context: Dict[str, Any]
    ) -> str:
        """Create real-time threat/opportunity assessment"""
        
        # Determine recommended action
        if threat_score > 0.8:
            recommended_action = "immediate_intervention"
            urgency_level = 4
        elif opportunity_score > 0.8:
            recommended_action = "capitalize_opportunity"
            urgency_level = 3
        elif threat_score > 0.5:
            recommended_action = "monitor_and_prepare"
            urgency_level = 2
        elif opportunity_score > 0.5:
            recommended_action = "evaluate_opportunity"
            urgency_level = 2
        else:
            recommended_action = "continue_monitoring"
            urgency_level = 1
        
        assessment_data = {
            'content': content,
            'threat_indicators': threat_indicators,
            'threat_score': threat_score,
            'opportunity_indicators': opportunity_indicators,
            'opportunity_score': opportunity_score,
            'recommended_action': recommended_action,
            'urgency_level': urgency_level,
            'assessed_at': datetime.now(timezone.utc).isoformat(),
            'context': context
        }
        
        result = await self.db.create('threat_assessments', assessment_data)
        return str(result[0]['id'])
    
    async def get_high_priority_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get highest priority emotional memories"""
        result = await self.db.query("""
            SELECT * FROM emotional_memories 
            ORDER BY priority_score DESC, emotional_weight DESC
            LIMIT $limit
        """, {'limit': limit})
        
        return result[0]['result'] if result else []
    
    async def get_active_threats(self) -> List[Dict[str, Any]]:
        """Get current active threats requiring attention"""
        result = await self.db.query("""
            SELECT * FROM threat_assessments 
            WHERE threat_score > 0.5 
            ORDER BY threat_score DESC, urgency_level DESC
        """)
        
        return result[0]['result'] if result else []
    
    async def get_available_opportunities(self) -> List[Dict[str, Any]]:
        """Get current opportunities worth pursuing"""
        result = await self.db.query("""
            SELECT * FROM threat_assessments 
            WHERE opportunity_score > 0.5 
            ORDER BY opportunity_score DESC, urgency_level DESC
        """)
        
        return result[0]['result'] if result else []
    
    async def update_emotional_trigger(self, trigger_pattern: str, emotional_response: Dict[str, Any]):
        """Update or create emotional trigger patterns"""
        await self.db.query("""
            UPDATE emotional_triggers SET 
                activation_count += 1,
                last_activated = time::now(),
                strength = MATH::min(1.0, strength + 0.1)
            WHERE trigger_pattern = $pattern
            OR CREATE emotional_triggers SET
                trigger_pattern = $pattern,
                emotional_response = $response,
                strength = 0.5,
                activation_count = 1,
                created_at = time::now(),
                last_activated = time::now()
        """, {
            'pattern': trigger_pattern,
            'response': emotional_response
        })
    
    async def get_emotional_boost(self, query: str, context: Dict[str, Any]) -> float:
        """Get emotional boost factor for memory recall"""
        # Assess emotional relevance of query
        assessment = await self.assess_emotional_content(query, context)
        
        # Return priority score as boost factor
        return assessment['priority_score']
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive amygdala statistics"""
        
        memory_stats = await self.db.query("""
            SELECT 
                count() as total_memories,
                math::mean(emotional_weight) as avg_emotional_weight,
                math::mean(priority_score) as avg_priority_score,
                math::max(priority_score) as max_priority_score
            FROM emotional_memories
        """)
        
        threat_stats = await self.db.query("""
            SELECT 
                count() as total_assessments,
                math::mean(threat_score) as avg_threat_score,
                math::mean(opportunity_score) as avg_opportunity_score,
                count(threat_score > 0.5) as active_threats,
                count(opportunity_score > 0.5) as active_opportunities
            FROM threat_assessments
        """)
        
        memory_result = memory_stats[0]['result'][0] if memory_stats else {}
        threat_result = threat_stats[0]['result'][0] if threat_stats else {}
        
        return {**memory_result, **threat_result}
    
    async def close(self):
        """Close SurrealDB connection"""
        if self.db:
            await self.db.close()
            logger.info("Amygdala connections closed")

# Example usage for MCP integration
async def create_amygdala_mcp():
    """Factory function for MCP server integration"""
    amygdala = AmygdalaProcessor(
        surrealdb_url="ws://localhost:8000/rpc",
        namespace="biomimetic",
        database="amygdala"
    )
    await amygdala.initialize()
    return amygdala

if __name__ == "__main__":
    # Test the amygdala implementation
    async def test_amygdala():
        amygdala = await create_amygdala_mcp()
        
        # Test emotional assessment
        result = await amygdala.assess_emotional_content(
            content="BREAKTHROUGH: Jordan discovered weight-based memory eliminates TTL limitations! This is revolutionary for superhuman AI capabilities.",
            context={'source': 'biomimetic_research', 'urgency': 'high'}
        )
        
        print(f"Emotional assessment: {result}")
        
        # Test threat detection
        threat_result = await amygdala.assess_emotional_content(
            content="CRITICAL ERROR: System failure detected, data corruption possible",
            context={'source': 'system_monitor', 'severity': 'high'}
        )
        
        print(f"Threat assessment: {threat_result}")
        
        # Get statistics
        stats = await amygdala.get_statistics()
        print(f"Amygdala stats: {stats}")
        
        await amygdala.close()
    
    asyncio.run(test_amygdala())
