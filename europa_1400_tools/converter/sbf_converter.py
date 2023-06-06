"""Class for converting SBF files."""

from pathlib import Path

import ffmpeg

from europa_1400_tools.const import (
    MP3_EXTENSION,
    WAV_EXTENSION,
    SoundType,
    TargetAudioFormat,
)
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.converter.base_converter import BaseConverter


class SbfConverter(BaseConverter[Sbf, dict[str, list[bytes]]]):
    """Class for converting SBF files."""

    @staticmethod
    def _convert_mp3_to_wav(mp3_bytes: bytes) -> bytes:
        """Convert MP3 to WAV"""

        process = (
            ffmpeg.input("pipe:")
            .output("pipe:", format="wav")
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )

        wav_bytes, _ = process.communicate(input=mp3_bytes)

        return wav_bytes

    @staticmethod
    def _convert_wav_to_mp3(wav_bytes: bytes):
        """Convert WAV to MP3"""

        process = (
            ffmpeg.input("pipe:")
            .output("pipe:", format="mp3")
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )

        mp3_bytes, _ = process.communicate(input=wav_bytes)

        return mp3_bytes

    @staticmethod
    def _convert_to_wav(sbf: Sbf) -> dict[str, list[bytes]]:
        """Convert SBF to WAV"""

        wav_bytes_dict: dict[str, list[bytes]] = {}

        for soundbank in sbf.soundbanks:
            wav_bytes_list: list[bytes] = []

            for i, sound in enumerate(soundbank.sounds):
                sound_definition = soundbank.sound_definitions[i]

                wav_bytes: bytes
                if sound_definition.sound_type == SoundType.MP3:
                    wav_bytes = SbfConverter._convert_mp3_to_wav(sound)
                else:
                    wav_bytes = sound

                wav_bytes_list.append(wav_bytes)

            wav_bytes_dict[soundbank.soundbank_definition.name] = wav_bytes_list

        return wav_bytes_dict

    @staticmethod
    def _convert_to_mp3(sbf: Sbf) -> dict[str, list[bytes]]:
        """Convert SBF to MP3"""

        mp3_bytes_dict: dict[str, list[bytes]] = {}

        for soundbank in sbf.soundbanks:
            mp3_bytes_list: list[bytes] = []

            for i, sound in enumerate(soundbank.sounds):
                sound_definition = soundbank.sound_definitions[i]

                mp3_bytes: bytes
                if sound_definition.sound_type == SoundType.MP3:
                    mp3_bytes = sound
                else:
                    mp3_bytes = SbfConverter._convert_wav_to_mp3(sound)

                mp3_bytes_list.append(mp3_bytes)

            mp3_bytes_dict[soundbank.soundbank_definition.name] = mp3_bytes_list

        return mp3_bytes_dict

    @staticmethod
    def convert(value: Sbf, **kwargs) -> dict[str, list[bytes]]:
        """Convert SBF to another format."""

        target_audio_format: TargetAudioFormat = kwargs.get(
            "target_audio_format", TargetAudioFormat.WAV
        )

        audio_bytes_dict: dict[str, list[bytes]] = {}

        for soundbank in value.soundbanks:
            audio_bytes_list: list[bytes] = []

            for i, sound in enumerate(soundbank.sounds):
                sound_definition = soundbank.sound_definitions[i]

                audio_bytes: bytes = sound

                if sound_definition.sound_type != target_audio_format:
                    if target_audio_format == TargetAudioFormat.MP3:
                        audio_bytes = SbfConverter._convert_wav_to_mp3(sound)
                    else:
                        audio_bytes = SbfConverter._convert_mp3_to_wav(sound)

                audio_bytes_list.append(audio_bytes)

            audio_bytes_dict[soundbank.soundbank_definition.name] = audio_bytes_list

        return audio_bytes_dict

    @staticmethod
    def convert_and_export(value: Sbf, output_path: Path, **kwargs) -> list[Path]:
        """Convert SBF and export to output_path."""

        target_audio_format: TargetAudioFormat = kwargs.get(
            "target_audio_format", TargetAudioFormat.WAV
        )
        audio_output_paths: list[Path] = []
        audio_bytes_dict: dict[str, list[bytes]]
        extension: str

        if target_audio_format == TargetAudioFormat.MP3:
            audio_bytes_dict = SbfConverter._convert_to_mp3(value)
            extension = MP3_EXTENSION
        else:
            audio_bytes_dict = SbfConverter._convert_to_wav(value)
            extension = WAV_EXTENSION

        for soundbank_name, audio_bytes_list in audio_bytes_dict.items():
            for i, audio_bytes in enumerate(audio_bytes_list):
                name = f"{value.name}_{soundbank_name}"
                if len(audio_bytes_list) > 1:
                    name += f"_{i}"

                audio_output_path = output_path / Path(name).with_suffix(extension)

                if not audio_output_path.parent.exists():
                    audio_output_path.parent.mkdir(parents=True)

                with open(audio_output_path, "wb") as wav_output_file:
                    wav_output_file.write(audio_bytes)

                audio_output_paths.append(audio_output_path)

        return audio_output_paths
