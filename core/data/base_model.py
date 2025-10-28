from datetime import datetime

class BaseModel:
    """Baseclass for all data models"""

    def __init__(self, name="", description=""):
        self.id = self._make_id()           # Unique ID for each object
        self.created = datetime.now()
        self.name = name
        self.description = description
        self.files = []
        self.notes = ""
        self.extra_fields = {}
        self.style = {}

    def _make_id(self):
        """unique ID"""
        return str(datetime.now().timestamp())

    def to_dict(self):
        """make dictionary"""
        return {
            'id': self.id,
            'created': self.created.isoformat(),
            'name': self.name,
            'description': self.description,
            'files': self.files,
            'notes': self.notes,
            'extra_fields': self.extra_fields,
            'style': self.style,
            'type': self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data):
        """Create objects"""
        obj = cls()
        obj.id = data.get('id', obj.id)
        obj.name = data.get('name', '')
        obj.description = data.get('description', '')
        obj.files = data.get('files', [])
        obj.notes = data.get('notes', '')
        obj.extra_fields = data.get('extra_fields', {})
        obj.style = data.get('style', {})

        created_str = data.get('created')
        if created_str:
            try:
                obj.created = datetime.fromisoformat(created_str)
            except ValueError:
                obj.created = datetime.now()

        return obj

    @property
    def image_path(self):
        """image path"""
        return self.files[0] if self.files else ""

    @image_path.setter
    def image_path(self, path):
        """Set path"""
        if path:
            self.files = [path]
        else:
            self.files = []

    def get_field(self, field_name):
        """Get value"""
        field = self.extra_fields.get(field_name)
        return field['value'] if field else None

    def __str__(self):
        """Return the object info as a readable string"""
        return f"{self.name} ({self.id})"