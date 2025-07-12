from datetime import datetime
from bson import ObjectId
from utils.database import get_db
from models.dataset import DatasetCreate, DatasetUpdate
from typing import List, Optional, Dict, Any

class DatasetService:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.datasets

    def create_dataset(self, dataset_data: DatasetCreate) -> Dict[str, Any]:
        """Create a new dataset"""
        now = datetime.utcnow()
        
        existing = self.collection.find_one({
            "name": dataset_data.name,
            "owner": dataset_data.owner,
            "is_deleted": False
        })
        
        if existing:
            raise ValueError("Dataset with this name already exists for this owner")
        
        dataset_doc = {
            "name": dataset_data.name,
            "owner": dataset_data.owner,
            "description": dataset_data.description,
            "tags": dataset_data.tags,
            "created_at": now,
            "updated_at": now,
            "is_deleted": False
        }
        
        result = self.collection.insert_one(dataset_doc)
        dataset_doc["_id"] = result.inserted_id
        
        return dataset_doc

    def get_datasets(self, owner: Optional[str] = None, tag: Optional[str] = None, 
                    page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get datasets with optional filtering and pagination"""
        query = {"is_deleted": False}
        
        if owner:
            query["owner"] = owner
        
        if tag:
            query["tags"] = {"$in": [tag]}
        
        skip = (page - 1) * limit
        
        total = self.collection.count_documents(query)
        
        datasets = list(
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        return {
            "datasets": datasets,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    def get_dataset_by_id(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get a dataset by ID"""
        if not ObjectId.is_valid(dataset_id):
            return None
        
        return self.collection.find_one({
            "_id": ObjectId(dataset_id),
            "is_deleted": False
        })

    def update_dataset(self, dataset_id: str, update_data: DatasetUpdate) -> Optional[Dict[str, Any]]:
        """Update a dataset"""
        if not ObjectId.is_valid(dataset_id):
            return None
        
        update_doc = {"updated_at": datetime.utcnow()}
        
        if update_data.name is not None:
            update_doc["name"] = update_data.name
        if update_data.owner is not None:
            update_doc["owner"] = update_data.owner
        if update_data.description is not None:
            update_doc["description"] = update_data.description
        if update_data.tags is not None:
            update_doc["tags"] = update_data.tags
        
        if update_data.name:
            existing = self.collection.find_one({
                "_id": {"$ne": ObjectId(dataset_id)},
                "name": update_data.name,
                "owner": update_data.owner or self.get_dataset_by_id(dataset_id)["owner"],
                "is_deleted": False
            })
            
            if existing:
                raise ValueError("Dataset with this name already exists for this owner")
        
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(dataset_id), "is_deleted": False},
            {"$set": update_doc},
            return_document=True
        )
        
        return result

    def delete_dataset(self, dataset_id: str) -> bool:
        """Soft delete a dataset"""
        if not ObjectId.is_valid(dataset_id):
            return False
        
        result = self.collection.update_one(
            {"_id": ObjectId(dataset_id), "is_deleted": False},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        total_datasets = self.collection.count_documents({"is_deleted": False})
        
        pipeline = [
            {"$match": {"is_deleted": False}},
            {"$group": {"_id": "$owner", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_owners = list(self.collection.aggregate(pipeline))
        
        pipeline = [
            {"$match": {"is_deleted": False}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_tags = list(self.collection.aggregate(pipeline))
        
        return {
            "total_datasets": total_datasets,
            "top_owners": top_owners,
            "top_tags": top_tags
        }
