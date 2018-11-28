import numpy as np
from . import Bossphorus, create_app
from .storage import InProcessStorageProxy
from .marmara.engine import InMemoryNumpyStorageEngine

def main():
    print("main")
    app = create_app(Bossphorus(
        InProcessStorageProxy(
            InMemoryNumpyStorageEngine(
                np.zeros((1024, 1024, 1024))
            )
        )
    ))
    app.run(host="0.0.0.0", debug=True)
