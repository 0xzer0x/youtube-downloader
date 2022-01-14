import os
import pathlib
import sys
import re
import subprocess
import colorama

isLinux = True if sys.platform != "win32" else False
if not isLinux:
    colorama.init(convert=True)
    pyex = "python"
else:
    pyex = "python3"


class bcolors:
    BRBLUE = (colorama.Fore.BLUE + colorama.Style.BRIGHT)
    BRCYAN = (colorama.Fore.CYAN + colorama.Style.BRIGHT)
    BRRED = (colorama.Fore.RED + colorama.Style.BRIGHT)
    RED = (colorama.Fore.RED)
    WARNING = (colorama.Fore.YELLOW)
    ENDC = (colorama.Style.RESET_ALL)
    BOLD = '\033[1m' if isLinux else ''


os.chdir(pathlib.Path(__file__).parent.resolve())

print(bcolors.BRRED + bcolors.BOLD + '''
      ___                      ___       
     / _ \__  __ _______ _ __ / _ \__  __
    | | | \ \/ /|_  / _ \ '__| | | \ \/ /
    | |_| |>  <  / /  __/ |  | |_| |>  < 
     \___//_/\_\/___\___|_|   \___//_/\_\\
 ''')
print("<~~Python Youtube Downloader~~>".center(47))
print("-------------------------------\n".center(47))
print(bcolors.ENDC, end='')

class ytVideo:

    url_pattern = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
    if not isLinux:
        mp3_command = f"python yt-dlp --no-playlist -x --audio-format mp3 -o Output\%(title)s-%(resolution)s.%(ext)s"
    else:
        mp3_command = f"python3 yt-dlp --no-playlist -x --audio-format mp3 -o Output/%\(title\)s-%\(resolution\)s.%\(ext\)s"
    def __init__(self):

        print(bcolors.RED, end='')
        print("[+]Checking yt-dlp version...")
        self.run_command(f'{pyex} yt-dlp -U')

        while True:
            try:
                self.file_count = 0

                while self.file_count < 1:
                    self.file_count = int(input("[Options] How many files do you want to download?\n>>> "))

                break
            except ValueError:

                print("Invalid value, please enter a number.")
                continue

        links_list = []
        for i in range(self.file_count):
            youtube_link = ''
            # Check if youtube link is valid
            while re.search(self.url_pattern, youtube_link) is None:
                youtube_link = input(f"[Options] Please Enter valid link to youtube video #{i+1}\n>>> ")

            links_list.append(youtube_link)

        # creates a txt file called links_list and adds the links to it
        with open('links_list.txt', "w") as file:
            file.write("\n".join(links_list))

        download_type = self.chooseFromOptions('[Options] What do you want to save the video as?\n1-Mp4/video file\n2-Mp3/audio file', '1/2')

        if download_type == "1":
            is_batchfile = ''

            if self.file_count > 1:
                is_batchfile = self.chooseFromOptions('[Options] Do you want to batch download these videos?(y/n)', 'yes/no/y/n')
            else:
                is_batchfile = "no"

            if is_batchfile in ["no", "n"]:

                for link in links_list:
                    listAllFormats = self.chooseFromOptions('[Options] List all available download formats?(y/n)', 'y/n/yes/no')

                    if listAllFormats in ['y', 'yes']:

                        print(bcolors.RED, end='')
                        print('[+]Fetching all available video qualities...')
                        print(bcolors.ENDC, end='')

                        # Get formats nested list to display qualities
                        self.videoFormats = self.getFormatsList(link)
                        vidHeights = []
                        self.vidOnlyCheckList = []

                        # map video-only tags
                        # to the corresponding index of the video
                        print(bcolors.BRCYAN, end='')
                        for index, vidFormat in enumerate(self.videoFormats):
                            self.vidOnlyCheckList.append("(video only)" if vidFormat[3] == " " else "")
                            print(f"[{index+1}] Quality: {vidFormat[4]} {vidFormat[1]}, Size ~{vidFormat[2]} {self.vidOnlyCheckList[index]}")
                            vidHeights.append(vidFormat[4].split("p")[0])

                        print(bcolors.ENDC, end='')
                        self.link = link
                        # choose the quality to download from available qualities         
                        self.choose_quality_and_download(displayedFormats=True, heightsList=vidHeights)

            # if batch-downloading videos select the quality once
            elif is_batchfile in ['yes', 'y']:
                self.link = "--batch-file links_list.txt"
                self.choose_quality_and_download(heightsList=['1080','720','480','360','144'])    

        # Downloading audio from batch file directly in highest audio quality
        elif download_type == "2":
            self.link = "--batch-file links_list.txt"
            self.run_command(f"{self.mp3_command} {self.link}")

    def choose_quality_and_download(self,
                                    displayedFormats=False,
                                    heightsList=[]):
        if (displayedFormats):
            vidHeightIndex = int(self.chooseFromOptions("[Options] Please select a quality to download",
                                                        "/".join([str(x) for x in range(1, len(heightsList) + 1)]))) - 1
            fileID = self.videoFormats[vidHeightIndex][0]

            # Check if the quality choosen has audio codec or not
            # through it's corresponding index in the video-only list
            if (self.vidOnlyCheckList[vidHeightIndex]):
                print(bcolors.WARNING, end='')
                mergeWithAudio = self.chooseFromOptions("[Alert] No audio file detected, do you want to download audio separately & merge with video?(y/n)",
                                                        "y/n/yes/no")
                print(bcolors.ENDC, end='')

                if (mergeWithAudio in ['y', 'yes']):
                    selectedFormat = f"{fileID}+ba"
                else:
                    selectedFormat = f"{fileID}"

            else:
                selectedFormat = f"{fileID}"

        # If formats aren't listed,
        # suggest most probable available video qualities
        else:
            print(bcolors.BRCYAN, end='')
            video_quality = self.chooseFromOptions("[Options] Please select a quality to download\n1-1080p\n2-720p\n3-480p\n4-360p\n5-Highest possible(if higher than 1080p is available)\n6-Custom",
                                                   '1/2/3/4/5/6')
            print(bcolors.ENDC, end='')

            if video_quality == "1": selectedFormat = 'bv[height=1080]+ba'

            elif video_quality == "2": selectedFormat = 'bv[height=720]+ba'

            elif video_quality == "3": selectedFormat = 'bv[height=480]+ba'

            elif video_quality == "4": selectedFormat = 'bv[height=360]+ba'

            elif video_quality == "5": selectedFormat = 'bv+ba'

            # If user wants to specify a quality not listed
            elif video_quality == "6":
                entered_height = int(self.chooseFromOptions("Enter desired video height: ",
                                                            '/'.join(heightsList)))
                selectedFormat = f'bv[height={entered_height}]+ba'

        if isLinux:
            cmd = f"{pyex} yt-dlp --no-playlist -f {selectedFormat} --merge-output-format mp4 -o Output/%\(title\)s-%\(resolution\)s.%\(ext\)s {self.link}"
        else:
            cmd = f"{pyex} yt-dlp --no-playlist -f {selectedFormat} --merge-output-format mp4 -o Output/%(title)s-%(resolution)s.%(ext)s {self.link}"
        self.run_command(cmd)
        
    def chooseFromOptions(self, promptText, validChoices):
        choice = ''
        while choice not in validChoices.split("/"):
            choice = input(f'{promptText}\n>>> ').lower()
        return choice

    # Use regex to get information about each quality available in a list
    # which are returned in a list of quality lists
    def getFormatsList(self, l):
        # use subprocess to return the output as string
        cmdPipe = subprocess.Popen(f"{pyex} yt-dlp -F {l}",
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdout=subprocess.PIPE)
        allFormats = cmdPipe.communicate()[0].decode()
        cmdPipe.terminate()

        #                format-code  mp4/webm     file-size     audio codec if it exists/space    resolution[fps]
        vF = re.findall(r'(\d{2,3}).+([m,w]\w+).*?(\d+\.?\d+\wiB).*?(mp4a.+\S|aac.+\S|opus.+\S| ).(\d{3,4}p(\d{2})?)',allFormats)
        # list of tuples in the following format:
        # [("22","mp4","222MiB","mp4a/aac/opus...","720p[60]"),
        # (group1,group2,group3,group4,group5),...]
        return vF

    # run the commands through "os" module
    def run_command(self, func_command):
        try:
            print(bcolors.ENDC, end='')
            print(bcolors.BRCYAN, end='')

            os.system((f"{func_command}" if isLinux
                        else f"cmd /c {func_command}"))

            print(bcolors.ENDC, end='')

        except KeyboardInterrupt:
            print(bcolors.WARNING, end='')
            confirm_exit = self.chooseFromOptions('[!]Keyboard interrupt,are you sure you want to exit?(y/n)', 'y/n')
            print(bcolors.ENDC, end='')

            if confirm_exit == 'y':
                sys.exit()
            else:
                self.run_command(func_command)


main = ytVideo()
