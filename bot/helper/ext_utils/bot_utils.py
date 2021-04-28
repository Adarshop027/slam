import logging
import re
import threading
import time

from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import download_dict, download_dict_lock

LOGGER = logging.getLogger(__name__)

MAGNET_REGEX = r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*"

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"


class MirrorStatus:
    STATUS_UPLOADING = "📤.𝙐𝙥𝙡𝙤𝙖𝙙𝙞𝙣𝙜.📤"
    STATUS_DOWNLOADING = "📥𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙞𝙣𝙜.📥"
    STATUS_WAITING = "📝𝙌𝙪𝙚𝙪𝙚𝙙.📝"
    STATUS_FAILED = "🔴𝙁𝙖𝙞𝙡𝙚𝙙.𝘾𝙡𝙚𝙖𝙣𝙞𝙣𝙜 𝙙𝙤𝙬𝙣𝙡𝙤𝙖𝙙♻"
    STATUS_CANCELLED = "❌.𝘾𝙖𝙣𝙘𝙚𝙡𝙡𝙚𝙙.❌"
    STATUS_ARCHIVING = "🗜️.𝘼𝙧𝙘𝙝𝙞𝙫𝙞𝙣𝙜.🗜️"
    STATUS_EXTRACTING = "🤐𝙀𝙭𝙩𝙧𝙖𝙘𝙩𝙞𝙣𝙜.🤐"


PROGRESS_MAX_SIZE = 100 // 8
PROGRESS_INCOMPLETE = ['▰', '▰', '▰', '▰', '▰', '▰', '▰']

SIZE_UNITS = ['𝘽', '𝙆𝘽', '𝙈𝘽', '𝙂𝘽', '𝙏𝘽', '𝙋𝘽'] 


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return '👺𝙁𝙞𝙡𝙚 𝙞𝙨 𝙩𝙤𝙤 𝙡𝙖𝙧𝙜𝙚'


def getDownloadByGid(gid):
    with download_dict_lock:
        for dl in download_dict.values():
            status = dl.status()
            if status != MirrorStatus.STATUS_UPLOADING and status != MirrorStatus.STATUS_ARCHIVING \
                    and status != MirrorStatus.STATUS_EXTRACTING:
                if dl.gid() == gid:
                    return dl
    return None


def get_progress_bar_string(status):
    completed = status.processed_bytes() / 8
    total = status.size_raw() / 8
    if total == 0:
        p = 0
    else:
        p = round(completed * 100 / total)
    p = min(max(p, 0), 100)
    cFull = p // 8
    cPart = p % 8 - 1
    p_str = '▰' * cFull
    if cPart >= 0:
        p_str += PROGRESS_INCOMPLETE[cPart]
    p_str += '▱' * (PROGRESS_MAX_SIZE - cFull)
    p_str = f"[{p_str}]"
    return p_str


def get_readable_message():
    with download_dict_lock:
        msg = ""
        for download in list(download_dict.values()):
            msg += f"<b>🗃𝙁𝙞𝙡𝙚𝙣𝙖𝙢𝙚 :</b> <code>{download.name()}</code>"
            msg += f"\n<b>🔁𝙎𝙩𝙖𝙩𝙪𝙨 :</b> <i>{download.status()}</i>"
            if download.status() != MirrorStatus.STATUS_ARCHIVING and download.status() != MirrorStatus.STATUS_EXTRACTING:
                msg += f"\n<code>{get_progress_bar_string(download)} {download.progress()}</code>"
                if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                    msg += f"\n<b>📥𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙚𝙙 :</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"
                else:
                    msg += f"\n<b>📤𝙐𝙥𝙡𝙤𝙖𝙙𝙚𝙙 :</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"
                msg += f"\n<b>💨𝙎𝙥𝙚𝙚𝙙 :</b> {download.speed()}, \n<b>⏳𝙀𝙏𝘼:</b> {download.eta()} "
                # if hasattr(download, 'is_torrent'):
                try:
                    msg += f"\n<b>🟢𝙎𝙚𝙚𝙙𝙚𝙧𝙨 :</b> {download.aria_download().num_seeders}" \
                        f" | <b>🔴𝙋𝙚𝙚𝙧𝙨 :</b> {download.aria_download().connections}"
                except:
                    pass
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                msg += f"\n<b>❌𝙏𝙤 𝘾𝙖𝙣𝙘𝙚𝙡:</b> <code>/{BotCommands.CancelMirror} {download.gid()}</code>"
            msg += "\n\n"
        return msg


def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


def is_mega_link(url: str):
    return "mega.nz" in url


def is_url(url: str):
    url = re.findall(URL_REGEX, url)
    if url:
        return True
    return False


def is_magnet(url: str):
    magnet = re.findall(MAGNET_REGEX, url)
    if magnet:
        return True
    return False


def new_thread(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper
