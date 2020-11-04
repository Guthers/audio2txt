# Audio 2 Text
This repo uses googles python api to turn speech into text. This is something I did fairly
quickly in my own time, it's not the best code, but it'll work, feel free to send me a pull
request if you want anything changed.

## Requirements
- A file called `creds.json` placed at the root of the repo, this is the credentials file provided by google
- Ensure `ffmpeg` works on your system
- Your python environment has access to `google.oauth2` and `google.cloud.speech_v1p1beta1` (pip install something, I don't remember what)
- A subdirectory under the root folder called `audios`

## How it works
- Takes the audio files (ending in `mp3`) in the `audios` sub directory.
- Uses `ffmpeg` to split them into 50s chunks (as there is a limit on the google api)
- Sends each segment of the audio to the google api for translation
- Combines the audio sub segments together into an output file
- Removes the temporary 50s audio files