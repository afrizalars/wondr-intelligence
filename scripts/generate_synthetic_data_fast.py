#!/usr/bin/env python3
"""
Fast synthetic data generator that uses the embedding service properly
"""
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

# Load environment variables BEFORE importing modules
from dotenv import load_dotenv
env_path = os.path.join(backend_path, '.env')
load_dotenv(env_path)

# Set minimal required environment variables
if not os.getenv('ANTHROPIC_API_KEY'):
    os.environ['ANTHROPIC_API_KEY'] = 'dummy-key-for-data-generation'

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
]

PROMO_TEMPLATES = [
    {"title": "Cashback {discount}%", "type": "cashback", "category": "Food and Drink"},
    {"title": "Diskon {discount}% All Items", "type": "percentage", "category": "E-commerce"},
    {"title": "Buy 1 Get 1", "type": "bogo", "category": "Food and Drink"},
    {"title": "Free Delivery", "type": "free_delivery", "category": "Transportation"},
    {"title": "Points 2x", "type": "points", "category": "E-commerce"},
    {"title": "Voucher Rp {amount}", "type": "voucher", "category": "Grocery"}
]

class FastDataGenerator:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        self.embedding_service = None
        
    async def connect(self):
        print(f"Connecting to database...")
        self.conn = await asyncpg.connect(self.db_url)
        print("✅ Connected to database")
        
    async def disconnect(self):
        if self.conn:
            await self.conn.close()
    
    def get_embedding_service(self):
        """Lazy load embedding service only when needed"""
        if self.embedding_service is None:
            print("Loading embedding service...")
            from services.embeddings import embedding_service
            self.embedding_service = embedding_service
            print("✅ Embedding service loaded")
        return self.embedding_service
    
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
        
        print(f"✅ Generated {count} customers")
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
                "preferred_channels": ["Mobile", "Web"] if random.random() > 0.5 else ["ATM", "Branch"]
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
        
        print(f"✅ Generated {len(profiles)} customer profiles")
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
            print(f"  Inserted transaction batch {i//batch_size + 1}/{(len(transactions)-1)//batch_size + 1}")
        
        print(f"✅ Generated {len(transactions)} transactions")
        return transactions
    
    async def generate_embeddings_with_service(self, use_real_embeddings: bool = False):
        """Generate embeddings using either real model or random vectors"""
        print(f"Generating embeddings (real={use_real_embeddings})...")
        
        # Get transactions to embed
        rows = await self.conn.fetch(
            "SELECT * FROM transactions_raw ORDER BY cif, transaction_date LIMIT 500"
        )
        
        if not rows:
            print("  No transactions to embed")
            return
        
        kb_documents = []
        current_cif = None
        row_no = 0
        
        # Prepare texts for embedding
        texts_to_embed = []
        
        for row in rows:
            row_dict = dict(row)
            
            # Reset row_no for new CIF
            if row_dict["cif"] != current_cif:
                current_cif = row_dict["cif"]
                row_no = 0
            else:
                row_no += 1
            
            # Prepare text for embedding
            text = f"Transaction: {row_dict.get('description', '')} "
            if row_dict.get('merchant_name'):
                text += f"at {row_dict['merchant_name']} "
            text += f"for amount {row_dict.get('amount', 0)} {row_dict.get('currency', 'IDR')} "
            text += f"on {row_dict.get('transaction_date', '')} "
            if row_dict.get('category'):
                text += f"category: {row_dict['category']}"
            
            texts_to_embed.append(text.strip())
            
            # Generate title
            title = f"{row_dict.get('merchant_name', 'Transaction')} · Rp {abs(row_dict['amount']):,.0f} · {row_dict['transaction_date']}"
            
            kb_doc = {
                "id": str(uuid.uuid4()),
                "cif": row_dict["cif"],
                "row_no": row_no,
                "source_table": "transactions_raw",
                "source_id": row_dict["id"],
                "title": title,
                "text": text.strip(),
                "metadata": {
                    "category": row_dict.get("category"),
                    "merchant": row_dict.get("merchant_name"),
                    "amount": float(row_dict.get("amount", 0))
                }
            }
            kb_documents.append(kb_doc)
        
        # Generate embeddings
        if use_real_embeddings:
            print(f"  Generating real embeddings for {len(texts_to_embed)} texts...")
            service = self.get_embedding_service()
            embeddings = service.embed_batch(texts_to_embed, batch_size=32)
        else:
            print(f"  Generating random embeddings for {len(texts_to_embed)} texts...")
            embeddings = []
            for _ in texts_to_embed:
                # Generate random 768-dimensional vector
                vec = np.random.randn(768).astype(np.float32)
                vec = vec / np.linalg.norm(vec)  # Normalize
                embeddings.append(vec)
            embeddings = np.array(embeddings)
        
        # Add embeddings to documents
        for i, doc in enumerate(kb_documents):
            doc["embedding"] = embeddings[i].tolist()
        
        # Insert embeddings
        print(f"  Inserting {len(kb_documents)} embeddings...")
        for doc in kb_documents:
            embedding_str = '[' + ','.join(map(str, doc["embedding"])) + ']'
            
            await self.conn.execute(
                """INSERT INTO kb_documents 
                   (id, cif, row_no, source_table, source_id, title, text, embedding, metadata)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector, $9::jsonb)
                   ON CONFLICT (source_table, source_id) DO NOTHING""",
                doc["id"], doc["cif"], doc["row_no"], doc["source_table"], doc["source_id"],
                doc["title"], doc["text"], embedding_str, json.dumps(doc["metadata"])
            )
        
        print(f"✅ Generated {len(kb_documents)} embeddings")
    
    async def generate_merchants(self):
        print("Generating merchant catalog...")
        
        for merchant in MERCHANTS:
            await self.conn.execute(
                """INSERT INTO merchants (id, name, mcc, category, status)
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (name, mcc) DO NOTHING""",
                str(uuid.uuid4()), merchant["name"], merchant["mcc"], merchant["category"], "active"
            )
        
        print(f"✅ Generated {len(MERCHANTS)} merchants")
    
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
        
        print(f"✅ Generated {len(guardrails)} guardrails")
    
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
        
        print(f"✅ Generated {len(templates)} prompt templates")

async def main():
    # Get database URL from environment
    DB_URL = os.getenv("DATABASE_SYNC_URL") or os.getenv("DATABASE_URL", "postgresql://63628@localhost:5432/wondr_intelligence")
    
    # Clean up the URL for asyncpg
    if "+asyncpg" in DB_URL:
        DB_URL = DB_URL.replace("+asyncpg", "")
    if not DB_URL.startswith("postgresql://"):
        DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    generator = FastDataGenerator(DB_URL)
    
    try:
        await generator.connect()
        print("Connected to database")
        
        # Ask user for options
        print("\nOptions:")
        print("1. Quick setup (20 customers, random embeddings)")
        print("2. Full setup (100 customers, real embeddings)")
        print("3. Custom setup")
        
        choice = input("\nSelect option (1-3) [default: 1]: ").strip() or "1"
        
        if choice == "1":
            # Quick setup
            cifs = await generator.generate_customers(20)
            await generator.generate_customer_profiles(cifs)
            await generator.generate_transactions(cifs[:10], days_back=30, txn_per_day=3)
            await generator.generate_embeddings_with_service(use_real_embeddings=False)
        elif choice == "2":
            # Full setup
            cifs = await generator.generate_customers(100)
            await generator.generate_customer_profiles(cifs)
            await generator.generate_transactions(cifs[:20], days_back=90, txn_per_day=5)
            await generator.generate_embeddings_with_service(use_real_embeddings=True)
        else:
            # Custom setup
            num_customers = int(input("Number of customers (default: 20): ").strip() or "20")
            days_back = int(input("Days of transaction history (default: 30): ").strip() or "30")
            use_real = input("Use real embeddings? (y/n) [default: n]: ").strip().lower() == "y"
            
            cifs = await generator.generate_customers(num_customers)
            await generator.generate_customer_profiles(cifs)
            await generator.generate_transactions(cifs[:min(20, num_customers)], days_back=days_back)
            await generator.generate_embeddings_with_service(use_real_embeddings=use_real)
        
        # Always generate these
        await generator.generate_merchants()
        await generator.generate_default_guardrails()
        await generator.generate_prompt_templates()
        
        print("\n✅ Synthetic data generation complete!")
        
    finally:
        await generator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())