#from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import Community, Board, Quiz
from .serializers import CommunitySerializer, BoardSerializer, QuizSerializer
from django.shortcuts import get_object_or_404, render, get_list_or_404
from rest_framework import status
from django.conf import settings
import requests, json

from wordcloud import WordCloud
from wordcloud import STOPWORDS
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io, os, matplotlib, PIL

# Create your views here.

PERSONAL_DATA_API_KEY = settings.PERSONAL_DATA_API_KEY

@api_view(['GET'])
def politician_list(request, poly_nm):
    url = 'https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu'
    params = {
        'KEY': PERSONAL_DATA_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100,
        'POLY_NM': poly_nm
    }
    response = requests.get(url, params=params)
    data = response.json()['nwvrqwxyaytdsfvhu'][1]
    
    result = []
    for i in range(params['pSize']):
        if poly_nm == data['row'][i]['POLY_NM']:
            result.append({'POLY_NM': data['row'][i]['POLY_NM'], 'HG_NM': data['row'][i]['HG_NM'], 'ENG_NM': data['row'][i]['ENG_NM'], 'ORIG_NM': data['row'][i]['ORIG_NM'], 'HOMEPAGE': data['row'][i]['HOMEPAGE']})
    
    return Response(result)



class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer

def create(self, request):
    serializer = self.get_serailizer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    #community = serializer.instance

    return Response(serializer.data)



class BoardViewSet(viewsets.ModelViewSet):

    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    @action(detail=True, methods=['GET'])
    def result(self, request, pk, community_id):
        total_count = Board.objects.count()
        option1_count = Board.objects.filter(pick='option1').count()
        option2_count = Board.objects.filter(pick='option2').count()
        option3_count = Board.objects.filter(pick='option3').count()
        
        pick_title = Board.objects.filter(pk=pk).values('pick_title').first()

        option1_percentage = (option1_count / total_count) * 100
        option2_percentage = (option2_count / total_count) * 100
        option3_percentage = (option3_count / total_count) * 100
        
        data = {
            'option1_count': option1_percentage,
            'option2_count': option2_percentage,
            'option3_count': option3_percentage,
            'pick_title': pick_title['pick_title'],
        }

        return Response(data)
    
def generate_wordcloud(request, community_id):
    community = Community.objects.get(pk=community_id)
    comment_messages = Board.objects.filter(community=community)
    
    word_frequencies = {} 
    # Create a WordCloud object
    excluded_words = ['ㅅㅂ', '시발' ,'존나', '개']  

    for message in comment_messages:
        words = message.comment.split()  # 공백을 기준으로 단어 분리
        for word in words:
            if word not in excluded_words:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1

    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'
    wordcloud = WordCloud(
        width=400, height=400, 
        max_font_size=200, 
        background_color='white', 
        font_path=font_path, 
        prefer_horizontal = True,
        collocations=False,
        colormap='binary'
    ).generate_from_frequencies(word_frequencies)

    image_file_path = os.path.join(settings.MEDIA_ROOT, f'wordcloud_{community_id}.png')
    wordcloud.to_file(image_file_path)

    community.wordcloud_image_path = f'wordcloud_{community_id}.png'
    community.save()

    buf = io.BytesIO()
    plt.figure(figsize=(6, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer