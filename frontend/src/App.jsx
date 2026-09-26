import { useCallback, useEffect, useState } from "react";
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
import {
  CURRENT_LOCATION_VALUE,
  getCurrentLocation,
} from "./services/locationService";

export function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [selectedCity, setSelectedCity] = useState("Kanpur");
  const [locationMode, setLocationMode] = useState("city"); // "current" | "city"
  const [userCoords, setUserCoords] = useState(null);
  const [resolvedLocationName, setResolvedLocationName] = useState("");
  const [locationNotice, setLocationNotice] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);

  const requestUserGeolocation = useCallback(async (forceRefresh = false) => {
    const loc = await getCurrentLocation({ forceRefresh });
    if (loc.granted && loc.latitude != null && loc.longitude != null) {
      setUserCoords({ lat: loc.latitude, lon: loc.longitude });
      setLocationMode("current");
      setLocationNotice(null);
    } else {
      setLocationMode("city");
      setLocationNotice(
        loc.message ||
          "Location access is unavailable. Showing the selected city."
      );
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    checkHealth().then((health) => {
      if (isMounted) {
        setSystemHealth(health);
      }
    });

    // Attempt browser geolocation once on initial startup
    getCurrentLocation({ forceRefresh: false }).then((loc) => {
      if (!isMounted) return;
      if (loc.granted && loc.latitude != null && loc.longitude != null) {
        setUserCoords({ lat: loc.latitude, lon: loc.longitude });
        setLocationMode("current");
        setLocationNotice(null);
      } else {
        setLocationMode("city");
        setLocationNotice(
          loc.message ||
            "Location access is unavailable. Showing the selected city."
        );
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

  const handleLocationSelect = (value) => {
    if (value === CURRENT_LOCATION_VALUE) {
      requestUserGeolocation(true);
    } else {
      setLocationMode("city");
      setSelectedCity(value);
      setLocationNotice(null);
    }
  };

  const handleLocationResolved = useCallback((resolvedName) => {
    if (!resolvedName) return;
    setResolvedLocationName(resolvedName);
    const shortCity = String(resolvedName).split(",")[0].trim();
    if (shortCity && !shortCity.includes("°")) {
      setSelectedCity(shortCity);
    }
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
          locationMode={locationMode}
          resolvedLocationName={resolvedLocationName}
          onLocationSelect={handleLocationSelect}
        />

        {activePage === "dashboard" && (
          <Dashboard
            navigateTo={navigateTo}
            selectedCity={selectedCity}
            locationMode={locationMode}
            userCoords={userCoords}
            locationNotice={locationNotice}
            onDismissLocationNotice={() => setLocationNotice(null)}
            onLocationResolved={handleLocationResolved}
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