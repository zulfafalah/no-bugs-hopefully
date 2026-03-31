from rest_framework import serializers


class BookSerializer(serializers.Serializer):
    """Serializer for Book objects"""
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255, required=True)
    author = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    published_year = serializers.IntegerField(required=False, allow_null=True)


class BookCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating Book objects"""
    title = serializers.CharField(max_length=255, required=True)
    author = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    published_year = serializers.IntegerField(required=False, allow_null=True)


class BookPartialUpdateSerializer(serializers.Serializer):
    """Serializer for partial update of Book objects (PUT method)"""
    title = serializers.CharField(max_length=255, required=False, help_text="Book title")
    author = serializers.CharField(max_length=255, required=False, help_text="Book author")
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True, help_text="Book description")
    published_year = serializers.IntegerField(required=False, allow_null=True, help_text="Year of publication")


class EchoRequestSerializer(serializers.Serializer):
    """Serializer for echo request"""
    message = serializers.CharField(required=False)


class StandardResponseSerializer(serializers.Serializer):
    """Standard response format"""
    status = serializers.CharField()
    data = serializers.JSONField(required=False)
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
