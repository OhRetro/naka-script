from ns_engine import run

if __name__ == "__main__":
    while True:
        command_text = input("ns > ")
        result, error = run.execute("<stdin>", command_text)

        if error: print(error.as_string())
        elif result: print(result)
        # else: raise Exception("Something went really wrong somehow.")
        