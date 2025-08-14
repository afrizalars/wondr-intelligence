#!/usr/bin/env python3
"""
Simple synthetic data generator that directly uses the database
without requiring the backend services.
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import numpy as np
from faker import Faker
import os
import json
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
load_dotenv(env_path)

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_SYNC_URL', 'postgresql://63628@localhost:5432/wondr_intelligence')
if DATABASE_URL.startswith('postgresql://'):
    # asyncpg needs the URL without the postgresql:// prefix for the format we're using
    pass
else:
    # Convert from async format if needed
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

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

class SimpleDataGenerator:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        
    async def connect(self):
        print(f"Connecting to database...")
        self.conn = await asyncpg.connect(self.db_url)
        print("✅ Connected to database")
        
    async def disconnect(self):
        if self.conn:
            await self.conn.close()
    
    async def clear_existing_data(self):
        """Clear existing test data"""
        print("Clearing existing data...")
        tables = [
            'kb_documents',
            'search_history',
            'conversations',
            'api_keys',
            'promos',
            'transfer_contacts',
            'customer_profiles',
            'transactions_raw',
            'cifs',
            'merchants',
            'guardrails',
            'prompt_templates'
        ]
        
        for table in tables:
            try:
                await self.conn.execute(f"DELETE FROM {table}")
                print(f"  Cleared {table}")
            except Exception as e:
                print(f"  Skipping {table}: {str(e)[:50]}")
    
    async def generate_customers(self, count: int = 20):
        print(f"\nGenerating {count} customers...")
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
        print(f"\nGenerating customer profiles...")
        
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
    
    async def generate_transactions(self, cifs: list, days_back: int = 30, txn_per_day: int = 3):
        print(f"\nGenerating transactions for {len(cifs)} customers...")
        
        transactions = []
        start_date = datetime.now() - timedelta(days=days_back)
        
        for cif in cifs[:10]:  # Only first 10 customers get transactions for demo
            balance = Decimal(str(random.uniform(1000000, 10000000)))  # Starting balance
            
            for day in range(days_back):
                current_date = start_date + timedelta(days=day)
                num_txn = random.randint(0, txn_per_day)
                
                for _ in range(num_txn):
                    merchant = random.choice(MERCHANTS)
                    is_credit = random.random() < 0.2  # 20% chance of credit
                    
                    if is_credit:
                        amount = Decimal(str(random.uniform(100000, 2000000)))
                        description = f"Transfer from {fake.name()}"
                        txn_type = "CREDIT"
                        merchant_name = None
                        mcc = None
                        category = "Transfer"
                    else:
                        amount = -Decimal(str(random.uniform(10000, 300000)))
                        description = f"Payment at {merchant['name']}"
                        txn_type = "DEBIT"
                        merchant_name = merchant["name"]
                        mcc = merchant["mcc"]
                        category = merchant["category"]
                    
                    balance += amount
                    
                    transaction = {
                        "id": str(uuid.uuid4()),
                        "cif": cif,
                        "transaction_date": current_date.date(),
                        "posting_date": current_date.date(),
                        "description": description,
                        "merchant_name": merchant_name,
                        "mcc": mcc,
                        "amount": float(amount),
                        "currency": "IDR",
                        "balance": float(balance),
                        "transaction_type": txn_type,
                        "category": category,
                        "location": fake.city(),
                        "reference_number": fake.uuid4()[:12].upper()
                    }
                    transactions.append(transaction)
        
        # Insert in batches
        if transactions:
            batch_size = 500
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
        
        print(f"✅ Generated {len(transactions)} transactions")
        return transactions
    
    async def generate_merchants(self):
        print(f"\nGenerating merchant catalog...")
        
        for merchant in MERCHANTS:
            await self.conn.execute(
                """INSERT INTO merchants (id, name, mcc, category, status)
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (name, mcc) DO NOTHING""",
                str(uuid.uuid4()), merchant["name"], merchant["mcc"], merchant["category"], "active"
            )
        
        print(f"✅ Generated {len(MERCHANTS)} merchants")
    
    async def generate_default_guardrails(self):
        print(f"\nGenerating default guardrails...")
        
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
                "name": "Profanity Filter",
                "rule_type": "keyword",
                "pattern": "inappropriate,offensive",
                "action": "warn",
                "severity": "medium",
                "message": "Please use appropriate language"
            }
        ]
        
        for g in guardrails:
            await self.conn.execute(
                """INSERT INTO guardrails 
                   (id, name, rule_type, pattern, action, severity, message, is_active)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                   ON CONFLICT DO NOTHING""",
                str(uuid.uuid4()), g["name"], g["rule_type"], g["pattern"],
                g["action"], g["severity"], g["message"], True
            )
        
        print(f"✅ Generated {len(guardrails)} guardrails")
    
    async def generate_prompt_templates(self):
        print(f"\nGenerating prompt templates...")
        
        templates = [
            {
                "name": "professional",
                "category": "tone",
                "template": "Please respond in a professional and formal manner.",
                "is_default": True
            },
            {
                "name": "friendly",
                "category": "tone", 
                "template": "Please respond in a friendly and conversational tone.",
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
    
    async def generate_sample_embeddings(self, cifs: list):
        """Generate simple placeholder embeddings for testing"""
        print(f"\nGenerating sample embeddings for transactions...")
        
        # Get transactions
        transactions = await self.conn.fetch(
            "SELECT * FROM transactions_raw WHERE cif = ANY($1) ORDER BY cif, transaction_date",
            cifs[:5]  # Only for first 5 customers
        )
        
        kb_documents = []
        current_cif = None
        row_no = 0
        
        for txn in transactions:
            if txn['cif'] != current_cif:
                current_cif = txn['cif']
                row_no = 0
            else:
                row_no += 1
            
            # Create text representation
            text = f"Transaction: {txn['description']} for amount {abs(txn['amount'])} IDR on {txn['transaction_date']}"
            if txn['merchant_name']:
                text += f" at {txn['merchant_name']}"
            if txn['category']:
                text += f" category: {txn['category']}"
            
            # Generate random embedding (placeholder - in production use real embeddings)
            embedding = np.random.randn(768).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            
            kb_doc = {
                "id": str(uuid.uuid4()),
                "cif": txn['cif'],
                "row_no": row_no,
                "source_table": "transactions_raw",
                "source_id": txn['id'],
                "title": f"{txn.get('merchant_name', 'Transaction')} · Rp {abs(txn['amount']):,.0f}",
                "text": text,
                "embedding": embedding.tolist(),
                "metadata": {
                    "category": txn.get('category'),
                    "merchant": txn.get('merchant_name'),
                    "amount": float(txn.get('amount', 0))
                }
            }
            kb_documents.append(kb_doc)
        
        # Insert embeddings in batches
        if kb_documents:
            batch_size = 100
            for i in range(0, len(kb_documents), batch_size):
                batch = kb_documents[i:i+batch_size]
                
                for doc in batch:
                    embedding_str = '[' + ','.join(map(str, doc["embedding"])) + ']'
                    
                    await self.conn.execute(
                        """INSERT INTO kb_documents 
                           (id, cif, row_no, source_table, source_id, title, text, embedding, metadata)
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector, $9::jsonb)
                           ON CONFLICT (source_table, source_id) DO NOTHING""",
                        doc["id"], doc["cif"], doc["row_no"], doc["source_table"], doc["source_id"],
                        doc["title"], doc["text"], embedding_str, 
                        json.dumps(doc["metadata"])
                    )
        
        print(f"✅ Generated {len(kb_documents)} sample embeddings")

async def main():
    print("=" * 50)
    print("Wondr Intelligence - Synthetic Data Generator")
    print("=" * 50)
    
    generator = SimpleDataGenerator(DATABASE_URL)
    
    try:
        await generator.connect()
        
        # Clear existing data
        await generator.clear_existing_data()
        
        # Generate data
        cifs = await generator.generate_customers(20)
        await generator.generate_customer_profiles(cifs)
        await generator.generate_transactions(cifs, days_back=30)
        await generator.generate_merchants()
        await generator.generate_default_guardrails()
        await generator.generate_prompt_templates()
        await generator.generate_sample_embeddings(cifs)
        
        print("\n" + "=" * 50)
        print("✅ Synthetic data generation complete!")
        print("=" * 50)
        print("\nYou can now:")
        print("1. Start the backend: ./start-backend.sh")
        print("2. Start the frontend: ./start-frontend.sh")
        print("3. Login and use CIF00000001 through CIF00000020")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await generator.disconnect()

if __name__ == "__main__":
    asyncio.run(main())