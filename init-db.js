
db = db.getSiblingDB('dataset_catalog');


db.createCollection('datasets');
db.createCollection('quality_logs');


db.datasets.createIndex({ "name": 1 });
db.datasets.createIndex({ "owner": 1 });
db.datasets.createIndex({ "tags": 1 });
db.datasets.createIndex({ "created_at": -1 });
db.datasets.createIndex({ "is_deleted": 1 });

db.quality_logs.createIndex({ "dataset_id": 1 });
db.quality_logs.createIndex({ "check_type": 1 });
db.quality_logs.createIndex({ "timestamp": -1 });
db.quality_logs.createIndex({ "dataset_id": 1, "timestamp": -1 });

print('Database initialization completed!');
