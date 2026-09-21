from database.schema.base_schema import (
    DATABASE_NAME,
    create_database_sql,
)


def test_default_database_name():
    assert DATABASE_NAME == "projectai"


def test_create_database_sql():
    sql = create_database_sql()

    assert "CREATE DATABASE IF NOT EXISTS" in sql
    assert "`projectai`" in sql
    assert "utf8mb4" in sql


def test_create_database_sql_custom_name():
    sql = create_database_sql("projectai_test")

    assert "`projectai_test`" in sql