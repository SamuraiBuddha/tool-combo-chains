"""
Cerebellum Brain Region - Neo4j Implementation
Biomimetic Neuromorphic Architecture - Procedural Memory & Skill Learning

Function: Skills, procedures, automated behaviors, and muscle memory
Database: Neo4j for graph-based skill sequences and connection weights
"""

import asyncio
from neo4j import AsyncGraphDatabase
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import json
import logging
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class SkillLevel(Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

@dataclass
class Skill:
    id: str
    name: str
    skill_type: str
    level: SkillLevel
    confidence: float
    practice_count: int
    last_practiced: datetime
    success_rate: float

@dataclass
class ProcedureStep:
    id: str
    action: str
    parameters: Dict[str, Any]
    expected_outcome: str
    confidence: float

class CerebellumProcessor:
    """
    Cerebellum - Procedural Memory & Skill Learning Processor
    
    Biological Functions Implemented:
    - Skill sequence learning and execution
    - Motor pattern automation (muscle memory)
    - Connection weights that strengthen with practice
    - Automated behavior chains
    - Procedural knowledge storage
    - Error correction and fine-tuning
    """
    
    def __init__(self, neo4j_uri: str, username: str, password: str):
        self.neo4j_uri = neo4j_uri
        self.username = username
        self.password = password
        self.driver = None
        
    async def initialize(self):
        """Initialize Neo4j connection and create constraints"""
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.username, self.password)
        )
        
        await self._create_constraints()
        await self._create_indexes()
        logger.info("Cerebellum initialized with Neo4j")
        
    async def _create_constraints(self):
        """Create Neo4j constraints for data integrity"""
        async with self.driver.session() as session:
            # Skill node constraints
            await session.run("""
                CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
                FOR (s:Skill) REQUIRE s.id IS UNIQUE
            """)
            
            # Procedure step constraints
            await session.run("""
                CREATE CONSTRAINT step_id_unique IF NOT EXISTS
                FOR (step:ProcedureStep) REQUIRE step.id IS UNIQUE
            """)
            
            # Tool combo constraints
            await session.run("""
                CREATE CONSTRAINT combo_id_unique IF NOT EXISTS
                FOR (combo:ToolCombo) REQUIRE combo.id IS UNIQUE
            """)
            
    async def _create_indexes(self):
        """Create indexes for performance optimization"""
        async with self.driver.session() as session:
            # Index on skill confidence for fast sorting
            await session.run("""
                CREATE INDEX skill_confidence_idx IF NOT EXISTS
                FOR (s:Skill) ON (s.confidence)
            """)
            
            # Index on practice count
            await session.run("""
                CREATE INDEX skill_practice_idx IF NOT EXISTS  
                FOR (s:Skill) ON (s.practice_count)
            """)
            
            # Index on relationship strength
            await session.run("""
                CREATE INDEX relationship_strength_idx IF NOT EXISTS
                FOR ()-[r:LEADS_TO]-() ON (r.strength)
            """)
    
    async def learn_skill_sequence(
        self, 
        skill_name: str,
        steps: List[Dict[str, Any]],
        skill_type: str = "tool_combo",
        initial_confidence: float = 0.3
    ) -> str:
        """
        Learn a new skill sequence through practice
        
        Biological Process: Cerebellar learning of motor sequences
        """
        skill_id = str(uuid.uuid4())
        
        async with self.driver.session() as session:
            # Create skill node
            await session.run("""
                CREATE (s:Skill {
                    id: $skill_id,
                    name: $skill_name,
                    skill_type: $skill_type,
                    level: 'novice',
                    confidence: $initial_confidence,
                    practice_count: 0,
                    created_at: datetime(),
                    last_practiced: datetime(),
                    success_rate: 0.0
                })
            """, skill_id=skill_id, skill_name=skill_name, 
                skill_type=skill_type, initial_confidence=initial_confidence)
            
            # Create procedure steps and connections
            previous_step_id = None
            for i, step_data in enumerate(steps):
                step_id = str(uuid.uuid4())
                
                # Create step node
                await session.run("""
                    CREATE (step:ProcedureStep {
                        id: $step_id,
                        action: $action,
                        parameters: $parameters,
                        expected_outcome: $expected_outcome,
                        step_number: $step_number,
                        confidence: $confidence,
                        created_at: datetime()
                    })
                """, 
                    step_id=step_id,
                    action=step_data['action'],
                    parameters=json.dumps(step_data.get('parameters', {})),
                    expected_outcome=step_data.get('expected_outcome', ''),
                    step_number=i,
                    confidence=initial_confidence
                )
                
                # Connect skill to first step
                if i == 0:
                    await session.run("""
                        MATCH (s:Skill {id: $skill_id})
                        MATCH (step:ProcedureStep {id: $step_id})
                        CREATE (s)-[:STARTS_WITH {strength: 1.0}]->(step)
                    """, skill_id=skill_id, step_id=step_id)
                
                # Connect previous step to current step
                if previous_step_id:
                    await session.run("""
                        MATCH (prev:ProcedureStep {id: $prev_id})
                        MATCH (curr:ProcedureStep {id: $curr_id})
                        CREATE (prev)-[:LEADS_TO {
                            strength: $strength,
                            practice_count: 0,
                            success_rate: 0.0
                        }]->(curr)
                    """, prev_id=previous_step_id, curr_id=step_id, strength=initial_confidence)
                
                previous_step_id = step_id
            
            logger.info(f"Learned new skill sequence: {skill_name} with {len(steps)} steps")
            return skill_id
    
    async def execute_skill(self, skill_id: str) -> List[Dict[str, Any]]:
        """
        Execute a learned skill by following the strongest path
        
        Biological Process: Automated execution of learned motor patterns
        """
        async with self.driver.session() as session:
            # Get skill execution path
            result = await session.run("""
                MATCH (s:Skill {id: $skill_id})-[:STARTS_WITH]->(first:ProcedureStep)
                MATCH path = (first)-[:LEADS_TO*]->(last:ProcedureStep)
                WHERE NOT (last)-[:LEADS_TO]->()
                WITH path, 
                     [r in relationships(path) | r.strength] as strengths,
                     reduce(total = 0, str in [r in relationships(path) | r.strength] | total + str) as total_strength
                ORDER BY total_strength DESC
                LIMIT 1
                RETURN nodes(path) as steps, total_strength as confidence
            """, skill_id=skill_id)
            
            record = await result.single()
            if not record:
                logger.warning(f"No execution path found for skill {skill_id}")
                return []
            
            steps = []
            for step_node in record['steps']:
                step = {
                    'id': step_node['id'],
                    'action': step_node['action'],
                    'parameters': json.loads(step_node['parameters']),
                    'expected_outcome': step_node['expected_outcome'],
                    'confidence': step_node['confidence']
                }
                steps.append(step)
            
            # Update practice statistics
            await self._update_practice_stats(skill_id, success=True)
            
            logger.info(f"Executed skill {skill_id} with {len(steps)} steps")
            return steps
    
    async def reinforce_skill_practice(
        self, 
        skill_id: str, 
        execution_success: bool,
        step_performances: List[Dict[str, Any]] = None
    ):
        """
        Reinforce skill through practice (Hebbian learning)
        
        Strengthens connections for successful executions, weakens for failures
        """
        async with self.driver.session() as session:
            # Update overall skill statistics
            if execution_success:
                await session.run("""
                    MATCH (s:Skill {id: $skill_id})
                    SET s.practice_count = s.practice_count + 1,
                        s.confidence = CASE 
                            WHEN s.confidence < 0.95 THEN s.confidence + 0.05
                            ELSE 0.95 
                        END,
                        s.last_practiced = datetime(),
                        s.success_rate = (s.success_rate * s.practice_count + 1.0) / (s.practice_count + 1)
                """, skill_id=skill_id)
                
                # Strengthen all connections in the successful path
                await session.run("""
                    MATCH (s:Skill {id: $skill_id})-[:STARTS_WITH]->(first:ProcedureStep)
                    MATCH (first)-[r:LEADS_TO*]->(last)
                    WHERE NOT (last)-[:LEADS_TO]->()
                    FOREACH (rel in r |
                        SET rel.strength = CASE 
                            WHEN rel.strength < 0.95 THEN rel.strength + 0.1
                            ELSE 0.95
                        END,
                        rel.practice_count = rel.practice_count + 1,
                        rel.success_rate = (rel.success_rate * rel.practice_count + 1.0) / (rel.practice_count + 1)
                    )
                """, skill_id=skill_id)
                
            else:
                # Slightly weaken connections for failed executions
                await session.run("""
                    MATCH (s:Skill {id: $skill_id})
                    SET s.practice_count = s.practice_count + 1,
                        s.confidence = CASE 
                            WHEN s.confidence > 0.1 THEN s.confidence - 0.02
                            ELSE 0.1
                        END,
                        s.last_practiced = datetime(),
                        s.success_rate = (s.success_rate * s.practice_count + 0.0) / (s.practice_count + 1)
                """, skill_id=skill_id)
            
            # Update skill level based on confidence and practice
            await self._update_skill_level(skill_id)
            
            logger.info(f"Reinforced skill {skill_id}, success: {execution_success}")
    
    async def _update_skill_level(self, skill_id: str):
        """Update skill level based on confidence and practice count"""
        async with self.driver.session() as session:
            await session.run("""
                MATCH (s:Skill {id: $skill_id})
                SET s.level = CASE
                    WHEN s.confidence >= 0.9 AND s.practice_count >= 100 THEN 'master'
                    WHEN s.confidence >= 0.8 AND s.practice_count >= 50 THEN 'expert'
                    WHEN s.confidence >= 0.7 AND s.practice_count >= 25 THEN 'advanced'
                    WHEN s.confidence >= 0.5 AND s.practice_count >= 10 THEN 'intermediate'
                    WHEN s.confidence >= 0.3 AND s.practice_count >= 3 THEN 'beginner'
                    ELSE 'novice'
                END
            """, skill_id=skill_id)
    
    async def _update_practice_stats(self, skill_id: str, success: bool):
        """Update practice statistics for skill execution"""
        async with self.driver.session() as session:
            await session.run("""
                MATCH (s:Skill {id: $skill_id})
                SET s.practice_count = s.practice_count + 1,
                    s.last_practiced = datetime()
            """, skill_id=skill_id)
    
    async def find_relevant_skills(self, query_context: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find skills relevant to current context"""
        async with self.driver.session() as session:
            # Simple relevance based on skill names and types
            result = await session.run("""
                MATCH (s:Skill)
                WHERE s.name CONTAINS $query OR s.skill_type CONTAINS $query
                RETURN s.id as id, s.name as name, s.skill_type as skill_type,
                       s.confidence as confidence, s.level as level, 
                       s.practice_count as practice_count, s.success_rate as success_rate
                ORDER BY s.confidence DESC, s.practice_count DESC
                LIMIT $limit
            """, query=query_context, limit=limit)
            
            skills = []
            async for record in result:
                skill = {
                    'id': record['id'],
                    'name': record['name'],
                    'skill_type': record['skill_type'],
                    'confidence': record['confidence'],
                    'level': record['level'],
                    'practice_count': record['practice_count'],
                    'success_rate': record['success_rate']
                }
                skills.append(skill)
            
            return skills
    
    async def create_tool_combo_skill(
        self, 
        combo_name: str,
        tools: List[str],
        expected_amplification: float = 100.0
    ) -> str:
        """Create a specialized tool combo skill"""
        
        # Convert tools into procedure steps
        steps = []
        for i, tool in enumerate(tools):
            step = {
                'action': f'execute_tool_{i+1}',
                'parameters': {'tool_name': tool, 'step_order': i+1},
                'expected_outcome': f'{tool} execution successful'
            }
            steps.append(step)
        
        skill_id = await self.learn_skill_sequence(
            skill_name=combo_name,
            steps=steps,
            skill_type='tool_combo'
        )
        
        # Add tool combo specific metadata
        async with self.driver.session() as session:
            await session.run("""
                MATCH (s:Skill {id: $skill_id})
                SET s.expected_amplification = $amplification,
                    s.tools = $tools,
                    s.combo_type = 'biomimetic'
            """, skill_id=skill_id, amplification=expected_amplification, tools=tools)
        
        logger.info(f"Created tool combo skill: {combo_name}")
        return skill_id
    
    async def get_skill_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about procedural memory"""
        async with self.driver.session() as session:
            stats = await session.run("""
                MATCH (s:Skill)
                RETURN 
                    count(s) as total_skills,
                    avg(s.confidence) as avg_confidence,
                    avg(s.practice_count) as avg_practice_count,
                    avg(s.success_rate) as avg_success_rate,
                    collect(DISTINCT s.level) as skill_levels,
                    collect(DISTINCT s.skill_type) as skill_types
            """)
            
            record = await stats.single()
            
            # Get relationship statistics
            rel_stats = await session.run("""
                MATCH ()-[r:LEADS_TO]->()
                RETURN 
                    count(r) as total_connections,
                    avg(r.strength) as avg_connection_strength,
                    avg(r.success_rate) as avg_connection_success
            """)
            
            rel_record = await rel_stats.single()
            
            return {
                'total_skills': record['total_skills'],
                'avg_confidence': record['avg_confidence'],
                'avg_practice_count': record['avg_practice_count'],
                'avg_success_rate': record['avg_success_rate'],
                'skill_levels': record['skill_levels'],
                'skill_types': record['skill_types'],
                'total_connections': rel_record['total_connections'],
                'avg_connection_strength': rel_record['avg_connection_strength'],
                'avg_connection_success': rel_record['avg_connection_success']
            }
    
    async def optimize_skill_paths(self, min_strength: float = 0.1):
        """Optimize skill execution paths by removing weak connections"""
        async with self.driver.session() as session:
            # Remove very weak connections (natural forgetting)
            result = await session.run("""
                MATCH ()-[r:LEADS_TO]->()
                WHERE r.strength < $min_strength
                DELETE r
                RETURN count(r) as removed_connections
            """, min_strength=min_strength)
            
            record = await result.single()
            removed = record['removed_connections']
            
            logger.info(f"Optimized skill paths, removed {removed} weak connections")
            return removed
    
    async def identify_skill_patterns(self) -> List[Dict[str, Any]]:
        """Identify common patterns across different skills"""
        async with self.driver.session() as session:
            # Find common step sequences across skills
            result = await session.run("""
                MATCH (s1:Skill)-[:STARTS_WITH]->(step1:ProcedureStep)-[:LEADS_TO]->(step2:ProcedureStep)
                MATCH (s2:Skill)-[:STARTS_WITH]->(other1:ProcedureStep)-[:LEADS_TO]->(other2:ProcedureStep)
                WHERE s1.id <> s2.id 
                AND step1.action = other1.action 
                AND step2.action = other2.action
                RETURN step1.action as first_action, step2.action as second_action,
                       count(*) as pattern_frequency,
                       collect(DISTINCT s1.name) as skills_using_pattern
                ORDER BY pattern_frequency DESC
                LIMIT 10
            """)
            
            patterns = []
            async for record in result:
                pattern = {
                    'sequence': [record['first_action'], record['second_action']],
                    'frequency': record['pattern_frequency'],
                    'skills': record['skills_using_pattern']
                }
                patterns.append(pattern)
            
            logger.info(f"Identified {len(patterns)} skill patterns")
            return patterns
    
    async def close(self):
        """Close Neo4j driver connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Cerebellum connections closed")

# Example usage for MCP integration
async def create_cerebellum_mcp():
    """Factory function for MCP server integration"""
    cerebellum = CerebellumProcessor(
        neo4j_uri="bolt://localhost:7687",
        username="neo4j",
        password="biomimetic_brain"
    )
    await cerebellum.initialize()
    return cerebellum

if __name__ == "__main__":
    # Test the cerebellum implementation
    async def test_cerebellum():
        cerebellum = await create_cerebellum_mcp()
        
        # Test tool combo skill creation
        skill_id = await cerebellum.create_tool_combo_skill(
            combo_name="Memory → Sequential → Sandbox Analysis",
            tools=["hybrid_memory", "sequential_thinking", "sandbox_analysis"],
            expected_amplification=100.0
        )
        
        print(f"Created skill: {skill_id}")
        
        # Test skill execution
        execution_steps = await cerebellum.execute_skill(skill_id)
        print(f"Execution steps: {len(execution_steps)}")
        
        # Reinforce the skill
        await cerebellum.reinforce_skill_practice(skill_id, success=True)
        
        # Get statistics
        stats = await cerebellum.get_skill_statistics()
        print(f"Cerebellum stats: {stats}")
        
        await cerebellum.close()
    
    asyncio.run(test_cerebellum())
