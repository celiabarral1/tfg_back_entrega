import pytest
from datetime import datetime, timedelta
from app.module_graphic.graphic_processor import GraphicProcessor, TimeModel, ShiftModel, date_range

# mockeo toda la clase para luego hacer sus pruebas
class MockDataSource:
    def __init__(self):
        self.data = [
            {"user_id": 1, "timestamp": "2024-01-06"},
            {"user_id": 2, "timestamp": "2024-03-14"},
            {"user_id": 1, "timestamp": "2024-07-25"},
        ]
        self.index = {1: [self.data[0], self.data[2]], 2: [self.data[1]]}

    def get_user_ids(self):
        return list(set(record["user_id"] for record in self.data))

    def filter_records_by_user_date(self, user_id, start_date, end_date):
        return [
            record for record in self.index.get(user_id, [])
            if start_date <= datetime.strptime(record["timestamp"], "%Y-%m-%d") <= end_date
        ]

    def filter_by_date_and_shift(self, start_date, end_date, shift):
        return [
            record for record in self.data
            if start_date <= datetime.strptime(record["timestamp"], "%Y-%m-%d") <= end_date
        ]

    def get_emotions(self):
        return ["happiness","sadness","anger","fear","neutral","disgust"]

@pytest.fixture
def graphic_processor():
    return GraphicProcessor(MockDataSource())

def test_get_ids(graphic_processor):
    assert graphic_processor.get_ids() == [1, 2]


def test_find_records_by_id(graphic_processor):
    records = graphic_processor.find_records_by_id(1)
    assert len(records) == 2 
    assert records[0]["timestamp"] == "2024-01-06"

def test_filtered_by_id_time(graphic_processor):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 8)
    records = graphic_processor.filtered_by_id_time(1, start_date, end_date)
    assert len(records) == 1

def test_filtered_by_shift_time(graphic_processor):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 10)
    records = graphic_processor.filtered_by_shift_time("mañana", start_date, end_date)
    assert len(records) == 1  

def test_get_all_emotions(graphic_processor):
    assert graphic_processor.get_all_emotions() == ["happiness","sadness","anger","fear","neutral","disgust"]


@pytest.mark.parametrize("option,expected_days", [
    ("15d", 15), ("1m", 30), ("3m", 90), ("6m", 180), ("1y", 365)
])
def test_get_time_range(option, expected_days):
    time_model = TimeModel()
    time_range = time_model.get_time_range(option)
    assert (datetime.now() - time_range["start_date"]).days == expected_days


def test_get_shifts():
    shift_model = ShiftModel()
    shifts = shift_model.get_shifts()
    assert len(shifts) == 4
    assert shifts[0]["value"] == "mañana"


def test_date_range():
    start_date_obj, end_date_obj = date_range("1m", None, None)
    assert (datetime.now() - start_date_obj).days == 30  


    start_date_obj, end_date_obj = date_range(None, "2024-12-24", "2025-07-31")
    assert start_date_obj == datetime(2024, 12, 24)
    assert end_date_obj == datetime(2025, 7, 31)
