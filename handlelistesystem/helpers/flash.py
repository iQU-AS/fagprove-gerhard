from collections import defaultdict
from typing import Literal
from fastapi import Request

type Category = Literal['success', 'error']


def flash(request: Request, message: str, category: Category = 'error'):
    request.session.setdefault('_flashes', defaultdict(list))[category].append(message)


def get_flashed_messages(request: Request):
    # return request.session.pop('_flashes', defaultdict(list))
    # test example
    return {
        'success': [
            'Success message 1',
            'Success message 2',
        ],
        'error': [
            'Error message 1',
            'Error message 2',
        ],
    }
