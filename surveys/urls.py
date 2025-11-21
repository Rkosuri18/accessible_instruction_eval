from django.urls import path
from . import views

app_name = "surveys"

urlpatterns = [
    path("", views.home, name="home"),
    path("start", views.start, name="start"),                     
    path("evaluate/<int:step>/", views.evaluate, name="evaluate"),
    path("done", views.done, name="done"),                        
    path("thanks/", views.thanks, name="thanks"),
    path("doc/<int:pk>/inline/", views.inline_pdf, name="inline_pdf"), 
    path("stream/video/<str:filename>", views.stream_video, name="stream_video"),
    path("api/save/<int:session_id>/<int:question_id>/", views.save_partial_answer, name="save_partial_answer"),               
]

