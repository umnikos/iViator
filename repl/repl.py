def repl(state):
    while True:
        options = state()
        # if no options were given then end repl session
        if not options:
            break

        i = 0
        letters = []
        functions = []
        for letter, description, function in options:
            print("%s - %s" % (letter, description))
            letters.append(letter)
            functions.append(function)
            i += 1

        while True:
            try:
                choice = input("> ")
                chosen = letters.index(choice)
                state = functions[chosen]
                break
            except ValueError:
                print("Unknown option.")
            except EOFError:
                return
            except KeyboardInterrupt:
                return

