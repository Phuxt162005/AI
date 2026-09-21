from database.config import DatabaseConfig


def test_database_config_defaults():
    config = DatabaseConfig()

    assert config.host == "localhost"
    assert config.port == 3306
    assert config.user == "root"
    assert config.database == "projectai"
    assert config.charset == "utf8mb4"


def test_database_config_connection_dict():
    config = DatabaseConfig(
        host="db.example",
        port=3307,
        user="admin",
        password="secret",
        database="projectai_test",
    )

    result = config.to_connection_dict()

    assert result["host"] == "db.example"
    assert result["port"] == 3307
    assert result["user"] == "admin"
    assert result["password"] == "secret"
    assert result["database"] == "projectai_test"


def test_database_config_from_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "PROJECTAI_DB_HOST",
        "mysql.local",
    )
    monkeypatch.setenv(
        "PROJECTAI_DB_PORT",
        "3307",
    )
    monkeypatch.setenv(
        "PROJECTAI_DB_USER",
        "projectai",
    )
    monkeypatch.setenv(
        "PROJECTAI_DB_PASSWORD",
        "password",
    )
    monkeypatch.setenv(
        "PROJECTAI_DB_NAME",
        "projectai_test",
    )

    config = DatabaseConfig.from_environment()

    assert config.host == "mysql.local"
    assert config.port == 3307
    assert config.user == "projectai"
    assert config.password == "password"
    assert config.database == "projectai_test"


def test_database_config_rejects_invalid_port():
    try:
        DatabaseConfig(port=0)
        assert False
    except ValueError:
        assert True