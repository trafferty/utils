cmd_list = ['init', 'jog', 'rec', 'open', 'close']

while True:
    inp = input("\n>>> ")
    cmd, *args = inp.split()
    cmd = cmd.lower()
    if cmd == 'init':
        print(f"Init, args: {','.join(args)}")

    elif cmd == 'jog':
        print(f"Jog, args: {','.join(args)}")

    elif cmd == 'rec':
        print(f"Rec, args: {','.join(args)}")

    elif cmd == 'open':
        print(f"Open, args: {','.join(args)}")

    elif cmd == 'close':
        print(f"Close, args: {','.join(args)}")


    elif cmd == 'q' or cmd == 'quit':
        break

    elif cmd == '?' or cmd == 'help':
        print("-----------------------\nCommand List:")
        for i,c in enumerate(cmd_list):
            print(f"  {i}: {c}")
        print("-----------------------")
    else:
        pass

print("Exiting")
