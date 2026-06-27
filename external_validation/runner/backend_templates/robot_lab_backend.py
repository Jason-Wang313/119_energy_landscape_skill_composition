from __future__ import annotations

from external_validation.runner.backend_contract import ExternalCollectionBackend


class Backend(ExternalCollectionBackend):
    TEMPLATE_ONLY = True
    BACKEND_NAME = "third_party_robot_lab_backend_template"


def create_backend() -> Backend:
    return Backend()

