# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_books_get(self):
        """Test case for books_get

        Lấy danh sách tất cả sách
        """
        response = self.client.open(
            '/api/books',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_delete(self):
        """Test case for books_id_delete

        Xóa sách theo ID
        """
        response = self.client.open(
            '/api/books/{id}'.format(id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_get(self):
        """Test case for books_id_get

        Lấy thông tin sách theo ID
        """
        response = self.client.open(
            '/api/books/{id}'.format(id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_put(self):
        """Test case for books_id_put

        Cập nhật sách theo ID
        """
        body = Book()
        response = self.client.open(
            '/api/books/{id}'.format(id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_post(self):
        """Test case for books_post

        Thêm sách mới
        """
        body = Book()
        response = self.client.open(
            '/api/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
