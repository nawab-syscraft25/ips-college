# Multi-College CMS Architecture Diagram

## Database Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         COLLEGES TABLE                          │
├─────────────┬──────────┬───────────┬────────────┬───────────────┤
│ id (PK)     │ name     │ slug      │ parent_id  │ is_parent     │
├─────────────┼──────────┼───────────┼────────────┼───────────────┤
│ 1           │ IPS Academy │ ips-academy │ NULL   │ TRUE          │
│ 2           │ IBMR     │ ibmr      │ 1          │ FALSE         │
│ 3           │ SOC      │ soc       │ 1          │ FALSE         │
│ 4           │ ISR      │ isr       │ 1          │ FALSE         │
│ ...         │ ...      │ ...       │ ...        │ ...           │
└─────────────┴──────────┴───────────┴────────────┴───────────────┘
                              │
                              │ One-to-Many
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          PAGES TABLE                            │
├─────────┬──────────┬──────────┬───────────┬──────────┬───────────┤
│ id (PK) │ college  │ slug     │ title     │parent_pg │inheritable│
├─────────┼──────────┼──────────┼───────────┼──────────┼───────────┤
│ 1       │ 1 (IPS)  │ home     │ IPS Home  │ NULL     │ TRUE      │
│ 2       │ 1 (IPS)  │ about    │ About IPS │ NULL     │ TRUE      │
│ 3       │ 2 (IBMR) │ home     │ IBMR Home │ 1        │ FALSE     │
│ 4       │ 2 (IBMR) │ courses  │ Courses   │ NULL     │ FALSE     │
│ ...     │ ...      │ ...      │ ...       │ ...      │ ...       │
└─────────┴──────────┴──────────┴───────────┴──────────┴───────────┘
                              │
                              │ One-to-Many
                              ▼
┌──────────────────────────────────────────────────────┐
│            PAGE_SECTIONS TABLE                      │
├────────┬────────┬──────────┬──────────┬─────────────┤
│ id     │ page_id│ type     │ title    │ sort_order  │
├────────┼────────┼──────────┼──────────┼─────────────┤
│ 1      │ 1      │ HERO     │ Hero     │ 0           │
│ 2      │ 1      │ ABOUT    │ About    │ 1           │
│ 3      │ 1      │ COURSES  │ Courses  │ 2           │
│ ...    │ ...    │ ...      │ ...      │ ...         │
└────────┴────────┴──────────┴──────────┴─────────────┘
                              │
                              │ One-to-Many
                              ▼
┌──────────────────────────────────────────────────────┐
│            SECTION_ITEMS TABLE                      │
├────────┬──────────┬──────────┬──────────┬───────────┤
│ id     │ section_ │ title    │ content  │sort_order │
│        │ id       │          │          │           │
├────────┼──────────┼──────────┼──────────┼───────────┤
│ 1      │ 1        │ Hero Text│ Welcome  │ 0         │
│ 2      │ 3        │ Course 1 │ B.Tech   │ 0         │
│ ...    │ ...      │ ...      │ ...      │ ...       │
└────────┴──────────┴──────────┴──────────┴───────────┘

┌──────────────────────────────────────────────────────┐
│             SEO_META TABLE                          │
├────────┬────────┬──────────────┬───────────┬────────┤
│ id     │ page_id│ meta_title   │ keywords  │seo_scor│
├────────┼────────┼──────────────┼───────────┼────────┤
│ 1      │ 1      │ IPS Home ... │ education │ 92     │
│ 2      │ 2      │ About IPS... │ history   │ 88     │
│ ...    │ ...    │ ...          │ ...       │ ...    │
└────────┴────────┴──────────────┴───────────┴────────┘
```

## Hierarchy Structure

```
                         ┌─────────────────────┐
                         │   IPS ACADEMY       │
                         │  (Root Parent)      │
                         │  id=1, is_parent=T  │
                         └─────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
          ┌──────────┐      ┌──────────┐      ┌──────────┐
          │   IBMR   │      │    SOC   │      │    ISR   │
          │ id=2     │      │  id=3    │      │  id=4    │
          │parent=1  │      │parent=1  │      │parent=1  │
          └──────────┘      └──────────┘      └──────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
    ┌────────┐   ┌─────────┐
    │ Alumni │   │ Counseling
    │ id=5   │   │ id=6
    │parent=2│   │parent=2
    └────────┘   └─────────┘

Each college can have:
- Pages (Home, About, Courses, etc)
- Courses
- Faculty
- Placements
- Facilities
- Applications
- Enquiries
```

## Page Inheritance Flow

```
PARENT COLLEGE (IPS Academy)
│
├─ PAGE: "Home"
│  └─ is_inheritable: TRUE
│     (Can be used by child colleges)
│
├─ PAGE: "About"
│  └─ is_inheritable: TRUE
│
└─ PAGE: "Courses"
   └─ is_inheritable: FALSE
      (Child colleges must create their own)


CHILD COLLEGE (IBMR)
│
├─ PAGE: "Home" (Inherited from parent, read-only)
│  └─ parent_page_id: 1
│     (Points to parent's home page)
│
├─ PAGE: "About" (Inherited from parent, read-only)
│  └─ parent_page_id: 2
│
├─ PAGE: "Courses" (Own page, not inherited)
│  └─ parent_page_id: NULL
│     (Custom courses page for IBMR)
│
└─ PAGE: "Faculty" (Own page)
   └─ parent_page_id: NULL
```

## Admin Panel Flow

```
┌──────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                                     │
│                                                      │
│  Topbar:                                            │
│  ┌────────────────────────────────────────────────┐ │
│  │ IPS Admin | [College ▼] | Logout              │ │
│  │           ├─ IPS Academy                       │ │
│  │           ├─ IBMR        ← User selects       │ │
│  │           ├─ SOC                               │ │
│  │           └─ ISR                               │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  Sidebar Updates:                                   │
│  ┌──────────────────────┐                          │
│  │ Dashboard            │                          │
│  │ CMS                  │                          │
│  │ ├─ Menus             │                          │
│  │ ├─ Pages             │                          │
│  │ ├─ Media             │                          │
│  │ Colleges             │                          │
│  │ College Content      │◄─ Now shows selected    │
│  │ ├─ Courses ────────┐ │   college's items      │
│  │ ├─ Faculty        │ │   (if IBMR selected)   │
│  │ ├─ Placements     │ │                        │
│  │ ├─ Applications   │ │                        │
│  │ └─ Enquiries      │ │                        │
│  └──────────────────────┘                          │
│                                                      │
│  Main Content Area:                                 │
│  ┌──────────────────────────────────────────────┐ │
│  │ Courses - IBMR                               │ │
│  │                                               │ │
│  │ [+ New Course]                               │ │
│  │                                               │ │
│  │ ┌──────────────┐  ┌──────────────┐          │ │
│  │ │ B.Tech CSE   │  │ B.Tech ECE    │          │ │
│  │ │ [Edit][Del]  │  │ [Edit][Del]   │          │ │
│  │ └──────────────┘  └──────────────┘          │ │
│  │                                               │ │
│  │ All items filtered by IBMR college_id ◄─────│ │
│  └──────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Query Flow for College-Scoped Content

```
USER VISITS ADMIN
│
▼
┌─────────────────────────┐
│ Check Session           │
│ college_id = 2 (IBMR)   │
└─────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────┐
│ User navigates to /admin/courses?college_id=2      │
└─────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────┐
│ Handler: list_courses()                            │
│ college = _get_selected_college(request, db)       │
│ → Returns College(id=2, name="IBMR")               │
└─────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────┐
│ Query Database:                                    │
│ courses = db.query(Course).filter(               │
│     Course.college_id == 2  ◄─ Filter by IBMR    │
│ ).all()                                           │
└─────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────┐
│ Render Template:                                    │
│ return templates.TemplateResponse(                │
│     "admin/courses.html",                        │
│     {                                             │
│         "courses": [...IBMR courses only...],    │
│         "selected_college_id": 2,                │
│         "colleges": [...all root colleges...]    │
│     }                                             │
│ )                                                  │
└─────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────┐
│ User sees ONLY IBMR's 5 courses                    │
│ (Not courses from IPS, SOC, ISR, etc)             │
│ ✅ Data isolation achieved!                        │
└─────────────────────────────────────────────────────┘
```

## Page Builder Section Types

```
Available Section Types:

┌─────────────────────┐
│ HERO                │  ← Hero banner with CTA
│ ┌─────────────────┐ │
│ │  Hero Section   │ │
│ │  Large image    │ │
│ │  [CTA Button]   │ │
│ └─────────────────┘ │
└─────────────────────┘

┌─────────────────────┐
│ ABOUT               │  ← About/Description
│ ┌─────────────────┐ │
│ │ About Title     │ │
│ │ Description text│ │
│ └─────────────────┘ │
└─────────────────────┘

┌─────────────────────┐
│ STATS               │  ← Key numbers
│ ┌──────┬──────────┐ │
│ │ 500+ │ 1500+    │ │
│ │ Alum │ Students │ │
│ └──────┴──────────┘ │
└─────────────────────┘

┌─────────────────────┐
│ COURSES             │  ← Course grid
│ ┌──────┬──────────┐ │
│ │ B.Tec│ B.Tech   │ │
│ │ h CSE│ ECE      │ │
│ └──────┴──────────┘ │
└─────────────────────┘

┌─────────────────────┐
│ FACULTY             │  ← Faculty cards
│ ┌──────┬──────────┐ │
│ │ Photo│ Photo    │ │
│ │ Name │ Name     │ │
│ └──────┴──────────┘ │
└─────────────────────┘

┌─────────────────────┐
│ FACILITIES          │  ← Facility cards
│ ┌──────┬──────────┐ │
│ │ Image│ Image    │ │
│ │ Name │ Name     │ │
│ └──────┴──────────┘ │
└─────────────────────┘

(And more: PLACEMENTS, TESTIMONIALS, FAQ, FORM, etc)
```

---

This architecture ensures:
✅ Multi-tenant isolation
✅ Flexible page hierarchy
✅ Inheritance of common content
✅ College-specific customization
✅ WordPress-like editing experience
