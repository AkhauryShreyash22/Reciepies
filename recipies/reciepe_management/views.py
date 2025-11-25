from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema

from authentication.auth import CookieJWTAuthentication
from .models import Reciepe, ReciepeImagess, ReciepeRating
from .serializers import (
    ReciepeCreateSerializer,
    ReciepeCreateResponseSerializer,
    ReciepeResponseSerializer,
    ReciepeImagesUploadSerializer,
    ReciepeImagesUploadResponseSerializer,
    ReciepeUpdateSerializer,
    ReciepeRatingCreateSerializer,
    ReciepeRatingListResponseSerializer,
    ReciepeRatingResponseSerializer,
    ReciepeRatingUpdateSerializer
)
from .permissions import IsSeller, IsCustomer
from drf_spectacular.utils import OpenApiParameter


@method_decorator(csrf_exempt, name='dispatch')
class CreateReciepeAPI(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication]
    serializer_class = ReciepeCreateSerializer

    @extend_schema(
        request=ReciepeCreateSerializer,
        responses={201: ReciepeCreateResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reciepe = serializer.save()

        return Response({
            "message": "Reciepe created successfully",
            "reciepe": ReciepeResponseSerializer(reciepe).data
        }, status=status.HTTP_201_CREATED)




@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "reciepe_id": {"type": "integer", "example": 1},
                "images": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"}
                }
            },
            "required": ["reciepe_id", "images"]
        }
    },
    responses={201: ReciepeImagesUploadResponseSerializer},
)
class UploadReciepeImagessAPI(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ReciepeImagesUploadSerializer

    def post(self, request, *args, **kwargs):

        # Validate reciepe_id via serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reciepe_id = serializer.validated_data["reciepe_id"]

        images = request.FILES.getlist("images")
        if not images:
            return Response({"images": ["Upload at least one image"]}, status=400)

        reciepe = Reciepe.objects.get(id=reciepe_id)

        if reciepe.seller != request.user:
            return Response({"error": "Not allowed"}, status=403)

        for img in images:
            ReciepeImagess.objects.create(reciepe=reciepe, image=img)

        return Response({
            "message": "Images uploaded successfully",
            "reciepe": ReciepeResponseSerializer(reciepe).data
        }, status=201)

@extend_schema(
    request=ReciepeUpdateSerializer,
    responses={200: ReciepeResponseSerializer}
)
class UpdateReciepeAPI(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication]
    serializer_class = ReciepeUpdateSerializer

    def put(self, request, reciepe_id, *args, **kwargs):
        try:
            reciepe = Reciepe.objects.get(id=reciepe_id)
        except Reciepe.DoesNotExist:
            return Response({"error": "Reciepe not found"}, status=404)

        if reciepe.seller != request.user:
            return Response({"error": "Not allowed"}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = serializer.update(reciepe, serializer.validated_data)

        return Response(ReciepeResponseSerializer(updated).data, status=200)

@extend_schema(
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class DeleteReciepeAPI(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication]

    def delete(self, request, reciepe_id, *args, **kwargs):
        try:
            reciepe = Reciepe.objects.get(id=reciepe_id)
        except Reciepe.DoesNotExist:
            return Response({"error": "Reciepe not found"}, status=404)

        if reciepe.seller != request.user:
            return Response({"error": "Not allowed"}, status=403)

        reciepe.delete()

        return Response({"message": "Reciepe deleted successfully"}, status=200)


@extend_schema(
    responses={200: ReciepeResponseSerializer(many=True)},
)
class ListReciepeAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication]
    serializer_class = ReciepeResponseSerializer

    def get_queryset(self):
        queryset = Reciepe.objects.all().order_by("-id")

        reciepe_id = self.request.query_params.get("id")  

        if reciepe_id:
            return queryset.filter(id=reciepe_id)

        return queryset

@extend_schema(
    request=ReciepeRatingCreateSerializer,
    responses={201: {"message": "Rating added successfully"}}
)
class AddReciepeRatingAPI(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = ReciepeRatingCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        reciepe_id = serializer.validated_data["reciepe_id"]
        reciepe = Reciepe.objects.get(id=reciepe_id)

        if reciepe.seller == request.user:
            return Response(
                {"error": "Sellers cannot rate their own recipe."},
                status=403
            )

        serializer.save()

        return Response({"message": "Rating added successfully"}, status=201)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="reciepe_id",
            type=int,
            location=OpenApiParameter.QUERY,
            required=True,
            description="ID of the recipe"
        )
    ],
    responses={200: ReciepeRatingListResponseSerializer},
)
class ListReciepeRatingAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reciepe_id = request.query_params.get("reciepe_id")

        if not reciepe_id:
            return Response({"reciepe_id": "This field is required"}, status=400)

        if not Reciepe.objects.filter(id=reciepe_id).exists():
            return Response({"error": "Reciepe not found"}, status=404)

        ratings = ReciepeRating.objects.filter(reciepe_id=reciepe_id)

        if ratings.exists():
            avg = sum(r.rating for r in ratings) / ratings.count()
        else:
            avg = 0

        data = {
            "reciepe_id": int(reciepe_id),
            "average_rating": round(avg, 1),
            "ratings": ReciepeRatingResponseSerializer(ratings, many=True).data
        }

        return Response(data, status=200)
    
@extend_schema(
    request=ReciepeRatingUpdateSerializer,
    responses={200: {"message": "Rating updated successfully"}},
)
class UpdateReciepeRatingAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReciepeRatingUpdateSerializer

    def put(self, request, rating_id, *args, **kwargs):
        try:
            rating_obj = ReciepeRating.objects.get(id=rating_id)
        except ReciepeRating.DoesNotExist:
            return Response({"error": "Rating not found"}, status=404)

        if rating_obj.customer != request.user:
            return Response({"error": "Not allowed"}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating_obj.rating = serializer.validated_data["rating"]
        rating_obj.description = serializer.validated_data.get("description", rating_obj.description)
        rating_obj.save()

        return Response({"message": "Rating updated successfully"}, status=200)
