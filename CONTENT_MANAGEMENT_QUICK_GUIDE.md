# 📋 Content Management Guide - Easy Operations

## Quick Management Operations

### Bulk Operations

#### Managing Multiple Pages
```
Dashboard → Pages Section → View All
→ Select pages → Bulk Actions (Publish/Archive)
```

#### Managing Courses
```
Dashboard → Click "Courses" stat card
→ View all courses → Filter by college/status
→ Edit or delete individual courses
```

#### Managing Faculty
```
Dashboard → Overview → Click "Faculty Members"
→ View faculty list → Search by name
→ Edit profiles → Update photos
```

---

## Forms & Submissions

### Handling Applications

**View Applications:**
1. Dashboard → Recent Applications (or View All)
2. See applicant details instantly
3. Check applied course
4. Review application status

**Change Status:**
1. Click application row
2. Select new status:
   - **Pending** → Under review
   - **Approved** → Accepted
   - **Rejected** → Not selected
3. Save changes
4. Status auto-notified (if email enabled)

**Download Application:**
- Click Download/Export button
- Get applicant data with documents
- Use for archival records

### Handling Enquiries

**View Inquiries:**
1. Admin → Enquiries section
2. See visitor name, email, message
3. View inquiry date and status

**Follow Up:**
1. Click on enquiry
2. Add internal notes
3. Mark as "Contacted" when done
4. Track response status

---

## Page Builder Operations

### Creating Sections

**Available Section Types:**
- **Hero**: Large banner with image & CTA
- **About**: College/program overview
- **Stats**: Statistics blocks
- **Courses**: Course listing section
- **Faculty**: Faculty directory
- **Facilities**: Facility showcase
- **Activities**: Event listing
- **Testimonials**: Student/staff quotes
- **FAQ**: Frequently asked questions
- **Form**: Inquiry/contact form
- **Text**: Custom HTML content
- **Cards**: Feature cards grid

### Section Settings

**Each Section Has:**
- Title & subtitle
- Background image/color
- Sort order
- Active/inactive toggle
- Type-specific settings

**Quick Tips:**
- Hero sections should have clear CTA
- Use images max 2MB for speed
- Keep text short and readable
- Order sections logically (Hero first)
- Test mobile view

### Adding Items to Sections

**Items Can Include:**
- Title and description
- Image and/or video
- Call-to-action button
- Custom links
- Sort order

**Item Types by Section:**
- **Courses**: Course preview cards
- **Faculty**: Faculty profile cards
- **Facilities**: Facility photos
- **Testimonials**: Quote cards
- **FAQ**: Question/answer pairs

---

## Media Management

### Uploading Images

**Best Practices:**
```
✓ Format: JPG, PNG, or WebP
✓ Size: Compress before upload
✓ Max: 5MB per file
✓ Dimensions: 
  - Hero: 1920x600 px
  - Cards: 400x300 px
  - Thumbnails: 200x200 px
```

**Using Media Library:**
1. Admin → CMS → Media Library
2. Click "Upload New"
3. Select image file
4. Add title and alt text
5. Organize by folder
6. Use in content

### Image Optimization

**Tools to Use:**
- TinyPNG.com - Compress images
- Canva - Resize images
- Photopea.com - Edit online
- ImageMagick - Batch conversion

**When to Compress:**
- Before uploading
- Keep quality high
- Reduce file size
- Improve page speed

---

## Menus & Navigation

### Creating Navigation Menus

**Step 1: Create Menu**
1. Admin → CMS → Menus
2. Click "New Menu"
3. Enter menu title (e.g., "Main Menu")
4. Click Create

**Step 2: Add Items**
1. Click menu to edit
2. Click "Add Item"
3. Enter label (what shows)
4. Enter URL (where it links)
5. Set order/position
6. Mark as active

**Step 3: Setup Dropdowns**
1. Create parent menu item
2. Add child items (indented)
3. Child items appear as dropdown
4. Set active state
5. Save

**Menu Types:**
- **Main Menu**: Top navigation
- **Footer Menu**: Bottom links
- **Sidebar**: Left/right menu
- **Mobile**: Mobile-specific menu

### Managing Menu Items

**Edit Item:**
1. Click item in menu
2. Change label or URL
3. Reorder with drag
4. Toggle active/inactive
5. Save

**Delete Item:**
1. Click item
2. Click Delete
3. Confirm deletion
4. Item removed from menu

**Best Practices:**
- Keep menu items brief
- Limit main menu to 5-7 items
- Use logical grouping
- Update active page indicator
- Test menu links regularly

---

## College Management

### Setting Up a College

**Required Info:**
- College name
- Slug (URL identifier)
- Logo image
- Primary color
- Parent college (if branch)

**Optional Settings:**
- Subdomain
- Contact info
- Social media links
- Additional themes
- Custom settings

### College Settings

**Basic Settings:**
- Name and description
- Logo and banner
- Brand colors
- Contact details

**Advanced Settings:**
- Domain mapping
- Subdomain routing
- Custom templates
- API access

### Multi-College Setup

**When You Have Multiple Colleges:**

1. **Create College Base**
   - Add college info
   - Upload logo
   - Set colors

2. **Create Separate Content**
   - Pages per college
   - Courses per college
   - Faculty per college
   - Facilities per college

3. **Organize**
   - Use filters by college
   - Avoid mixing content
   - Maintain consistency

**Example Structure:**
```
Main College (Parent)
├── Electronics Department
├── Mechanical Department
└── Computer Department

Each with:
- Separate pages
- Own courses
- Own faculty
- Shared facilities
```

---

## Content Organization

### Folder Structure Best Practices

**Recommended Organization:**
```
Pages/
├── Home
├── About
├── Academics
│   ├── Courses
│   ├── Programs
│   └── Faculty
├── Admissions
│   ├── Application
│   └── Eligibility
├── Campus Life
│   ├── Activities
│   ├── Facilities
│   └── Placement
└── Contact

Media/
├── Hero Images
├── Faculty Photos
├── Campus Photos
├── Logos
└── Icons

Courses/
├── Engineering
├── Management
├── Sciences
└── Arts

Faculty/
├── Department Name
└── Faculty Name
```

### Naming Conventions

**Pages:**
- Use lowercase
- Hyphenate spaces (about-us)
- Keep short (max 50 chars)
- Be descriptive

**Images:**
- Descriptive names (faculty-john-doe.jpg)
- Include date if relevant (event-2025-01.jpg)
- Avoid special characters
- Use standard formats

**Files:**
- Use version numbers (course-v2.pdf)
- Include department (engg-2024-syllabus.pdf)
- Date format: YYYY-MM-DD

---

## Batch Operations

### Publishing Multiple Pages
1. Select pages to publish
2. Click "Bulk Publish"
3. Confirm action
4. All pages go live

### Archiving Content
1. Select items to archive
2. Click "Archive"
3. Content hidden but retained
4. Can restore anytime

### Deleting Content
1. Select items
2. Click "Delete"
3. Permanent - cannot restore
4. Confirm carefully

### Moving Content Between Colleges
1. Select content
2. Choose new college
3. Click "Move"
4. Content transfers
5. Update references if needed

---

## Quality Checks

### Before Publishing

**Content Checklist:**
- [ ] All fields filled (title, description, etc.)
- [ ] Images uploaded and optimized
- [ ] Links tested and working
- [ ] Spelling and grammar correct
- [ ] Formatting looks good
- [ ] Mobile view verified
- [ ] SEO metadata complete
- [ ] College assignment correct

**Image Checklist:**
- [ ] File size reasonable
- [ ] Resolution adequate
- [ ] Alt text provided
- [ ] No copyrighted content
- [ ] Matches site branding
- [ ] Mobile-friendly size

**Link Checklist:**
- [ ] All links functional
- [ ] No broken links
- [ ] External links open new tab
- [ ] Anchor links work
- [ ] Email links formatted

### Testing Published Content

**Mobile Test:**
1. Open page on phone
2. Check layout
3. Test navigation
4. Verify images
5. Test forms

**Desktop Test:**
1. View in browser
2. Check resolution
3. Test responsiveness
4. Verify all features
5. Check performance

**Functionality Test:**
1. Click all buttons
2. Test forms
3. Verify filters
4. Check sorting
5. Test search

---

## Performance Tips

### Page Speed Optimization

**Image Optimization:**
- Compress before upload
- Use appropriate formats
- Avoid oversized images
- Use thumbnails for lists

**Content Organization:**
- Limit items per page (20-50)
- Use pagination
- Lazy load images
- Minimize redirects

**Caching:**
- Enable browser cache
- Use CDN if available
- Cache database queries
- Compress assets

### Database Maintenance

**Regular Tasks:**
- Backup database weekly
- Archive old content
- Delete unused media
- Optimize tables
- Monitor disk space

---

## Common Tasks Quick Reference

| Task | Steps | Time |
|------|-------|------|
| Create Page | Title → College → SEO → Publish | 5 min |
| Add Course | Name → Details → Faculty → Publish | 10 min |
| Add Faculty | Name → Photo → Bio → Publish | 5 min |
| Upload Image | Select → Compress → Upload → Organize | 2 min |
| Process Application | View → Change Status → Save | 1 min |
| Create Menu | Title → Items → Order → Publish | 10 min |
| Setup College | Info → Logo → Colors → Publish | 15 min |

---

## Keyboard Shortcuts

**Save**: Ctrl+S / Cmd+S  
**Publish**: Ctrl+Enter / Cmd+Enter  
**Preview**: Ctrl+Shift+P / Cmd+Shift+P  
**Edit**: Ctrl+E / Cmd+E  
**Delete**: Ctrl+Shift+D / Cmd+Shift+D  
**Search**: Ctrl+F / Cmd+F  

---

## Troubleshooting Common Issues

### Image Won't Upload
- Check file size (max 5MB)
- Try different format (JPG vs PNG)
- Verify file isn't corrupted
- Check file permissions
- Try uploading to media library first

### Page Won't Publish
- Check required fields
- Verify college selected
- Check for broken links
- Verify media attached
- Check user permissions

### Content Not Showing
- Verify marked as "Active"
- Check college assignment
- Clear browser cache
- Check page visibility settings
- Verify correct URL

### Search Not Working
- Rebuild search index
- Check database connection
- Clear cache
- Verify content published
- Check search settings

---

## Best Practices Summary

✅ **DO:**
- Plan content before creating
- Use descriptive titles
- Organize logically
- Test before publishing
- Keep backups
- Update regularly
- Monitor performance

❌ **DON'T:**
- Upload huge images
- Publish incomplete content
- Use special characters
- Leave required fields empty
- Mix content between colleges
- Forget to save work
- Ignore SEO metadata

---

**Version**: 1.0  
**Last Updated**: January 2026
