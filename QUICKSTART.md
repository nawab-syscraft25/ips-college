# Quick Start Guide - Multi-College CMS

## 🚀 Get Started in 5 Steps

### Step 1: Run Database Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add_page_inheritance_and_templates"

# Review generated migration file in:
# alembic/versions/xxxx_add_page_inheritance_and_templates.py

# Apply migration to your database
alembic upgrade head
```

**What this does:**
- Adds `parent_page_id`, `is_inheritable`, `template_type` to pages table
- Adds background customization fields to page_sections table
- Adds SEO enhancement fields to seo_meta table
- Creates necessary indexes for performance

---

### Step 2: Update One Admin Route (as example)

Open `app/api/v1/admin.py` and find the `list_courses` endpoint.

Replace:
```python
@router.get("/courses", include_in_schema=False)
def list_courses(request: Request, db: Session = Depends(get_db)):
    courses = db.query(Course).all()  # ❌ Shows ALL courses
    return templates.TemplateResponse("admin/courses.html", {...})
```

With:
```python
from app.utils.college_context import get_college_courses

@router.get("/courses", include_in_schema=False)
def list_courses(request: Request, db: Session = Depends(get_db)):
    # Get selected college from session/request
    college_id = getattr(request.state, "selected_college_id", None)
    if not college_id:
        college_id = request.session.get("selected_college_id")
    
    college = db.query(College).filter(College.id == college_id).first()
    
    if not college:
        courses = []
    else:
        courses = get_college_courses(db, college.id)  # ✅ Only this college's courses
    
    all_colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/courses.html", {
        "request": request,
        "title": f"Courses - {college.name if college else 'Select a College'}",
        "courses": courses,
        "colleges": all_colleges,
        "selected_college_id": college.id if college else None,
    })
```

**Key changes:**
1. Get selected college from request state/session
2. Use `get_college_courses()` to filter by college
3. Pass `colleges` and `selected_college_id` to template

---

### Step 3: Test in Browser

1. Start your FastAPI server:
   ```bash
   python -m app.main
   # Or: uvicorn app.main:app --reload
   ```

2. Visit: `http://localhost:8000/admin`

3. Look at the **top-right corner** of the admin panel:
   - You should see a **College Selector** dropdown
   - Select a college (or create one first)

4. The **sidebar should update** with college-specific items:
   - Courses
   - Faculty
   - Placements
   - etc.

5. Click on "Courses" → Should show only selected college's courses

---

### Step 4: Create Colleges & Pages

**Create an IPS Academy college:**
```
/admin/colleges/new
- Name: IPS Academy
- Slug: ips-academy
- Is Parent: YES
- Click Save
```

**Create a child college:**
```
/admin/colleges/new
- Name: IBMR (Institute of Business Management & Research)
- Slug: ibmr
- Is Parent: NO
- Parent College: IPS Academy
- Click Save
```

This will **automatically create standard pages** for IBMR:
- Home
- About
- Courses
- Faculty
- Placements
- Facilities
- Admissions
- Contact

---

### Step 5: Manage Pages & Content

**Switch to IBMR college** using the dropdown in topbar.

**Edit IBMR Home Page:**
1. Click CMS → Pages
2. Click "IBMR - Home" page
3. Click "Edit Sections"
4. Add sections:
   - HERO section (banner)
   - ABOUT section
   - STATS section (key numbers)
   - COURSES section (course list)
   - APPLY CTA button
5. Click "Save"

**Add Courses:**
1. Click "Courses" in sidebar
2. Click "+ New Course"
3. Fill in:
   - Name: B.Tech Computer Science
   - Duration: 4 Years
   - Overview: Best engineering program
   - Click Save
4. Courses now appear in COURSES section on home page!

---

## 📋 Checklist: Apply to All Admin Routes

Use this checklist when updating each endpoint:

```
□ Import utilities:
  from app.utils.college_context import get_college_*

□ Get selected college:
  college_id = getattr(request.state, "selected_college_id", None)
  if not college_id: college_id = request.session.get("selected_college_id")
  college = db.query(College).filter(College.id == college_id).first()

□ Check if college selected:
  if not college: return error or empty list

□ Filter queries by college:
  items = get_college_courses(db, college.id)  # Instead of .all()

□ Pass to template:
  "colleges": db.query(College).filter(College.parent_id == None).all(),
  "selected_college_id": college.id if college else None,

□ Update template links:
  href="/admin/courses/{{ item.id }}/edit?college_id={{ selected_college_id }}"

□ Form submissions:
  Post to: /admin/courses/new?college_id={{ selected_college_id }}
```

---

## 📚 Routes to Update

Apply the integration pattern to these routes:

```
CMS
├─ /admin/cms/menus
├─ /admin/cms/shared-sections
├─ /admin/cms/media
└─ /admin/pages (PRIORITY)
   ├─ /admin/pages/new
   ├─ /admin/pages/{id}/edit
   ├─ /admin/pages/{id}/sections
   └─ /admin/pages/{id}/sections/{section_id}/*

Colleges (Already good)
├─ /admin/colleges
└─ /admin/colleges/{id}/edit

College Content (PRIORITY)
├─ /admin/courses → Filter by college_id ✅
├─ /admin/faculty → Filter by college_id ✅
├─ /admin/placements → Filter by college_id ✅
├─ /admin/activities → Filter by college_id ✅
├─ /admin/facilities → Filter by college_id ✅
├─ /admin/admissions → Filter by college_id ✅
├─ /admin/applications → Filter by college_id ✅
└─ /admin/enquiries → Filter by college_id ✅
```

---

## 🎨 Frontend: Render Pages

**Example: Render IBMR Home Page**

```python
from app.utils.college_context import get_college_pages
from app.schemas.schema import Page

# Get college by subdomain
college = db.query(College).filter(College.subdomain == "ibmr").first()

# Get home page
page = get_college_pages(db, college.id)[0]  # First page

# Render with macro
return templates.TemplateResponse("public/page.html", {
    "page": page,
    "college": college,
})
```

**Template:**
```html
{% from "includes/page_builder_macros.html" import render_page %}

{{ render_page(page, courses=courses, faculty=faculty) }}
```

**Output:** Professional website with all sections!

---

## 🔐 Security Notes

**Always verify college ownership before editing:**

```python
# ❌ BAD - Anyone can edit
item = db.query(Course).get(course_id)
item.name = new_name

# ✅ GOOD - Verify college ownership
college = _get_selected_college(request, db)
item = db.query(Course).filter(
    Course.id == course_id,
    Course.college_id == college.id  # ← Security check
).first()

if not item:
    return error_404()

item.name = new_name
```

---

## 🐛 Troubleshooting

**Migration fails:**
```
Issue: "Table pages doesn't have column parent_page_id"
Solution: Review the auto-generated migration, ensure it's correct, run alembic upgrade head
```

**College selector not showing:**
```
Issue: Dropdown empty or missing
Solution: Create at least one college first (must be parent college)
```

**Content from different colleges showing:**
```
Issue: "I set college_id=2 but see data from all colleges"
Solution: Forgot to filter query - use get_college_*() functions
```

**Links broken after switching colleges:**
```
Issue: Clicking link goes to wrong place
Solution: Add ?college_id={{ selected_college_id }} to all admin template links
```

---

## 📖 Reference Files

| File | Purpose |
|------|---------|
| `IMPLEMENTATION_SUMMARY.md` | Overview of all changes |
| `MULTICOLLEGE_CMS_GUIDE.md` | Detailed guide with examples |
| `INTEGRATION_PATTERNS.py` | Code patterns for all CRUD operations |
| `ARCHITECTURE_DIAGRAM.md` | Visual diagrams of structure |
| `app/utils/college_context.py` | Ready-to-use utility functions |
| `app/api/v1/admin_examples.py` | Working endpoint examples |
| `templet/includes/page_builder_macros.html` | Section rendering macros |

---

## ✅ After Integration Checklist

- [ ] Migration applied (alembic upgrade head)
- [ ] Updated 3-5 admin routes as examples
- [ ] Tested college selector dropdown
- [ ] Created test college (IBMR)
- [ ] Verified content filters by college
- [ ] Updated admin templates with college links
- [ ] Created pages with sections
- [ ] Tested page builder (add/edit sections)
- [ ] Rendered page on frontend
- [ ] Verified SEO fields save correctly

---

## 🎯 Next Phase Features

Once basic integration works, you can add:

1. **Page Inheritance UI**
   - Mark pages as "Inheritable"
   - Show inherited pages in child college
   - Allow override of inherited content

2. **SEO Editor**
   - Visual SEO score
   - Keyword density checker
   - Readability analyzer
   - Meta preview

3. **Drag-Drop Page Builder**
   - Add frontend JS for dragging sections
   - Preview before publish
   - Undo/redo support

4. **Multi-Language Support**
   - Pages in different languages
   - Language selector in admin
   - Translated menus

5. **Advanced Theme Customization**
   - Color picker for college theme
   - Font selection
   - Layout templates

---

**Questions?** Check the detailed guide: `MULTICOLLEGE_CMS_GUIDE.md`

**Ready to code?** Follow patterns in: `INTEGRATION_PATTERNS.py`

**See it working?** Check examples in: `app/api/v1/admin_examples.py`
