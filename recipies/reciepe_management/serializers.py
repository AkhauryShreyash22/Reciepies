from rest_framework import serializers
from .models import Reciepe, ReciepeRating
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample


class ReciepeCreateSerializer(serializers.Serializer):
    reciepe_name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        seller = self.context["request"].user
        reciepe = Reciepe.objects.create(
            seller=seller,
            reciepe_name=validated_data["reciepe_name"],
            description=validated_data.get("description", "")
        )
        return reciepe


class ReciepeImagesResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    image = serializers.ImageField()


class ReciepeResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    reciepe_name = serializers.CharField()
    description = serializers.CharField()
    images = ReciepeImagesResponseSerializer(many=True)


class ReciepeCreateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    reciepe = ReciepeResponseSerializer()



class ReciepeImagesUploadSerializer(serializers.Serializer):
    reciepe_id = serializers.IntegerField()

    def validate_reciepe_id(self, value):
        if not Reciepe.objects.filter(id=value).exists():
            raise serializers.ValidationError("Reciepe not found.")
        return value


class ReciepeImagesUploadResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    reciepe = ReciepeResponseSerializer()


class ReciepeUpdateSerializer(serializers.Serializer):
    reciepe_name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        instance.reciepe_name = validated_data.get("reciepe_name", instance.reciepe_name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()
        return instance


class ReciepeRatingCreateSerializer(serializers.Serializer):
    reciepe_id = serializers.IntegerField()
    rating = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_reciepe_id(self, value):
        if not Reciepe.objects.filter(id=value).exists():
            raise serializers.ValidationError("Reciepe not found.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        reciepe_id = attrs["reciepe_id"]

        if ReciepeRating.objects.filter(customer=user, reciepe_id=reciepe_id).exists():
            raise serializers.ValidationError("You already rated this reciepe.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        reciepe = Reciepe.objects.get(id=validated_data["reciepe_id"])

        rating = ReciepeRating.objects.create(
            reciepe=reciepe,
            customer=user,
            rating=validated_data["rating"],
            description=validated_data.get("description", "")
        )
        return rating


class ReciepeRatingResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer = serializers.CharField(source="customer.username")
    rating = serializers.IntegerField()
    description = serializers.CharField()


class ReciepeRatingListResponseSerializer(serializers.Serializer):
    reciepe_id = serializers.IntegerField()
    average_rating = serializers.FloatField()
    ratings = ReciepeRatingResponseSerializer(many=True)

class ReciepeRatingUpdateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value