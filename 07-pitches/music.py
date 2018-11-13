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
from math import log2, pow
import heapq


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
  parser.add_argument("frequency", help="Frequency of the pitch a’", type=int)
  parser.add_argument("audio", help="File with audio to analyze")
  parser.add_argument("-v", action='store_true', help="Activation of verbose mode")

  args = parser.parse_args()

  if not os.path.isfile(args.audio):
    eprint("Filename doesn't refer to a valid file")
    exit(2)

  return args.frequency, args.audio, args.v


def get_sliding_windows(audio_filename, step):
  "This function parses sliding windows from audio file"
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
    verbose_print("Audio is stereo signal")

  #calculate window sliding step
  sliding_step = int(frame_rate * step)
  verbose_print("Sliding step: {}".format(sliding_step))
  #split samples into sliding window arrays by window range
  #window range == frame_rate
  windows_data = [samples[idx:idx+frame_rate] 
                  for idx in range(0, len(samples) - frame_rate, sliding_step)]

  return windows_data


def find_highest_peaks(windows):
  "This function finds 3 highest peaks in each window"
  max_peaks_for_windows = []
  for window in windows:
    #get absolutes of amplitudes
    amplitudes = np.abs(np.fft.rfft(window))
    #get limit for window
    limit = np.mean(amplitudes) * 20
    #filter only peaks
    peaks = [ampl if ampl >= limit else 0 for ampl in amplitudes]

    #cluster the peaks, find 3 highest peaks
    max_peaks = []
    for i in range(3):
      n_max = heapq.nlargest(3, peaks)
      if n_max[i] == 0:
        break
      idx_max = peaks.index(n_max[i])
      max_peaks.append(idx_max)
      try:
        peaks[idx_max-1] = 0
      except IndexError:
        pass
      try:
        peaks[idx_max+1] = 0
      except IndexError:
        pass

    max_peaks.sort()
    max_peaks_for_windows.append(max_peaks)

  return max_peaks_for_windows


def print_pitches(peaks, frq_A4, sliding_step):
  verbose_print("Number of sliding windows: " + str(len(peaks)))
  time_window_start = 0
  time_window_end = 0
  for time, peak in enumerate(peaks):
    if time > 0:
      if (peak != peaks[time-1]):
        print("{:.1f}-{:.1f} {}".format(time_window_start, time_window_end, " ".join(pitches)))

        time_window_start = time_window_end
        pitches = [pitch(frq, frq_A4) for frq in peak]
    else:
      pitches = [pitch(frq, frq_A4) for frq in peak]
    time_window_end += sliding_step

  print("{:.1f}-{:.1f} {}".format(time_window_start, time_window_end, " ".join(pitches)))


def pitch(frequency, frq_A4):
  def octave_to_str(pitch, octave):
    if octave in (0,1,2):
      return pitch.title() + ',' * (2 - octave)
    else:
      return pitch + "'" * (octave - 3)

  PITCH_NAME = ('c', "cis", "d", "es", "e", "f", "fis", "g", "gis", "a", "bes", "b")
  C0 = frq_A4*pow(2, -4.75)

  h = 12*log2(frequency/C0)
  octave = int(h // 12)
  pitch = int(h % 12)
  cents = round((h % 1) * 100)

  if cents >= 50:
    pitch += 1
    cents = cents - 100

  if cents <= -50:
    pitch -= 1
    cents += 100

  return octave_to_str(PITCH_NAME[pitch], octave) + ("+" if cents >= 0 else "") + str(cents)


#sliding window step
STEP = 0.1
FRQ_A4, FILENAME, VERBOSE = parse_args()
WINDOWS = get_sliding_windows(FILENAME, STEP)
highest_peaks = find_highest_peaks(WINDOWS)
print_pitches(highest_peaks, FRQ_A4, STEP)
