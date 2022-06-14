"""
simple python script to automate yt-dlp commands
"""
import os
import pathlib
import sys
import re
import subprocess
import colorama
import yt_dlp

IS_LINUX = True if sys.platform != "win32" else False

class CmdColors:
    """ Terminal color constants """
    BRBLUE = (colorama.Fore.BLUE + colorama.Style.BRIGHT)
    BRCYAN = (colorama.Fore.CYAN + colorama.Style.BRIGHT)
    BRRED = (colorama.Fore.RED + colorama.Style.BRIGHT)
    RED = (colorama.Fore.RED)
    WARNING = (colorama.Fore.YELLOW)
    ENDC = (colorama.Style.RESET_ALL)
    BOLD = '\033[1m' if IS_LINUX else ''


os.chdir(pathlib.Path(__file__).parent.resolve())

print(CmdColors.BRRED + CmdColors.BOLD + r'''
      ___                      ___
     / _ \__  __ _______ _ __ / _ \__  __
    | | | \ \/ /|_  / _ \ '__| | | \ \/ /
    | |_| |>  <  / /  __/ |  | |_| |>  <
     \___//_/\_\/___\___|_|   \___//_/\_\
 ''')
print("<~~Python Youtube Downloader~~>".center(47))
print("-------------------------------\n".center(47))
print(CmdColors.ENDC, end='')


class YtVideo:
    """ Deals with the links and formats of the youtube videos """

    URL_PATTERN = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

    OUTPUT_TEMPLATE = {"default": "Output/%(title)s-%(resolution)s.%(ext)s"}

    MP3_OPTS = {"format": "bestaudio", "noplaylist": True, "outtmpl": OUTPUT_TEMPLATE, "postprocessors": [
        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]}

    def __init__(self):

        print(CmdColors.WARNING, end='')
        print("[+]Checking yt-dlp version...")
        try:
            with yt_dlp.YoutubeDL() as ytdlp:
                yt_dlp.update.run_update(ytdlp)
        except yt_dlp.utils.DownloadError:
            pass
        print(CmdColors.ENDC, end="")

        while True:
            try:
                self.file_count = 0

                while self.file_count < 1:
                    self.file_count = int(
                        input("[Options] How many files do you want to download?\n>>> "))

                break
            except ValueError:

                print("Invalid value, please enter a number.")
                continue

        # create a list of the youtube videos to download
        links_list = []
        for i in range(self.file_count):
            youtube_link = ''
            # Check if youtube link is valid
            while re.search(self.URL_PATTERN, youtube_link) is None:
                youtube_link = input(
                    f"[Options] Please Enter valid link to youtube video #{i+1}\n>>> ")

            links_list.append(youtube_link)

        # creates a txt file called links_list and adds the links to it
        # with open('links_list.txt', "w", encoding="utf-8") as file:
        #     file.write("\n".join(links_list))

        download_type = self.choose_from_options(
            '[Options] What do you want to save the video as?\n1-Mp4/video file\n2-Mp3/audio file', '1/2')

        if download_type == "1":
            is_batchfile = ''

            if self.file_count > 1:
                is_batchfile = self.choose_from_options(
                    '[Options] Do you want to batch download these videos?(y/n)', 'yes/no/y/n')
            else:
                is_batchfile = "no"

            if is_batchfile in ["no", "n"]:

                for link_number, link in enumerate(links_list, 1):
                    self.link = link
                    list_all_formats = self.choose_from_options(
                        f'[Options] List all available download formats for video #{link_number}?(y/n)', 'y/n/yes/no')
                    if list_all_formats in ['y', 'yes']:

                        print(CmdColors.WARNING, end='')
                        print('[+]Fetching all available video qualities...')
                        print(CmdColors.ENDC, end='')

                        # Get formats nested list to display qualities
                        self.vid_formats = self.get_formats_list(link)
                        vid_heights = []
                        self.vid_only_checklist = []

                        # map video-only tags
                        # to the corresponding index of the video
                        print(CmdColors.BRCYAN, end='')
                        for index, vid_format in enumerate(self.vid_formats):
                            self.vid_only_checklist.append(
                                "(video only)" if vid_format[3] == " " else "")
                            format_details = f"[{index+1}] Quality: {vid_format[4]} {vid_format[1]}, Size ~{vid_format[2]} {self.vid_only_checklist[index]}"
                            print(format_details)
                            vid_heights.append(vid_format[4].split("p")[0])

                        print(CmdColors.ENDC, end='')

                        # choose the quality to download from available qualities
                        self.choose_quality_and_download(
                            displayed_formats=True, heights_list=vid_heights)
                    else:
                        self.choose_quality_and_download(displayed_formats=False)
            # if batch-downloading videos select the quality once (skips video if it doesn't have the selected quality)
            elif is_batchfile in ['yes', 'y']:
                self.choose_quality_and_download(
                    heights_list=['1080', '720', '480', '360', '144'])

        # Downloading audio from list directly in highest audio quality
        elif download_type == "2":
            self._ytdlp_download(None, links_to_dl=links_list, audio_only=True)

    def choose_quality_and_download(self,
                                    displayed_formats=False,
                                    heights_list=[]):
        """ Select the format to pass to yt-dlp """
        if displayed_formats:
            vid_height_index = int(self.choose_from_options(
                "[Options] Please select a quality to download",
                "/".join(
                    [str(x) for x in range(1,
                                           len(heights_list) + 1)]))) - 1
            file_id = self.vid_formats[vid_height_index][0]

            # Check if the quality chosen has audio codec or not
            # through it's corresponding index in the video-only list
            if self.vid_only_checklist[vid_height_index]:
                print(CmdColors.WARNING, end='')
                merge_audio = self.choose_from_options("[Alert] No audio file detected, do you want to download audio separately & merge with video?(y/n)",
                                                       "y/n/yes/no")
                print(CmdColors.ENDC, end='')

                if (merge_audio in ['y', 'yes']):
                    selected_format = f"{file_id}+ba"

                else:
                    selected_format = f"{file_id}"

            else:
                selected_format = f"{file_id}"

        # If formats aren't listed,
        # suggest most probable available video qualities
        else:
            print(CmdColors.BRCYAN, end='')
            video_quality = self.choose_from_options("[Options] Please select a quality to download\n1-1080p\n2-720p\n3-480p\n4-360p\n5-Highest possible(if higher than 1080p is available)\n6-Custom",
                                                     '1/2/3/4/5/6')
            print(CmdColors.ENDC, end='')

            if video_quality == "1":
                selected_format = 'bv[height=1080]+ba'

            elif video_quality == "2":
                selected_format = 'bv[height=720]+ba'

            elif video_quality == "3":
                selected_format = 'bv[height=480]+ba'

            elif video_quality == "4":
                selected_format = 'bv[height=360]+ba'

            elif video_quality == "5":
                selected_format = 'bv[ext=mp4]+ba[ext=mp4a]\\bv+ba'

            # If user wants to specify a quality not listed
            elif video_quality == "6":
                entered_height = int(self.choose_from_options("Enter desired video height: ",
                                                              '/'.join(heights_list)))
                selected_format = f'bv[height={entered_height}]+ba'

        self._ytdlp_download(format=selected_format, links_to_dl=[self.link])

    def _ytdlp_download(self, format: str, links_to_dl: list, audio_only=False):
        """Function that uses the yt_dlp module to download the video

        Arguments:
            format (str) - the format selection string according to the yt-dlp docs

            links_to_dl (str) - link of the youtube video to download

            audio_only (bool) - download audio only if True
        """
        # Setup the yt-dlp options if downloading video else use mp3 options
        if not audio_only:
            ytdlp_opts = {"format": format, "noplaylist": True,
                          "outtmpl": self.OUTPUT_TEMPLATE}
        else:
            ytdlp_opts = self.MP3_OPTS

        print(CmdColors.ENDC)
        with yt_dlp.YoutubeDL(ytdlp_opts) as ytdl:
            ytdl.download(links_to_dl)

    @staticmethod
    def choose_from_options(prompt_text, valid_choices):
        """
            Description: Makes sure that the user enters one of the valid_choices separated by "/"
            return: one of the valid_choices specified
        """
        choice = ''
        while choice not in valid_choices.split("/"):
            choice = input(f'{prompt_text}\n>>> ').lower()
        return choice

    # Use regex to get information about each quality available in a list
    # which are returned in a list of quality lists
    @ staticmethod
    def get_formats_list(link):
        """ Use subprocess to return the formats returned by yt-dlp as string """
        cmd_pipe = subprocess.Popen(f"yt-dlp -F {link}",
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdout=subprocess.PIPE)
        all_formats = cmd_pipe.communicate()[0].decode()
        cmd_pipe.terminate()

        formats_regex = '(\d{2,3}).+([m,w]\w+).*?(\d+\.?\d+\wiB).*?(mp4a.+\S|aac.+\S|opus.+\S| ).(\d{3,4}p(\d{2})?)'
        # (format-code, mp4/webm, file-size audio codec(if it exists/space), resolution[fps])
        video_formats = re.findall(formats_regex, all_formats)
        # list of tuples in the following format:
        # [("22","mp4","222MiB","mp4a/aac/opus...","720p[60]"),
        # (group1,group2,group3,group4,group5), etc.]
        return video_formats


try:
    main = YtVideo()
except KeyboardInterrupt:
    print("\n[!] keyboard interrupt, exiting...")
    sys.exit()

