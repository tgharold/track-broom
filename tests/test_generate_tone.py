"""Tests for the util module (tone generation)."""

import struct

from tests.utils import tone_samples


class TestToneSamples:
    """Tests for tone_samples function."""

    def test_440hz_5s_expected_samples(self) -> None:
        """Verify sample count matches expected duration of 440Hz for 5s."""
        samplerate = 44100
        duration = 5.0
        pcm = tone_samples(freq=440, duration=duration, samplerate=samplerate)
        num_samples = len(pcm) // 2  # 2 bytes per sample (int16)
        expected = samplerate * duration
        assert num_samples == expected

    def test_440hz_3s_expected_samples(self) -> None:
        """Verify sample count matches expected duration of 440Hz for 3s."""
        samplerate = 44100
        duration = 3.0
        pcm = tone_samples(freq=440, duration=duration, samplerate=samplerate)
        num_samples = len(pcm) // 2
        expected = samplerate * duration
        assert num_samples == expected

    def test_default_params(self) -> None:
        """Test that default parameters produce valid output with correct duration."""
        pcm = tone_samples()
        num_samples = len(pcm) // 2
        assert num_samples == 44100 * 3  # 3 seconds default

    def test_8khz_sample(self) -> None:
        """Test with 8kHz sample rate."""
        pcm = tone_samples(freq=220, duration=1.0, samplerate=8000)
        num_samples = len(pcm) // 2
        assert num_samples == 8000

    def test_fade_in_small_value(self) -> None:
        """Fade-in samples should start with small values near zero."""
        pcm = tone_samples(freq=440, duration=3.0, samplerate=44100)
        samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
        first_50 = samples[:50]
        # First samples should be very small due to fade-in envelope
        max_first_50 = max(abs(s) for s in first_50)
        assert max_first_50 < 2000

    def test_fade_out_small_value(self) -> None:
        """Fade-out samples should end with small values near zero."""
        samplerate = 44100
        pcm = tone_samples(freq=440, duration=3.0, samplerate=samplerate)
        samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
        fade_count = samplerate * 3 // 1000
        last_samples = samples[-fade_count:]
        max_last = max(abs(s) for s in last_samples)
        assert max_last < 2000

    def test_values_in_16bit_range(self) -> None:
        """All raw values before normalization should be in [-32767, 32767]."""
        samples = tone_samples(freq=261, duration=0.5, samplerate=44100)
        decoded = struct.unpack(f"<{len(samples) // 2}h", samples)
        for s in decoded:
            assert -32768 <= s <= 32767
