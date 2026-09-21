from database.access.data_access import DataAccess


class FakeConnection:
    def __init__(self):
        self.committed = 0
        self.rolled_back = 0
        self.executed = []

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolled_back += 1


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rows = []

    def execute(self, sql, parameters=()):
        self.connection.executed.append(
            (sql, tuple(parameters))
        )
        return "executed"

    def fetchall(self):
        return self.rows

    def fetchone(self):
        if not self.rows:
            return None
        return self.rows[0]


class FakeDatabaseConnection:
    def __init__(self):
        self.raw = FakeConnection()

    def cursor(self):
        return self.raw.cursor()

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()


def test_execute_commits():
    connection = FakeDatabaseConnection()
    data_access = DataAccess(connection)

    result = data_access.execute(
        "INSERT INTO test VALUES (%s)",
        [1],
    )

    assert result == "executed"
    assert connection.raw.committed == 1
    assert connection.raw.rolled_back == 0


def test_query():
    connection = FakeDatabaseConnection()
    data_access = DataAccess(connection)

    cursor = connection.raw.cursor()
    cursor.rows = [
        {"id": 1},
        {"id": 2},
    ]

    # Replace cursor creation for this test.
    original_cursor = connection.cursor

    def cursor_with_rows():
        result = original_cursor()
        result.rows = [
            {"id": 1},
            {"id": 2},
        ]
        return result

    connection.cursor = cursor_with_rows

    result = data_access.query(
        "SELECT * FROM test"
    )

    assert result == [
        {"id": 1},
        {"id": 2},
    ]


def test_query_one():
    connection = FakeDatabaseConnection()
    data_access = DataAccess(connection)

    original_cursor = connection.cursor

    def cursor_with_row():
        result = original_cursor()
        result.rows = [
            {"id": 1},
        ]
        return result

    connection.cursor = cursor_with_row

    result = data_access.query_one(
        "SELECT * FROM test WHERE id = %s",
        [1],
    )

    assert result == {"id": 1}