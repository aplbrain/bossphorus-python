import numpy as np

from bossphorus import Bossphorus, create_app
from bossphorus.storage import InProcessStorageProxy
from bossphorus.marmara.engine import InMemoryNumpyStorageEngine

def main():
    app = create_app(Bossphorus(
        InProcessStorageProxy(
            InMemoryNumpyStorageEngine(
                np.zeros((1024, 1024, 1024))
            )
        )
    ))
    app.run(host="0.0.0.0", debug=True)

if __name__ == '__main__':
    main()
