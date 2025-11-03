from worker import init_service
import logging

if __name__=="__main__":
    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    init_service()
