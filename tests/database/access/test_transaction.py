from database.access.data_access import DataAccess
from database.access.transaction import Transaction


class FakeConnection:
    def __init__(self):
        self.connected = False
        self.committed = 0
        self.rolled_back = 0
        self.executed = []

    def connect(self):
        self.connected = True
        return self

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolled_back += 1


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def execute(
        self,
        sql,
        parameters=(),
    ):
        self.connection.executed.append(
            (sql, tuple(parameters))
        )


def create_data_access():
    connection = FakeConnection()
    data_access = DataAccess(connection)

    return connection, data_access


def test_transaction_begin():
    connection, data_access = (
        create_data_access()
    )

    transaction = Transaction(
        data_access
    )

    transaction.begin()

    assert transaction.active is True
    assert connection.connected is True


def test_transaction_commit():
    connection, data_access = (
        create_data_access()
    )

    transaction = Transaction(
        data_access
    )

    transaction.begin()
    transaction.commit()

    assert transaction.active is False
    assert connection.committed == 1


def test_transaction_rollback():
    connection, data_access = (
        create_data_access()
    )

    transaction = Transaction(
        data_access
    )

    transaction.begin()
    transaction.rollback()

    assert transaction.active is False
    assert connection.rolled_back == 1


def test_transaction_context_commits():
    connection, data_access = (
        create_data_access()
    )

    with Transaction(data_access):
        assert data_access.transaction_active is True

    assert connection.committed == 1
    assert connection.rolled_back == 0


def test_transaction_context_rolls_back_on_error():
    connection, data_access = (
        create_data_access()
    )

    try:
        with Transaction(data_access):
            raise RuntimeError("test error")
    except RuntimeError:
        pass

    assert connection.committed == 0
    assert connection.rolled_back == 1
    assert data_access.transaction_active is False


def test_transaction_cannot_begin_twice():
    connection, data_access = (
        create_data_access()
    )

    transaction = Transaction(
        data_access
    )

    transaction.begin()

    try:
        transaction.begin()
        assert False
    except RuntimeError:
        assert True


def test_transaction_requires_active_state():
    connection, data_access = (
        create_data_access()
    )

    transaction = Transaction(
        data_access
    )

    try:
        transaction.commit()
        assert False
    except RuntimeError:
        assert True


def test_execute_does_not_commit_inside_transaction():
    connection, data_access = (
        create_data_access()
    )

    transaction = Transaction(
        data_access
    )

    transaction.begin()

    data_access.execute(
        "INSERT INTO test VALUES (%s)",
        [1],
    )

    assert connection.committed == 0
    assert data_access.transaction_active is True

    transaction.commit()

    assert connection.committed == 1
    assert data_access.transaction_active is False


def test_multiple_operations_commit_once():
    connection, data_access = (
        create_data_access()
    )

    with Transaction(data_access):
        data_access.execute(
            "INSERT INTO test VALUES (%s)",
            [1],
        )

        data_access.execute(
            "INSERT INTO test VALUES (%s)",
            [2],
        )

        data_access.execute(
            "UPDATE test SET id = %s",
            [3],
        )

    assert connection.committed == 1
    assert connection.rolled_back == 0


def test_transaction_rolls_back_after_operation_error():
    class FailingCursor(FakeCursor):
        def execute(
            self,
            sql,
            parameters=(),
        ):
            raise RuntimeError(
                "database error"
            )

    class FailingConnection(FakeConnection):
        def cursor(self):
            return FailingCursor(self)

    connection = FailingConnection()
    data_access = DataAccess(connection)

    try:
        with Transaction(data_access):
            data_access.execute(
                "INSERT INTO test VALUES (%s)",
                [1],
            )
    except RuntimeError:
        pass

    assert connection.committed == 0
    assert connection.rolled_back == 1
    assert data_access.transaction_active is False