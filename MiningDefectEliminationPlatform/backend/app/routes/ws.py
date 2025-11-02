from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from app import sockets, utils


router = APIRouter()


@router.on_event("startup")
async def startup():
    await sockets.startup()


@router.on_event("shutdown")
async def shutdown():
    await sockets.shutdown()


@router.websocket("/global")
async def global_websocket(websocket: WebSocket, token: str = None):

    try:
        db = next(utils.get_db())
        user = utils.get_current_user(db=db, token=token)
        db.close()

        await sockets.add_websocket(websocket, user.id)
    except Exception:
        try:
            await websocket.accept()
            await websocket.send_text("NO")
            await websocket.close()
        except Exception as e:
            print(e)


@router.get("/test")
def test_send_message(
    user=Depends(utils.get_current_user),
):
    sockets.send(
        user.id,
        sockets.Socket_Group.NOTIFICATION,
        dict(
            title="New Action",
            message="You have been assigned to the investigation 'Hello World'",
            type="error",
        ),
    )
