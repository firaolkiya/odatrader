"""Cloud deployment helpers for multi-bot container orchestration."""
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("odatrade.cloud_deployer")


@dataclass
class ContainerSpec:
    bot_id: str
    name: str
    image: str = "odatrade/bot:latest"
    cpu_limit: str = "1000m"
    memory_limit: str = "1Gi"
    env: Dict[str, str] = field(default_factory=dict)
    replicas: int = 1
    cloud_provider: str = "docker"
    region: Optional[str] = None


class CloudDeployer:
    """
    Manages bot deployment across cloud providers.
    Each bot gets an isolated container with its own event pipeline.
    """

    PROVIDERS = ("docker", "kubernetes", "aws", "gcp", "digitalocean")

    def __init__(self, provider: str = "docker"):
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Choose from {self.PROVIDERS}")
        self.provider = provider
        self._deployments: Dict[str, ContainerSpec] = {}

    def create_spec(self, bot_id: str, name: str, config: dict) -> ContainerSpec:
        spec = ContainerSpec(
            bot_id=bot_id,
            name=name,
            env={
                "BOT_ID": bot_id,
                "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                "DATABASE_URL": os.getenv("DATABASE_URL", ""),
                "EVENT_BACKEND": os.getenv("EVENT_BACKEND", "redis"),
                "SYMBOLS": ",".join(config.get("symbols", ["btcusdt"])),
                "RISK_PROFILE": config.get("risk_profile", "moderate"),
            },
            cloud_provider=self.provider,
            region=config.get("cloud_region"),
        )
        self._deployments[bot_id] = spec
        return spec

    def generate_docker_compose_service(self, spec: ContainerSpec) -> dict:
        return {
            f"odatrade-bot-{spec.bot_id}": {
                "build": ".",
                "container_name": f"odatrade_bot_{spec.bot_id}",
                "command": ["python", "odatrade_cli.py", "start"],
                "environment": [f"{k}={v}" for k, v in spec.env.items()],
                "depends_on": ["odatrade-redis", "odatrade-db"],
                "deploy": {
                    "resources": {
                        "limits": {"cpus": spec.cpu_limit, "memory": spec.memory_limit},
                    },
                },
                "labels": {
                    "odatrade.bot_id": spec.bot_id,
                    "odatrade.name": spec.name,
                },
            },
        }

    def generate_k8s_manifest(self, spec: ContainerSpec) -> dict:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"odatrade-bot-{spec.bot_id}",
                "namespace": "odatrade",
                "labels": {"app": "odatrade-bot", "bot_id": spec.bot_id},
            },
            "spec": {
                "replicas": spec.replicas,
                "selector": {"matchLabels": {"bot_id": spec.bot_id}},
                "template": {
                    "metadata": {"labels": {"bot_id": spec.bot_id}},
                    "spec": {
                        "containers": [{
                            "name": "bot",
                            "image": spec.image,
                            "command": ["python", "odatrade_cli.py", "start"],
                            "env": [{"name": k, "value": v} for k, v in spec.env.items()],
                            "resources": {
                                "limits": {"cpu": spec.cpu_limit, "memory": spec.memory_limit},
                            },
                        }],
                    },
                },
            },
        }

    def deploy(self, bot_id: str) -> dict:
        spec = self._deployments.get(bot_id)
        if not spec:
            raise ValueError(f"No deployment spec for bot {bot_id}")

        if self.provider == "docker":
            return {"status": "configured", "service": self.generate_docker_compose_service(spec)}
        elif self.provider == "kubernetes":
            return {"status": "configured", "manifest": self.generate_k8s_manifest(spec)}
        else:
            logger.info("Cloud deploy stub for %s bot %s", self.provider, bot_id)
            return {"status": "stub", "provider": self.provider, "bot_id": bot_id}

    def list_deployments(self) -> List[dict]:
        return [
            {"bot_id": s.bot_id, "name": s.name, "provider": s.cloud_provider, "region": s.region}
            for s in self._deployments.values()
        ]

    def teardown(self, bot_id: str) -> bool:
        return self._deployments.pop(bot_id, None) is not None
