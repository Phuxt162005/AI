from database.access.transaction import Transaction


class FakeConnection:
    def __init__(self):
        self.connected = False
        self.committed = 0
        self.rolled_back = 0

    def connect(self):
        self.connected = True
        return self

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolled_back += 1


def test_transaction_begin():
    connection = FakeConnection()

    transaction = Transaction(connection)

    transaction.begin()

    assert transaction.active is True
    assert connection.connected is True


def test_transaction_commit():
    connection = FakeConnection()

    transaction = Transaction(connection)

    transaction.begin()
    transaction.commit()

    assert transaction.active is False
    assert connection.committed == 1


def test_transaction_rollback():
    connection = FakeConnection()

    transaction = Transaction(connection)

    transaction.begin()
    transaction.rollback()

    assert transaction.active is False
    assert connection.rolled_back == 1


def test_transaction_context_commits():
    connection = FakeConnection()

    with Transaction(connection):
        assert connection.connected is True

    assert connection.committed == 1
    assert connection.rolled_back == 0


def test_transaction_context_rolls_back_on_error():
    connection = FakeConnection()

    try:
        with Transaction(connection):
            raise RuntimeError("test error")
    except RuntimeError:
        pass

    assert connection.committed == 0
    assert connection.rolled_back == 1


def test_transaction_cannot_begin_twice():
    connection = FakeConnection()

    transaction = Transaction(connection)

    transaction.begin()

    try:
        transaction.begin()
        assert False
    except RuntimeError:
        assert True


def test_transaction_requires_active_state():
    connection = FakeConnection()

    transaction = Transaction(connection)

    try:
        transaction.commit()
        assert False
    except RuntimeError:
        assert True