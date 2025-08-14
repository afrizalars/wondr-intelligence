#!/usr/bin/env python3
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import numpy as np
from faker import Faker
import sys
import os
import json

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

# Load environment variables BEFORE importing modules that need them
from dotenv import load_dotenv
env_path = os.path.join(backend_path, '.env')
load_dotenv(env_path)

# Set environment variable defaults if not present
if not os.getenv('ANTHROPIC_API_KEY'):
    os.environ['ANTHROPIC_API_KEY'] = 'dummy-key-for-data-generation'

# Now import the modules
from services.embeddings import embedding_service
fake = Faker('id_ID')  # Indonesian locale

# Merchant data
MERCHANTS = [
    {"name": "Starbucks", "mcc": "5814", "category": "Food and Drink"},
    {"name": "McDonald's", "mcc": "5814", "category": "Food and Drink"},
    {"name": "KFC", "mcc": "5814", "category": "Food and Drink"},
    {"name": "Pizza Hut", "mcc": "5814", "category": "Food and Drink"},
    {"name": "Indomaret", "mcc": "5411", "category": "Grocery"},
    {"name": "Alfamart", "mcc": "5411", "category": "Grocery"},
    {"name": "Transmart", "mcc": "5411", "category": "Grocery"},
    {"name": "Tokopedia", "mcc": "5999", "category": "E-commerce"},
    {"name": "Shopee", "mcc": "5999", "category": "E-commerce"},
    {"name": "Lazada", "mcc": "5999", "category": "E-commerce"},
    {"name": "Grab", "mcc": "4121", "category": "Transportation"},
    {"name": "Gojek", "mcc": "4121", "category": "Transportation"},
    {"name": "Blue Bird", "mcc": "4121", "category": "Transportation"},
    {"name": "PLN", "mcc": "4900", "category": "Utilities"},
    {"name": "PDAM", "mcc": "4900", "category": "Utilities"},
    {"name": "Telkomsel", "mcc": "4814", "category": "Telecommunications"},
    {"name": "XL Axiata", "mcc": "4814", "category": "Telecommunications"},
    {"name": "Indosat", "mcc": "4814", "category": "Telecommunications"},
    {"name": "Netflix", "mcc": "5968", "category": "Entertainment"},
    {"name": "Spotify", "mcc": "5968", "category": "Entertainment"},
    {"name": "CGV Cinemas", "mcc": "7832", "category": "Entertainment"},
    {"name": "XXI", "mcc": "7832", "category": "Entertainment"},
    {"name": "Ace Hardware", "mcc": "5200", "category": "Home Improvement"},
    {"name": "IKEA", "mcc": "5712", "category": "Furniture"},
    {"name": "Apotek K24", "mcc": "5912", "category": "Pharmacy"},
    {"name": "Guardian", "mcc": "5912", "category": "Pharmacy"},
    {"name": "Uniqlo", "mcc": "5651", "category": "Clothing"},
    {"name": "Zara", "mcc": "5651", "category": "Clothing"},
    {"name": "H&M", "mcc": "5651", "category": "Clothing"}
]

PROMO_TEMPLATES = [
    {"title": "Cashback {discount}%", "type": "cashback", "category": "Food and Drink"},
    {"title": "Diskon {discount}% All Items", "type": "percentage", "category": "E-commerce"},
    {"title": "Buy 1 Get 1", "type": "bogo", "category": "Food and Drink"},
    {"title": "Free Delivery", "type": "free_delivery", "category": "Transportation"},
    {"title": "Points 2x", "type": "points", "category": "E-commerce"},
    {"title": "Voucher Rp {amount}", "type": "voucher", "category": "Grocery"}
]

class SyntheticDataGenerator:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        
    async def connect(self):
        self.conn = await asyncpg.connect(self.db_url)
        
    async def disconnect(self):
        if self.conn:
            await self.conn.close()
    
    async def generate_customers(self, count: int = 100):
        print(f"Generating {count} customers...")
        customers = []
        
        for i in range(count):
            cif = f"CIF{str(i+1).zfill(8)}"
            customer_name = fake.name()
            
            customers.append({
                "cif": cif,
                "customer_name": customer_name,
                "customer_type": "individual",
                "status": "active",
                "metadata": {
                    "registration_date": fake.date_between(start_date='-2y', end_date='today').isoformat(),
                    "branch": fake.city()
                }
            })
        
        # Insert customers
        await self.conn.executemany(
            """INSERT INTO cifs (cif, customer_name, customer_type, status, metadata)
               VALUES ($1, $2, $3, $4, $5::jsonb)
               ON CONFLICT (cif) DO NOTHING""",
            [(c["cif"], c["customer_name"], c["customer_type"], c["status"], json.dumps(c["metadata"])) for c in customers]
        )
        
        return [c["cif"] for c in customers]
    
    async def generate_customer_profiles(self, cifs: list):
        print(f"Generating customer profiles for {len(cifs)} customers...")
        
        profiles = []
        for cif in cifs:
            profile = {
                "id": str(uuid.uuid4()),
                "cif": cif,
                "age": random.randint(18, 70),
                "gender": random.choice(["Male", "Female"]),
                "occupation": fake.job(),
                "income_range": random.choice([
                    "< 5 juta", "5-10 juta", "10-25 juta", "25-50 juta", "> 50 juta"
                ]),
                "risk_profile": random.choice(["Conservative", "Moderate", "Aggressive"]),
                "preferred_channels": random.sample(["Mobile", "Web", "ATM", "Branch"], k=2)
            }
            profiles.append(profile)
        
        await self.conn.executemany(
            """INSERT INTO customer_profiles 
               (id, cif, age, gender, occupation, income_range, risk_profile, preferred_channels)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
               ON CONFLICT (cif) DO NOTHING""",
            [(p["id"], p["cif"], p["age"], p["gender"], p["occupation"], 
              p["income_range"], p["risk_profile"], json.dumps(p["preferred_channels"])) for p in profiles]
        )
        
        return profiles
    
    async def generate_transactions(self, cifs: list, days_back: int = 90, txn_per_day: int = 5):
        print(f"Generating transactions for {len(cifs)} customers...")
        
        transactions = []
        start_date = datetime.now() - timedelta(days=days_back)
        
        for cif in cifs:
            balance = Decimal(str(random.uniform(1000000, 50000000)))  # Starting balance
            
            for day in range(days_back):
                current_date = start_date + timedelta(days=day)
                num_txn = random.randint(0, txn_per_day)
                
                for _ in range(num_txn):
                    merchant = random.choice(MERCHANTS)
                    is_credit = random.random() < 0.2  # 20% chance of credit
                    
                    if is_credit:
                        amount = Decimal(str(random.uniform(100000, 5000000)))
                        description = f"Transfer from {fake.name()}"
                        txn_type = "CREDIT"
                    else:
                        amount = -Decimal(str(random.uniform(10000, 500000)))
                        description = f"Payment at {merchant['name']}"
                        txn_type = "DEBIT"
                    
                    balance += amount
                    
                    transaction = {
                        "id": str(uuid.uuid4()),
                        "cif": cif,
                        "transaction_date": current_date.date(),
                        "posting_date": current_date.date(),
                        "description": description,
                        "merchant_name": merchant["name"] if not is_credit else None,
                        "mcc": merchant["mcc"] if not is_credit else None,
                        "amount": float(amount),
                        "currency": "IDR",
                        "balance": float(balance),
                        "transaction_type": txn_type,
                        "category": merchant["category"] if not is_credit else "Transfer",
                        "location": fake.city(),
                        "reference_number": fake.uuid4()[:12].upper()
                    }
                    transactions.append(transaction)
        
        # Insert in batches
        batch_size = 1000
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i+batch_size]
            await self.conn.executemany(
                """INSERT INTO transactions_raw 
                   (id, cif, transaction_date, posting_date, description, merchant_name,
                    mcc, amount, currency, balance, transaction_type, category, location, reference_number)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)""",
                [(t["id"], t["cif"], t["transaction_date"], t["posting_date"], t["description"],
                  t["merchant_name"], t["mcc"], t["amount"], t["currency"], t["balance"],
                  t["transaction_type"], t["category"], t["location"], t["reference_number"]) for t in batch]
            )
            print(f"  Inserted batch {i//batch_size + 1}/{(len(transactions)-1)//batch_size + 1}")
        
        return transactions
    
    async def generate_contacts(self, cifs: list, contacts_per_cif: int = 10):
        print(f"Generating transfer contacts...")
        
        contacts = []
        for cif in cifs:
            num_contacts = random.randint(3, contacts_per_cif)
            
            for _ in range(num_contacts):
                contact = {
                    "id": str(uuid.uuid4()),
                    "cif": cif,
                    "contact_name": fake.name(),
                    "account_number": fake.iban()[-10:],
                    "bank_name": random.choice(["BCA", "Mandiri", "BNI", "BRI", "CIMB", "Permata"]),
                    "contact_type": random.choice(["personal", "business", "family"]),
                    "frequency": random.randint(0, 50),
                    "last_transfer_date": fake.date_between(start_date='-30d', end_date='today'),
                    "total_amount": float(random.uniform(100000, 10000000))
                }
                contacts.append(contact)
        
        await self.conn.executemany(
            """INSERT INTO transfer_contacts 
               (id, cif, contact_name, account_number, bank_name, contact_type,
                frequency, last_transfer_date, total_amount)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
            [(c["id"], c["cif"], c["contact_name"], c["account_number"], c["bank_name"],
              c["contact_type"], c["frequency"], c["last_transfer_date"], c["total_amount"]) for c in contacts]
        )
        
        return contacts
    
    async def generate_promos(self, cifs: list, promos_per_cif: int = 5):
        print(f"Generating promos...")
        
        promos = []
        for cif in cifs:
            num_promos = random.randint(2, promos_per_cif)
            
            for _ in range(num_promos):
                template = random.choice(PROMO_TEMPLATES)
                
                promo = {
                    "id": str(uuid.uuid4()),
                    "cif": cif,
                    "promo_code": fake.uuid4()[:8].upper(),
                    "title": template["title"].format(
                        discount=random.randint(10, 50),
                        amount=random.randint(10, 100) * 1000
                    ),
                    "description": fake.sentence(),
                    "discount_type": template["type"],
                    "discount_value": float(random.randint(10, 50)),
                    "merchant_category": template["category"],
                    "valid_from": datetime.now().date(),
                    "valid_until": (datetime.now() + timedelta(days=random.randint(7, 60))).date(),
                    "terms_conditions": fake.paragraph(),
                    "is_used": random.random() < 0.3
                }
                promos.append(promo)
        
        await self.conn.executemany(
            """INSERT INTO promos 
               (id, cif, promo_code, title, description, discount_type, discount_value,
                merchant_category, valid_from, valid_until, terms_conditions, is_used)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)""",
            [(p["id"], p["cif"], p["promo_code"], p["title"], p["description"],
              p["discount_type"], p["discount_value"], p["merchant_category"],
              p["valid_from"], p["valid_until"], p["terms_conditions"], p["is_used"]) for p in promos]
        )
        
        return promos
    
    async def generate_embeddings(self):
        print("Generating embeddings for all data...")
        
        # Clear existing embeddings first
        print("  Clearing existing embeddings...")
        await self.conn.execute("DELETE FROM kb_documents")
        
        # Get all data that needs embedding
        sources = [
            ("transactions_raw", "SELECT * FROM transactions_raw ORDER BY cif, transaction_date"),
            ("customer_profiles", "SELECT * FROM customer_profiles"),
            ("transfer_contacts", "SELECT * FROM transfer_contacts"),
            ("promos", "SELECT * FROM promos WHERE is_used = false")
        ]
        
        # Track row numbers per CIF globally
        cif_row_counters = {}
        
        for source_table, query in sources:
            print(f"  Processing {source_table}...")
            rows = await self.conn.fetch(query)
            
            kb_documents = []
            
            for row in rows:
                row_dict = dict(row)
                cif = row_dict.get("cif")
                
                # Initialize or increment row counter for this CIF
                if cif not in cif_row_counters:
                    cif_row_counters[cif] = 0
                
                row_no = cif_row_counters[cif]
                cif_row_counters[cif] += 1
                
                # Prepare text for embedding
                text = embedding_service.prepare_text_for_embedding(row_dict, source_table)
                
                # Generate title
                if source_table == "transactions_raw":
                    title = f"{row_dict.get('merchant_name', 'Transaction')} · Rp {abs(row_dict['amount']):,.0f} · {row_dict['transaction_date']}"
                elif source_table == "transfer_contacts":
                    title = f"Contact: {row_dict['contact_name']}"
                elif source_table == "promos":
                    title = f"Promo: {row_dict['title']}"
                else:
                    title = f"Profile: {row_dict['cif']}"
                
                # Generate embedding
                embedding = embedding_service.embed_text(text)[0]
                
                kb_doc = {
                    "id": str(uuid.uuid4()),
                    "cif": row_dict["cif"],
                    "row_no": row_no,
                    "source_table": source_table,
                    "source_id": row_dict["id"],
                    "title": title,
                    "text": text,
                    "embedding": embedding.tolist(),
                    "metadata": {
                        "category": row_dict.get("category"),
                        "merchant": row_dict.get("merchant_name"),
                        "amount": float(row_dict.get("amount", 0))
                    } if source_table == "transactions_raw" else {}
                }
                kb_documents.append(kb_doc)
            
            # Insert embeddings in batches
            batch_size = 100
            for i in range(0, len(kb_documents), batch_size):
                batch = kb_documents[i:i+batch_size]
                
                # Convert embeddings to PostgreSQL vector format
                for doc in batch:
                    doc["embedding_str"] = '[' + ','.join(map(str, doc["embedding"])) + ']'
                
                await self.conn.executemany(
                    """INSERT INTO kb_documents 
                       (id, cif, row_no, source_table, source_id, title, text, embedding, metadata)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector, $9::jsonb)
                       ON CONFLICT (source_table, source_id) DO NOTHING""",
                    [(d["id"], d["cif"], d["row_no"], d["source_table"], d["source_id"],
                      d["title"], d["text"], d["embedding_str"], json.dumps(d["metadata"])) for d in batch]
                )
                print(f"    Inserted embedding batch {i//batch_size + 1}/{(len(kb_documents)-1)//batch_size + 1}")
    
    async def generate_merchants(self):
        print("Generating merchant catalog...")
        
        for merchant in MERCHANTS:
            await self.conn.execute(
                """INSERT INTO merchants (id, name, mcc, category, status)
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (name, mcc) DO NOTHING""",
                str(uuid.uuid4()), merchant["name"], merchant["mcc"], merchant["category"], "active"
            )
    
    async def generate_default_guardrails(self):
        print("Generating default guardrails...")
        
        guardrails = [
            {
                "name": "Block Credit Card Numbers",
                "rule_type": "regex",
                "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                "action": "transform",
                "severity": "high",
                "message": "Credit card numbers are not allowed"
            },
            {
                "name": "Block SSN/KTP",
                "rule_type": "regex",
                "pattern": r"\b\d{16}\b",
                "action": "transform",
                "severity": "high",
                "message": "Personal identification numbers are not allowed"
            },
            {
                "name": "Profanity Filter",
                "rule_type": "keyword",
                "pattern": "anjing,babi,bangsat,tolol",
                "action": "warn",
                "severity": "medium",
                "message": "Please use appropriate language"
            },
            {
                "name": "SQL Injection Detection",
                "rule_type": "regex",
                "pattern": r"(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER)\s+(TABLE|DATABASE|INDEX)",
                "action": "block",
                "severity": "critical",
                "message": "Potential SQL injection detected"
            }
        ]
        
        for g in guardrails:
            await self.conn.execute(
                """INSERT INTO guardrails 
                   (id, name, rule_type, pattern, action, severity, message, is_active)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                str(uuid.uuid4()), g["name"], g["rule_type"], g["pattern"],
                g["action"], g["severity"], g["message"], True
            )
    
    async def generate_prompt_templates(self):
        print("Generating prompt templates...")
        
        templates = [
            {
                "name": "professional",
                "category": "tone",
                "template": "Please respond in a professional and formal manner, using banking terminology where appropriate.",
                "is_default": True
            },
            {
                "name": "friendly",
                "category": "tone",
                "template": "Please respond in a friendly and conversational tone, making financial concepts easy to understand.",
                "is_default": False
            },
            {
                "name": "concise",
                "category": "style",
                "template": "Provide brief, to-the-point responses focusing only on essential information.",
                "is_default": False
            },
            {
                "name": "detailed",
                "category": "style",
                "template": "Provide comprehensive responses with detailed explanations and examples.",
                "is_default": False
            }
        ]
        
        for t in templates:
            await self.conn.execute(
                """INSERT INTO prompt_templates 
                   (id, name, category, template, is_default)
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (name) DO NOTHING""",
                str(uuid.uuid4()), t["name"], t["category"], t["template"], t["is_default"]
            )

async def main():
    # Get database URL from environment
    DB_URL = os.getenv("DATABASE_SYNC_URL") or os.getenv("DATABASE_URL", "postgresql://63628@localhost:5432/wondr_intelligence")
    
    # Clean up the URL for asyncpg
    if "+asyncpg" in DB_URL:
        DB_URL = DB_URL.replace("+asyncpg", "")
    if not DB_URL.startswith("postgresql://"):
        DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    generator = SyntheticDataGenerator(DB_URL)
    
    try:
        await generator.connect()
        print("Connected to database")
        
        # Generate data
        cifs = await generator.generate_customers(100)
        await generator.generate_customer_profiles(cifs)
        await generator.generate_transactions(cifs[:20], days_back=90)  # Only first 20 customers get transactions
        await generator.generate_contacts(cifs)
        await generator.generate_promos(cifs)
        await generator.generate_embeddings()
        await generator.generate_merchants()
        await generator.generate_default_guardrails()
        await generator.generate_prompt_templates()
        
        print("✅ Synthetic data generation complete!")
        
    finally:
        await generator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())