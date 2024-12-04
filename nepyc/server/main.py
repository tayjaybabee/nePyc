from nepyc.server.server import ImageServer


def main():
    server = ImageServer()
    server.start()

    return server


if __name__ == '__main__':
    main()
