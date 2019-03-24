def parse_args(args, args_type, default_val):
    if args_type == int:
        try:
            args = int(args)
        except:
            args = default_val
    elif args_type == str:
        args = default_val if args == None else args

    return args