from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import ast
from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
from PIL import Image

import sys
import os
sys.path.append(os.pardir)
from Smallfunctions import gpt
from pathlib import Path
from dotenv import load_dotenv



# Create your views here.
class UserView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'
    # return htmlfile from get request
    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        form = UploadFileForm()
        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['past_info'] = []
        context['form'] = form

        return context

    # upadate page form user text
    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = UploadFileForm(request.POST, request.FILES)
        # file_obj = request.FILES['file']
        print(request.POST)
        new_info = str(request.POST['text'])
        past_info = ast.literal_eval(request.POST['past_info'])
        gpt_ = gpt()
        if 'file' in request.FILES:
            image = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            print(filename)
            path_from_this_file = "./media/" + filename
            imageResize(self, path_from_this_file, path_from_this_file)
            path = "../../../media/" + filename
            value = {"role":"user","type":"image","path":path}
            past_info.append(value)
              # if user send a text and image
            res = gpt_.sendMessage(prompt=new_info, image_path=path_from_this_file)
        else :# if user send only a text
            res = gpt_.sendMessage(prompt=new_info)
            # pass
        value = {"role":"user","type":"text","text":new_info}
        past_info.append(value)

        ## -------here is request to GPT API ----------
        # res = "This text comes from GPT"
        value = {"role":"gpt","type":"text","text":res}
        ## --------------------------------------------
        past_info.append(value)
        context = {
            'user': user,
            'past_info':past_info,
            'form':form
        }

        return self.render_to_response(context)
        # return render(request, 'error.html')



def imageResize(self, input_image_path, output_image_path):
    """
    Resizes the input image so that the longest side is 512 pixels while maintaining the aspect ratio.
        
    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the resized image.
    """
    with Image.open(input_image_path) as img:
        max_size = 512
        width, height = img.size
        if width > height:
            new_width = max_size
            new_height = int((height / width) * max_size)
        else:
            new_height = max_size
            new_width = int((width / height) * max_size)
            
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(output_image_path)