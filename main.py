from core.interpreter import Interpreter

version = ">>> TF SetWorK v.0.3.7 <<<"

if __name__ == "__main__":
    with open("test.tf", "r", encoding="utf-8") as f:
        code = f.read()

    print(version)

    interp = Interpreter()
    try:
        interp.run(code)
    except Exception as e:
        print(f"~ ~ ~ ~ ~ ~ ~ ~\nError in {e}")
