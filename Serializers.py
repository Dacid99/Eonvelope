from rest_framework import serializers

class EMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailModel
        fields = '__all__'


class CorrespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrespondentModel
        fields = '__all__'


class EMailCorrespondentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailCorrespondentsModel
        fields = '__all__'