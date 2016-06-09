import sys

def main():
    import core
    core.runTests()

if __name__ == "__main__":
    sys.exit(int(main() or 0))
