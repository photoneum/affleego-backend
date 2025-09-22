# Affleego Backend Implementation Plan

## Overview

This document outlines the backend implementation plan for supporting the Next.js frontend dashboard refactoring. The plan follows Django REST Framework patterns and ensures OpenAPI contract compatibility for type-safe frontend development.

## Current Backend Analysis

### Existing Infrastructure
- **Django 5.2** with DRF and drf-spectacular for OpenAPI
- **Authentication**: JWT with SimpleJWT
- **Database**: PostgreSQL
- **Existing Apps**: `main`, `users`, `deals`
- **Response Pattern**: `ApiResponse` class for standardized responses
- **Code Style**: Following `AGENTS.md` guidelines

### Existing Models & APIs
- **User Management**: `User`, `VerificationCode`, `UserOnboarding` models
- **Authentication**: Complete auth flow with JWT tokens
- **Deals**: `Deal` model with basic CRUD and featured deals endpoint
- **Current API Endpoints**:
  - `POST /api/v1/auth/register` - User registration
  - `POST /api/v1/auth/verify` - Email verification
  - `POST /api/v1/auth/login` - JWT login
  - `GET /api/v1/deals` - List deals
  - `GET /api/v1/deals/featured` - Featured deals

## Implementation Plan by Phase

### Phase 1: Core Dashboard Infrastructure (Priority 1)

#### New Models Required

```python
# server/apps/main/models.py
@final
class CommunityStats(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for storing community statistics."""

    weekly_ftds = models.IntegerField(_('weekly FTDs'), default=0)
    top_geo = models.CharField(_('top GEO'), max_length=100, blank=True)
    total_affiliates = models.IntegerField(_('total affiliates'), default=0)
    total_deals = models.IntegerField(_('total deals'), default=0)
    week_starting = models.DateField(_('week starting'))

    class Meta:
        verbose_name = _('Community Stats')
        verbose_name_plural = _('Community Stats')
        ordering = ['-week_starting']

# server/apps/users/models.py (extend existing User model)
class User(AbstractUser, UUIDMixin):
    # Add new fields to existing model
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    locale = models.CharField(_('locale'), max_length=10, default='en')
    last_login_ip = models.GenericIPAddressField(_('last login IP'), null=True, blank=True)
```

#### New API Endpoints

```python
# server/apps/main/views.py
@extend_schema(tags=['Dashboard'])
class DashboardViewSet(viewsets.GenericViewSet):
    """ViewSet for dashboard operations."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DashboardOverviewSerializer},
        description='Get dashboard overview data including user greeting and community stats',
        summary='Dashboard Overview',
    )
    @action(detail=False, methods=['get'])
    def overview(self, request: Request) -> Response:
        """Get dashboard overview data."""
        pass

# server/apps/users/views.py (extend existing AuthViewSet)
class AuthViewSet(viewsets.GenericViewSet):
    # Add new action to existing viewset
    @extend_schema(
        responses={200: UserProfileSerializer},
        description='Get complete user profile data',
        summary='User Profile',
    )
    @action(detail=False, methods=['get'])
    def profile(self, request: Request) -> Response:
        """Get user profile data."""
        pass

    @extend_schema(
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer},
        description='Update user profile data',
        summary='Update User Profile',
    )
    @action(detail=False, methods=['put'])
    def update_profile(self, request: Request) -> Response:
        """Update user profile data."""
        pass
```

**Required API Endpoints:**
- `GET /api/v1/dashboard/overview` - User greeting + community stats
- `GET /api/v1/auth/profile` - Complete user profile
- `PUT /api/v1/auth/profile` - Update user profile

### Phase 2: Deals & Deals System (Priority 2)

#### Model Enhancements

```python
# server/apps/deals/models.py (extend existing Deal model)
@final
class Deal(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    # Add new fields to existing model
    category = models.CharField(_('category'), max_length=100, blank=True)
    geo_restrictions = models.CharField(_('geo restrictions'), max_length=255, blank=True)
    conversion_rate = models.DecimalField(_('CR %'), max_digits=5, decimal_places=2, null=True, blank=True)
    epc = models.DecimalField(_('EPC'), max_digits=10, decimal_places=2, null=True, blank=True)
    weekly_performance = models.JSONField(_('weekly performance'), default=dict, blank=True)

# New models
@final
class DealMetrics(UUIDMixin, CreatedAtMixin, models.Model):
    """Model for storing deal performance metrics."""

    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='metrics')
    week_starting = models.DateField(_('week starting'))
    clicks = models.IntegerField(_('clicks'), default=0)
    conversions = models.IntegerField(_('conversions'), default=0)
    revenue = models.DecimalField(_('revenue'), max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Deal Metrics')
        verbose_name_plural = _('Deal Metrics')
        unique_together = ['deal', 'week_starting']
```

#### Enhanced API Endpoints

```python
# server/apps/deals/views.py (enhance existing DealViewSet)
@extend_schema(tags=['Deals'])
class DealViewSet(viewsets.ModelViewSet):
    # Add filtering and pagination to existing viewset
    filterset_fields = ['category', 'status', 'is_featured']
    search_fields = ['name', 'description', 'keywords']
    ordering_fields = ['created_at', 'conversion_rate', 'epc']

    @extend_schema(
        responses={200: DealDetailResponseSerializer(many=True)},
        description='Get top performing deals with rankings',
        summary='Top Deals',
    )
    @action(detail=False, methods=['get'])
    def top(self, request: Request) -> Response:
        """Get top performing deals."""
        pass
```

**Required API Endpoints:**
- `GET /api/v1/deals` (enhanced with filters, pagination, search)
- `GET /api/v1/deals/featured` (existing - enhance response)
- `GET /api/v1/deals/top` - Top performing deals with metrics

### Phase 3: Announcements & Promotions (Priority 2)

#### New Models

```python
# server/apps/main/models.py
@final
class Announcement(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for storing announcements and promotions."""

    class Type(models.TextChoices):
        PROMOTION = 'promotion', _('Promotion')
        UPDATE = 'update', _('Update')
        WEBINAR = 'webinar', _('Webinar')
        NEWS = 'news', _('News')

    title = models.CharField(_('title'), max_length=255)
    content = tinymce_models.HTMLField(_('content'))
    banner_image = models.ImageField(_('banner image'), upload_to='announcements/', blank=True)
    type = models.CharField(_('type'), max_length=20, choices=Type.choices)
    is_active = models.BooleanField(_('is active'), default=True)
    priority = models.IntegerField(_('priority'), default=0, help_text=_('Higher numbers show first'))
    starts_at = models.DateTimeField(_('starts at'))
    ends_at = models.DateTimeField(_('ends at'))
    external_link = models.URLField(_('external link'), blank=True)

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-priority', '-starts_at']

@final
class WebinarPromotion(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for webinar promotions."""

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    presenter = models.CharField(_('presenter'), max_length=255)
    scheduled_at = models.DateTimeField(_('scheduled at'))
    duration_minutes = models.IntegerField(_('duration minutes'), default=60)
    registration_link = models.URLField(_('registration link'))
    banner_image = models.ImageField(_('banner image'), upload_to='webinars/', blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    max_attendees = models.IntegerField(_('max attendees'), null=True, blank=True)

    class Meta:
        verbose_name = _('Webinar Promotion')
        verbose_name_plural = _('Webinar Promotions')
        ordering = ['scheduled_at']
```

#### New API Endpoints

```python
# server/apps/main/views.py
@extend_schema(tags=['Announcements'])
class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for announcements and promotions."""

    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter active announcements within date range."""
        now = timezone.now()
        return self.queryset.filter(
            starts_at__lte=now,
            ends_at__gte=now
        )

@extend_schema(tags=['Promotions'])
class WebinarPromotionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for webinar promotions."""

    queryset = WebinarPromotion.objects.filter(is_active=True)
    serializer_class = WebinarPromotionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def upcoming(self, request: Request) -> Response:
        """Get upcoming webinar promotions."""
        pass
```

**Required API Endpoints:**
- `GET /api/v1/announcements` - Active announcements with carousel data
- `GET /api/v1/promotions/webinars` - Webinar promotions
- `GET /api/v1/promotions/webinars/upcoming` - Upcoming webinars

### Phase 4: Support System (Priority 3)

#### New Models

```python
# server/apps/support/ (new app)
@final
class FAQCategory(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for FAQ categories."""

    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    order = models.IntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('FAQ Category')
        verbose_name_plural = _('FAQ Categories')
        ordering = ['order', 'name']

@final
class FAQ(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for frequently asked questions."""

    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(_('question'), max_length=500)
    answer = tinymce_models.HTMLField(_('answer'))
    order = models.IntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    tags = models.CharField(_('tags'), max_length=255, blank=True, help_text=_('Comma-separated tags'))

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['order', 'question']

@final
class SupportContact(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for support contact information."""

    class Type(models.TextChoices):
        EMAIL = 'email', _('Email')
        TELEGRAM = 'telegram', _('Telegram')
        WHATSAPP = 'whatsapp', _('WhatsApp')
        PHONE = 'phone', _('Phone')

    type = models.CharField(_('type'), max_length=20, choices=Type.choices)
    label = models.CharField(_('label'), max_length=255)
    value = models.CharField(_('value'), max_length=255)
    manager_name = models.CharField(_('manager name'), max_length=255, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    order = models.IntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('Support Contact')
        verbose_name_plural = _('Support Contacts')
        ordering = ['order', 'type']

@final
class ContactSubmission(UUIDMixin, CreatedAtMixin, models.Model):
    """Model for contact form submissions."""

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_submissions')
    subject = models.CharField(_('subject'), max_length=255)
    message = models.TextField(_('message'))
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.OPEN)
    admin_response = models.TextField(_('admin response'), blank=True)

    class Meta:
        verbose_name = _('Contact Submission')
        verbose_name_plural = _('Contact Submissions')
        ordering = ['-created_at']

@final
class ContactAttachment(UUIDMixin, CreatedAtMixin, models.Model):
    """Model for contact submission attachments."""

    submission = models.ForeignKey(ContactSubmission, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(_('file'), upload_to='support/attachments/')
    original_name = models.CharField(_('original name'), max_length=255)

    class Meta:
        verbose_name = _('Contact Attachment')
        verbose_name_plural = _('Contact Attachments')
```

#### New API Endpoints

```python
# server/apps/support/views.py
@extend_schema(tags=['Support'])
class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for FAQ management."""

    queryset = FAQ.objects.filter(is_active=True).select_related('category')
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']
    search_fields = ['question', 'answer', 'tags']

@extend_schema(tags=['Support'])
class SupportContactViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for support contacts."""

    queryset = SupportContact.objects.filter(is_active=True)
    serializer_class = SupportContactSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=['Support'])
class ContactSubmissionViewSet(viewsets.ModelViewSet):
    """ViewSet for contact form submissions."""

    serializer_class = ContactSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter submissions for current user."""
        return ContactSubmission.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set user from request."""
        serializer.save(user=self.request.user)
```

**Required API Endpoints:**
- `GET /api/v1/support/faq` - FAQ with categories and search
- `GET /api/v1/support/contacts` - Support contact methods
- `POST /api/v1/support/contact` - Submit contact form with attachments
- `GET /api/v1/support/contact` - User's contact submissions history

### Phase 5: Profile & External Affiliates (Priority 3)

#### New Models

```python
# server/apps/users/models.py (add to existing)
@final
class ExternalAffiliateNetwork(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for external affiliate networks."""

    name = models.CharField(_('name'), max_length=255, unique=True)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(_('logo'), upload_to='networks/', blank=True)
    verification_instructions = models.TextField(_('verification instructions'))
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('External Affiliate Network')
        verbose_name_plural = _('External Affiliate Networks')
        ordering = ['name']

@final
class UserExternalAffiliate(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for user's external affiliate accounts."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Verification')
        VERIFIED = 'verified', _('Verified')
        REJECTED = 'rejected', _('Rejected')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='external_affiliates')
    network = models.ForeignKey(ExternalAffiliateNetwork, on_delete=models.CASCADE)
    affiliate_id = models.CharField(_('affiliate ID'), max_length=255)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    verification_notes = models.TextField(_('verification notes'), blank=True)
    verified_at = models.DateTimeField(_('verified at'), null=True, blank=True)

    class Meta:
        verbose_name = _('User External Affiliate')
        verbose_name_plural = _('User External Affiliates')
        unique_together = ['user', 'network']
```

#### New API Endpoints

```python
# server/apps/users/views.py (extend existing AuthViewSet)
class AuthViewSet(viewsets.GenericViewSet):

    @extend_schema(
        responses={200: UserExternalAffiliateSerializer(many=True)},
        description='Get user external affiliate connections',
        summary='External Affiliates',
    )
    @action(detail=False, methods=['get'], url_path='external-affiliates')
    def external_affiliates(self, request: Request) -> Response:
        """Get user's external affiliate accounts."""
        pass

    @extend_schema(
        request=ExternalAffiliateVerificationSerializer,
        responses={201: UserExternalAffiliateSerializer},
        description='Verify external affiliate account',
        summary='Verify External Affiliate',
    )
    @action(detail=False, methods=['post'], url_path='external-affiliates/verify')
    def verify_external_affiliate(self, request: Request) -> Response:
        """Submit external affiliate for verification."""
        pass
```

**Required API Endpoints:**
- `GET /api/v1/auth/external-affiliates` - User's external affiliate connections
- `POST /api/v1/auth/external-affiliates/verify` - Submit for verification
- `GET /api/v1/auth/external-affiliates/networks` - Available networks

### Phase 6: Future Features Preparation (Priority 4)

#### Placeholder Models

```python
# server/apps/academy/ (new app for future)
@final
class Course(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for affiliate academy courses."""

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    is_coming_soon = models.BooleanField(_('is coming soon'), default=True)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

# server/apps/webinars/ (new app for future)
@final
class Webinar(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for webinars system."""

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    is_coming_soon = models.BooleanField(_('is coming soon'), default=True)

    class Meta:
        verbose_name = _('Webinar')
        verbose_name_plural = _('Webinars')

# server/apps/news/ (new app for future)
@final
class NewsArticle(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for news and alerts."""

    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    is_coming_soon = models.BooleanField(_('is coming soon'), default=True)

    class Meta:
        verbose_name = _('News Article')
        verbose_name_plural = _('News Articles')
```

**Placeholder API Endpoints:**
- `GET /api/v1/academy/courses` - Coming soon courses
- `GET /api/v1/webinars` - Coming soon webinars
- `GET /api/v1/news` - Coming soon news & alerts

## Implementation Steps

### Step 1: Project Setup
1. Create new Django apps: `support`, `academy`, `webinars`, `news`
2. Update `INSTALLED_APPS` in settings
3. Create URL routing for new apps

### Step 2: Model Implementation (Per Phase)
1. Create models following existing patterns (UUIDMixin, etc.)
2. Generate and run migrations
3. Register models in admin
4. Write model tests

### Step 3: Serializer Implementation
1. Create serializers following existing patterns
2. Use proper field validation
3. Include nested relationships where needed
4. Add custom methods for computed fields

### Step 4: ViewSet Implementation
1. Create ViewSets with proper permissions
2. Add `@extend_schema` decorations for OpenAPI
3. Use `ApiResponse` for consistent responses
4. Implement proper filtering and pagination
5. Add proper error handling

### Step 5: URL Configuration
1. Add URLs to app-level `urls.py`
2. Include in main `server/urls.py`
3. Ensure proper namespacing

### Step 6: Testing
1. Write comprehensive tests for each endpoint
2. Test authentication and permissions
3. Test data validation and error cases
4. Performance testing for complex queries

## Database Migrations Strategy

### Migration Order
1. **Phase 1**: Extend existing `User` model, add `CommunityStats`
2. **Phase 2**: Extend existing `Deal` model, add `DealMetrics`
3. **Phase 3**: Add `Announcement`, `WebinarPromotion` models
4. **Phase 4**: Add all support-related models
5. **Phase 5**: Add external affiliate models
6. **Phase 6**: Add placeholder future models

### Migration Best Practices
- Use `AddField` operations for extending existing models
- Create indexes for frequently queried fields
- Use database constraints where appropriate
- Include data migrations for initial data (FAQ, support contacts)

## OpenAPI Schema Compliance

### Schema Requirements
- All endpoints must have `@extend_schema` decorations
- Proper request/response serializer definitions
- Detailed descriptions and summaries
- Appropriate HTTP status codes
- Tag organization by feature area

### Generated Types Structure
```typescript
// Expected frontend types structure
interface DashboardOverview {
  user: UserProfile
  community_stats: CommunityStats
  last_login: string
}

interface Deal {
  uuid: string
  name: string
  category: string
  conversion_rate?: number
  epc?: number
  // ... other fields
}
```

## Security Considerations

### Authentication & Authorization
- All endpoints require authentication unless explicitly public
- User data isolation (users only see their own data)
- Admin-only endpoints for management operations
- Proper permission classes on all ViewSets

### Data Validation
- Input validation on all POST/PUT endpoints
- File upload restrictions and validation
- SQL injection protection via ORM
- XSS protection for HTML content fields

### Rate Limiting
- Consider implementing rate limiting for contact form submissions
- File upload size limits
- Bulk operation limits

## Performance Optimizations

### Database Optimizations
- Use `select_related` and `prefetch_related` appropriately
- Add database indexes on frequently queried fields
- Implement pagination on list endpoints
- Use database aggregations for statistics

### Caching Strategy
- Consider caching community stats (updated weekly)
- Cache FAQ data (rarely changes)
- Cache support contact information
- Use Redis for session and query caching

### Query Optimizations
- Optimize deal listing with proper filtering
- Use database-level filtering vs Python filtering
- Implement search functionality at database level
- Consider full-text search for FAQ

## Monitoring & Logging

### API Monitoring
- Track endpoint usage and performance
- Monitor error rates and response times
- Log authentication failures
- Track file upload statistics

### Business Metrics
- Deal view/click tracking
- FAQ search analytics
- Contact form submission rates
- User engagement metrics

## Development Workflow

### Branch Strategy
```bash
develop (main development branch)
├── feature/phase-1-dashboard-api
├── feature/phase-2-deals-enhancement
├── feature/phase-3-announcements
├── feature/phase-4-support-system
├── feature/phase-5-profile-management
└── feature/phase-6-future-features
```

### Code Quality
- Follow existing code style in `AGENTS.md`
- Use type hints throughout
- Maintain 100-character line limit
- Write comprehensive docstrings
- Ensure test coverage above 80%

### API Documentation
- Update OpenAPI schema after each phase
- Provide example requests/responses
- Document error responses
- Include authentication requirements

## Deployment Considerations

### Environment Variables
```bash
# Add to .env files
SUPPORT_EMAIL=support@affleego.com
TELEGRAM_SUPPORT_URL=https://t.me/affleego_support
MAX_UPLOAD_SIZE=10485760  # 10MB
FAQ_SEARCH_INDEX_UPDATE_INTERVAL=3600  # 1 hour
```

### Static Files
- Configure media file serving for uploads
- Set up CDN for announcement/webinar images
- Optimize image storage and delivery

### Background Tasks
- Consider Celery for heavy operations
- Email notifications for contact submissions
- Weekly community stats calculations
- File processing for uploads

## Success Metrics

### Technical Metrics
- [ ] All planned endpoints implemented and documented
- [ ] OpenAPI schema generates correct TypeScript types
- [ ] Response times under 200ms for simple endpoints
- [ ] Test coverage above 80%
- [ ] Zero security vulnerabilities

### Business Metrics
- [ ] Dashboard load time under 2 seconds
- [ ] Deal discovery improved with filtering/search
- [ ] Support ticket resolution through self-service FAQ
- [ ] User profile completion rate increase
- [ ] External affiliate verification process automated

## Conclusion

This implementation plan provides a structured approach to building the backend APIs required for the Next.js frontend dashboard. Each phase builds upon the previous one, allowing for incremental development and testing. The plan follows Django best practices and ensures OpenAPI compliance for seamless frontend integration.

The phased approach allows frontend development to begin as soon as Phase 1 APIs are completed, enabling parallel development and faster time to market.
