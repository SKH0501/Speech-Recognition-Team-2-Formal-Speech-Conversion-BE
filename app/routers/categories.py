from fastapi import APIRouter

router = APIRouter(prefix="/api/categories", tags=["categories"])


CATEGORIES  =[
    {"id": "food", "name": "밥"},
    {"id": "name", "name": "이름"},
    {"id": "age", "name": "나이"},
    {"id":"birthday", "name" : "생일"}  
]

@router.get("")
def categories():
    return {
        
        "success" : True,
        "data" : CATEGORIES ,    
    }