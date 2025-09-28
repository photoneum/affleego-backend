"""Pagination utilities for standardized API responses."""

from typing import Any

from django.core.paginator import Page, Paginator


class PaginationHelper:
    """Helper class for building standardized pagination metadata."""

    def __init__(self, paginator: Paginator, page_obj: Page) -> None:
        """Initialize with Django paginator and page objects.

        Args:
            paginator: Django Paginator instance
            page_obj: Django Page instance from paginator.get_page()
        """
        self.paginator = paginator
        self.page_obj = page_obj

    def build_response(self, serialized_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Build standardized pagination response with data and metadata.

        Args:
            serialized_data: List of serialized objects for current page

        Returns:
            Dictionary with 'results' and 'pagination' keys
        """
        return {
            'results': serialized_data,
            'pagination': self.get_pagination_metadata(),
        }

    def get_pagination_metadata(self) -> dict[str, Any]:
        """Get standardized pagination metadata.

        Returns:
            Dictionary containing pagination information
        """
        return {
            'current_page': self.page_obj.number,
            'total_pages': self.paginator.num_pages,
            'page_size': self.paginator.per_page,
            'total_count': self.paginator.count,
            'has_next': self.page_obj.has_next(),
            'has_previous': self.page_obj.has_previous(),
            'next_page': self.page_obj.next_page_number() if self.page_obj.has_next() else None,
            'previous_page': self.page_obj.previous_page_number()
            if self.page_obj.has_previous()
            else None,
        }

    @classmethod
    def paginate_queryset(
        cls,
        queryset: Any,
        page: int,
        page_size: int,
        serializer_class: Any,
        serializer_context: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], bool]:
        """Convenience method to paginate a queryset and return formatted response.

        Args:
            queryset: Django QuerySet to paginate
            page: Page number (1-based)
            page_size: Number of items per page
            serializer_class: DRF Serializer class for serializing objects
            serializer_context: Optional context to pass to serializer

        Returns:
            Tuple of (response_data, is_valid_page)
            - response_data: Formatted pagination response or error info
            - is_valid_page: Boolean indicating if page number is valid
        """
        paginator = Paginator(queryset, page_size)

        # Check if page number is valid
        if page > paginator.num_pages:
            return {
                'error': f'Page {page} does not exist. Total pages: {paginator.num_pages}',
                'total_pages': paginator.num_pages,
            }, False

        page_obj = paginator.get_page(page)

        # Serialize the data
        context = serializer_context or {}
        serializer = serializer_class(page_obj.object_list, many=True, context=context)

        # Build response using helper
        helper = cls(paginator, page_obj)
        return helper.build_response(serializer.data), True
