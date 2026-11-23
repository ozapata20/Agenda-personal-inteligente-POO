from peewee import DoesNotExist, Model


def get_record(model: type[Model], record_id: int, label: str) -> Model:
    if record_id <= 0:
        raise ValueError(f"El ID de {label} debe ser positivo.")
    try:
        return model.get_by_id(record_id)
    except DoesNotExist as exc:
        raise ValueError(f"No existe {label} con ID {record_id}.") from exc


def atomic_for(model: type[Model]):
    return model._meta.database.atomic()


def delete_record(model: type[Model], record_id: int, label: str) -> None:
    record = get_record(model, record_id, label)
    record.delete_instance(recursive=True)
