# API Configuration

This directory contains the centralized API configuration for the frontend application.

## Files

### `api.js`

Centralized backend URL configuration that automatically switches between development and production environments.

## Environment Configuration

The system automatically detects the environment and uses the appropriate backend URL:

### Development (Localhost)

- **URL:** `http://localhost:5000`
- **When:** Running on localhost or 127.0.0.1
- **Usage:** Local development with Flask dev server

### Production (Render)

- **URL:** `https://your-app-name.onrender.com`
- **When:** Deployed to production
- **Usage:** Live application

### Staging (Optional)

- **URL:** `https://staging-your-app-name.onrender.com`
- **When:** Staging environment detected
- **Usage:** Testing before production

## Usage

### Basic Import

```javascript
import { API_ENDPOINTS } from "../config/api";

// Use predefined endpoints
const response = await fetch(API_ENDPOINTS.analyzeResume, {
  method: "POST",
  body: formData,
});
```

### Building URLs with Parameters

```javascript
import { buildURL, API_ENDPOINTS } from "../config/api";

// Build URL with query parameters
const searchURL = buildURL(API_ENDPOINTS.searchRecruiters, {
  company: "Google",
  location: "India",
});
// Result: http://localhost:5000/api/search?company=Google&location=India
```

### Environment Detection

```javascript
import { getEnvironmentInfo } from "../config/api";

// Get current environment info
const info = getEnvironmentInfo();
console.log(info);
// {
//   environment: 'development',
//   baseURL: 'http://localhost:5000',
//   hostname: 'localhost',
//   nodeEnv: 'development'
// }
```

## Available Endpoints

| Endpoint           | Description           | Method |
| ------------------ | --------------------- | ------ |
| `health`           | Health check          | GET    |
| `analyzeResume`    | Resume analysis       | POST   |
| `searchRecruiters` | Search recruiters     | GET    |
| `getCompanies`     | Get companies list    | GET    |
| `findContact`      | Find email & phone    | POST   |
| `findPhone`        | Find phone only       | POST   |
| `guessEmails`      | Guess email addresses | POST   |

## Changing Backend URL

### For Development

Edit the `development` URL in `api.js`:

```javascript
const API_CONFIG = {
  development: "http://localhost:8000", // Change port if needed
  // ...
};
```

### For Production (Render)

1. Deploy your backend to Render
2. Get your Render app URL (e.g., `https://my-app-name.onrender.com`)
3. Update the `production` URL in `api.js`:

```javascript
const API_CONFIG = {
  // ...
  production: "https://my-app-name.onrender.com", // Your actual Render URL
};
```

### Environment Variables (Optional)

You can also use environment variables by creating a `.env` file:

```bash
# .env
REACT_APP_API_URL=https://my-custom-backend.com
```

Then modify `api.js` to use it:

```javascript
const API_CONFIG = {
  development: process.env.REACT_APP_API_URL || "http://localhost:5000",
  production:
    process.env.REACT_APP_API_URL || "https://your-app-name.onrender.com",
};
```

## Benefits

✅ **Centralized Configuration:** One place to manage all API URLs  
✅ **Environment Auto-Detection:** Automatically switches between dev/prod  
✅ **Easy Deployment:** Just update one URL for production  
✅ **Type Safety:** Predefined endpoints prevent typos  
✅ **Debugging:** Built-in environment info logging  
✅ **Flexibility:** Easy to add new environments or endpoints

## Migration from Hardcoded URLs

Before:

```javascript
const response = await fetch(
  "http://localhost:5000/api/search?company=" + company
);
```

After:

```javascript
import { buildURL, API_ENDPOINTS } from "../config/api";
const url = buildURL(API_ENDPOINTS.searchRecruiters, { company });
const response = await fetch(url);
```

## Troubleshooting

### Backend Not Connecting

1. Check if backend is running: `curl http://localhost:5000/health`
2. Verify the URL in browser developer tools Network tab
3. Check CORS settings on backend

### Wrong Environment Detected

The system uses this priority:

1. `process.env.NODE_ENV === 'development'`
2. `window.location.hostname` includes 'localhost' or '127.0.0.1'
3. `window.location.hostname` includes 'staging'
4. Default to production

### Debug Environment Detection

```javascript
import { getEnvironmentInfo } from "../config/api";
console.log("Environment Info:", getEnvironmentInfo());
```
