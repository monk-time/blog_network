def get_field_from_context(context, field_type):
    for field in context.keys():  # noqa: SIM118
        if field not in {'user', 'request'} and isinstance(
            context[field], field_type
        ):
            return context[field]
    return None
