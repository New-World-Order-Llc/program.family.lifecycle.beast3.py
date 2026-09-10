# program.family.lifecycle.beast3.py
# Beast System 3.0 — Deterministic Family Lifecycle Module

from dataclasses import dataclass, field
import time
import hashlib

LIFECYCLE_STATES = [
    "ENROLLED",
    "ACTIVE_SUPPORT",
    "ELEVATED_SUPPORT",
    "STABILIZATION",
    "TRANSITION",
    "COMPLETED"
]

@dataclass
class LifecycleEvent:
    old_state: str
    new_state: str
    metadata: dict
    ts: float = field(default_factory=time.time)

@dataclass
class LifecycleProfile:
    family_id: str
    state: str = "ENROLLED"
    history: list = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

    def transition(self, new_state: str, metadata: dict):
        if new_state not in LIFECYCLE_STATES:
            raise ValueError("Invalid lifecycle state")

        event = LifecycleEvent(self.state, new_state, metadata)
        self.history.append(event)
        self.state = new_state
        self.last_update = event.ts

class LifecycleEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.profiles = {}

    def create_profile(self, family_id: str):
        profile = LifecycleProfile(family_id)
        self.profiles[family_id] = profile

        return self.kernel.dispatch(
            module="family.lifecycle",
            action="create_profile",
            payload={"family_id": family_id}
        )

    def transition(self, family_id: str, new_state: str, metadata: dict):
        if family_id not in self.profiles:
            raise ValueError("Lifecycle profile not found")

        profile = self.profiles[family_id]
        profile.transition(new_state, metadata)

        return self.kernel.dispatch(
            module="family.lifecycle",
            action="transition",
            payload={
                "family_id": family_id,
                "old_state": profile.history[-1].old_state,
                "new_state": new_state,
                "metadata": metadata
            }
        )

    def get_profile(self, family_id: str):
        return self.profiles.get(family_id, None)
