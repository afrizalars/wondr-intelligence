from sqlalchemy import Column, String, DateTime, Text, Integer, Numeric, Date, Boolean, ForeignKey, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base
import uuid

class CIF(Base):
    __tablename__ = "cifs"
    
    cif = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_type = Column(String, default='individual')
    status = Column(String, default='active')
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    transactions = relationship("TransactionRaw", back_populates="customer", cascade="all, delete-orphan")
    profile = relationship("CustomerProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("TransferContact", back_populates="customer", cascade="all, delete-orphan")
    promos = relationship("Promo", back_populates="customer", cascade="all, delete-orphan")
    kb_documents = relationship("KBDocument", back_populates="customer", cascade="all, delete-orphan")

class TransactionRaw(Base):
    __tablename__ = "transactions_raw"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cif = Column(String, ForeignKey("cifs.cif", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    posting_date = Column(Date)
    description = Column(Text, nullable=False)
    merchant_name = Column(String)
    mcc = Column(String)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String, default='IDR')
    balance = Column(Numeric(15, 2))
    transaction_type = Column(String)
    category = Column(String)
    location = Column(String)
    reference_number = Column(String)
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("CIF", back_populates="transactions")

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cif = Column(String, ForeignKey("cifs.cif", ondelete="CASCADE"), nullable=False, unique=True)
    age = Column(Integer)
    gender = Column(String)
    occupation = Column(String)
    income_range = Column(String)
    risk_profile = Column(String)
    preferred_channels = Column(JSONB, default=[])
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    customer = relationship("CIF", back_populates="profile")

class TransferContact(Base):
    __tablename__ = "transfer_contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cif = Column(String, ForeignKey("cifs.cif", ondelete="CASCADE"), nullable=False)
    contact_name = Column(String, nullable=False)
    account_number = Column(String)
    bank_name = Column(String)
    contact_type = Column(String, default='personal')
    frequency = Column(Integer, default=0)
    last_transfer_date = Column(Date)
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("CIF", back_populates="contacts")

class Promo(Base):
    __tablename__ = "promos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cif = Column(String, ForeignKey("cifs.cif", ondelete="CASCADE"), nullable=False)
    promo_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    discount_type = Column(String)
    discount_value = Column(Numeric(10, 2))
    merchant_category = Column(String)
    valid_from = Column(Date)
    valid_until = Column(Date)
    terms_conditions = Column(Text)
    is_used = Column(Boolean, default=False)
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("CIF", back_populates="promos")

class KBDocument(Base):
    __tablename__ = "kb_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cif = Column(String, ForeignKey("cifs.cif", ondelete="CASCADE"), nullable=False)
    row_no = Column(BigInteger, nullable=False)
    source_table = Column(String, nullable=False)
    source_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    meta_data = Column("metadata", JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("CIF", back_populates="kb_documents")