from rest_framework import serializers


class SessionActionType(serializers.Serializer):
    ALLOWED_ACTIONS = (
        'login',
        'logout',
        'buy',
        'review',
        'shopping-cart',
    )
    action = serializers.ChoiceField(choices=ALLOWED_ACTIONS, required=True)


class SessionResolutionSerializer(serializers.Serializer):
    width = serializers.IntegerField(required=True)
    height = serializers.IntegerField(required=True)


class SessionActionSerializer(serializers.Serializer):
    ip = serializers.IPAddressField(required=True)
    resolution = SessionResolutionSerializer(required=True)


class SessionLocationDetails(serializers.Serializer):
    lon = serializers.FloatField(required=True)
    lat = serializers.FloatField(required=True)
    city = serializers.CharField(required=True)
    region = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    countryCode = serializers.CharField(required=True)


class SessionActionDetailsSerializer(serializers.Serializer):
    action = serializers.CharField(required=True)
    info = SessionActionSerializer(required=True)
    location = SessionLocationDetails(required=True)
    action_date = serializers.DateTimeField(required=True)
