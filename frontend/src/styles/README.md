# CSS Organization Structure

This directory contains the organized CSS architecture for the RecruiterFinder application.

## 📁 File Structure

```
styles/
├── variables.css          # Design system variables
├── base.css              # Global styles & reset
├── App.css               # Main utilities & components
└── README.md             # This documentation
```

## 🎨 Design System

### Variables (`variables.css`)

Contains all design tokens:

- **Colors**: Primary purple theme, supporting colors, grayscale
- **Typography**: Font families, sizes, weights
- **Spacing**: Consistent spacing scale
- **Shadows**: Elevation system
- **Border Radius**: Rounded corner system
- **Transitions**: Animation timing
- **Z-Index**: Layer management

### Base Styles (`base.css`)

Global foundation:

- CSS Reset
- Body & html styles
- Accessibility styles
- Print styles
- Focus management

### App Styles (`App.css`)

Utility classes and base components:

- Utility classes (flexbox, spacing, text)
- Base button styles
- Form element styles
- Card components
- Animation classes
- Responsive utilities

## 🧩 Component Organization

Each component now has its own CSS file co-located with the component:

### Layout Components

- `components/layout/Layout.css` - Main layout wrapper
- `components/layout/Sidebar.css` - Navigation sidebar

### Page Components

- `components/pages/ResumeAnalysis.css` - Resume analysis page
- `components/pages/CompanySearch.css` - Company search page
- `components/pages/CompanyGallery.css` - Company gallery page

### Common Components

- `components/common/CompanyCard.css` - Company card styling
- `components/common/CompanyGrid.css` - Grid layout
- `components/common/CompanyFilters.css` - Filter controls
- `components/common/GalleryStats.css` - Statistics display
- `components/common/LoadingSpinner.css` - Loading states
- `components/common/ErrorMessage.css` - Error handling
- `components/common/SearchResults.css` - Search results
- `components/common/RecruiterCard.css` - Recruiter profiles

### Form Components

- `components/forms/FileUpload.css` - File upload styling
- `components/forms/SearchForm.css` - Search form controls

## 🎯 Benefits of This Organization

### 1. **Maintainability**

- Each component's styles are isolated
- Easy to find and modify specific styles
- Clear separation of concerns

### 2. **Scalability**

- New components get their own CSS files
- Design system variables ensure consistency
- Easy to add new features without style conflicts

### 3. **Performance**

- Only load styles for components in use
- Reduced CSS bundle size
- Better caching strategies

### 4. **Developer Experience**

- Logical file organization
- Consistent naming conventions
- Easy debugging and development

### 5. **Design Consistency**

- Centralized design tokens
- Consistent spacing and typography
- Unified color palette

## 🚀 Usage Guidelines

### Adding New Components

1. Create a new CSS file alongside your component
2. Import the design system: `@import '../../styles/variables.css';`
3. Use CSS variables for consistency
4. Follow the naming conventions

### Modifying Styles

1. **Global changes**: Edit `variables.css`
2. **Component changes**: Edit the specific component CSS
3. **Utility changes**: Edit `App.css`

### Best Practices

- Always use CSS variables instead of hardcoded values
- Follow BEM naming convention for CSS classes
- Use responsive design patterns
- Include hover and focus states
- Add appropriate transitions

## 📱 Responsive Design

The design system includes responsive utilities and breakpoints:

- Mobile-first approach
- Consistent breakpoints across components
- Responsive utility classes available

## 🎨 Color System

```css
/* Primary Colors */
--primary-purple: #401664;
--primary-purple-light: #5a1a8b;
--primary-purple-dark: #2d0e47;

/* Supporting Colors */
--accent-green: #10b981;
--accent-red: #ef4444;
--linkedin-blue: #0077b5;

/* Grayscale */
--white: #ffffff;
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
/* ... and more */
```

## 🔧 Development Workflow

1. **Design Changes**: Start with `variables.css`
2. **Component Styling**: Edit component-specific CSS files
3. **Global Utilities**: Add to `App.css`
4. **Testing**: Verify changes across all components

This organization ensures maintainable, scalable, and consistent styling across the entire application.
