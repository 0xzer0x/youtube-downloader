import os, pathlib, sys, re
import subprocess
from colorama import init, Fore, Back, Style

init(convert=True)
os.chdir(pathlib.Path(__file__).parent.resolve())

print(Fore.RED + Style.BRIGHT + '''
      ___                      ___       
     / _ \__  __ _______ _ __ / _ \__  __
    | | | \ \/ /|_  / _ \ '__| | | \ \/ /
    | |_| |>  <  / /  __/ |  | |_| |>  < 
     \___//_/\_\/___\___|_|   \___//_/\_\\
 ''')
print("<~~Python Youtube Downloader~~>".center(47))
print("-------------------------------\n".center(47))
print(Style.RESET_ALL, end='')
class ytVideo:

    url_pattern = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
    mp3_command = f"python yt-dlp --no-playlist -x --audio-format mp3 -o \Output\%(title)s-%(resolution)s.%(ext)s"
    def __init__(self):
        print(Fore.RED, end='')
        print("[+]Checking yt-dlp version...")
        self.run_command('python yt-dlp -U')
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
                        print(Fore.BLUE, end='')
                        print('[+]Fetching all available video qualities...')
                        print(Style.RESET_ALL, end='')
                        self.videoFormats = self.getFormatsList(link)
                        vidHeights = []
                        self.vidOnlyCheckList = []
                        print(Fore.CYAN, end='')
                        for index, vidFormat in enumerate(self.videoFormats):
                            self.vidOnlyCheckList.append("(video only)" if vidFormat[3] == " " else "")
                            print(f"[{index+1}] Quality: {vidFormat[4]} {vidFormat[1]}, Size ~{vidFormat[2]} {self.vidOnlyCheckList[index]}")
                            vidHeights.append(vidFormat[4].split("p")[0])
                        print(Style.RESET_ALL, end='')
                        self.link = link
                        self.choose_quality_and_download(displayedFormats=True, heightsList=vidHeights)

            elif is_batchfile in ['yes', 'y']:
                self.link = "--batch-file links_list.txt"
                self.choose_quality_and_download(heightsList=['1080','720','480','360','144'])    
        elif download_type == "2":
            self.link = "--batch-file links_list.txt" 
            self.run_command(f"{self.mp3_command} {self.link}")      
    def run_command(self,func_command): 
        try:
            print(Fore.CYAN + Style.BRIGHT, end='')
            os.system(f"cmd /c {func_command}")
            print(Style.RESET_ALL, end='')
        except KeyboardInterrupt:
            print(Style.RESET_ALL, end='')
            print(Fore.RED, Style.BRIGHT, end='')
            confirm_exit = self.chooseFromOptions('[!]Keyboard interrupt,are you sure you want to exit?(y/n)', 'y/n')
            print(Style.RESET_ALL, end='')
            if confirm_exit == 'y':
                sys.exit()
            else:
                self.run_command(func_command)
    def choose_quality_and_download(self,displayedFormats=False,heightsList=[]):
        if (displayedFormats):
            vidHeightIndex = int(self.chooseFromOptions("[Options] Please select a quality to download", "/".join([str(x) for x in range(1,len(heightsList)+1)]))) - 1
            fileID = self.videoFormats[vidHeightIndex][0]
            if (self.vidOnlyCheckList[vidHeightIndex]):
                print(Fore.RED, end='')
                mergeWithAudio = self.chooseFromOptions("[Alert] No audio file detected, do you want to download audio separately & merge with video?(y/n)", "y/n/yes/no")
                print(Style.RESET_ALL, end='')
                if (mergeWithAudio in ['y', 'yes']):
                    selectedFormat = f"{fileID}+ba"
                else:
                    selectedFormat = f"{fileID}"
            else:
                selectedFormat = f"{fileID}"
        else:
            print(Fore.CYAN, end='')
            video_quality = self.chooseFromOptions("[Options] Please select a quality to download\n1-1080p\n2-720p\n3-480p\n4-360p\n5-Highest possible(if higher than 1080p is available)\n6-Custom", '1/2/3/4/5/6') 
            print(Style.RESET_ALL, end='')
            if video_quality == "1": selectedFormat = 'bv[height=1080]+ba'
            elif video_quality == "2": selectedFormat = 'bv[height=720]+ba'
            elif video_quality == "3": selectedFormat = 'bv[height=480]+ba'
            elif video_quality == "4": selectedFormat = 'bv[height=360]+ba'
            elif video_quality == "5": selectedFormat = 'bv+ba'
            elif video_quality == "6": 
                entered_height = int(self.chooseFromOptions("Enter desired video height: ", '/'.join(heightsList)))
                selectedFormat = f'bv[height={entered_height}]+ba'            
        self.run_command(f"python yt-dlp --no-playlist -f {selectedFormat} --merge-output-format mp4 -o \Output\%(title)s-%(resolution)s.%(ext)s {self.link}")
    def chooseFromOptions(self,promptText, validChoices):
        choice = ''
        while choice not in validChoices.split("/"):
            choice = input(f'{promptText}\n>>> ').lower()
        return choice
    def getFormatsList(self,l):
        cmdPipe = subprocess.Popen(f"python yt-dlp -F {l}", shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        allFormats = cmdPipe.communicate()[0].decode()
        cmdPipe.terminate()
        #                format-code  mp4/webm     file-size     audio codec if it exists/space    resolution[fps]
        vF = re.findall(r'(\d{2,3}).+([m,w]\w+).*?(\d+\.?\d+\wiB).*?(mp4a.+\S|aac.+\S|opus.+\S| ).(\d{3,4}p(\d{2})?)',allFormats)
        return vF # list of tuples in the following format: [("22","mp4","222MiB","mp4a/aac/opus...","720p[60]"),(group1,group2,group3,group4,group5),...]

main = ytVideo()