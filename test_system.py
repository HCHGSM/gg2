import sys
import os
import threading
import time

sys.path.insert(0, os.path.abspath('.'))
os.environ['POS_ERP_DB_PATH'] = ':memory:'

from pos_erp.database.db import SessionLocal, init_db, engine
from pos_erp.database.models import User, Product
from pos_erp.services.auth_service import AuthService
from pos_erp.services.product_service import ProductService

def setup_test_db():
    init_db()

def test_authentication():
    setup_test_db()
    print("--- STARTING AUTH TEST ---")
    
    user, msg = AuthService.authenticate('admin', 'admin123')
    print(f"Auth Success (Expected True): {user is not None}")
    
    user, msg = AuthService.authenticate('admin', 'wrongpass')
    print(f"Auth Failure (Expected False): {user is None}")
    
    if user is not None:
        print("ERROR: Authentication failed validation!")
    
    print("--- AUTH TEST COMPLETE ---")

def stress_test_database():
    os.environ['POS_ERP_DB_PATH'] = 'test_stress.db'
    if os.path.exists('test_stress.db'):
        os.remove('test_stress.db')
    
    # re-init engine for the new path
    from pos_erp.database.db import init_db
    init_db()
    
    print("--- STARTING DB STRESS TEST ---")
    
    def worker(worker_id):
        for i in range(50):
            ProductService.add_product({
                'name': f'Stress Product {worker_id}-{i}',
                'sku': f'SP-{worker_id}-{i}',
                'purchase_price': 10.0,
                'selling_price': 20.0,
                'quantity': 100.0,
            }, user_id=1)
            
    threads = []
    start_time = time.time()
    for i in range(10): # 10 threads adding 50 products each
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    session = SessionLocal()
    count = session.query(Product).filter(Product.sku.like('SP-%')).count()
    print(f"Total stress products inserted: {count} (Expected 500)")
    print(f"Time taken: {time.time() - start_time:.2f}s")
    print("--- DB STRESS TEST COMPLETE ---")

if __name__ == '__main__':
    test_authentication()

