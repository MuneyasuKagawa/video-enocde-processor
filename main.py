from math import e
import os
import sys
from audio import download_audio_mp3, download_audio_wav
from common import clear_screen, print_dedent, change_dir
import const
from encode import encode_movie
from movie import download_movie
from extract_vocal import extract_vocal

actions = {"1": download_movie, "2": download_audio_wav, "3": download_audio_mp3, "4": encode_movie, "5": extract_vocal, "6": change_dir}


def main():
    # last_save_dir.txt から作業フォルダを取得
    outputDir = None
    lastPathFile = f"{os.path.dirname(os.path.abspath(__file__))}/{const.lastPathFileName}"
    if os.path.exists(lastPathFile):
        with open(lastPathFile, "r") as f:
            outputDir = f.read()

    while True:
        process = 0

        if outputDir is None:
            newDir = actions.get("6")(".")
            outputDir = newDir

        while True:

            clear_screen()

            if outputDir:
                print_dedent(
                    f"""\
                    作業フォルダ: {outputDir}
                    
                    """
                )

            # command_listのキーを表示
            print_dedent(
                """\
                処理を選択してください
                
                """
            )
            for key, value in const.command_list.items():
                print(f"{key}) {value['label']}")

            print_dedent(
                """
                選択: """
            )

            process = input().strip()
            if process in const.command_list.keys():
                break

            continue

        if process == "q":
            print()
            sys.exit(0)

        if process == "6":
            action = actions.get(process)
            if action:
                newDir = action(outputDir)
                outputDir = newDir
            continue

        if process in ["1", "2", "3"]:
            print_dedent(
                """
                動画のURLを入力してください
                URL: """
            )
            url = input()

            action = actions.get(process)
            if action:
                action(url, outputDir)
        
        else:
            action = actions.get(process)
            if action:
                action(outputDir)

        print_dedent(
            """
            完了しました！
            
            エンターを押して続行...
            """
        )
        input()
        clear_screen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)
