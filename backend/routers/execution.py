import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user


router = APIRouter(tags=["Execution"])

JUDGE0_URL = "https://ce.judge0.com/submissions?base64_encoded=false&wait=true"

LANGUAGE_IDS = {
    "python": 109,
    "javascript": 102,
    "typescript": 101,
    "java": 91,
    "cpp": 105,
    "go": 107,
}


class ExecuteRequest(BaseModel):
    code: str
    language: str


@router.post("/execute")
async def execute_code(
    payload: ExecuteRequest,
    current_user=Depends(get_current_user),
):
    language_id = LANGUAGE_IDS.get(payload.language)

    if not language_id:
        raise HTTPException(status_code=400, detail="Unsupported language")

    try:
        async with httpx.AsyncClient(timeout=20) as http_client:
            response = await http_client.post(
                JUDGE0_URL,
                json={
                    "source_code": payload.code,
                    "language_id": language_id,
                },
            )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Could not reach the code execution service"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Code execution service error"
        )

    result = response.json()

    return {
        "stdout": result.get("stdout") or "",
        "stderr": result.get("stderr") or "",
        "compile_output": result.get("compile_output") or "",
        "status": result.get("status", {}).get("description", "Unknown"),
    }
