"""
MongoDB Brainstem Implementation (Autonomic Data Processing)
Raw data ingestion and basic processing before higher cognition
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT

logger = logging.getLogger(__name__)

class BrainstemProcessor:
    """
    Brainstem/Medulla implementation using MongoDB for autonomic data processing.
    
    The brainstem handles basic life functions automatically before conscious awareness:
    - Raw data ingestion from external sources
    - Basic pattern filtering and routing
    - Autonomic background processing
    - Sensory data preprocessing
    - Reflexive data handling
    - System health monitoring
    
    This is the foundation layer that feeds processed data to higher brain regions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.db = None
        self.stats = {
            'raw_ingestion': 0,
            'processed_items': 0,
            'filtered_items': 0,
            'routed_items': 0,
            'autonomic_cycles': 0,
            'system_checks': 0
        }
        
        # Brainstem parameters
        self.db_name = config.get('database', 'brainstem_autonomic')
        self.batch_size = config.get('batch_size', 100)
        self.processing_interval = config.get('processing_interval', 5)  # seconds
        self.retention_days = config.get('retention_days', 365)  # Keep raw data for 1 year
        
        # Collections for different autonomic functions
        self.collections = {
            'raw_input': 'raw_sensory_input',      # All incoming data
            'processed': 'processed_autonomic',    # Filtered and categorized
            'system_health': 'system_vitals',     # Health monitoring
            'reflexive': 'reflexive_responses',   # Immediate responses
            'routing_log': 'routing_decisions'    # Routing to higher regions
        }
        
    async def initialize(self):
        """Initialize MongoDB connection and collections for brainstem processing"""
        mongodb_url = self.config.get('url', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client[self.db_name]
        
        # Test connection
        await self.client.admin.command('ping')
        
        # Initialize collections and indexes
        await self._setup_brainstem_collections()
        
        # Start autonomic processing loops
        asyncio.create_task(self._autonomic_processing_loop())
        asyncio.create_task(self._system_health_monitoring())
        
        logger.info("Brainstem (autonomic processor) initialized")
    
    async def _setup_brainstem_collections(self):
        """Set up MongoDB collections and indexes for brainstem functions"""
        
        # Raw input collection - all incoming data
        raw_input = self.db[self.collections['raw_input']]
        await raw_input.create_indexes([
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("source", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("data_type", ASCENDING)]),
            IndexModel([("processed", ASCENDING)]),
            IndexModel([("priority", DESCENDING)])
        ])
        
        # Processed collection - categorized data
        processed = self.db[self.collections['processed']]
        await processed.create_indexes([
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("routed_to", ASCENDING)]),
            IndexModel([("importance_score", DESCENDING)]),
            IndexModel([("content", TEXT)])  # Text search capability
        ])
        
        # System health collection
        health = self.db[self.collections['system_health']]
        await health.create_indexes([
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("component", ASCENDING)]),
            IndexModel([("status", ASCENDING)])
        ])
        
        # Reflexive responses collection
        reflexive = self.db[self.collections['reflexive']]
        await reflexive.create_indexes([
            IndexModel([("trigger_pattern", ASCENDING)]),
            IndexModel([("response_time", ASCENDING)]),
            IndexModel([("timestamp", DESCENDING)])
        ])
        
        logger.info("Brainstem collections and indexes initialized")
    
    async def ingest_raw_data(self, data: Any, source: str, data_type: str = 'unknown',
                             priority: int = 5) -> str:
        """
        Ingest raw data into the brainstem for autonomic processing.
        
        This is the entry point for all external data before higher cognition.
        """
        self.stats['raw_ingestion'] += 1
        
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Create raw data entry
        raw_entry = {
            '_id': entry_id,
            'data': data,
            'source': source,
            'data_type': data_type,
            'priority': priority,
            'timestamp': timestamp,
            'processed': False,
            'size_bytes': len(str(data)),
            'brainstem_id': entry_id
        }
        
        # Store in raw input collection
        collection = self.db[self.collections['raw_input']]
        await collection.insert_one(raw_entry)
        
        # Trigger immediate processing for high-priority items
        if priority >= 8:
            await self._process_immediate(raw_entry)
        
        logger.debug(f"Ingested raw data: {entry_id} from {source}")
        return entry_id
    
    async def _process_immediate(self, raw_entry: Dict[str, Any]):
        """
        Immediate processing for high-priority data (reflexive response).
        
        This simulates brainstem reflexes that happen before conscious thought.
        """
        try:
            # Categorize the data
            category = await self._categorize_data(raw_entry)
            
            # Calculate importance score
            importance = await self._calculate_importance(raw_entry, category)
            
            # Determine routing target
            routing_target = await self._determine_routing(category, importance)
            
            # Create processed entry
            processed_entry = {
                'brainstem_id': raw_entry['_id'],
                'original_data': raw_entry['data'],
                'source': raw_entry['source'],
                'category': category,
                'importance_score': importance,
                'routed_to': routing_target,
                'processing_time_ms': 0,  # Immediate processing
                'timestamp': datetime.utcnow(),
                'reflexive': True
            }
            
            # Store processed data
            collection = self.db[self.collections['processed']]
            await collection.insert_one(processed_entry)
            
            # Log routing decision
            await self._log_routing_decision(raw_entry['_id'], routing_target, importance)
            
            # Mark raw data as processed
            raw_collection = self.db[self.collections['raw_input']]
            await raw_collection.update_one(
                {'_id': raw_entry['_id']},
                {'$set': {'processed': True, 'processing_type': 'immediate'}}
            )
            
            self.stats['processed_items'] += 1
            
        except Exception as e:
            logger.error(f"Immediate processing failed for {raw_entry['_id']}: {str(e)}")
    
    async def _autonomic_processing_loop(self):
        """
        Background autonomic processing loop.
        
        This continuously processes raw data in the background,
        similar to how the brainstem handles vital functions automatically.
        """
        while True:
            try:
                # Get unprocessed raw data
                collection = self.db[self.collections['raw_input']]
                unprocessed = await collection.find(
                    {'processed': False},
                    limit=self.batch_size
                ).sort('priority', DESCENDING).to_list(length=self.batch_size)
                
                if unprocessed:
                    # Process batch
                    for raw_entry in unprocessed:
                        await self._process_autonomic(raw_entry)
                    
                    self.stats['autonomic_cycles'] += 1
                    logger.debug(f"Autonomic cycle processed {len(unprocessed)} items")
                
                # Wait before next cycle
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Autonomic processing loop error: {str(e)}")
                await asyncio.sleep(30)  # Longer wait on error
    
    async def _process_autonomic(self, raw_entry: Dict[str, Any]):
        """Process data autonomically (background processing)"""
        start_time = datetime.utcnow()
        
        try:
            # Categorize and analyze
            category = await self._categorize_data(raw_entry)
            importance = await self._calculate_importance(raw_entry, category)
            routing_target = await self._determine_routing(category, importance)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create processed entry
            processed_entry = {
                'brainstem_id': raw_entry['_id'],
                'original_data': raw_entry['data'],
                'source': raw_entry['source'],
                'category': category,
                'importance_score': importance,
                'routed_to': routing_target,
                'processing_time_ms': processing_time,
                'timestamp': datetime.utcnow(),
                'reflexive': False
            }
            
            # Store processed data
            collection = self.db[self.collections['processed']]
            await collection.insert_one(processed_entry)
            
            # Log routing decision
            await self._log_routing_decision(raw_entry['_id'], routing_target, importance)
            
            # Mark as processed
            raw_collection = self.db[self.collections['raw_input']]
            await raw_collection.update_one(
                {'_id': raw_entry['_id']},
                {'$set': {'processed': True, 'processing_type': 'autonomic'}}
            )
            
            self.stats['processed_items'] += 1
            
        except Exception as e:
            logger.error(f"Autonomic processing failed for {raw_entry['_id']}: {str(e)}")
    
    async def _categorize_data(self, raw_entry: Dict[str, Any]) -> str:
        """
        Categorize incoming data for routing to appropriate brain regions.
        
        This is basic pattern recognition before higher cognitive processing.
        """
        data = raw_entry['data']
        source = raw_entry['source']
        data_type = raw_entry['data_type']
        
        # Basic categorization logic
        if isinstance(data, dict):
            if 'error' in str(data).lower() or 'exception' in str(data).lower():
                return 'system_alert'
            elif 'memory' in str(data).lower() or 'remember' in str(data).lower():
                return 'memory_operation'
            elif 'tool' in str(data).lower() or 'function' in str(data).lower():
                return 'tool_execution'
            elif 'user' in str(data).lower() or 'input' in str(data).lower():
                return 'user_interaction'
        
        # Source-based categorization
        if 'sensor' in source.lower():
            return 'sensory_input'
        elif 'api' in source.lower():
            return 'api_data'
        elif 'file' in source.lower():
            return 'file_data'
        elif 'database' in source.lower():
            return 'database_operation'
        
        # Data type categorization
        if data_type in ['json', 'dict']:
            return 'structured_data'
        elif data_type in ['text', 'string']:
            return 'text_data'
        elif data_type in ['image', 'binary']:
            return 'binary_data'
        
        return 'unclassified'
    
    async def _calculate_importance(self, raw_entry: Dict[str, Any], category: str) -> float:
        """
        Calculate importance score for routing decisions.
        
        This helps determine which brain region should receive the data.
        """
        base_importance = raw_entry.get('priority', 5) / 10.0  # Normalize to 0-1
        
        # Category-based importance adjustment
        category_weights = {
            'system_alert': 0.9,
            'memory_operation': 0.8,
            'user_interaction': 0.7,
            'tool_execution': 0.6,
            'api_data': 0.5,
            'sensory_input': 0.4,
            'file_data': 0.3,
            'structured_data': 0.4,
            'text_data': 0.3,
            'binary_data': 0.2,
            'unclassified': 0.1
        }
        
        category_weight = category_weights.get(category, 0.3)
        
        # Size factor (larger data might be more important)
        size_factor = min(0.2, raw_entry.get('size_bytes', 0) / 10000)
        
        # Time sensitivity (newer data might be more important)
        age_seconds = (datetime.utcnow() - raw_entry['timestamp']).total_seconds()
        time_factor = max(0.0, 0.2 - (age_seconds / 3600))  # Decay over hours
        
        final_importance = min(1.0, base_importance + category_weight + size_factor + time_factor)
        return final_importance
    
    async def _determine_routing(self, category: str, importance: float) -> List[str]:
        """
        Determine which brain regions should receive this data.
        
        This implements the routing function of the brainstem.
        """
        targets = []
        
        # High importance items go to multiple regions
        if importance >= 0.8:
            targets.append('hippocampus')  # Working memory
            targets.append('amygdala')     # Priority assessment
        
        # Category-specific routing
        if category in ['memory_operation', 'user_interaction']:
            targets.append('hippocampus')
            targets.append('neocortex')
        elif category in ['tool_execution', 'api_data']:
            targets.append('cerebellum')
            targets.append('hippocampus')
        elif category == 'system_alert':
            targets.append('amygdala')
            targets.append('hippocampus')
        elif category in ['sensory_input', 'text_data']:
            targets.append('neocortex')
        
        # Default routing for unclassified
        if not targets:
            targets.append('hippocampus')
        
        return list(set(targets))  # Remove duplicates
    
    async def _log_routing_decision(self, brainstem_id: str, targets: List[str], importance: float):
        """Log routing decisions for analysis"""
        routing_entry = {
            'brainstem_id': brainstem_id,
            'targets': targets,
            'importance': importance,
            'timestamp': datetime.utcnow(),
            'decision_type': 'autonomic_routing'
        }
        
        collection = self.db[self.collections['routing_log']]
        await collection.insert_one(routing_entry)
        
        self.stats['routed_items'] += 1
    
    async def _system_health_monitoring(self):
        """
        Monitor system health (vital signs of the cognitive architecture).
        
        This is like monitoring heart rate, breathing, etc.
        """
        while True:
            try:
                self.stats['system_checks'] += 1
                
                # Check processing queue health
                raw_collection = self.db[self.collections['raw_input']]
                unprocessed_count = await raw_collection.count_documents({'processed': False})
                
                # Check processing rate
                recent_processed = await self.db[self.collections['processed']].count_documents({
                    'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=5)}
                })
                
                # Calculate health metrics
                queue_health = 'healthy' if unprocessed_count < 1000 else 'congested'
                processing_rate = recent_processed / 5.0  # items per minute
                
                # Store health data
                health_entry = {
                    'component': 'brainstem_processor',
                    'timestamp': datetime.utcnow(),
                    'status': queue_health,
                    'metrics': {
                        'unprocessed_queue': unprocessed_count,
                        'processing_rate_per_minute': processing_rate,
                        'total_processed': self.stats['processed_items'],
                        'total_ingested': self.stats['raw_ingestion']
                    }
                }
                
                health_collection = self.db[self.collections['system_health']]
                await health_collection.insert_one(health_entry)
                
                # Clean up old health data (keep last 24 hours)
                cutoff = datetime.utcnow() - timedelta(hours=24)
                await health_collection.delete_many({'timestamp': {'$lt': cutoff}})
                
                logger.debug(f"System health check: {queue_health}, rate: {processing_rate:.1f}/min")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"System health monitoring error: {str(e)}")
                await asyncio.sleep(300)  # Longer wait on error
    
    async def get_processed_data(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get processed data for routing to higher brain regions"""
        collection = self.db[self.collections['processed']]
        
        query = {}
        if category:
            query['category'] = category
        
        cursor = collection.find(query).sort('importance_score', DESCENDING).limit(limit)
        results = await cursor.to_list(length=limit)
        
        return results
    
    async def get_routing_targets(self, brainstem_id: str) -> List[str]:
        """Get routing targets for a specific data item"""
        collection = self.db[self.collections['routing_log']]
        routing_info = await collection.find_one({'brainstem_id': brainstem_id})
        
        return routing_info.get('targets', []) if routing_info else []
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        collection = self.db[self.collections['system_health']]
        latest_health = await collection.find_one(
            sort=[('timestamp', DESCENDING)]
        )
        
        return latest_health if latest_health else {'status': 'unknown'}
    
    async def cleanup_old_data(self):
        """Clean up old raw data based on retention policy"""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # Clean up old raw input
        raw_collection = self.db[self.collections['raw_input']]
        result = await raw_collection.delete_many({
            'timestamp': {'$lt': cutoff},
            'processed': True
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old raw data entries")
        
        return result.deleted_count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get brainstem processing statistics"""
        # Get collection counts
        raw_count = await self.db[self.collections['raw_input']].count_documents({})
        processed_count = await self.db[self.collections['processed']].count_documents({})
        unprocessed_count = await self.db[self.collections['raw_input']].count_documents({'processed': False})
        
        # Get recent processing rate
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_processed = await self.db[self.collections['processed']].count_documents({
            'timestamp': {'$gte': recent_cutoff}
        })
        
        return {
            **self.stats,
            'total_raw_entries': raw_count,
            'total_processed': processed_count,
            'unprocessed_queue': unprocessed_count,
            'recent_processing_rate': recent_processed,
            'processing_efficiency': (processed_count / max(raw_count, 1)) * 100,
            'autonomic_functions': [
                'raw_data_ingestion',
                'pattern_categorization',
                'importance_assessment',
                'routing_decisions',
                'system_health_monitoring',
                'reflexive_processing'
            ],
            'status': 'autonomic_active'
        }
    
    async def shutdown(self):
        """Gracefully shutdown brainstem processor"""
        if self.client:
            self.client.close()
        logger.info("Brainstem (autonomic processor) shutdown")

# Integration helpers
async def brainstem_data_ingestion(data: Any, source: str, importance: int = 5):
    """Helper function for ingesting data into brainstem processing"""
    # This would be injected with actual brainstem instance
    pass

async def get_processed_for_brain_region(region: str, limit: int = 50):
    """Helper to get processed data for specific brain region"""
    # This would be injected with actual brainstem instance
    pass
