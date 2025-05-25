"""
Test cases for Account Model using pytest
"""
import pytest
from datetime import date
from flask import Flask
from service.models import Account, DataValidationError, init_db, db


@pytest.fixture(scope='function')
def tmp_sqlite_db():
    """Create a temporary SQLite database for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    init_db(app)
    yield
    # no explicit teardown needed for in-memory db


def test_deserialize_missing_field(tmp_sqlite_db):
    """Should raise DataValidationError on missing required field"""
    acc = Account()
    bad = {"email": "a@b.com", "address": "X"}  # no 'name'
    with pytest.raises(DataValidationError) as exc:
        acc.deserialize(bad)
    assert "Invalid Account: missing name" in str(exc.value)


def test_deserialize_type_error(tmp_sqlite_db):
    """Should raise DataValidationError on wrong type (e.g. not a dict)"""
    acc = Account()
    with pytest.raises(DataValidationError) as exc:
        acc.deserialize(None)   # TypeError inside
    assert "Invalid Account: body of request contained bad or no data" in str(exc.value)


def test_serialize_and_repr_and_find_by_name(tmp_sqlite_db):
    """
    Round-trip: create two accounts, test serialize(), __repr__(), 
    and find_by_name() and class methods all()/find()
    """
    a1 = Account().deserialize({
        "name": "Alice", "email": "a@x.com", "address": "Addr1"
    })
    a1.create()
    a2 = Account().deserialize({
        "name": "Bob", "email": "b@x.com", "address": "Addr2"
    })
    a2.create()

    # test all()
    all_accounts = Account.all()
    assert len(all_accounts) == 2

    # test find()
    assert Account.find(a1.id).name == "Alice"

    # test find_by_name()
    res = list(Account.find_by_name("Bob"))
    assert len(res) == 1 and res[0].email == "b@x.com"

    # test serialize & repr
    d = a1.serialize()
    assert d["name"] == "Alice"
    assert repr(a1).startswith("<Account Alice id=[")


def test_deserialize_with_empty_dict(tmp_sqlite_db):
    """Should raise DataValidationError on empty dict"""
    acc = Account()
    with pytest.raises(DataValidationError) as exc:
        acc.deserialize({})
    assert "Invalid Account: missing name" in str(exc.value)


def test_deserialize_with_invalid_date(tmp_sqlite_db):
    """Should handle invalid date format"""
    acc = Account()
    with pytest.raises(DataValidationError) as exc:
        acc.deserialize({
            "name": "Test",
            "email": "test@test.com",
            "address": "Test Address",
            "date_joined": "invalid-date"
        })
    assert "Invalid Account: invalid date format" in str(exc.value) 