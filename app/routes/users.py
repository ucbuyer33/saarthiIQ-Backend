from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse  # Pydantic validation schema sync ke liye

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 1. response_model lagaya aur async def me convert kiya
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the complete profile details of the currently authenticated system user.
    """
    # 2. Direct object return: Pydantic response_model automatic data parse aur filter kar lega,
    # kisi manual dict mapping ki zaroorat nahi padegi!
    return current_user