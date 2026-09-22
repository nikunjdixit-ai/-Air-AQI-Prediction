import {
  Activity,
  BarChart3,
  Brain,
  LayoutDashboard,
  Sparkles,
  Wind,
} from "lucide-react";

export function Sidebar({ activePage, navigateTo, menuOpen, systemHealth }) {
  const navItems = [
    { id: "dashboard", name: "Dashboard", icon: LayoutDashboard },
    { id: "predict", name: "Predict AQI", icon: Activity },
    { id: "analytics", name: "Analytics", icon: BarChart3 },
    { id: "model", name: "ML Model", icon: Brain },
    { id: "agent", name: "AI Advisor", icon: Sparkles },
  ];

  const isOnline = systemHealth?.online;

  return (
    <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
      <div className="logo">
        <div className="logo-icon">
          <Wind size={24} />
        </div>

        <div>
          <h1>AirSense</h1>
          <p>AQI Prediction &amp; AI</p>
        </div>
      </div>

      <nav>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;

          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => navigateTo(item.id)}
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <div
          className="online-dot"
          style={{
            backgroundColor: isOnline ? "#c6f36b" : "#f59e0b",
            boxShadow: isOnline ? "0 0 8px #c6f36b" : "none",
          }}
        ></div>

        <div>
          <strong>ML System</strong>
          <span>
            {isOnline
              ? `Online & Active (${systemHealth?.version || "v1.1"})`
              : "Connecting / Demo Mode"}
          </span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
