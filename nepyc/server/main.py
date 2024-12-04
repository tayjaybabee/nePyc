import os
import sys
import time
import threading
from nepyc.server.cli import ARGS
from nepyc.log_engine import ROOT_LOGGER
from nepyc.server.signals import setup_signal_handler, exit_flag


ROOT_LOGGER.set_level(console_level=ARGS.parsed.log_level)

APP_LOGGER = ROOT_LOGGER.get_child('Server')




def main():
    from nepyc.server.server import ImageServer
    setup_signal_handler()
    log = APP_LOGGER.get_child('main')
    log.debug('Starting the image server...')

    server = ImageServer(host=ARGS.parsed.host, port=ARGS.parsed.port)

    try:
        server_thread = threading.Thread(target=server.run_server, daemon=True)
        server_thread.start()

        server.gui.start()
    except KeyboardInterrupt:
        log.info('Exiting due to keyboard interrupt')
        exit_flag.set()
    finally:
        server.stop()
        server_thread.join()
        log.info('Exiting...')
        os._exit(0)


if __name__ == '__main__':
    if os.name == 'nt' and not os.environ.get('NEPYC_DETACHED'):
        os.environ['NEPYYC_DETACHED'] = '1'
        subprocess.Popen(
            [sys.executable, *sys.argv],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        sys.exit(0)
    else:
        main()
