def validate_command_arg(arg: str):
    # sourcery skip: assign-if-exp, reintroduce-else
    if not arg:
        return None
    if not arg.isdigit():
        return None
    return int(arg)
