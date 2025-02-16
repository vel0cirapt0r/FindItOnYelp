from backend.models.database import database_proxy
from peewee import Model, CharField, FloatField, IntegerField, BooleanField, TextField, ForeignKeyField, DateTimeField
from datetime import datetime
from backend.utils.utils import format_datetime


class BaseModel(Model):
    class Meta:
        database = database_proxy

class SearchTerm(BaseModel):
    id = IntegerField(primary_key=True)  # Auto-incrementing ID
    term = CharField(index=True)  # "pizza", "gym", etc.
    location = CharField(index=True)  # "New York", "Los Angeles"
    sort_by = CharField(default="best_match")  # "best_match", "rating", "review_count", "distance"
    limit = IntegerField(default=10)  # Number of results requested per Yelp API call
    max_results = IntegerField(default=50)  # Max results to fetch using pagination
    created_at = DateTimeField(default=datetime.now())  # Track when the search happened

    class Meta:
        indexes = (
            (("term", "location", "sort_by", "limit", "max_results"), True),  # Unique constraint
        )

    def to_dict(self):
        """Convert SearchTerm model instance to dictionary"""
        return {
            "id": self.id,
            "term": self.term,
            "location": self.location,
            "sort_by": self.sort_by,
            "limit": self.limit,
            "max_results": self.max_results,
            "created_at": format_datetime(self.created_at)  # Ensure datetime is JSON serializable
        }

class Business(BaseModel):
    id = CharField(primary_key=True)
    alias = CharField(unique=True, index=True)
    name = CharField()
    image_url = TextField(null=True)
    is_closed = BooleanField(default=False)
    url = TextField()
    review_count = IntegerField()
    rating = FloatField()
    price = CharField(null=True)
    phone = CharField(null=True)
    display_phone = CharField(null=True)
    distance = FloatField()

    # Explicitly define related fields to prevent pycharm warnings
    location = None  # Will be set by ForeignKeyField
    categories = None
    business_hours = None
    attributes = None

    def to_dict(self):
        """Converts the model instance to a dictionary for API responses."""
        return {
            "id": self.id,
            "alias": self.alias,
            "name": self.name,
            "image_url": self.image_url,
            "is_closed": self.is_closed,
            "url": self.url,
            "review_count": self.review_count,
            "rating": self.rating,
            "price": self.price,
            "phone": self.phone,
            "display_phone": self.display_phone,
            "distance": self.distance,
            "location": self.location.to_dict() if hasattr(self, "location") else None,
            "categories": [c.category.category_name for c in self.categories],
            "business_hours": [h.to_dict() for h in self.business_hours],
            "attributes": {a.key: a.value for a in self.attributes}
        }

class BusinessSearch(BaseModel):
    search_term = ForeignKeyField(SearchTerm, backref="businesses", on_delete="CASCADE")
    business = ForeignKeyField(Business, backref="searches", on_delete="CASCADE")
    searched_at = DateTimeField(default=datetime.now())

class Location(BaseModel):
    business = ForeignKeyField(Business, backref="location", unique=True, on_delete="CASCADE")
    address1 = CharField()
    address2 = CharField(null=True)
    address3 = CharField(null=True)
    city = CharField(index=True)
    zip_code = CharField()
    state = CharField()
    country = CharField()
    latitude = FloatField()
    longitude = FloatField()

    def to_dict(self):
        """Convert location model instance to dictionary"""
        return {
            "address1": self.address1,
            "address2": self.address2,
            "address3": self.address3,
            "city": self.city,
            "zip_code": self.zip_code,
            "state": self.state,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

class Category(BaseModel):
    category_name = CharField(unique=True, index=True)

class BusinessCategory(BaseModel):
    business = ForeignKeyField(Business, backref="categories", on_delete="CASCADE")
    category = ForeignKeyField(Category, backref="businesses", on_delete="CASCADE")

class BusinessHours(BaseModel):
    business = ForeignKeyField(Business, backref="business_hours", on_delete="CASCADE")
    day = IntegerField()  # 0 = Monday, 6 = Sunday
    start_time = CharField()  # "0900"
    end_time = CharField()  # "2000"
    is_overnight = BooleanField(default=False)

    def to_dict(self):
        return {
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_overnight": self.is_overnight
        }

class Attribute(BaseModel):
    business = ForeignKeyField(Business, backref="attributes", on_delete="CASCADE")
    key = CharField()
    value = TextField()
