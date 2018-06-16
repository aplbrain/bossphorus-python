import bossphorus

def main():
    app = bossphorus.create_app()
    app.run(host="0.0.0.0", port=5000)
