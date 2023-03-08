# DiscordSlicer
DiscordSlice is a program that allows you to easily upload large files to Discord by slicing them up into 8MB parts. Once the files are uploaded, you can merge the parts back together again and download the complete file.

## Current Issues

- The program crashes when files take longer than 15 minutes to upload or download, as an interaction only lasts for 15 minutes. A possible solution would be to use `ctx` instead of interactions.
- Media files such as `mp4` or `mp3` get corrupted when uploaded, as they need to be split differently to avoid corruption.
