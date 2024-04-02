import datetime


def year(request):  # noqa: ARG001
    """Добавляет переменную с текущим годом."""
    return {'year': datetime.datetime.now(datetime.UTC).year}
