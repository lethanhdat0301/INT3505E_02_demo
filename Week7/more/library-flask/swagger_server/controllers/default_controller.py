import connexion
import six

from swagger_server.models.book import Book  # noqa: E501
from swagger_server import util


def books_get():  # noqa: E501
    """Lấy danh sách tất cả sách

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def books_id_delete(id):  # noqa: E501
    """Xóa sách theo ID

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: None
    """
    return 'do some magic!'


def books_id_get(id):  # noqa: E501
    """Lấy thông tin sách theo ID

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: None
    """
    return 'do some magic!'


def books_id_put(body, id):  # noqa: E501
    """Cập nhật sách theo ID

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param id: 
    :type id: int

    :rtype: None
    """
    if connexion.request.is_json:
        body = Book.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def books_post(body):  # noqa: E501
    """Thêm sách mới

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Book.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
