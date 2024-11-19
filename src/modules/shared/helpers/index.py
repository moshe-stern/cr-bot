def chunk_list(lst, n):
    """Split a list into n roughly equal chunks."""
    chunk_size = max(1, len(lst) // n)
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


class AuthorizationSettingsNotFound(Exception):
    pass


class NoAppointmentsFound(Exception):
    pass
