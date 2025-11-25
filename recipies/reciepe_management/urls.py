from django.urls import path
from .views import CreateReciepeAPI, UploadReciepeImagessAPI, UpdateReciepeAPI, DeleteReciepeAPI, ListReciepeAPI, AddReciepeRatingAPI, ListReciepeRatingAPI, UpdateReciepeRatingAPI

urlpatterns = [
    path('create/', CreateReciepeAPI.as_view(), name='create'),
    path('upload/', UploadReciepeImagessAPI.as_view(), name='upload'),
    path("update/<int:reciepe_id>/", UpdateReciepeAPI.as_view()),
    path("delete/<int:reciepe_id>/", DeleteReciepeAPI.as_view()),
    path("list/", ListReciepeAPI.as_view(), name="list-reciepe"),
    path("rating_add/", AddReciepeRatingAPI.as_view()),
    path("rating_list/", ListReciepeRatingAPI.as_view()),
    path("rating_update/<int:rating_id>/", UpdateReciepeRatingAPI.as_view()),
]