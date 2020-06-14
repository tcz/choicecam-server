import signal
import os
import time

from config import has_config_for_streaming
from ssdp import run as run_ssdp
from webservice import run as run_webservice
from videocapturer import run as run_videcapturer
from videouploader import run as run_videouploader

def start_config_services():
    ssdp_process_id = os.fork()
    if ssdp_process_id == 0:
        run_ssdp()
        return

    webservice_process_id = os.fork()
    if webservice_process_id == 0:
        run_webservice()
        return

    exited_process_id, exited_process_status = os.wait()
    if exited_process_id == webservice_process_id and exited_process_status == 0:
        os.kill(ssdp_process_id, signal.SIGTERM)
        time.sleep(1)
        start_services()
        return

    restart = False
    if ssdp_process_id == exited_process_id:
        os.kill(webservice_process_id, signal.SIGTERM)
        restart = True
    elif webservice_process_id == exited_process_id:
        os.kill(ssdp_process_id, signal.SIGTERM)
        restart = True

    if restart:
        time.sleep(1)
        start_config_services()


def start_streaming_services():
    capturer_process_id = os.fork()
    if capturer_process_id == 0:
        run_videcapturer()
        return

    uploader_process_id = os.fork()
    if uploader_process_id == 0:
        run_videouploader()
        return

    exited_process_id, exited_process_status = os.wait()

    if capturer_process_id == exited_process_id:
        os.kill(uploader_process_id, signal.SIGTERM)
    elif uploader_process_id == exited_process_id:
        os.kill(capturer_process_id, signal.SIGTERM)

    time.sleep(1)
    start_streaming_services()

def start_services():
    if not has_config_for_streaming():
        start_config_services()
    else:
        start_streaming_services()

if __name__ == '__main__':
    start_services()
