from core.interpreter import Interpreter

version = ">>> TF SetWorK v.0.5.2 <<<"

if __name__ == "__main__":
    with open("app.tf", "r", encoding="utf-8") as f:
        code = f.read()

    print(version)

    interp = Interpreter()
    try:
        interp.run(code)
    except Exception as e:
        print(f"~ ~ ~ ~ ~ ~ ~ ~\n{e}")
