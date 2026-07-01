from __future__ import annotations

from external_validation.runner.backend_contract import ExternalCollectionBackend


class Backend(ExternalCollectionBackend):
    TEMPLATE_ONLY = True
    BACKEND_NAME = "mujoco_robosuite_backend_template"


def create_backend() -> Backend:
    return Backend()

