# Distributed Shadow Clone Infrastructure with Ray

## Overview

Evolution from local shadow clones (n8n + VLLM) to distributed shadow clones across MAGI/NAS infrastructure using Ray.

## Infrastructure Mapping

### MAGI Systems (Compute Nodes)

**Melchior** (Primary Workstation)
- CPU: Intel i9-11900K
- GPU: RTX A5000 24GB
- RAM: 128GB
- OS: Windows (needs WSL2 for VLLM)
- Role: Large model inference, primary development

**Balthazar** (Secondary Workstation)  
- CPU: AMD Ryzen 9 5950X
- GPU: RTX A4000 16GB
- RAM: 128GB
- OS: Windows (consider Linux dual-boot)
- Role: Fast model inference, parallel experiments

**Caspar** (Future)
- Reserved for expansion

### NAS Systems (Storage/Service Nodes)

**Adam** (TrueNAS)
- Role: Distributed database (SurrealDB)
- Edge computing coordinator
- Real-time data sync

**Lilith** (Storage/Database Server)
- Role: PostgreSQL + pgvector + AGE
- Hybrid memory backend
- Optimized for I/O operations

## Ray Distributed Architecture

```python
# ray_config.yaml
cluster_name: shadow_clone_network

provider:
  type: local
  
nodes:
  melchior:
    ip: 192.168.1.100
    resources:
      GPU: 1
      GPU_memory: 24000
      node_type: "inference_heavy"
      
  balthazar:
    ip: 192.168.1.101  
    resources:
      GPU: 1
      GPU_memory: 16000
      node_type: "inference_fast"
      
  lilith:
    ip: 192.168.1.102
    resources:
      node_type: "database"
      memory: 64000
      
  adam:
    ip: 192.168.1.103
    resources:
      node_type: "edge"
      distributed_db: true
```

## Deployment Phases

### Phase 1: Local Proof of Concept (Current)
- Single machine n8n + VLLM
- Test shadow clone patterns
- Measure baseline performance

### Phase 2: WSL2 VLLM Setup
```bash
# On Melchior/Balthazar Windows machines
wsl --install
wsl --set-default-version 2

# Inside WSL2
curl -sSL https://install.python-poetry.org | python3 -
poetry new vllm-inference
cd vllm-inference
poetry add vllm ray torch

# Configure GPU passthrough
```

### Phase 3: Ray Cluster Setup
```python
# ray_head.py (run on Melchior)
import ray
ray.init(
    address="0.0.0.0:6379",
    include_dashboard=True,
    dashboard_host="0.0.0.0"
)

# ray_worker.py (run on other nodes)
ray.init(address="melchior:6379")
```

### Phase 4: Distributed Shadow Clones

```python
import ray
from typing import List, Dict, Any

# Define specialized clones for each node
@ray.remote(resources={"node_type": "inference_heavy"})
class HeavyInferenceClone:
    def __init__(self):
        from vllm import LLM
        self.llm = LLM("meta-llama/Llama-3.1-70B-Instruct", 
                      tensor_parallel_size=1,
                      gpu_memory_utilization=0.9)
    
    def deep_analysis(self, prompt: str) -> str:
        return self.llm.generate(prompt, max_tokens=2000)

@ray.remote(resources={"node_type": "inference_fast"})
class FastIterationClone:
    def __init__(self):
        from vllm import LLM
        self.llm = LLM("mistralai/Mistral-7B-Instruct-v0.3",
                      gpu_memory_utilization=0.8)
    
    def rapid_variations(self, prompts: List[str]) -> List[str]:
        return self.llm.generate(prompts, max_tokens=200)

@ray.remote(resources={"node_type": "database"})
class MemoryClone:
    def __init__(self):
        import psycopg2
        self.conn = psycopg2.connect(
            host="lilith",
            database="hybrid_memory",
            user="shadow_clone",
            password="secure_pass"
        )
    
    def vector_search(self, embedding, limit=10):
        # Direct DB operations on Lilith
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_entities 
            ORDER BY embedding <-> %s 
            LIMIT %s
        """, (embedding, limit))
        return cursor.fetchall()

@ray.remote(resources={"node_type": "edge"})
class ConsensusClone:
    def __init__(self):
        from surrealdb import SurrealDB
        self.db = SurrealDB("ws://adam:8000/rpc")
        
    def distributed_consensus(self, results: List[Dict]) -> Dict:
        # Use SurrealDB's distributed features
        return self.db.query("""
            CREATE consensus:result SET
                votes = $results,
                timestamp = time::now(),
                consensus = array::group($results)
        """, {"results": results})

# Orchestrator that uses all clones
class DistributedShadowCloneOrchestrator:
    def __init__(self):
        self.heavy = HeavyInferenceClone.remote()
        self.fast = FastIterationClone.remote()
        self.memory = MemoryClone.remote()
        self.consensus = ConsensusClone.remote()
    
    async def execute_mission(self, mission: Dict[str, Any]):
        # Spawn shadow clones across the network
        tasks = []
        
        # Heavy analysis on Melchior
        if mission.get("needs_deep_analysis"):
            tasks.append(self.heavy.deep_analysis.remote(mission["prompt"]))
        
        # Fast iterations on Balthazar
        if mission.get("variations"):
            tasks.append(self.fast.rapid_variations.remote(mission["variations"]))
        
        # Memory search on Lilith
        if mission.get("context_needed"):
            tasks.append(self.memory.vector_search.remote(mission["embedding"]))
        
        # Wait for all clones
        results = await ray.get(tasks)
        
        # Consensus on Adam
        consensus = await ray.get(
            self.consensus.distributed_consensus.remote(results)
        )
        
        return consensus
```

## Network Considerations

### GPU Access in WSL2
```bash
# Install NVIDIA Container Toolkit in WSL2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```

### Ray Dashboard Access
- Primary dashboard: http://melchior:8265
- Grafana metrics: http://lilith:3000
- Ray timeline: http://melchior:8265/timeline

## Performance Expectations

| Operation | Local (n8n) | Distributed (Ray) | Improvement |
|-----------|--------------|-------------------|-------------|
| Single inference | 500ms | 450ms | 1.1x |
| Parallel inference (10) | 5000ms | 500ms | 10x |
| Memory + Inference | 1000ms | 600ms | 1.7x |
| Full shadow clone op | 2000ms | 400ms | 5x |

## Monitoring and Observability

```python
# ray_monitor.py
import ray
from ray.dashboard.modules.job.job_head import JobHead

@ray.remote
class ShadowCloneMonitor:
    def get_cluster_status(self):
        nodes = ray.nodes()
        return {
            "total_nodes": len(nodes),
            "gpu_nodes": sum(1 for n in nodes if n.get("GPU", 0) > 0),
            "total_gpus": sum(n.get("GPU", 0) for n in nodes),
            "active_clones": len(ray.util.list_actors())
        }
    
    def get_performance_metrics(self):
        return ray.get(ray.util.get_cluster_metrics())
```

## Security Considerations

1. **WSL2 Firewall**: Configure Windows Defender for WSL2 ports
2. **Ray Authentication**: Use TLS between nodes
3. **Database Access**: Tunnel DB connections through SSH
4. **Model Weights**: Store on Adam, mount via SMB/NFS

## Next Steps

1. [ ] Test VLLM in WSL2 on Melchior
2. [ ] Install Ray on all nodes
3. [ ] Configure network discovery
4. [ ] Set up monitoring stack
5. [ ] Migrate n8n workflows to Ray
6. [ ] Benchmark distributed vs local performance

---

*"From local shadow clones to distributed consciousness across the MAGI network"*
