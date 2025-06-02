import pytest
from datetime import datetime
from unittest.mock import MagicMock
from app.module_workers.worker import RolModel, Worker
from app.module_workers.workers_processor import WorkersProcessor

# 📌 Mock para la persistencia de datos en CSV
class MockWorkersData:
    def __init__(self):
        self.workers = [
            {"id": "101", "workstation": "WS-001", "hiring_date": "2022-01-15", "rol": "operario", "register_date": "2025-01-18T00:00:00.000Z"},
            {"id": "102", "workstation": "WS-002", "hiring_date": "2022-02-20", "rol": None, "register_date": None},
            {"id": "103", "workstation": "WS-003", "hiring_date": "2022-03-25", "rol": None, "register_date": None},
        ]

    def read_workers(self):
        pass  # Simula la lectura sin hacer nada

    def get_workers_no_role(self):
        return [w["id"] for w in self.workers if w["rol"] is None]

    def find_worker_by_id(self, worker_id):
        for w in self.workers:
            if w["id"] == worker_id:
                return w
        return None

    def insert_worker(self, worker):
        self.workers.append(worker)

    def update_worker(self, worker_id, rol, register_date):
        for w in self.workers:
            if w["id"] == worker_id:
                w["rol"] = rol
                w["register_date"] = register_date
                return True
        return False

@pytest.fixture
def workers_processor():
    return WorkersProcessor(MockWorkersData())

def test_get_workers_no_role(workers_processor):
    workers = workers_processor.get_workers_no_role()
    assert workers == ["102", "103"]  # Solo estos trabajadores no tienen rol asignado

def test_find_worker_by_id(workers_processor):
    worker = workers_processor.find_worker_by_id("101")
    assert worker is not None
    assert worker["workstation"] == "WS-001"

    worker_not_found = workers_processor.find_worker_by_id("999")
    assert worker_not_found is None  # No existe


def test_update_worker(workers_processor):
    assert workers_processor.update_worker("102", "psicólogo", "2025-02-10T00:00:00.000Z") is True
    updated_worker = workers_processor.find_worker_by_id("102")
    assert updated_worker["rol"] == "psicólogo"
    assert updated_worker["register_date"] == "2025-02-10T00:00:00.000Z"


def test_insert_worker(workers_processor):
    new_worker = {"id": "104", "workstation": "WS-004", "hiring_date": "2023-05-15", "rol": None, "register_date": None}
    workers_processor.insert_worker(new_worker)

    worker = workers_processor.find_worker_by_id("104")
    assert worker is not None
    assert worker["workstation"] == "WS-004"


def test_worker_class():
    worker = Worker("105", "WS-005", "2023-06-10", "operario", "2025-03-15T12:30:00.000Z")
    assert worker.id == "105"
    assert worker.workstation == "WS-005"
    assert worker.hiring_date == datetime(2023, 6, 10)
    assert worker.rol == "operario"
    assert worker.register_date == datetime(2025, 3, 15, 12, 30, 0)

def test_rol_model():
    rol_model = RolModel()
    rols = rol_model.get_rols()
    assert len(rols) == 2
    assert rols[0]["value"] == "operario"
    assert rols[1]["value"] == "psicólogo"
