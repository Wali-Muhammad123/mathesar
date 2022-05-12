from django.core.files import File
import pytest
from rest_framework.test import APIClient
from sqlalchemy import text

from mathesar.database.base import create_mathesar_engine
from mathesar.imports.csv import create_table_from_csv
from mathesar.models import DataFile


TEST_SCHEMA = 'import_csv_schema'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_data_file():
    def _create_data_file(file_path, file_name):
        with open(file_path, 'rb') as csv_file:
            data_file = DataFile.objects.create(file=File(csv_file), created_from='file',
                                                base_name=file_name)

        return data_file
    return _create_data_file


@pytest.fixture
def create_data_types_table(data_types_csv_filename, create_schema):
    with open(data_types_csv_filename, 'rb') as csv_file:
        data_file = DataFile.objects.create(file=File(csv_file))

    def _create_table(table_name, schema='Data Types'):
        schema_model = create_schema(schema)
        return create_table_from_csv(data_file, table_name, schema_model)
    return _create_table


@pytest.fixture
def create_self_referential_table(self_referential_filename, create_schema):
    with open(self_referential_filename, 'rb') as csv_file:
        data_file = DataFile.objects.create(file=File(csv_file))

    def _create_table(table_name, schema='Patents'):
        schema_model = create_schema(schema)
        return create_table_from_csv(data_file, table_name, schema_model)

    return _create_table


@pytest.fixture
def create_related_table(create_schema):
    def read_table(related_csv_filename_tuple):
        with open(related_csv_filename_tuple[0], 'rb') as csv_file:
            data_file = DataFile.objects.create(file=File(csv_file))
        with open(related_csv_filename_tuple[1], 'rb') as ref_csv_file:
            ref_data_file = DataFile.objects.create(file=File(ref_csv_file))

        def _create_table(table_name, ref_table_name, schema='Patents'):
            schema_model = create_schema(schema)
            return create_table_from_csv(data_file, table_name, schema_model), create_table_from_csv(
                ref_data_file,
                ref_table_name,
                schema_model
            )

        return _create_table

    return read_table


@pytest.fixture
def create_foreign_key_table(foreign_key_csv_filename_tuple, create_related_table):
    return create_related_table(foreign_key_csv_filename_tuple)


@pytest.fixture
def create_multi_column_foreign_key_table(multi_column_foreign_key_csv_filename_tuple, create_related_table):
    return create_related_table(multi_column_foreign_key_csv_filename_tuple)


@pytest.fixture
def create_invalid_related_data_foreign_key_table(
        invalid_related_data_foreign_key_csv_filename_tuple,
        create_related_table
):
    return create_related_table(invalid_related_data_foreign_key_csv_filename_tuple)


@pytest.fixture
def table_for_reflection(test_db_name):
    engine = create_mathesar_engine(test_db_name)
    schema_name = 'a_new_schema'
    table_name = 'a_new_table'
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA {schema_name};'))
    with engine.begin() as conn:
        conn.execute(
            text(
                f'CREATE TABLE {schema_name}.{table_name}'
                f' (id INTEGER, name VARCHAR);'
            )
        )
    yield schema_name, table_name, engine
    with engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA {schema_name} CASCADE;'))
