"""Class for converting SBF files."""

from pathlib import Path

import ffmpeg

from europa_1400_tools.const import SoundType, TargetFormat
from europa_1400_tools.construct.sbf import Sbf
from europa_1400_tools.converter.base_converter import BaseConverter
from europa_1400_tools.helpers import rebase_path


class SbfConverter(BaseConverter):
    """Class for converting SBF files."""

    def convert_file(
        self,
        file_path: Path,
        output_path: Path,
        base_path: Path,
        target_format: TargetFormat,
        create_subdirectories: bool = False,
    ) -> list[Path]:
        """Convert SBF to another format."""

        sbf = Sbf.from_file(file_path)

        audio_bytes_dict: dict[str, list[bytes]] = {}
        audio_output_paths: list[Path] = []

        if target_format == TargetFormat.MP3:
            audio_bytes_dict = SbfConverter._convert_to_mp3(sbf)
        else:
            audio_bytes_dict = SbfConverter._convert_to_wav(sbf)

        for soundbank in sbf.soundbanks:
            audio_bytes_list: list[bytes] = []

            for i, sound in enumerate(soundbank.sounds):
                sound_definition = soundbank.sound_definitions[i]
                audio_bytes: bytes = sound

                if (
                    sound_definition.sound_type == SoundType.WAV
                    and target_format != TargetFormat.WAV
                    or sound_definition.sound_type == SoundType.MP3
                    and target_format != TargetFormat.MP3
                ):
                    if target_format == TargetFormat.MP3:
                        audio_bytes = SbfConverter._convert_wav_to_mp3(sound)
                    else:
                        audio_bytes = SbfConverter._convert_mp3_to_wav(sound)

                audio_bytes_list.append(audio_bytes)

            audio_bytes_dict[soundbank.soundbank_definition.name] = audio_bytes_list

        sbf_output_path = rebase_path(file_path.parent, base_path, output_path)

        for soundbank_name, audio_bytes_list in audio_bytes_dict.items():
            for i, audio_bytes in enumerate(audio_bytes_list):
                name = f"{sbf.name}_{soundbank_name}"
                if len(audio_bytes_list) > 1:
                    name += f"_{i}"

                audio_output_path = (
                    sbf_output_path
                    / soundbank_name
                    / Path(name).with_suffix(target_format.extension)
                )

                if not audio_output_path.parent.exists():
                    audio_output_path.parent.mkdir(parents=True)

                with open(audio_output_path, "wb") as wav_output_file:
                    wav_output_file.write(audio_bytes)

                audio_output_paths.append(audio_output_path)

        return audio_output_paths

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
