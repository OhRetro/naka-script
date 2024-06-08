from ns_engine import run

if __name__ == "__main__":
    print("Welcome to NakaScript Shell")
    while True:
        try:
            command_text = input(">>> ")
            result, error = run.execute(run.SHELL_FILENAME, command_text)
            
            if error: print(error.as_string())
            elif result: print(result)
            
        except KeyboardInterrupt:
            quit()
        