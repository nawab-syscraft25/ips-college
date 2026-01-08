# 🔌 UI Integration Guide for Admin Routes

This guide shows you exactly how to connect the new UI templates to your FastAPI routes.

---

## 📦 New Templates Created

| File | Purpose |
|------|---------|
| `templet/base.html` | Main admin layout (UPDATED) |
| `templet/admin/pages_list.html` | Page list/grid view |
| `templet/admin/page_builder.html` | Drag-drop page designer |
| `templet/admin/page_seo.html` | SEO optimization panel |
| `templet/admin/colleges.html` | College management (UPDATED) |

---

## 🚀 Quick Integration - Step by Step

### **Step 1: Update Imports in admin.py**

```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schema import Page, PageSection, College, SEOMeta
from app.utils.college_context import get_college_pages, inherit_page, create_standard_pages_for_college
import os

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templet")
```

---

### **Step 2: Pages List Route**

```python
@router.get("/pages", response_class=HTMLResponse)
async def pages_list(
    request: Request,
    college_id: int = None,
    db: Session = Depends(get_db)
):
    """Display list of pages for selected college"""
    
    # Get college context
    selected_college_id = college_id or getattr(request.state, 'selected_college_id', None)
    
    # Get all colleges for dropdown
    colleges = db.query(College).filter(College.is_active == True).all()
    
    # Get pages for this college
    pages = []
    if selected_college_id:
        pages = get_college_pages(db, selected_college_id, include_inherited=True)
    
    return templates.TemplateResponse("admin/pages_list.html", {
        "request": request,
        "title": "Pages",
        "subtitle": f"Manage pages for {selected_college_id}",
        "colleges": colleges,
        "selected_college_id": selected_college_id,
        "pages": pages,
    })
```

---

### **Step 3: Page Builder Route**

```python
@router.get("/page/{page_id}/design", response_class=HTMLResponse)
async def page_builder(
    request: Request,
    page_id: int = None,
    college_id: int = None,
    db: Session = Depends(get_db)
):
    """Page builder/designer interface"""
    
    selected_college_id = college_id or getattr(request.state, 'selected_college_id', None)
    colleges = db.query(College).filter(College.is_active == True).all()
    
    page = None
    if page_id:
        page = db.query(Page).filter(Page.id == page_id).first()
    
    return templates.TemplateResponse("admin/page_builder.html", {
        "request": request,
        "title": page.title if page else "New Page",
        "colleges": colleges,
        "selected_college_id": selected_college_id,
        "page": page,
    })

# Save page design
@router.post("/page/{page_id}/design")
async def save_page_design(
    page_id: int,
    request: Request,
    college_id: int,
    db: Session = Depends(get_db)
):
    """Save page title and sections"""
    form_data = await request.form()
    
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        page = Page(college_id=college_id, title=form_data.get('title', 'Untitled'))
        db.add(page)
    
    page.title = form_data.get('title')
    page.background_color = form_data.get('background_color', '#ffffff')
    page.is_published = form_data.get('is_published') == 'on'
    
    db.commit()
    return {"status": "success", "page_id": page.id}
```

---

### **Step 4: SEO Panel Routes**

```python
@router.get("/page/{page_id}/seo", response_class=HTMLResponse)
async def page_seo(
    request: Request,
    page_id: int,
    college_id: int = None,
    db: Session = Depends(get_db)
):
    """SEO optimization panel"""
    
    selected_college_id = college_id or getattr(request.state, 'selected_college_id', None)
    colleges = db.query(College).filter(College.is_active == True).all()
    
    page = db.query(Page).filter(Page.id == page_id).first()
    
    return templates.TemplateResponse("admin/page_seo.html", {
        "request": request,
        "title": f"SEO: {page.title if page else 'Unknown'}",
        "colleges": colleges,
        "selected_college_id": selected_college_id,
        "page": page,
        "domain": "ipsacademy.edu.in",
    })

# Save SEO settings
@router.post("/page/{page_id}/seo")
async def save_page_seo(
    page_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Save SEO meta information"""
    form_data = await request.form()
    
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        return {"status": "error", "message": "Page not found"}
    
    # Get or create SEO meta
    seo_meta = page.seo_meta or SEOMeta()
    seo_meta.meta_title = form_data.get('meta_title')
    seo_meta.meta_description = form_data.get('meta_description')
    seo_meta.focus_keyword = form_data.get('focus_keyword')
    seo_meta.og_title = form_data.get('og_title')
    seo_meta.og_description = form_data.get('og_description')
    seo_meta.og_image = form_data.get('og_image')
    seo_meta.no_index = form_data.get('no_index') == 'on'
    seo_meta.no_follow = form_data.get('no_follow') == 'on'
    
    # Calculate scores (simplified)
    seo_meta.seo_score = 70 + (len(seo_meta.focus_keyword or '') > 0) * 15
    seo_meta.readability_score = 80
    
    if not page.seo_meta:
        page.seo_meta = seo_meta
    
    db.commit()
    return {"status": "success", "seo_score": seo_meta.seo_score}
```

---

### **Step 5: Page CRUD Routes**

```python
@router.get("/page/new", response_class=HTMLResponse)
async def new_page(
    request: Request,
    college_id: int,
    db: Session = Depends(get_db)
):
    """New page creation form"""
    colleges = db.query(College).filter(College.is_active == True).all()
    
    return templates.TemplateResponse("admin/page_builder.html", {
        "request": request,
        "title": "New Page",
        "colleges": colleges,
        "selected_college_id": college_id,
        "page": None,
    })

@router.post("/page/create")
async def create_page(
    request: Request,
    college_id: int,
    db: Session = Depends(get_db)
):
    """Create new page"""
    form_data = await request.form()
    
    page = Page(
        college_id=college_id,
        title=form_data.get('title', 'Untitled Page'),
        slug=form_data.get('title', 'untitled').lower().replace(' ', '-'),
        is_published=False
    )
    
    db.add(page)
    db.commit()
    
    return {"status": "success", "page_id": page.id}

@router.post("/page/{page_id}/delete")
async def delete_page(
    page_id: int,
    college_id: int,
    db: Session = Depends(get_db)
):
    """Delete a page"""
    page = db.query(Page).filter(Page.id == page_id, Page.college_id == college_id).first()
    
    if page:
        db.delete(page)
        db.commit()
        return {"status": "success"}
    
    return {"status": "error", "message": "Page not found"}
```

---

### **Step 6: Section Management Routes**

```python
@router.post("/page/{page_id}/section/add")
async def add_section(
    page_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Add a new section to page"""
    form_data = await request.form()
    
    # Get highest sort_order for this page
    max_order = db.query(PageSection).filter(
        PageSection.page_id == page_id
    ).count()
    
    section = PageSection(
        page_id=page_id,
        section_type=form_data.get('section_type'),
        section_description=form_data.get('description', ''),
        sort_order=max_order + 1
    )
    
    db.add(section)
    db.commit()
    
    return {"status": "success", "section_id": section.id}

@router.post("/page/{page_id}/section/{section_id}/edit")
async def edit_section(
    page_id: int,
    section_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Edit section content"""
    form_data = await request.form()
    
    section = db.query(PageSection).filter(
        PageSection.id == section_id,
        PageSection.page_id == page_id
    ).first()
    
    if section:
        section.section_description = form_data.get('description')
        section.background_color = form_data.get('background_color')
        db.commit()
        return {"status": "success"}
    
    return {"status": "error"}

@router.post("/page/{page_id}/section/{section_id}/delete")
async def delete_section(
    page_id: int,
    section_id: int,
    db: Session = Depends(get_db)
):
    """Delete a section"""
    section = db.query(PageSection).filter(
        PageSection.id == section_id,
        PageSection.page_id == page_id
    ).first()
    
    if section:
        db.delete(section)
        db.commit()
        return {"status": "success"}
    
    return {"status": "error"}
```

---

### **Step 7: College Routes (Updated)**

```python
@router.get("/colleges", response_class=HTMLResponse)
async def list_colleges(request: Request, db: Session = Depends(get_db)):
    """List all colleges with new card UI"""
    
    colleges = db.query(College).filter(College.is_active == True).all()
    
    return templates.TemplateResponse("admin/colleges.html", {
        "request": request,
        "title": "Manage Colleges",
        "subtitle": "View and manage all colleges and institutes",
        "colleges": colleges,
        "selected_college_id": None,
    })

@router.get("/colleges/new", response_class=HTMLResponse)
async def new_college_form(request: Request, db: Session = Depends(get_db)):
    """New college form"""
    parent_colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/college_form.html", {
        "request": request,
        "title": "Create New College",
        "parent_colleges": parent_colleges,
    })

@router.post("/colleges/create")
async def create_college(request: Request, db: Session = Depends(get_db)):
    """Create new college"""
    form_data = await request.form()
    
    college = College(
        name=form_data.get('name'),
        parent_id=form_data.get('parent_id') or None,
        established_year=int(form_data.get('established_year', 0)),
        is_active=form_data.get('is_active') == 'on',
        slug=form_data.get('name', '').lower().replace(' ', '-')
    )
    
    db.add(college)
    db.commit()
    
    # Create standard pages
    create_standard_pages_for_college(db, college.id, college.name)
    
    return {"status": "success", "college_id": college.id}
```

---

## 🎯 Template Context Variables

Each template expects these variables in the response:

### **All Admin Templates:**
```python
{
    "request": Request,                    # Starlette request object
    "title": str,                         # Page title
    "colleges": List[College],            # All colleges for dropdown
    "selected_college_id": int or None,   # Currently selected college
}
```

### **Page List Template:**
```python
{
    ...base variables...
    "subtitle": str,                      # Page subtitle
    "pages": List[Page],                  # Pages to display
}
```

### **Page Builder Template:**
```python
{
    ...base variables...
    "page": Page or None,                 # Existing page or None for new
}
```

### **SEO Template:**
```python
{
    ...base variables...
    "page": Page,                         # Page with SEO meta
    "domain": str,                        # Domain for URL preview
}
```

---

## 🔗 URL Structure

All routes follow this pattern:

```
/admin/pages?college_id=X                  # List pages
/admin/page/new?college_id=X               # New page
/admin/page/{id}/design?college_id=X       # Design page
/admin/page/{id}/seo?college_id=X          # SEO settings
/admin/page/{id}/delete?college_id=X       # Delete page

/admin/colleges                            # List colleges
/admin/colleges/new                        # New college form
/admin/colleges/{id}/edit                  # Edit college form
```

---

## ✅ Testing Checklist

After integration:

- [ ] College selector dropdown loads all colleges
- [ ] Selecting college changes college_id in URL
- [ ] Pages list shows only selected college's pages
- [ ] Page builder loads without errors
- [ ] Sections can be added/edited/deleted
- [ ] Page title updates in header
- [ ] SEO panel loads page's SEO meta
- [ ] Character counters work (title, description)
- [ ] Save buttons work and redirect correctly
- [ ] Mobile view is responsive
- [ ] Search/filter on pages list works
- [ ] College cards display hierarchy

---

## 🐛 Common Issues & Fixes

### **404 on Template**
```
Error: TemplateNotFound
Fix: Ensure templates are in correct folder:
- templet/admin/pages_list.html
- templet/admin/page_builder.html
- templet/admin/page_seo.html
```

### **College Selector Not Working**
```
Error: Colleges list empty
Fix: Ensure colleges query returns active colleges:
colleges = db.query(College).filter(College.is_active == True).all()
```

### **CSS Not Loading**
```
Error: Styles missing
Fix: Ensure static folder is mounted in main.py:
app.mount("/static", StaticFiles(directory="templet/static"), name="static")
```

### **Form Submissions Fail**
```
Error: 422 Unprocessable Entity
Fix: Use form_data = await request.form() not request.json()
```

---

## 📝 Notes

1. **college_id must be in URL** - All college content routes require ?college_id=X
2. **Page objects must have college_id** - Filter queries by both page_id AND college_id
3. **Sections belong to pages** - When deleting pages, sections cascade delete
4. **SEO is optional** - Create SEO meta only when needed
5. **Timestamps auto-set** - created_at and updated_at are automatic

---

**Version**: 1.0
**Status**: Ready for Implementation
**Last Updated**: January 2026
