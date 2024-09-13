import os
import subprocess
import textwrap
import threading
from urllib.parse import parse_qs, urlparse


def extract_video_url(url):
    parse_result = urlparse(url)
    if not parse_result:
        return None

    v = parse_qs(parse_result.query).get("v")
    if not v:
        return None

    return f"{parse_result.scheme}://{parse_result.netloc}{parse_result.path}?v={v[0]}"


def print_output(stream, encoding="utf-8", display_output=True):
    for line in iter(stream.readline, b""):
        if display_output:
            print(line.decode(encoding, "ignore"), end="")


def run_command(command, encoding="utf-8", display_output=True):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=False,
    )

    # スレッドを作成して標準出力と標準エラーをリアルタイムで処理する
    stdout_thread = threading.Thread(target=print_output, args=(process.stdout, encoding, display_output))
    stderr_thread = threading.Thread(target=print_output, args=(process.stderr, encoding, display_output))

    # スレッドを開始
    stdout_thread.start()
    stderr_thread.start()

    # スレッドの終了を待つ
    stdout_thread.join()
    stderr_thread.join()

    # プロセスの終了コードを取得
    process.wait()
    return process.returncode


def print_dedent(text, end=""):
    print(textwrap.dedent(text), end=end)


def clear_screen():
    # 画面をクリアする
    os.system("cls")
