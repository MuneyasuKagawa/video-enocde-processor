import os
import random
import shutil
import string
import time
import wave
from common import clear_screen, print_dedent, run_command
import const
from movie import download_movie
from detect import detect_start_times


def encode_movie(saveDir):
    clear_screen()

    print_dedent(
        """\
        エンコード対象の作業フォルダを入力してください
        
        フォルダ: """
    )

    outputPath = saveDir

    movie_files = [
        f for f in os.listdir(outputPath) if os.path.isfile(os.path.join(outputPath, f)) and f.endswith(".mp4")
    ]
    audio_files = [
        f for f in os.listdir(outputPath) if os.path.isfile(os.path.join(outputPath, f)) and f.endswith(".wav")
    ]
    if not movie_files:
        while True:
            print_dedent(
                """
                動画ファイルが存在しません
                本家動画のDLを行いますか？(Y/n): """
            )
            download = input()
            if download in ["", "y", "n"]:
                break
        if download == "" or download.lower() == "y":
            url = None
            while not url:
                print_dedent(
                    """
                    動画のURLを入力してください
                    URL: """
                )
                url = input()
                if not url or not url.startswith("http"):
                    continue
            download_movie(url, saveDir=f"{outputPath}")
            movie_files = [
                f for f in os.listdir(outputPath) if os.path.isfile(os.path.join(outputPath, f)) and f.endswith(".mp4")
            ]
        else:
            return

    if not audio_files:
        print_dedent(
            """
            .wavファイルが存在しません
            """
        )
        print(f"対象フォルダ: {outputPath}")
        print()
        return

    clear_screen()
    for i, movie_file in enumerate(movie_files):
        print(f"{i}) {movie_file}")
    movie_index = None
    while True:
        print_dedent(
            """

            エンコード対象の動画ファイルを選択してください
            
            選択: """
        )
        movie_index = input()
        if not movie_index.isdigit() or int(movie_index) >= len(movie_files):
            continue
        break

    movie_input = os.path.join(outputPath, movie_files[int(movie_index)])

    clear_screen()
    for i, audio_file in enumerate(audio_files):
        print(f"{i}) {audio_file}")

    audio_index = None
    while True:
        print_dedent(
            """
            
            エンコード対象の音声ファイルを選択してください
            選択: """
        )
        audio_index = input()
        if not audio_index.isdigit() or int(audio_index) >= len(audio_files):
            continue
        break

    audio_input = os.path.join(outputPath, audio_files[int(audio_index)])

    outputFile = os.path.join(outputPath, f"output.mp4")
    if os.path.exists(outputFile):
        # 上書き確認
        while True:
            print_dedent(
                """
                出力先にすでにファイルが存在します
                上書きしますか？(y/n): """
            )
            overwrite = input()
            if overwrite in ["y", "n"]:
                break
        if overwrite == "n":
            clear_screen()
            return

    clear_screen()
    print("動画ファイルと音声ファイルの音声開始地点を解析中...")

    # tmpフォルダを作成
    r = "".join([random.choice(string.ascii_letters + string.digits) for i in range(5)])
    tmpPath = os.path.join(outputPath, f"tmp_{r}")
    if not os.path.exists(tmpPath):
        run_command(f"mkdir {tmpPath}")

    # エンコード対象の動画ファイルから音声ファイルをtmpフォルダに抽出
    run_command(f'ffmpeg -i "{movie_input}" -c:a pcm_s16le -ar 44100 "{tmpPath}/original.wav"', display_output=False)

    # エンコード対象の音声ファイルをtmpフォルダにコピー(ビット深度を16bitに変換しておく)
    run_command(f'ffmpeg -i "{audio_input}" -c:a pcm_s16le -ar 44100 "{tmpPath}/target.wav"', display_output=False)

    # 音声の開始地点を解析
    original_time, target_time = detect_start_times(f"{tmpPath}/original.wav", f"{tmpPath}/target.wav")

    # エンコード対象音声ファイルのオフセットを計算(動画とのずれを補正するため)
    proposed_offset = original_time - target_time

    # tmpフォルダを強制的に削除
    shutil.rmtree(tmpPath, ignore_errors=True)

    offset = ""
    while True:
        clear_screen()
        print_dedent(
            f"""\
            対象音声ファイルのオフセットを入力してください(マイナス可)
            入力せずにエンターを押すと推奨値を使用します

            オフセット(推奨値 {proposed_offset}): """
        )
        offset = input()
        if offset == "":
            offset = str(proposed_offset)
            break
        if offset.startswith("-"):
            if not offset.replace("-", "").isdigit():
                print_dedent(
                    """
                    数値で入力してください(マイナス可)
                    """
                )
                print(f"入力された値: {offset}")
                print()
                continue
            break
        if not offset.isdigit():
            print_dedent(
                """
                数値で入力してください(マイナス可)
                """
            )
            print(f"入力された値: {offset}")
            print()
            continue

    command = (
        const.command_list["4"]["command"]
        .replace("{{movie_input}}", movie_input)
        .replace("{{audio_input}}", audio_input)
        .replace("{{offset}}", offset)
        .replace("{{output}}", outputFile)
    )

    if os.path.exists(outputFile):
        os.remove(outputFile)
    
    # 1秒待機
    time.sleep(1)

    run_command(command, encoding="cp932")

    clear_screen()

    print_dedent(
        f"""\
        出力先: {outputFile}
        """
    )


def get_sampwidth(filename):
    with wave.open(filename, "r") as audio_file:
        _, sampwidth, _, _, _, _ = audio_file.getparams()
        return sampwidth
