def validate_command_arg(arg: str):
    if not arg:
        return None
    return int(arg) if arg.isdigit() else None
