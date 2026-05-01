# Docky - Distributed Compute Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/alan-eisenberg/docky-main/actions/workflows/ci.yml/badge.svg)](https://github.com/alan-eisenberg/docky-main/actions)

A high-throughput distributed compute framework for scheduling and executing
computational workloads across heterogeneous node clusters. Docky provides
abstractions for executor process management, service discovery, and real-time
resource monitoring.

## Features

- **Executor Orchestration**: Spawn and manage compute executor processes with
  automatic lifecycle management and health monitoring
- **Service Discovery**: Built-in pool of compute service endpoints with TCP
  health checking and automatic failover on connection failure
- **Resource Monitoring**: Real-time CPU, memory, and hugepages utilization
  tracking for capacity planning and load balancing
- **CLI Interface**: Simple command-line interface for starting, stopping,
  and monitoring compute workloads
- **Configurable Scheduling**: Fine-grained control over CPU allocation,
  node identity, and runtime limits

## Quick Start

### Installation

```bash
pip install -r requirements.txt
pip install -e .
```

### Usage

```bash
# Start compute executors
python -m docky

# Start with logging
python -m docky --log

# Set custom node identity
python -m docky --id node-alpha

# Auto-stop after N hours
python -m docky --h 8

# Stop all processes
python -m docky --stop
```

### Shell Launcher

```bash
# Start
./run.sh

# With logging
./run.sh --log

# Stop
./run.sh --stop
```

## Architecture

```
docky/
├── src/docky/
│   ├── __init__.py      # Package metadata
│   ├── __main__.py      # CLI entry point
│   ├── config.py        # Configuration management
│   ├── executor.py      # Executor process lifecycle
│   ├── discovery.py     # Service discovery & failover
│   └── monitor.py       # System resource monitoring
├── docky/engine/
│   └── processor        # Native compute engine (Rust)
├── tests/               # Test suite
├── docs/                # API documentation
└── benchmarks/          # Performance benchmarks
```

## Configuration

### .env

Environment configuration is stored in `.env`:

```
DOCKY_NODE_ID=your-node-identity-token
DOCKY_ENVIRONMENT=production
DOCKY_LOG_LEVEL=info
```

### Environment Variables

| Variable            | Description              |
|---------------------|--------------------------|
| DOCKY_NODE_ID      | Node identity string      |
| DOCKY_ENVIRONMENT  | Environment name          |
| DOCKY_LOG_LEVEL    | Logging level             |

## API Reference

See [docs/](docs/) for full API documentation.

### TaskExecutor

```python
from docky.executor import TaskExecutor
from docky.config import load_config

config = load_config()
executor = TaskExecutor(config)
pid = executor.start("eu.node-alpha.net:3333")
```

### ServiceDiscovery

```python
from docky.discovery import ServiceDiscovery

discovery = ServiceDiscovery(config)
service = discovery.find_available()
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Lint
ruff check src/

# Type check
mypy src/
```

## License

MIT License - see LICENSE for details.
