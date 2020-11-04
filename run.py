import os
from os import listdir
from os.path import isfile, join
import pathlib
from google.oauth2 import service_account
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
import io


def get_files(directory):
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    txtFiles = []
    audioFiles = []
    for f in files:
        if f.endswith(".txt"):
            txtFiles.append(f)
        elif f.endswith(".mp3"):
            audioFiles.append(f)
    result = []
    for f in audioFiles:
        if f.replace(".mp3", ".txt") not in txtFiles:
            result.append(f)

    return result


def google_speech_recognition(client, config, local_file_path):
    """
    Transcribe a long audio file using asynchronous speech recognition
    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    # Send off the operation
    operation = client.long_running_recognize(config, audio)

    # We can get the result later
    return operation


def split_audio_file(fp, directory):
    before_count = len([f for f in listdir(directory) if isfile(join(directory, f))])
    os.system(f"ffmpeg -hide_banner -loglevel panic -i {fp} -f segment -segment_time 50 -c copy {fp.replace('.mp3','%03d.mp3')}")

    result = []
    for i in range(len([f for f in listdir(directory) if isfile(join(directory, f))]) - before_count):
        result.append(fp.replace('.mp3', str(i).zfill(3) + '.mp3'))

    return result


def add_lines(txt):
    words = txt.split(" ")
    count = 0
    ll = 20
    result = ""
    for w in words:
        result += w + " "
        count += 1
        if count == ll:
            result += "\n"
            count = 0

    return result


def audio_to_text(directory, audio_file):
    txt_file = directory + audio_file.replace(".mp3", ".txt")

    # Need to split the audio file into 50 second sub files. thanks google
    files = split_audio_file(f"{directory}{audio_file}", directory)

    operations = []
    print(f"Transcribing file {audio_file}", flush=True)

    parts = len(files) * 3 + 1
    progress = 1

    i = 1

    client = speech_v1p1beta1.SpeechClient(credentials=get_google_credentials(pathlib.Path(__file__).parent.absolute()))
    language_code = "en-AU"
    sample_rate_hertz = 16000
    encoding = enums.RecognitionConfig.AudioEncoding.MP3
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }

    for f in files:
        print(f"File progress = {round((progress / parts)*100,0)}%", end="\r", flush=True)
        progress += 2

        i += 1
        operations.append(google_speech_recognition(client, config, f))
        os.system(f"rm {f}")

    txt = ""
    for operation in operations:
        print(f"File progress = {round(progress / parts,2)*100}%", end="\r", flush=True)
        progress += 1

        response = operation.result()
        for result in response.results:
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            txt += alternative.transcript

    txt = add_lines(txt)

    with open(txt_file, 'w') as f:
        f.write(txt)
    print(f"File progress = 100%                   ", flush=True)


def get_google_credentials(cDir):
    return service_account.Credentials.from_service_account_file(join(cDir, "creds.json"))


def main():
    cDir = pathlib.Path(__file__).parent.absolute()
    directory = join(cDir, "audios")
    files = get_files(directory)
    print(f"Converting the following {len(files)} files: [{', '.join(files)}]")

    for f in files:
        audio_to_text(directory, f)


if __name__ == "__main__":
    main()
