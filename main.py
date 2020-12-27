import Classes

if __name__ == "__main__":
    while True:
        d = Classes.Display()
        Classes.Game(d).play()
        # Game(d, 2, [1,1]).play()
        d.close()

        response = input("Replay? y/n: ").lower()
        while response not in ['y', 'n']:
            response = input("Must be y or n: ")
        if response == 'n':
            print("Thanks, goodbye.")
            break
