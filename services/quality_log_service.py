from datetime import datetime
from bson import ObjectId
from utils.database import get_db
from models.quality_log import QualityLogCreate
from typing import List, Optional, Dict, Any

class QualityLogService:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.quality_logs

    def create_quality_log(self, dataset_id: str, log_data: QualityLogCreate) -> Dict[str, Any]:
        """Create a new quality log for a dataset"""
        if not ObjectId.is_valid(dataset_id):
            raise ValueError("Invalid dataset ID")
        
        dataset_exists = self.db.datasets.find_one({
            "_id": ObjectId(dataset_id),
            "is_deleted": False
        })
        
        if not dataset_exists:
            raise ValueError("Dataset not found")
        
        log_doc = {
            "dataset_id": ObjectId(dataset_id),
            "status": log_data.status,
            "details": log_data.details,
            "timestamp": datetime.utcnow()
        }
        
        result = self.collection.insert_one(log_doc)
        log_doc["_id"] = result.inserted_id
        
        return log_doc

    def get_quality_logs(self, dataset_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get quality logs for a dataset with pagination"""
        if not ObjectId.is_valid(dataset_id):
            raise ValueError("Invalid dataset ID")
        
        query = {"dataset_id": ObjectId(dataset_id)}
        
        skip = (page - 1) * limit
        
        total = self.collection.count_documents(query)
        
        logs = list(
            self.collection.find(query)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        
        return {
            "logs": logs,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    def get_quality_summary(self, dataset_id: str) -> Dict[str, Any]:
        """Get quality summary for a dataset"""
        if not ObjectId.is_valid(dataset_id):
            raise ValueError("Invalid dataset ID")
        
        pipeline = [
            {"$match": {"dataset_id": ObjectId(dataset_id)}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        summary = {"PASS": 0, "FAIL": 0}
        for result in results:
            summary[result["_id"]] = result["count"]
        
        total_logs = sum(summary.values())
        
        return {
            "total_logs": total_logs,
            "pass_count": summary["PASS"],
            "fail_count": summary["FAIL"],
            "pass_rate": (summary["PASS"] / total_logs * 100) if total_logs > 0 else 0
        }

    def get_latest_quality_status(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest quality status for a dataset"""
        if not ObjectId.is_valid(dataset_id):
            return None
        
        latest_log = self.collection.find_one(
            {"dataset_id": ObjectId(dataset_id)},
            sort=[("timestamp", -1)]
        )
        
        return latest_log
