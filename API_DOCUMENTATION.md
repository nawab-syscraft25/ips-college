# IPS College Backend API Documentation

## Base URL
```
http://127.0.0.1:7777/api/v1
```

## API Endpoints

### 1. COLLEGES

#### List All Colleges
```
GET /colleges
```
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 11,
      "name": "IPS Academy",
      "slug": "ips academy",
      "description": "College description",
      "logo": null,
      "color": "#004aad"
    }
  ]
}
```

#### Get College Details
```
GET /colleges/{college_id}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 11,
    "name": "IPS Academy",
    "slug": "ips academy",
    "description": "College description",
    "logo": null,
    "theme_color": "#004aad",
    "stats": {
      "courses": 5,
      "faculty": 10,
      "facilities": 8,
      "events": 3
    },
    "courses": [ {...} ],
    "faculty": [ {...} ],
    "facilities": [ {...} ],
    "placements": { "year": 2024, "highest": 15, "average": 8 },
    "admission": { "procedure": "...", "eligibility": "..." }
  }
}
```

---

### 2. PAGES

#### List All Pages
```
GET /pages?college_id=11&page_type=HOME
```
**Query Parameters:**
- `college_id` (optional): Filter by college
- `page_type` (optional): Filter by page type

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 11,
      "title": "Home",
      "slug": "home",
      "college_id": 11,
      "page_type": "STATIC",
      "template_type": null
    }
  ]
}
```

#### Get Page Details (with Sections)
```
GET /pages/{page_id}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "page": {
      "id": 11,
      "title": "Home",
      "slug": "home",
      "college_id": 11,
      "college_name": "IPS Academy"
    },
    "seo": {
      "title": "Page Title",
      "description": "Meta description",
      "url": "https://example.com",
      "image": "https://example.com/image.jpg"
    },
    "sections": [
      {
        "id": 9,
        "type": "HERO",
        "title": "Hero Section",
        "subtitle": "Subtitle",
        "description": null,
        "background_image": "/path/to/image.jpg",
        "background_color": null,
        "items": [ {...} ],
        "extra_data": { "hero_image_url": "...", "hero_text_color": "white" }
      }
    ]
  }
}
```

---

### 3. COURSES

#### List All Courses
```
GET /courses?college_id=11
```
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "B.Tech Computer Science",
      "slug": "btech-cs",
      "college_id": 11,
      "level": "Bachelor",
      "department": "Engineering",
      "duration": "4 years",
      "fees": "500000"
    }
  ]
}
```

#### Get Course Details
```
GET /courses/{course_id}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "B.Tech Computer Science",
    "slug": "btech-cs",
    "college_id": 11,
    "college_name": "IPS Academy",
    "level": "Bachelor",
    "department": "Engineering",
    "duration": "4 years",
    "fees": "500000",
    "eligibility": "12th Pass with 60%",
    "overview": "Course overview text",
    "curriculum": { "semester1": [...] },
    "career_opportunities": "Software Engineer, Data Scientist...",
    "admission_process": "Merit-based admission"
  }
}
```

---

### 4. FACULTY

#### List Faculty
```
GET /faculty?college_id=11
```
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Dr. John Doe",
      "college_id": 11,
      "designation": "Professor",
      "photo": "https://example.com/photo.jpg"
    }
  ]
}
```

#### Get Faculty Details
```
GET /faculty/{faculty_id}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Dr. John Doe",
    "college_id": 11,
    "college_name": "IPS Academy",
    "designation": "Professor",
    "qualification": "PhD Computer Science",
    "photo": "https://example.com/photo.jpg",
    "bio": "Biography text"
  }
}
```

---

### 5. FACILITIES

#### List Facilities
```
GET /facilities?college_id=11
```
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Computer Lab",
      "description": "Modern computer lab with latest systems",
      "image": "https://example.com/facility.jpg"
    }
  ]
}
```

#### Get Facility Details
```
GET /facilities/{facility_id}
```

---

### 6. PLACEMENTS

#### List Placements
```
GET /placements?college_id=11
```
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "college_id": 11,
      "year": 2024,
      "highest": 15,
      "average": 8,
      "percentage": 95
    }
  ]
}
```

---

### 7. ACTIVITIES

#### List Activities
```
GET /activities?college_id=11
```
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Annual Fest",
      "type": "Event",
      "description": "Cultural and management events",
      "image": "https://example.com/event.jpg",
      "date": "2025-12-22T09:01:12"
    }
  ]
}
```

---

### 8. SUBMISSIONS

#### Submit Application
```
POST /applications/submit
Content-Type: application/json

{
  "college_id": 11,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "course_id": 1,
  "documents": null
}
```

#### Submit Enquiry
```
POST /enquiries/submit
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "message": "I'm interested in your programs",
  "college_id": 11
}
```

---

### 9. SEARCH

#### Global Search
```
GET /search?query=engineering&search_type=colleges
```
**Query Parameters:**
- `query` (required): Search term (min 2 chars)
- `search_type` (optional): `colleges`, `pages`, `courses`, `faculty`

**Response:**
```json
{
  "status": "success",
  "query": "engineering",
  "results": {
    "colleges": [ {...} ],
    "pages": [ {...} ],
    "courses": [ {...} ],
    "faculty": [ {...} ]
  }
}
```

---

## Response Format

All endpoints follow a standard response format:

### Success Response
```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

---

## Key Features

✅ **Clean, Simple API** - Only essential fields returned
✅ **Optimized for Frontend** - Matches design requirements
✅ **Dynamic Content** - Everything stored in database
✅ **Pagination Ready** - Limits on large result sets (20-50 items)
✅ **Filter Support** - Filter by college, type, etc.
✅ **SEO Optimized** - SEO metadata included in pages
✅ **Form Submissions** - Applications and enquiries
✅ **Global Search** - Cross-entity search capability
✅ **Error Handling** - Proper HTTP status codes
✅ **Database Efficient** - Optimized queries with proper indexing
