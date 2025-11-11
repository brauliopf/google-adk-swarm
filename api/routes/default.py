from fastapi import APIRouter

# Create router instance
router = APIRouter(prefix="/api/v1", tags=["App"])

######################################
# Health Check
######################################
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Agents Swarm API"}

@router.get("/")
def read_root():
    return {"message": "Welcome to Agents Swarm API", "status": "running"}