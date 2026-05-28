"""Neo4j connection settings for local demo scripts."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str
    user: str
    password: str


def load_config() -> Neo4jConfig:
    """Read Neo4j settings from environment variables with demo defaults."""
    return Neo4jConfig(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )
