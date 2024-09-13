from math import e
import sys
from audio import download_audio_mp3, download_audio_wav
from common import clear_screen, print_dedent
import const
from encode import encode_movie
from movie import download_movie

actions = {"1": download_movie, "2": download_audio_wav, "3": download_audio_mp3, "4": encode_movie}


def main():
    while True:
        process = 0

        while True:
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

            process = input()
            if process in const.command_list.keys():
                break

        if process == "q":
            print()
            sys.exit(0)

        if process in ["1", "2", "3"]:
            print_dedent(
                """
                動画のURLを入力してください
                URL: """
            )
            url = input()

            action = actions.get(process)
            if action:
                action(url)

        else:
            action = actions.get(process)
            if action:
                action()

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
