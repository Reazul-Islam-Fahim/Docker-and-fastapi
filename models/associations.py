from sqlalchemy import Table, Column, Integer, ForeignKey
from database.db import Base

sub_category_features = Table(
    'sub_category_features',
    Base.metadata,
    Column('sub_category_id', Integer, ForeignKey('sub_categories.id'), primary_key=True),
    Column('feature_id', Integer, ForeignKey('product_features.id'), primary_key=True)
)