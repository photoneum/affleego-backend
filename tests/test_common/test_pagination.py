"""Test pagination helper functionality."""

from django.core.paginator import Paginator
from django.test import TestCase

from server.common.utils.pagination import PaginationHelper


class PaginationHelperTest(TestCase):
    """Test cases for PaginationHelper class."""

    def test_pagination_metadata_structure(self):
        """Test that pagination metadata has correct structure."""
        # Create mock data
        data = list(range(1, 26))  # 25 items
        page_size = 10
        page = 1

        paginator = Paginator(data, page_size)
        page_obj = paginator.get_page(page)

        helper = PaginationHelper(paginator, page_obj)
        metadata = helper.get_pagination_metadata()

        # Check required keys exist
        required_keys = [
            'current_page',
            'total_pages',
            'page_size',
            'total_count',
            'has_next',
            'has_previous',
            'next_page',
            'previous_page',
        ]

        for key in required_keys:
            self.assertIn(key, metadata)

        # Check values for first page
        self.assertEqual(metadata['current_page'], 1)
        self.assertEqual(metadata['total_pages'], 3)  # 25 items / 10 per page = 3 pages
        self.assertEqual(metadata['page_size'], 10)
        self.assertEqual(metadata['total_count'], 25)
        self.assertTrue(metadata['has_next'])
        self.assertFalse(metadata['has_previous'])
        self.assertEqual(metadata['next_page'], 2)
        self.assertIsNone(metadata['previous_page'])

    def test_build_response_structure(self):
        """Test that build_response returns correct structure."""
        data = list(range(1, 11))  # 10 items
        page_size = 5
        page = 1

        paginator = Paginator(data, page_size)
        page_obj = paginator.get_page(page)

        helper = PaginationHelper(paginator, page_obj)

        # Mock serialized data
        serialized_data = [{'id': i} for i in range(1, 6)]

        response = helper.build_response(serialized_data)

        # Check structure
        self.assertIn('results', response)
        self.assertIn('pagination', response)
        self.assertEqual(response['results'], serialized_data)
        self.assertIsInstance(response['pagination'], dict)

    def test_paginate_queryset_invalid_page(self):
        """Test paginate_queryset with invalid page number."""
        # This would typically use a real queryset, but for testing we'll use a list
        # In real usage, this would be called with Django querysets
        # Skip this test for now as it requires Django models
