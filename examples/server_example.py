from nepyc.server.server import ImageServer


def main():
    server = ImageServer()
    server.start()


if __name__ == '__main__':
    main()
