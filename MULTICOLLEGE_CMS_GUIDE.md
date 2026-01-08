# Multi-College WordPress-Like CMS Implementation

## Overview
Your IPS Academy CMS now supports a hierarchical multi-college structure where:
- **IPS Academy** (root/parent) manages the main website
- **Child colleges** (IBMR, SOC, ISR, etc.) have their own pages, courses, faculty, and content
- **Page inheritance** allows child colleges to inherit pages from parents
- **Full page builder** with SEO optimization (WordPress-like)

## Database Schema Changes

### College Model
```python
# Added methods to College model:
- get_root_college(): Get the parent college in hierarchy
- is_child(): Check if college is a child
```

### Page Model - New Fields
```python
- parent_page_id: Link to inherited parent page
- is_inheritable: Mark page as inheritable by child colleges
- template_type: Page template (HERO_SECTION, COURSES_LIST, etc)
- Background fields: background_type, background_color, background_image, background_gradient
```

### PageSection Model - Enhanced
```python
# New section types: HERO, ABOUT, STATS, COURSES, FACULTY, PLACEMENTS, FACILITIES, TESTIMONIALS, ACHIEVEMENTS, FAQ, FORM, MEDIA_GALLERY, TEXT, CARDS
- section_description: Description for section
- background_type/color/image/gradient: Design customization
```

### SEOMeta Model - Enhanced
```python
- focus_keyword: Target keyword
- readability_score: good, okay, needs improvement
- seo_score: 0-100 SEO score
```

## New Utilities

### `app/utils/college_context.py`
Handles all college-scoped queries:

```python
# Get college hierarchy
get_college_hierarchy(db, college_id)
get_root_college(db, college_id)
get_all_colleges_in_hierarchy(db, college_id)

# Scoped queries
get_college_pages(db, college_id, include_inherited=False)
get_college_courses(db, college_id)
get_college_faculty(db, college_id)
get_college_placements(db, college_id)
get_college_activities(db, college_id)
get_college_facilities(db, college_id)
get_college_admissions(db, college_id)
get_college_applications(db, college_id)
get_college_enquiries(db, college_id)

# Page management
get_or_create_page(db, college_id, slug, defaults)
inherit_page(db, parent_page_id, child_college_id)
create_standard_pages_for_college(db, college_id, college_name)
```

### `app/core/college_middleware.py`
Middleware to manage college context in admin panel.

## Updating Admin Routes

### Pattern: College-Scoped Listing

**Before:**
```python
@router.get("/courses")
def list_courses(request: Request, db: Session = Depends(get_db)):
    courses = db.query(Course).all()  # Shows all courses
```

**After:**
```python
from app.utils.college_context import get_college_courses

@router.get("/courses")
def list_courses(request: Request, db: Session = Depends(get_db)):
    college_id = getattr(request.state, "selected_college_id", None)
    if not college_id:
        college_id = request.session.get("selected_college_id")
    
    college = db.query(College).filter(College.id == college_id).first()
    
    if not college:
        courses = []
    else:
        courses = get_college_courses(db, college.id)
    
    colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/courses.html", {
        "request": request,
        "title": f"Courses - {college.name if college else 'Select a College'}",
        "courses": courses,
        "colleges": colleges,
        "selected_college_id": college.id if college else None,
    })
```

### Pattern: College-Scoped Creation

**Before:**
```python
@router.post("/courses/new")
async def create_course(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    course = Course(
        college_id=1,  # Hardcoded!
        name=form_data.get("name"),
        ...
    )
```

**After:**
```python
@router.post("/courses/new")
async def create_course(request: Request, db: Session = Depends(get_db)):
    college_id = getattr(request.state, "selected_college_id", None)
    if not college_id:
        college_id = request.session.get("selected_college_id")
    
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        return RedirectResponse(url="/admin/courses")
    
    form_data = await request.form()
    course = Course(
        college_id=college.id,  # Dynamic!
        name=form_data.get("name"),
        ...
    )
    db.add(course)
    db.commit()
    
    return RedirectResponse(url=f"/admin/courses?college_id={college.id}")
```

## Frontend Templates

### Base Template Enhancement
`templet/base.html` now includes:
- **College selector dropdown** in top-right corner
- **Dynamic sidebar** that shows college-specific menu items once selected
- Automatic context passing to child templates

### Page Builder Macros
`templet/includes/page_builder_macros.html` provides ready-to-use section renderers:

```jinja
{{ hero_section(section) }}
{{ about_section(section) }}
{{ stats_section(section) }}
{{ courses_section(section, courses) }}
{{ faculty_section(section, faculty) }}
{{ placements_section(section, placement_data) }}
{{ facilities_section(section, facilities) }}
{{ cards_section(section) }}
{{ text_section(section) }}
{{ render_page(page, colleges, courses, faculty, placement, facilities) }}
```

## Migration Steps

### 1. Create Alembic Migration
```bash
alembic revision --autogenerate -m "add_page_inheritance_and_templates"
```

The migration will add:
- `parent_page_id` column to pages table
- `is_inheritable` column to pages table
- `template_type` column to pages table
- Background columns to page_sections table
- New columns to seo_meta table
- New indexes for performance

### 2. Update Admin.py
See `app/api/v1/admin_examples.py` for complete examples.

Key changes:
1. Import college context utilities
2. Add `get_selected_college()` helper at start of each handler
3. Replace hardcoded college IDs with `college.id`
4. Pass `colleges` and `selected_college_id` to templates
5. Update form submissions to use selected college

### 3. Update Templates
- All admin list templates should pass `selected_college_id` to links
- All forms should use query params: `?college_id={{ selected_college_id }}`
- Add college selector dropdown (already in base.html)

### Example Template Change
```html
<!-- Before -->
<a href="/admin/courses/{{ course.id }}/edit">Edit</a>

<!-- After -->
<a href="/admin/courses/{{ course.id }}/edit?college_id={{ selected_college_id }}">Edit</a>
```

## Usage Examples

### Create Standard Pages for New College
```python
from app.utils.college_context import create_standard_pages_for_college

@router.post("/colleges/new")
async def create_college(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    college = College(
        name=form_data.get("name"),
        slug=form_data.get("slug"),
        is_parent=form_data.get("is_parent") == "on",
    )
    db.add(college)
    db.commit()
    db.refresh(college)
    
    # Auto-create standard pages
    create_standard_pages_for_college(db, college.id, college.name)
    
    return RedirectResponse(url="/admin/colleges")
```

### Inherit Parent Pages to Child College
```python
from app.utils.college_context import inherit_page

# When creating a child college, inherit parent pages
parent_pages = db.query(Page).filter(
    Page.college_id == parent_id,
    Page.is_inheritable == True
).all()

for parent_page in parent_pages:
    inherit_page(db, parent_page.id, child_college_id)
```

### Get Pages with Inheritance
```python
from app.utils.college_context import get_college_pages

# Get both owned and inherited pages
pages = get_college_pages(db, college_id, include_inherited=True)
```

## Page Types & Templates

Standard pages are automatically created for each college:

| Page Type | Template | Use Case |
|-----------|----------|----------|
| HOME | HERO_SECTION | College home page with hero banner |
| ABOUT | BLANK | About college info |
| COURSES | COURSES_LIST | List all courses offered |
| FACULTY | FACULTY_LIST | Faculty directory |
| PLACEMENTS | PLACEMENTS | Placement statistics & details |
| FACILITIES | FACILITIES_LIST | Campus facilities showcase |
| ADMISSIONS | BLANK | Admission procedures & info |
| CONTACT | BLANK | Contact form & details |

## SEO Features

Each page now has comprehensive SEO:
- Meta title, description, keywords
- Open Graph (OG) tags for social sharing
- Canonical URL
- JSON-LD schema markup
- Focus keyword tracking
- Readability score
- SEO score (0-100)

## Admin Dashboard Flow

1. **Login** → Admin dashboard
2. **Select College** → Dropdown in topbar
3. **Navigate Menu** → Sidebar updates with college-specific items
4. **Manage Content** → Pages, courses, faculty, etc. (all filtered by college)
5. **Page Builder** → Edit pages with drag-drop sections
6. **SEO Editor** → Optimize meta tags and content

## Child College Features

Child colleges can:
- ✅ Have their own pages
- ✅ Inherit parent pages
- ✅ Override inherited pages
- ✅ Have own courses, faculty, placements
- ✅ Use own color scheme/theme
- ✅ Have separate applications/enquiries

## Performance Tips

1. Use `include_inherited=False` by default for faster queries
2. Cache college hierarchy with Redis for high-traffic sites
3. Index on `college_id` and `parent_id` for quick lookups
4. Consider pagination for large result sets

## Next Steps

1. [ ] Generate and run Alembic migration
2. [ ] Update all admin endpoints following examples
3. [ ] Update admin templates with college selector links
4. [ ] Test college selection and content filtering
5. [ ] Create frontend pages using page_builder_macros
6. [ ] Set up SEO editor UI in admin panel
7. [ ] Add page inheritance management UI
