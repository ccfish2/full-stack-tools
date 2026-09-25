// src/components/Navbar.tsx
import { Link, useLocation } from "react-router-dom";
import "../css/navbar.css";

export function Navbar() {
  const location = useLocation();

  // Define your main app sections matching backend apps
  const navItems = [
    { 
      label: "FeatureFlag", 
      path: "/core/feature-flag",
      description: "Feature flag control panel"
    },
    { 
      label: "Reports", 
      path: "/reports",
      description: "Analytics and insights"
    },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <Link to="/">
            <h2>Operations Console</h2>
          </Link>
        </div>
        <ul className="navbar-links">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`nav-link ${
                  location.pathname.startsWith(item.path) ? "active" : ""
                }`}
                title={item.description}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}