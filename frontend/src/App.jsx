import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import "./App.css";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import AgentConsultation from "./pages/AgentConsultation";
import Analytics from "./pages/Analytics";
import Dashboard from "./pages/Dashboard";
import Model from "./pages/Model";
import Prediction from "./pages/Prediction";
import { checkHealth } from "./services/aqiService";

export function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [selectedCity, setSelectedCity] = useState("Kanpur");
  const [menuOpen, setMenuOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);

  useEffect(() => {
    let isMounted = true;
    checkHealth().then((health) => {
      if (isMounted) {
        setSystemHealth(health);
      }
    });

    // Optional heartbeat check every 60 seconds
    const interval = setInterval(() => {
      checkHealth().then((health) => {
        if (isMounted) {
          setSystemHealth(health);
        }
      });
    }, 60000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navigateTo = (page) => {
    setActivePage(page);
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="app">
      <Sidebar
        activePage={activePage}
        navigateTo={navigateTo}
        menuOpen={menuOpen}
        systemHealth={systemHealth}
      />

      <button
        className="mobile-menu"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Toggle Navigation Menu"
      >
        {menuOpen ? <X /> : <Menu />}
      </button>

      <main className="main">
        <Header
          activePage={activePage}
          selectedCity={selectedCity}
          onCityChange={setSelectedCity}
        />

        {activePage === "dashboard" && (
          <Dashboard
            navigateTo={navigateTo}
            selectedCity={selectedCity}
          />
        )}

        {activePage === "predict" && (
          <Prediction selectedCity={selectedCity} />
        )}

        {activePage === "analytics" && (
          <Analytics selectedCity={selectedCity} />
        )}

        {activePage === "model" && (
          <Model systemHealth={systemHealth} />
        )}

        {activePage === "agent" && (
          <AgentConsultation selectedCity={selectedCity} />
        )}
      </main>
    </div>
  );
}

export default App;