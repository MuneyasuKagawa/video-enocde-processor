#!/usr/bin/env python

import struct
import wave


def detect_start_times(original_file_name, target_file_name):
    original_time = find_first_loud_sound(original_file_name, -20)
    target_time = find_first_loud_sound(target_file_name, -20)
    if original_time is None or target_time is None:
        print("音声が検出できませんでした")
        return None

    return round(original_time, 2), round(target_time, 2)


def db_to_amp(db, ref_amp=32767):
    # デシベル値を振幅に変換
    return ref_amp * (10 ** (db / 20))


def find_first_loud_sound(filename, threshold_db):
    with wave.open(filename, "r") as audio_file:
        n_channels, sampwidth, framerate, n_frames, _, _ = audio_file.getparams()

        if sampwidth == 1:
            fmt_char = "b"  # 8ビット（符号付き）
            max_amp = 128
        elif sampwidth == 2:
            fmt_char = "h"  # 16ビット（符号付き）
            max_amp = 32768
        elif sampwidth == 4:
            fmt_char = "i"  # 32ビット（符号付き）
            max_amp = 2147483648
        else:
            raise ValueError(f"サポートされていないサンプル幅です。: {sampwidth}")

        fmt = f"<{n_frames*n_channels}{fmt_char}"
        frames = audio_file.readframes(n_frames)
        frame_ints = struct.unpack(fmt, frames)

        # 閾値（デシベル）を振幅に変換
        threshold_amp = max_amp * (10 ** (threshold_db / 20.0))

        for i in range(0, len(frame_ints), n_channels):
            sample = frame_ints[i]
            if abs(sample) >= threshold_amp:
                time = i / float(framerate) / n_channels
                return time

        return None
