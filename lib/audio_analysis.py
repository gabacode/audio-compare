import os

import mutagen
import numpy as np
from pydub import AudioSegment


def analyze_file(path):
    """
    Analyze an audio file and extract metadata and properties.
    """
    info = {}
    audio = AudioSegment.from_file(path)

    info["Filename"] = os.path.basename(path)
    info["Duration"] = f"{int(audio.duration_seconds // 60)}:{int(audio.duration_seconds % 60):02d}"
    info["Channels"] = f"{audio.channels} ({'Stereo' if audio.channels == 2 else 'Mono' if audio.channels == 1 else 'Multi'})"
    info["Sample Rate"] = f"{audio.frame_rate} Hz"
    info["Bit Depth"] = f"{audio.sample_width * 8} bit"
    info["Volume (dBFS)"] = f"{round(audio.dBFS, 2)} dB"

    try:
        m = mutagen.File(path)
        if m is not None:
            def extract(tag_keys):
                value = next((m.get(k) for k in tag_keys if m.get(k)), None)
                if value is None:
                    return None
                return str(value[0]) if hasattr(value, '__iter__') and not isinstance(value, str) else str(value)

            tag_map = {
                "Artist": ["TPE1", "ARTIST", "©ART", "artist"],
                "Album": ["TALB", "ALBUM", "©alb", "album"],
                "Title": ["TIT2", "TITLE", "©nam", "title"],
                "Year": ["TDRC", "DATE", "©day", "year"],
                "Genre": ["TCON", "GENRE", "©gen", "genre"],
            }

            for field, keys in tag_map.items():
                val = extract(keys)
                if val:
                    info[field] = val

            if hasattr(m.info, 'bitrate'):
                info["Bitrate"] = f"{m.info.bitrate // 1000} kbps"

            if hasattr(m.info, 'mime'):
                info["Format"] = m.info.mime[0].split('/')[-1].upper()

    except Exception as e:
        print(f"Metadata extraction error: {e}")

    return audio, info


def plot_spectrum(audio, ax, title="Spectrum", global_limits=None):
    """
    Generate and plot frequency spectrum for an audio file.
    """
    try:
        samples = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            samples = samples.reshape((-1, 2)).mean(axis=1)

        if len(samples) > 88200:
            samples = samples[:88200]

        window = np.hanning(len(samples))
        samples = samples * window

        fft = np.fft.rfft(samples)
        freqs = np.fft.rfftfreq(len(samples), 1 / audio.frame_rate)
        magnitude_db = 20 * np.log10(np.abs(fft) + 1e-6)

        ax.clear()
        ax.plot(freqs, magnitude_db, linewidth=0.8, alpha=0.8)
        ax.set_xlabel("Frequency (Hz)", fontsize=10)
        ax.set_ylabel("Amplitude (dB)", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        max_freq = min(20000, audio.frame_rate // 2)
        ax.set_xlim(0, max_freq)

        if max_freq >= 20000:
            freq_ticks = [0, 1000, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 18000, 20000]
        else:
            freq_ticks = np.linspace(0, max_freq, 11).astype(int)

        ax.set_xticks(freq_ticks)
        ax.set_xticklabels([f"{f // 1000}k" if f >= 1000 else str(f) for f in freq_ticks], fontsize=9)

        if global_limits:
            ax.set_ylim(global_limits['y_min'] - 5, global_limits['y_max'] + 5)

        return {
            'y_min': np.min(magnitude_db),
            'y_max': np.max(magnitude_db),
            'freqs': freqs,
            'magnitude_db': magnitude_db
        }

    except Exception as e:
        ax.clear()
        ax.text(0.5, 0.5, f'Error plotting spectrum:\n{str(e)}',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=10)
        return None


def extract_numeric_value(value_str):
    """
    Extract numeric value from a metadata string for comparison.
    """
    try:
        import re
        numbers = re.findall(r'-?\d+\.?\d*', str(value_str))
        if numbers:
            return float(numbers[0])
    except Exception as e:
        print(e)
    return None
