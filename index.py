# Vercel entrypoint alias
from server import handler, DealsHandler

if __name__ == "__main__":
    from server import run_server
    run_server()
