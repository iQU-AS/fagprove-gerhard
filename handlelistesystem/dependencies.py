from fastapi import HTTPException, Request, Response


async def get_user_redirect(request: Request, response: Response):
    user = request.cookies.get('user')

    try:
        user = int(user)  # type: ignore
    except (TypeError, ValueError):
        user = None

    if not user:
        response.delete_cookie(key='user')
        raise HTTPException(status_code=307, headers={'Location': '/login'})
    return user
