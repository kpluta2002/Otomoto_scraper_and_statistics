from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, REAL, Sequence, SmallInteger, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = 'car'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'make', name='car_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    make: Mapped[str] = mapped_column(Text, primary_key=True)
    model: Mapped[Optional[str]] = mapped_column(Text)
    variant: Mapped[Optional[str]] = mapped_column(Text)
    engine_cc: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    power_hp: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class CarP0(Base):
    __tablename__ = 'car_p0'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'make', name='car_p0_pkey'),
        Index('car_p0_created_at_idx', 'created_at'),
        Index('car_p0_engine_cc_idx', 'engine_cc'),
        Index('car_p0_model_idx', 'model'),
        Index('car_p0_power_hp_idx', 'power_hp'),
        Index('car_p0_updated_at_idx', 'updated_at'),
        Index('car_p0_variant_idx', 'variant')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('car_id_seq'), primary_key=True)
    make: Mapped[str] = mapped_column(Text, primary_key=True)
    model: Mapped[Optional[str]] = mapped_column(Text)
    variant: Mapped[Optional[str]] = mapped_column(Text)
    engine_cc: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    power_hp: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class CarP1(Base):
    __tablename__ = 'car_p1'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'make', name='car_p1_pkey'),
        Index('car_p1_created_at_idx', 'created_at'),
        Index('car_p1_engine_cc_idx', 'engine_cc'),
        Index('car_p1_model_idx', 'model'),
        Index('car_p1_power_hp_idx', 'power_hp'),
        Index('car_p1_updated_at_idx', 'updated_at'),
        Index('car_p1_variant_idx', 'variant')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('car_id_seq'), primary_key=True)
    make: Mapped[str] = mapped_column(Text, primary_key=True)
    model: Mapped[Optional[str]] = mapped_column(Text)
    variant: Mapped[Optional[str]] = mapped_column(Text)
    engine_cc: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    power_hp: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class CarP2(Base):
    __tablename__ = 'car_p2'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'make', name='car_p2_pkey'),
        Index('car_p2_created_at_idx', 'created_at'),
        Index('car_p2_engine_cc_idx', 'engine_cc'),
        Index('car_p2_model_idx', 'model'),
        Index('car_p2_power_hp_idx', 'power_hp'),
        Index('car_p2_updated_at_idx', 'updated_at'),
        Index('car_p2_variant_idx', 'variant')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('car_id_seq'), primary_key=True)
    make: Mapped[str] = mapped_column(Text, primary_key=True)
    model: Mapped[Optional[str]] = mapped_column(Text)
    variant: Mapped[Optional[str]] = mapped_column(Text)
    engine_cc: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    power_hp: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class CarP3(Base):
    __tablename__ = 'car_p3'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'make', name='car_p3_pkey'),
        Index('car_p3_created_at_idx', 'created_at'),
        Index('car_p3_engine_cc_idx', 'engine_cc'),
        Index('car_p3_model_idx', 'model'),
        Index('car_p3_power_hp_idx', 'power_hp'),
        Index('car_p3_updated_at_idx', 'updated_at'),
        Index('car_p3_variant_idx', 'variant')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('car_id_seq'), primary_key=True)
    make: Mapped[str] = mapped_column(Text, primary_key=True)
    model: Mapped[Optional[str]] = mapped_column(Text)
    variant: Mapped[Optional[str]] = mapped_column(Text)
    engine_cc: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    power_hp: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class RawDetails(Base):
    __tablename__ = 'raw_details'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='raw_details_pkey'),
        Index('idx_raw_details_created_at', 'created_at'),
        Index('idx_raw_details_updated_at', 'updated_at')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    page_url: Mapped[Optional[str]] = mapped_column(Text)
    raw_description: Mapped[Optional[str]] = mapped_column(Text)
    raw_basic_information: Mapped[Optional[str]] = mapped_column(Text)
    raw_specification: Mapped[Optional[str]] = mapped_column(Text)
    raw_equipment: Mapped[Optional[str]] = mapped_column(Text)
    raw_seller_info: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class RawListing(Base):
    __tablename__ = 'raw_listing'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='raw_listing_pkey'),
        Index('idx_raw_listing_created_at', 'created_at'),
        Index('idx_raw_listing_details_like', 'raw_details'),
        Index('idx_raw_listing_price_like', 'raw_price'),
        Index('idx_raw_listing_summary_like', 'raw_summary')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    page_url: Mapped[Optional[str]] = mapped_column(Text)
    raw_summary: Mapped[Optional[str]] = mapped_column(Text)
    raw_details: Mapped[Optional[str]] = mapped_column(Text)
    raw_price: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    details: Mapped[List['Details']] = relationship('Details', back_populates='raw_listing')
    details_year_2000_2010: Mapped[List['DetailsYear20002010']] = relationship('DetailsYear20002010', back_populates='raw_listing')
    details_year_2010_2020: Mapped[List['DetailsYear20102020']] = relationship('DetailsYear20102020', back_populates='raw_listing')
    details_year_2020_2030: Mapped[List['DetailsYear20202030']] = relationship('DetailsYear20202030', back_populates='raw_listing')
    details_year_gte2030: Mapped[List['DetailsYearGte2030']] = relationship('DetailsYearGte2030', back_populates='raw_listing')
    details_year_lt2000: Mapped[List['DetailsYearLt2000']] = relationship('DetailsYearLt2000', back_populates='raw_listing')
    price: Mapped[List['Price']] = relationship('Price', back_populates='raw_listing')
    price_eur: Mapped[List['PriceEur']] = relationship('PriceEur', back_populates='raw_listing')
    price_pln: Mapped[List['PricePln']] = relationship('PricePln', back_populates='raw_listing')


class Sitemap(Base):
    __tablename__ = 'sitemap'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sitemap_pkey'),
        UniqueConstraint('sitemap_url', name='sitemap_sitemap_url_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sitemap_url: Mapped[str] = mapped_column(String(255))
    etag: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    size_mb: Mapped[Optional[float]] = mapped_column(Double(53))

    pages: Mapped[List['Pages']] = relationship('Pages', back_populates='sitemap')


class Details(Base):
    __tablename__ = 'details'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'year', name='details_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(100))
    gearbox_type: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(255))
    seller_type: Mapped[Optional[str]] = mapped_column(String(255))
    seller_info: Mapped[Optional[str]] = mapped_column(Text)
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_stamped: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='details')


class DetailsYear20002010(Base):
    __tablename__ = 'details_year_2000_2010'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'year', name='details_year_2000_2010_pkey'),
        Index('details_year_2000_2010_mileage_idx', 'mileage')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('details_id_seq'), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(100))
    gearbox_type: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(255))
    seller_type: Mapped[Optional[str]] = mapped_column(String(255))
    seller_info: Mapped[Optional[str]] = mapped_column(Text)
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_stamped: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='details_year_2000_2010')


class DetailsYear20102020(Base):
    __tablename__ = 'details_year_2010_2020'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'year', name='details_year_2010_2020_pkey'),
        Index('details_year_2010_2020_mileage_idx', 'mileage')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('details_id_seq'), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(100))
    gearbox_type: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(255))
    seller_type: Mapped[Optional[str]] = mapped_column(String(255))
    seller_info: Mapped[Optional[str]] = mapped_column(Text)
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_stamped: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='details_year_2010_2020')


class DetailsYear20202030(Base):
    __tablename__ = 'details_year_2020_2030'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'year', name='details_year_2020_2030_pkey'),
        Index('details_year_2020_2030_mileage_idx', 'mileage')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('details_id_seq'), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(100))
    gearbox_type: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(255))
    seller_type: Mapped[Optional[str]] = mapped_column(String(255))
    seller_info: Mapped[Optional[str]] = mapped_column(Text)
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_stamped: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='details_year_2020_2030')


class DetailsYearGte2030(Base):
    __tablename__ = 'details_year_gte2030'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'year', name='details_year_gte2030_pkey'),
        Index('details_year_gte2030_mileage_idx', 'mileage')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('details_id_seq'), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(100))
    gearbox_type: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(255))
    seller_type: Mapped[Optional[str]] = mapped_column(String(255))
    seller_info: Mapped[Optional[str]] = mapped_column(Text)
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_stamped: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='details_year_gte2030')


class DetailsYearLt2000(Base):
    __tablename__ = 'details_year_lt2000'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'year', name='details_year_lt2000_pkey'),
        Index('details_year_lt2000_mileage_idx', 'mileage')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('details_id_seq'), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    mileage: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(100))
    gearbox_type: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(255))
    seller_type: Mapped[Optional[str]] = mapped_column(String(255))
    seller_info: Mapped[Optional[str]] = mapped_column(Text)
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_stamped: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='details_year_lt2000')


class Pages(Base):
    __tablename__ = 'pages'
    __table_args__ = (
        ForeignKeyConstraint(['sitemap_id'], ['sitemap.id'], name='pages_sitemap_id_fkey'),
        PrimaryKeyConstraint('id', name='pages_pkey'),
        UniqueConstraint('page_url', name='pages_page_url_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    modified_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    priority: Mapped[Optional[float]] = mapped_column(REAL)
    change_frequency: Mapped[Optional[str]] = mapped_column(Enum('hourly', 'daily', 'weekly', 'monthly', name='enum_changefreq'))
    sitemap_id: Mapped[Optional[int]] = mapped_column(SmallInteger)

    sitemap: Mapped[Optional['Sitemap']] = relationship('Sitemap', back_populates='pages')


class Price(Base):
    __tablename__ = 'price'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'currency', name='price_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    currency: Mapped[str] = mapped_column(String(20), primary_key=True)
    amount: Mapped[Optional[float]] = mapped_column(Double(53))
    segment: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='price')


class PriceEur(Base):
    __tablename__ = 'price_eur'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'currency', name='price_eur_pkey'),
        Index('price_eur_segment_idx', 'segment')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('price_id_seq'), primary_key=True)
    currency: Mapped[str] = mapped_column(String(20), primary_key=True)
    amount: Mapped[Optional[float]] = mapped_column(Double(53))
    segment: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='price_eur')


class PricePln(Base):
    __tablename__ = 'price_pln'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['raw_listing.id'], name='fk_raw_listing'),
        PrimaryKeyConstraint('id', 'currency', name='price_pln_pkey'),
        Index('price_pln_segment_idx', 'segment')
    )

    id: Mapped[int] = mapped_column(BigInteger, Sequence('price_id_seq'), primary_key=True)
    currency: Mapped[str] = mapped_column(String(20), primary_key=True)
    amount: Mapped[Optional[float]] = mapped_column(Double(53))
    segment: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    raw_listing: Mapped['RawListing'] = relationship('RawListing', back_populates='price_pln')
