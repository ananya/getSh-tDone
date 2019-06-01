import subprocess
import numpy
import re
import math
import os
import argparse

from shutil import rmtree, copyfile
from contextlib import closing
from PIL import Image
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from scipy.io import wavfile
from pytube import YouTube

TEMP = "TEMP"

def GetVolume(s):
    maxvol = float(numpy.max(s))
    minvol = float(numpy.min(s))
    return max(maxvol,-minvol)


def FRameCopy(ip_frame,op_frame):
    source = TEMP+"/old_frame{:06d}".format(ip_frame+1)+".jpg"
    destination = TEMP+"/new_frame{:06d}".format(op_frame+1)+".jpg"
    if not os.path.isfile(source):
        return False
    copyfile(source, destination)
    if op_frame%20 == 19:
        print(str(op_frame+1)+" altered.")
    return True


def videoProcess(frame_rate,sample_rate,silent_threshold,frame_margin,
                    silent_speed,sounded_speed,url,input_file,output_file,frame_quality):
    try:
        print(frame_rate,sample_rate,silent_threshold,frame_margin,silent_speed,sounded_speed,url,input_file,output_file,frame_quality )
        
        New_Speed_silent_and_sounded = [silent_speed, sounded_speed]

        if url:
            name = YouTube(url).streams.first().download()
            renamed = name.replace(' ','_')
            os.rename(name,renamed)
            return renamed

        else:
            Input_Video = input_file


        assert Input_Video != None , "enter input video"
            

        if len(output_file) >= 1:
            Output_Video = output_file

        else:
            dot_position = filename.rfind(".")
            Output_Video = filename[:dot_position]+"NEWVIDEO"+filename[dot_position:]
        
        # print ( Output_Video)
        Audio_fade_envelope_size = 400 
            
            
        try:  
            os.mkdir(TEMP)
        except OSError:  
            assert False, "Directory Already existing"
            

        command = "ffmpeg -i "+Input_Video+" -qscale:v "+str(frame_quality)+" "+TEMP+"/old_frame%06d.jpg -hide_banner"
        subprocess.call(command, shell=True)
        
        command = "ffmpeg -i "+Input_Video+" -ab 160k -ac 2 -ar "+str(sample_rate)+" -vn "+TEMP+"/audio.wav"

        subprocess.call(command, shell=True)



        sampleRate, audioData = wavfile.read(TEMP+"/audio.wav")
        audioSampleCount = audioData.shape[0]
        maxAudioVolume = GetVolume(audioData)
        

        # print("  please  ")
        samplesPerFrame = 1470

        audioFrameCount = int(math.ceil(audioSampleCount/samplesPerFrame))

        hasLoudAudio = numpy.zeros((audioFrameCount))

        for i in range(audioFrameCount):
            start = int(i*samplesPerFrame)
            end = min(int((i+1)*samplesPerFrame),audioSampleCount)
            audiochunks = audioData[start:end]
            maxchunksVolume = float(GetVolume(audiochunks))/maxAudioVolume
            if maxchunksVolume >= silent_threshold:
                hasLoudAudio[i] = 1

        chunks = [[0,0,0]]
        shouldIncludeFrame = numpy.zeros((audioFrameCount))
        for i in range(audioFrameCount):
            start = int(max(0,i-frame_margin))
            end = int(min(audioFrameCount,i+1+frame_margin))
            shouldIncludeFrame[i] = numpy.max(hasLoudAudio[start:end])
            if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i-1]): 
                chunks.append([chunks[-1][1],i,shouldIncludeFrame[i-1]])

        chunks.append([chunks[-1][1],audioFrameCount,shouldIncludeFrame[i-1]])
        chunks = chunks[1:]

        outputAudioData = numpy.zeros((0,audioData.shape[1]))
        outputPointer = 0

        lastExistingFrame = None
        for chunk in chunks:
            audioChunk = audioData[int(chunk[0]*samplesPerFrame):int(chunk[1]*samplesPerFrame)]
            
            sFile = TEMP+"/tempStart.wav"
            eFile = TEMP+"/tempEnd.wav"
            wavfile.write(sFile,sample_rate,audioChunk)
            with WavReader(sFile) as reader:
                with WavWriter(eFile, reader.channels, reader.samplerate) as writer:
                    tsm = phasevocoder(reader.channels, speed=New_Speed_silent_and_sounded[int(chunk[2])])
                    tsm.run(reader, writer)
            _, alteredAudioData = wavfile.read(eFile)
            leng = alteredAudioData.shape[0]
            endPointer = outputPointer+leng
            outputAudioData = numpy.concatenate((outputAudioData,alteredAudioData/maxAudioVolume))


            if leng < Audio_fade_envelope_size:
                outputAudioData[outputPointer:endPointer] = 0 
            else:
                premask = numpy.arange(Audio_fade_envelope_size)/Audio_fade_envelope_size
                mask = numpy.repeat(premask[:, numpy.newaxis],2,axis=1) 
                outputAudioData[outputPointer:outputPointer+Audio_fade_envelope_size] *= mask
                outputAudioData[endPointer-Audio_fade_envelope_size:endPointer] *= 1-mask

            startOutputFrame = int(math.ceil(outputPointer/samplesPerFrame))
            endOutputFrame = int(math.ceil(endPointer/samplesPerFrame))
            for op_frame in range(startOutputFrame, endOutputFrame):
                ip_frame = int(chunk[0]+New_Speed_silent_and_sounded[int(chunk[2])]*(op_frame-startOutputFrame))
                didItWork = FRameCopy(ip_frame,op_frame)
                if didItWork:
                    lastExistingFrame = ip_frame
                else:
                    FRameCopy(lastExistingFrame,op_frame)

            outputPointer = endPointer

        wavfile.write(TEMP+"/audioNew.wav",sample_rate,outputAudioData)

     
        command = "ffmpeg -framerate "+str(frame_rate)+" -i "+TEMP+"/new_frame%06d.jpg -i "+TEMP+"/audioNew.wav -strict -2 "+Output_Video
        subprocess.call(command, shell=True)


        try:  
            rmtree(TEMP,ignore_errors=False)
        except OSError:  
            print ("Delete failed")

        
        
            return "done"              #not sure abt it
    except:
        return " nothing"
