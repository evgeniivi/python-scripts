import os
import sys
import shutil
import glob
import ffmpeg
import random
import datetime
import time
import random
from datetime import datetime
from pathlib import Path
from moviepy.editor import VideoFileClip

nums = sys.argv[2].split(',')
exts = sys.argv[3].split(',')
count = int(nums[0])
sec2 = int(nums[1])
dur = count * sec2
flags = sys.argv[1].split(',')
path = "."
folders = ["/videos1", "/videos2"]
musicfolders = ["/musics1", "musics2"]
#exts = [".mp4"]

# makes folder structure
def maketree(maketreevars):
	if 'cuts' in maketreevars:
		try:
			shutil.rmtree("./splits/cuts")
		except:
			pass
		try:
			os.makedirs("./splits/cuts")
		except:
			pass

	if 'prod' in maketreevars:
		try:
			shutil.rmtree("./splits/prod")
		except:
			pass
		try:
			os.makedirs("./splits/prod")
		except:
			pass

	if 'temp' in maketreevars:
		try:
			shutil.rmtree("./splits/temp")
		except:
			pass
		try:
			os.makedirs("./splits/temp")
		except:
			pass

# clears cuts dir for bad vids cuts
def clear():	
	video = glob.glob("./splits/cuts/*.mp4")
	for f in video:
		size = os.path.getsize(f)
		if (size < 1000):
			os.remove(f)

# gets time 
def gettime(seconds, dur = 1):
	result = []
	begin = random.randint(0, int(seconds))
	result.append([begin, begin + dur])

	if (seconds is None):
		return False

	return result

# finds files by exts in dir
def files(path, extss = exts) :
	result = []
	for file in os.listdir(path):
		newpath = path + "/" + file
		try:
			if not os.path.isfile(newpath):	
				result.extend(files(newpath, extss))
		except:
			pass
		for ext in extss:
			try:
				if os.path.isfile(newpath) and newpath.endswith(ext):
					result.append(newpath)
			except:
				pass
	return result

# makes splits from random files in folders with numbers
def ffmpegdo() :	
	videos = []

	for folder in folders:
		videos.extend(files(folder, exts))

	num = 0
	filesinsplits = []
	i = 0
	modv = random.choice([True, False])

	if ("horizontal" in flags):
		modv = False
	elif ("vertical" in flags):
		modv = True		
	elif ("both" in flags):
		modv = None		

	while i < count:
		num = num + 1
		file = random.choice(videos)
		with VideoFileClip(file) as clip:
			size = clip.size
			h = size[1]
			w = size[0]
			time = gettime(clip.duration, sec2)
			modvfile = h > w	

			# print(modv, modvfile, "modes")
			# print(file, i, "file")
			# print(time[0], file, w, h)

			pathoforiginal = Path(clip.filename) 
			if time != False and ((modv and modvfile) or (not modv and not modvfile) or (modv == None)):		
				filename = "./splits/cuts/" + str(i) + "-" + str(random.randrange(0, 10000)) + "-" + pathoforiginal.name + "-cut.mp4"			
				if "test" not in flags:
					try:
						vid = ffmpeg.input(file)		
						vid = vid.trim(start = time[0][0], end = time[0][1]).setpts('PTS-STARTPTS')			
						output = ffmpeg.output(vid, filename)
						output.run()
					except:
						pass			
				i = i + 1

# gets audio and combines final clip with audio
def addaudio() :
	with VideoFileClip("./splits/prod/final.mp4") as clip:
		filesofmusic = []
		for folder in musicfolders:
			filesofmusic.extend(files(folder, [".mp3"]))
		file = random.choice(filesofmusic)
		audio_input = ffmpeg.input(file)
		audio_cut = audio_input.audio.filter('atrim', duration=clip.duration)
		audio_output = ffmpeg.output(audio_cut, './splits/prod/sound.wav')
		ffmpeg.run(audio_output)
		video = ffmpeg.input('./splits/prod/final.mp4')
		audio = ffmpeg.input('./splits/prod/sound.wav')
		ffmpeg.concat(video, audio, v=1, a=1).output('./splits/final_' + datetime.now().strftime("%d.%m.%Y_%H:%M:%S") + '.mp4').run()

# concatentes splits to clip
def concatenate():
	vert = ""
	if ("vertical" in flags and "hand" in flags):
		vert = "/vert"
	elif ("horizontal" in flags and "hand" in flags):
		vert = "/gor"
	
	st = "ffmpeg -i \"concat:"
	video = glob.glob("./splits/cuts" + vert + "/*.mp4")
	file_temp = []
	for f in video:
		print(f)
		file = "./splits/temp/temp" + str(video.index(f) + 1) + ".ts"
		os.system("ffmpeg -i " + f + " -c copy -bsf:v h264_mp4toannexb -f mpegts " + file)
		file_temp.append(file)
	print(file_temp)
	random.shuffle(file_temp)
	for f in file_temp:
		st += f
		if file_temp.index(f) != len(file_temp)-1:
			st += "|"
		else:
			st += "\" -c copy -bsf:a aac_adtstoasc ./splits/prod/final.mp4"
	print(st)
	os.system(st)
 
 
print("here options:")
print(flags, "flags")
print(exts, "exts")
print(nums, "nums")

if 'cut' in flags:	
	maketree(['cuts'])
	ffmpegdo()

if 'all' in flags:
	maketree(['cuts', 'prod', 'temp'])
	ffmpegdo()
	clear()
	concatenate()
	addaudio()


if 'i' in flags:	
	maketree(['prod', 'temp'])
	clear()
	concatenate()
	addaudio()

if 'j' in flags:	
	maketree(['prod', 'temp'])
	concatenate()
	addaudio()
	
if 'final' in flags:
	addaudio()
	
