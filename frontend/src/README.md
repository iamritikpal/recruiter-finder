# Frontend Structure

This frontend has been restructured into a modern, component-based architecture for better maintainability and scalability.

## 📁 Directory Structure

```
src/
├── components/           # All React components
│   ├── layout/          # Layout components (Layout, Sidebar)
│   ├── pages/           # Page components (main views)
│   ├── common/          # Reusable UI components
│   └── forms/           # Form-specific components
├── hooks/               # Custom React hooks
├── services/            # API service functions
├── utils/               # Utility functions
├── styles/              # Global styles and CSS variables
├── App.js              # Main App component (simplified)
└── index.js            # Entry point

```

## 🧩 Component Architecture

### Layout Components

- **Layout.js** - Main app layout wrapper
- **Sidebar.js** - Navigation sidebar with mobile support

### Page Components

- **ResumeAnalysis.js** - Resume upload and analysis page
- **CompanySearch.js** - Company-based recruiter search page
- **CompanyGallery.js** - Company gallery with filtering

### Common Components (Reusable)

- **CompanyCard.js** - Individual company card component
- **CompanyGrid.js** - Grid layout for company cards
- **CompanyFilters.js** - Search and filter controls
- **GalleryStats.js** - Statistics display component
- **LoadingSpinner.js** - Reusable loading indicator
- **ErrorMessage.js** - Error display component
- **SearchResults.js** - Search results container
- **RecruiterCard.js** - Individual recruiter profile card
- **ResumeResults.js** - Resume analysis results display

### Form Components

- **FileUpload.js** - Resume file upload component
- **SearchForm.js** - Company search form

## 🪝 Custom Hooks

### useCompanyData.js

Manages all company-related data fetching and state management:

- Company data loading
- Filtering and searching
- Cache management
- API integration

## 🎨 Styling Organization

Each component has its own CSS file for better maintainability:

- Component-specific styles are co-located with components
- Global styles remain in `styles/App.css`
- CSS variables and design tokens are centralized

## 🔄 State Management

The app uses a combination of:

- **Local state** for component-specific data
- **Props drilling** for shared state (can be refactored to Context API if needed)
- **Custom hooks** for complex state logic

## 🚀 Benefits of This Structure

1. **Maintainability** - Each component has a single responsibility
2. **Reusability** - Common components can be used across pages
3. **Testability** - Components can be tested in isolation
4. **Scalability** - Easy to add new features and components
5. **Organization** - Clear separation of concerns
6. **Performance** - Components can be optimized individually

## 📝 Usage Examples

### Using a common component:

```jsx
import CompanyCard from "../common/CompanyCard";

function MyComponent() {
  return <CompanyCard company={companyData} onCompanyCardClick={handleClick} />;
}
```

### Using the custom hook:

```jsx
import useCompanyData from "../hooks/useCompanyData";

function MyComponent() {
  const { filteredCompanies, loading, fetchCompanies } = useCompanyData(
    activeTab,
    location,
    search
  );

  // Use the data...
}
```

## 🔧 Future Improvements

Consider these enhancements for further optimization:

- Add Context API for global state management
- Implement lazy loading for pages
- Add prop-types or TypeScript for type safety
- Create a design system with shared components
- Add unit tests for components
- Implement error boundaries
- Add code splitting and optimization
