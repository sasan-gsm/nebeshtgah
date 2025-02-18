from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Get the 'fields' parameter from kwargs
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields:
            # Drop fields not specified in the 'fields' argument
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
