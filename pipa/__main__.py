import sys

if __package__ == '':
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipa import main

if __name__ == '__main__':
    sys.exit(main())
