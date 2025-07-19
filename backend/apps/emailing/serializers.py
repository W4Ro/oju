from rest_framework import serializers

class EmailSenderSerializer(serializers.Serializer):
    subject = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Email subject"
    )
    to = serializers.EmailField(
        required=True,
        help_text="Primary Recipient (must be a focal point)"
    )
    cc = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        default=list,
        help_text="List of recipients in copy (focal points or users)"
    )
    bcc = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        default=list,
        help_text="List of recipients in blind copy (focal points or users)"
    )
    body = serializers.CharField(
        required=True,
        help_text="Message body"
    )
    attachments = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        required=False,
        default=list,
        help_text="List of attachments in format {filename: str, content: base64, content_type: str}"
    )