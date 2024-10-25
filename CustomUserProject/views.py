import os
import shutil
import threading
import subprocess
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse,JsonResponse
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from .utils import subscription_renewal_due,subscription_plan_retrieve
# Clean temporary and final output folders before new uploads
def clean_folders(userid,filename):
    upload_folder=os.path.join(settings.UPLOAD_FOLDER,userid)
    shutil.rmtree(upload_folder, ignore_errors=True)
    os.remove(os.path.join(settings.BEFORE_AUDIO_OUTPUT_FOLDER,filename))
    os.remove(os.path.join(settings.BEFORE_AUDIO_OUTPUT_FOLDER,"watermarked"+filename))
    os.remove(os.path.join(settings.FINAL_OUTPUT_FOLDER,filename))
    os.remove(os.path.join(settings.FINAL_OUTPUT_FOLDER,"watermarked"+filename))
@login_required
def loading(request):
    return render(request,'loading.html')

@login_required
@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
            video = request.FILES['videoFile']
            transcription = request.FILES['transcribedFile']
            apiKey=request.POST.get("apiKey")
            voiceID=request.POST.get("voiceID")
            fontFile=request.FILES['fontFile']
            fontSize=request.POST.get("fontSize")
            textColor=request.POST.get("textColor")
            bgColor=request.POST.get("bgColor")
            UPLOAD_FOLDER=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id))
            a=os.makedirs(os.path.join(settings.UPLOAD_FOLDER,str(request.user.id)), exist_ok=True)
            print("path" ,UPLOAD_FOLDER)
            fs = FileSystemStorage(location=UPLOAD_FOLDER)
            video_path = fs.save(video.name, video)
            transcription_path = fs.save(transcription.name, transcription)
            fontFile_path = fs.save(fontFile.name, fontFile)
            # Save the transcription as original_transcription.txt

            original_transcription_path = os.path.join(UPLOAD_FOLDER, 'original_transcription.txt')
            shutil.copy(os.path.join(UPLOAD_FOLDER, transcription.name), original_transcription_path)

            # Save session data
            session_data = {
                "video_name":video.name,
                "transcription_name":transcription.name,
                "video_path": os.path.join(UPLOAD_FOLDER, video.name),
                "font_path":os.path.join(UPLOAD_FOLDER, fontFile.name),
                "elevenlabs":apiKey,
                "voice_id":voiceID,
                "fontSize" : fontSize,
                "textColor": textColor,
                "bgColor"  : bgColor,
            }
            with open(os.path.join(UPLOAD_FOLDER, 'session_data.json'), 'w') as f:
                json.dump(session_data, f)

            return redirect(reverse('loadingforFileUpload') + f'?video_path={video.name}&transcription_path={transcription.name}')
    
    return HttpResponse("File upload failed.")
@login_required
@csrf_exempt
def edit_slides(request):
    print(request)
    if request.method == 'GET':
        
        UPLOAD_FOLDER=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id))
        with open(os.path.join(UPLOAD_FOLDER, 'session_data.json'), 'r') as f:
                session_data=json.loads(f.read())
        video_path = session_data['video_name']
        transcription_path = session_data['transcription_name']
        transcription_content = []
        with open(os.path.join(UPLOAD_FOLDER, transcription_path), 'r') as file:
            transcription_content = file.readlines()
        return render(request, 'create-lead.html', {
            'transcription_content': [i.strip() for i in transcription_content],
            'video_path': video_path,
            'transcription_path': transcription_path,
            "user":request.user
        })

    elif request.method == 'POST':
        UPLOAD_FOLDER=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id))
        with open(os.path.join(UPLOAD_FOLDER, 'session_data.json'), 'r') as f:
            session_data=json.loads(f.read())
       
        video_path = request.POST['video_path']
        transcription_path = request.POST['transcription_path']
        slide_texts = request.POST.getlist('slide_text[]')
        voice_id = session_data['voice_id']
        elevenlabs = session_data['elevenlabs']
        fontSize=session_data["fontSize"]
        textColor=session_data["textColor"]
        bgColor=session_data["bgColor"]
        font_path=session_data["font_path"]
        original_transcription_path = os.path.join(UPLOAD_FOLDER, transcription_path)
        with open(original_transcription_path, 'r') as f:
            original_transcription = f.readlines()

        manual_script_path = os.path.join(UPLOAD_FOLDER, 'manual_script.txt')
        manually_added_slides = [line for line in slide_texts if line.strip() not in [orig.strip() for orig in original_transcription]]
        with open(manual_script_path, 'w') as f:
            f.writelines("\n".join(manually_added_slides))
        updated_transcription = [line for line in original_transcription if line.strip() in slide_texts]
        updated_transcription_path = os.path.join(UPLOAD_FOLDER, 'updated_original_script.txt')
        with open(updated_transcription_path, 'w') as f:
            f.writelines(updated_transcription)

        slide_texts_path = os.path.join(UPLOAD_FOLDER, 'slide_text.txt')
        with open(slide_texts_path, 'w') as f:
            f.writelines(slide_texts)

        slide_images = request.FILES.getlist('slide_image[]')
        slide_images_paths = []
        for idx, image in enumerate(slide_images):
            if image.name != "":
                extension = "png" if image.content_type.startswith("image/") else "mp4"
                image_path = os.path.join(UPLOAD_FOLDER, f'slide_image_{idx}.{extension}')
                fs = FileSystemStorage(location=UPLOAD_FOLDER)
                fs.save(f'slide_image_{idx}.{extension}', image)
                slide_images_paths.append(image_path)

        session_data = {
            "original_transcription_path": original_transcription_path,
            "manual_script_path": manual_script_path,
            "updated_original_script_path": updated_transcription_path,
            "slide_images_paths": slide_images_paths,
            "voice_id": voice_id,
            "video_path": video_path,
            "elevenlabs": elevenlabs,
            "video_name":video_path,
            "transcription_name":transcription_path,
        }                
        
     
        session_data["font_path"]=font_path
        session_data["fontSize"] = fontSize
        session_data["textColor"]= textColor
        session_data["bgColor"]  = bgColor
        session_data["video_output_final_name"]=os.urandom(16).hex()+".mp4"
        import time 
        time.sleep(1)
        with open(os.path.join(UPLOAD_FOLDER, 'session_data.json'), 'w') as f:
            json.dump(session_data, f)

        threading.Thread(target=process_video, args=(session_data,str(request.user.id))).start()
        return redirect(reverse('loading'))

def process_video(session_data,userid):
    try:
        cmd = [
            "python3.10",
            "script.py",
            session_data["manual_script_path"],
            session_data["voice_id"],
            session_data["video_path"],
            session_data["elevenlabs"],
            userid,
        ]
        process = subprocess.Popen(cmd)
        process.wait()

    except Exception as e:
        print(f"Error during video processing: {e}")
@login_required
def download(request):
    UPLOAD_FOLDER=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id))
    try:
        with open(os.path.join(UPLOAD_FOLDER, 'audio_session.json'), 'r') as f:
            session_data=json.loads(f.read())
    except:
        return redirect(reverse("submitSubtitle"),context={"user":request.user})

    file_path = session_data["video_output_final_name"]
    print(file_path)
    file=reverse('download_file',args=[file_path])
    print(file)
    context={
        "video_path":"watermarked"+file_path,
        "video_href":file,
        "user":request.user
    }
    return render(request,"Download.html",context=context)

@login_required
def download_file(request, filename):

    file_path = os.path.join(settings.FINAL_OUTPUT_FOLDER, filename)
    file=open(file_path, 'rb')
    user=request.user
    if user.coins>0:
        user.coins=user.coins-1

        user.save()
        clean_folders(str(request.user.id),filename)
        return FileResponse(file, as_attachment=True)
    else:
        clean_folders(str(request.user.id),filename)
        return redirect("#pricing",context={"user":request.user})


@login_required
def submitSubtitle(request):
    subscription_renewal_due(request.user)
    return render(request,"submitSubtitle.html",{"user":request.user})

def readtime(i):
    return int(i.split(":")[0])*60+int(i.split(":")[1])


@csrf_exempt
def music(request):
    if request.method=="GET":
        UPLOAD_FOLDER=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id))
  
        with open(os.path.join(UPLOAD_FOLDER, 'session_data.json'), 'r') as f:
            session_data=json.loads(f.read())
        file_marked="watermarked"+session_data["video_output_final_name"]
        context={
            "video_path":file_marked,
            "user":request.user
        }
        return render(request,'music.html',context=context)
    elif request.method=="POST":
        UPLOAD_FOLDER=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id))
        with open(os.path.join(UPLOAD_FOLDER, 'session_data.json'), 'r') as f:
            session_data=json.loads(f.read())
        with open(os.path.join(UPLOAD_FOLDER, 'editing.json'), 'r+') as f:
            editing_checker=json.loads(f.read())
            editing_checker["status"]=False
            f.write(json.dumps(editing_checker))

            video_path=os.path.join(settings.BEFORE_AUDIO_OUTPUT_FOLDER, session_data["video_output_final_name"])
            print(video_path)
            outputpath=os.path.join("./static","final")
            audio_paths=[]
            for audio in request.FILES.getlist('mp3[]'):
                fs = FileSystemStorage(location=UPLOAD_FOLDER)
                audio_path = fs.save(audio.name, audio)
                audio_paths.append(os.path.join(UPLOAD_FOLDER, audio_path))
            backgroud_volume=[int(i)/100 for i in request.POST.getlist("volume[]")]
            start_audio=[readtime(i) for i in request.POST.getlist("starts[]")]
            duration=[readtime(i)-j for i,j in zip(request.POST.getlist("ends[]"),start_audio)]
            video_output_final_name=session_data["video_output_final_name"]
            audio_session={
                "backgroud_volume":backgroud_volume,
                "start_audio":start_audio,
                "duration":duration,
                "audio_paths":audio_paths,
                "video_output_final_name":video_output_final_name
            }

            with open(os.path.join(UPLOAD_FOLDER, 'audio_session.json'), 'w') as f:
                    f.write(json.dumps(audio_session))
            with open(os.path.join(UPLOAD_FOLDER, 'editing.json'), 'w') as f:
                    f.write(json.dumps({"status":False}))
    
            threading.Thread(target=process_audio, args=(video_path,os.path.join(UPLOAD_FOLDER, 'audio_session.json'),outputpath,UPLOAD_FOLDER)).start()
            return redirect(reverse("loadingMusic"),context={"number_of_Music":str(len(audio_paths))})
        


@login_required
def loadingMusic(request):
    return render(request,"LoadingMusic.html",context={"user":request.user})





@login_required
def loadingforFileUpload(request):
    return render(request,"loadingforFileUpload.html",context={"user":request.user})


@login_required
def checkEditing(request):
    editingchecker=os.path.join(settings.UPLOAD_FOLDER,str(request.user.id),"editing.json")
    try:
        video_edited_checker=json.loads(open(editingchecker,"r").read())
    except:
        video_edited_checker={"status":False}

    return JsonResponse(video_edited_checker) 


def process_audio(video_path,audio_path,outputpath,UPLOAD_FOLDER):

    try:
        cmd = [
            "python3.10",
            "music.py",
            video_path,
            audio_path,
            outputpath,
            UPLOAD_FOLDER,
        ]
        process = subprocess.Popen(cmd)
        process.wait()

    except Exception as e:
        print(f"Error during video processing: {e}")

def manage_subscription(request):
    user=request.user
    plan=subscription_plan_retrieve(user)
    bar_fill_value=0
    print(plan)
    if plan!=[0,"Free Trial",0]:
        bar_fill_value=int(user.coins*100/plan[0])
        if bar_fill_value>100:
            bar_fill_value=100
        bar_fill_value=100-bar_fill_value
        print(bar_fill_value)

    return render(request,"ManageSubscription.html",context={"user":request.user,"barvalue":bar_fill_value,"maxcoins":plan[0],"User_plan":plan[1],"daysleft":plan[2]})
