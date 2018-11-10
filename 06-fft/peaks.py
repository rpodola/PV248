#! python3

"""
This script analyze signal and prints its highest and lowest peak
"""
import sys
import os
import argparse
import wave
import struct
import numpy as np


def eprint(*args, **kwargs):
  "This function prints message to error output"
  print(*args, file=sys.stderr, **kwargs)


def verbose_print(*args, **kwargs):
  "This function prints message in verbose mode"
  if VERBOSE:
    print(*args, file=sys.stderr, **kwargs)


def parse_args():
  "This function parses command-line arguments and does basic checks"
  parser = argparse.ArgumentParser()
  parser.add_argument("audio", help="File with audio to analyze")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  if not os.path.isfile(args.audio):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  return args.audio, args.v


def get_windows(audio_filename):
  "This function parses windows from audio file"
  with wave.open(audio_filename, 'rb') as audio:
    frames = audio.getnframes()
    frame_rate = audio.getframerate()
    channels = audio.getnchannels()
    windows = frames // frame_rate

    verbose_print("Number of Frames: {}".format(frames))
    verbose_print("Frame Rate: {}".format(frame_rate))
    verbose_print("Number of Channels: {}".format(channels))
    verbose_print("Number of Windows: {}".format(windows))

    frames_data = audio.readframes(frames)
    samples = struct.unpack("<{}h".format(frames * channels), frames_data)

    if channels == 2:
      #averaging the channels for stereo signal
      samples = [sum(x)/2 for x in zip(samples[0::2], samples[1::2])]

    #split samples into window arrays
    windows_data = [samples[idx*frame_rate:idx*frame_rate+frame_rate] for idx in range(windows)]

    return windows_data


def find_peaks(windows):
  "This function finds lowest and highest peak in windows"
  low_peak = None
  high_peak = None

  for window in windows:
    #get absolutes of amplitudes
    amplitudes = np.abs(np.fft.rfft(window))
    #get limit for window
    limit = np.mean(amplitudes) * 20

    for frq, ampl in enumerate(amplitudes):
      #is peak?
      if ampl >= limit:
        if high_peak is None or frq > high_peak:
          high_peak = frq
        if low_peak is None or frq < low_peak:
          low_peak = frq

    return low_peak, high_peak


FILENAME, VERBOSE = parse_args()
WINDOWS = get_windows(FILENAME)
LOW, HIGH = find_peaks(WINDOWS)

if LOW is None or HIGH is None:
  print("no peaks")
else:
  print("low = {}, high = {}".format(LOW, HIGH))
