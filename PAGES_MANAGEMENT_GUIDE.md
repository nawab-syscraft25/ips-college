# 📄 Pages Management - Quick Reference

## Accessing Pages Management

**Dashboard → Pages stat card → View All**  
or  
**Admin Navigation → Pages**  
or  
Direct: `http://localhost:7777/admin/pages`

---

## Pages List View

The pages management interface shows all pages with quick actions:

### Available Actions

| Action | Icon | What It Does |
|--------|------|-------------|
| **Edit** | ⚙️ | Edit page title, slug, college, and metadata |
| **Design** | 🎨 | Add/edit page sections (Hero, About, Courses, etc.) |
| **SEO** | 🔍 | Configure meta tags, keywords, Open Graph |
| **Delete** | 🗑️ | Permanently remove the page |

### Page Information Displayed

- **Title**: Page name
- **Slug**: URL identifier (e.g., `/about-us`)
- **College**: Which college this page belongs to
- **Sections**: Number of content sections
- **Modified**: Last edit date

---

## Creating a New Page

### Method 1: From Dashboard
1. Click **Quick Actions → Create Page**
2. Fill in basic info
3. Click **Create Page**

### Method 2: From Pages List
1. Go to **Pages Management**
2. Click **New Page** button (top right)
3. Enter page details
4. Click **Create**

### Required Information

- **Page Title**: What the page will be called
- **College**: Which college it belongs to
- **Slug**: URL-friendly identifier (auto-generated if empty)

### Optional Information

- **Meta Title**: For search engines (60 chars)
- **Meta Description**: Search preview (160 chars)
- **Keywords**: SEO keywords (comma-separated)
- **Open Graph Tags**: Social media sharing info

---

## Editing a Page

### Edit Page Properties
1. Find page in list
2. Click **Edit** button
3. Modify:
   - Title
   - Slug
   - College assignment
   - Status (Published/Draft)
   - SEO metadata
4. Click **Save Changes**

### Design Page Sections
1. Find page in list
2. Click **Design** button
3. Add/edit sections:
   - Click "Add Section"
   - Choose section type (Hero, Text, Cards, etc.)
   - Configure section
   - Add items to section
4. Reorder sections by dragging
5. Click **Save**

### Optimize for Search
1. Find page in list
2. Click **SEO** button
3. Fill in:
   - Meta title
   - Meta description
   - Focus keywords
   - Canonical URL
   - Schema markup
4. Click **Save**

---

## Section Types Available

### Hero Section
- Large banner image
- Title and subtitle
- Call-to-action button
- Background styling

### Text/Content Section
- Rich text editor
- HTML support
- Formatting options
- Image embedding

### About Section
- Company/college overview
- Statistics display
- Team listing
- Mission statement

### Stats Section
- Number counters
- Performance metrics
- Achievement showcase
- Animated counters

### Courses Section
- Course listing
- Filter by department
- Course cards
- Linked to course database

### Faculty Section
- Faculty directory
- Profile cards
- Filter options
- Linked to faculty database

### Facilities Section
- Facility showcase
- Image gallery
- Description cards
- Linked to facilities

### Activities Section
- Event listing
- Date-based display
- Activity cards
- Linked to activities

### Testimonials Section
- Student/staff quotes
- Profile photos
- Rating display
- Carousel view

### FAQ Section
- Question/answer pairs
- Accordion display
- Expandable items
- Search functionality

### Form Section
- Contact forms
- Inquiry forms
- Newsletter signup
- Custom fields

### Cards Section
- Feature cards
- Icon cards
- Icon + text combo
- Grid layout

---

## Best Practices

### Page Organization
✅ **DO:**
- Use clear, descriptive titles
- Keep slugs short and simple
- Organize by college
- Publish completed pages only
- Use consistent naming

❌ **DON'T:**
- Use special characters in slugs
- Publish incomplete content
- Have duplicate page titles
- Leave SEO fields empty
- Mix content from different colleges

### Section Arrangement
✅ **DO:**
- Place Hero section first
- Follow logical flow
- Use white space between sections
- Keep sections focused
- Test on mobile

❌ **DON'T:**
- Overcrowd with sections
- Use conflicting colors
- Ignore mobile view
- Skip section titles
- Mix too many section types

### Image & Media
✅ **DO:**
- Compress images before upload
- Use descriptive alt text
- Keep file sizes small (<2MB)
- Use consistent image sizes
- Optimize for web

❌ **DON'T:**
- Upload large uncompressed images
- Use images without alt text
- Mix image styles/quality
- Skip image optimization
- Use copyrighted images

### SEO Optimization
✅ **DO:**
- Write descriptive meta titles (50-60 chars)
- Include keywords naturally
- Create compelling descriptions (150-160 chars)
- Use relevant keywords
- Add schema markup for products/events

❌ **DON'T:**
- Stuff keywords unnaturally
- Exceed character limits
- Use generic descriptions
- Ignore keywords
- Leave SEO fields blank

---

## Common Tasks

### Publishing a Page
1. Edit page
2. Mark as "Published"
3. Fill in SEO metadata
4. Review sections
5. Click "Publish"

### Copying a Page
1. Create new page
2. Use similar title/slug
3. Replicate sections
4. Modify content as needed
5. Publish

### Moving Page to Different College
1. Edit page
2. Change college in dropdown
3. Update related links
4. Save changes

### Archiving Old Content
1. Edit page
2. Mark as "Draft"
3. Keep for reference
4. Not visible on site

### Deleting a Page
1. Find page in list
2. Click **Delete** button
3. Confirm deletion
4. Page permanently removed
5. Update related links first!

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save page |
| Ctrl+P | Publish |
| Ctrl+Shift+D | Delete |
| Ctrl+F | Search pages |
| Tab | Navigate form fields |

---

## Troubleshooting

### Page Won't Save
**Problem**: "Error saving page"
- Check required fields are filled
- Verify college is selected
- Check for broken media links
- Try refreshing and retry

### Slug Already Exists
**Problem**: "This slug is already in use"
- Use different slug
- Add college name to slug
- Add number suffix (e.g., about-us-2)
- Rename existing page first

### Sections Not Showing
**Problem**: Sections don't appear on page
- Mark page as "Published"
- Check sections are "Active"
- Verify section visibility
- Clear browser cache
- Check browser console for errors

### Images Not Displaying
**Problem**: Page shows broken images
- Upload images to media library first
- Use correct image URLs
- Check image file size
- Verify image format (JPG, PNG, WebP)
- Check image permissions

### SEO Not Applied
**Problem**: Meta tags not showing in search
- Wait for search engine re-crawl (24-48 hrs)
- Verify page is published
- Check meta tags are filled
- Submit to Google Search Console
- Check for duplicate pages

---

## Performance Tips

### Optimize Page Speed
1. Compress images before upload
2. Limit sections per page (5-8 ideal)
3. Use lazy loading for images
4. Avoid heavy video embeds
5. Minimize custom JavaScript

### Mobile Optimization
1. Test all pages on mobile
2. Keep text readable at small sizes
3. Stack sections vertically
4. Use touch-friendly buttons
5. Test form functionality

### SEO Performance
1. Fill all SEO fields
2. Use descriptive alt text
3. Create unique meta descriptions
4. Use heading hierarchy (H1, H2, H3)
5. Link internally between pages

---

## File Organization Best Practices

### Naming Convention
```
Home Page: home
About Us: about-us
Contact: contact
Courses: courses or programs
Faculty: faculty or teachers
Admission: admissions or apply
News: news or blog
```

### College-Specific Pages
```
Engineering/
├── home (college home)
├── about-engineering
├── engineering-courses
├── engineering-faculty
└── placements

Management/
├── home (college home)
├── about-management
├── mba-programs
├── management-faculty
└── corporate-relations
```

---

## Admin Tips

**Quick Access:**
- Bookmark `/admin/pages` for quick access
- Use breadcrumb navigation
- Remember keyboard shortcuts
- Keep frequently edited pages handy

**Workflow:**
1. Plan content before creating
2. Create page structure
3. Add sections
4. Fill content
5. Optimize SEO
6. Test thoroughly
7. Publish

**Maintenance:**
- Monthly content review
- Update outdated information
- Archive old news/events
- Check broken links
- Monitor analytics

---

## Dashboard Stats

On the main admin dashboard, you can see:
- **Total Pages**: Count of all pages
- **Recent Pages**: Last 5 modified pages
- **Page Status**: Published vs Draft

Click the "Pages" stat card for full list.

---

**Last Updated**: January 2026  
**Version**: 2.0
