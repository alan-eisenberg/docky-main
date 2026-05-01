# Docky API Reference

## Modules

### `docky.config`

Configuration management for the compute framework.

```python
from docky.config import Config, load_config

# Load config from project files
config = load_config()

# Create custom config
config = Config(
    node_id="custom-node",
    cpu_limit=50,
    log_enabled=True,
)
```

**Config attributes:**
- `node_id`: Node identity string
- `auth_token`: Compute credential identifier
- `cpu_limit`: Maximum CPU allocation (0-100)
- `log_enabled`: Enable executor logging
- `max_runtime`: Auto-stop timeout in hours (-1 = disabled)

### `docky.discovery`

Service discovery with health checking.

```python
from docky.discovery import ServiceDiscovery

discovery = ServiceDiscovery(config)
service = discovery.find_available(timeout=3)
```

### `docky.executor`

Executor process lifecycle management.

```python
from docky.executor import TaskExecutor

executor = TaskExecutor(config)
pid = executor.start("eu.node-alpha.net:3333")
executor.stop()
```

### `docky.monitor`

System resource monitoring.

```python
from docky.monitor import SystemMonitor

monitor = SystemMonitor(config)
report = monitor.get_full_report()
print(report["cpu"])
print(report["memory"])
```
