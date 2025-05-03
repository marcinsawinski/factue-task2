def get_args(args, wrapper):

    resource_type = None
    resource_list = []
    new_args = args.copy()

    i = 0
    while i < len(args):
        if args[i] == "--resource-type" and i + 1 < len(args):
            resource_type = args[i + 1]
            i += 2
        elif args[i] == "--resource-list" and i + 1 < len(args):
            resource_list = args[i + 1]
            i += 2
        else:
            i += 1

    if resource_type and resource_list:
        new_args.append(f"--workers={len(resource_list)}")
    return [wrapper, "--local-scheduler"] + new_args
