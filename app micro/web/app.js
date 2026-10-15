/**
 * SkyCast Dashboard — Client Logic & Interactive Weather Analytics
 * - Real-time Weather Modeling
 * - 5-Day & 7-Day (Week) Extended Forecast Projections
 * - Canvas Meteorological Trend Chart
 * - Dynamic Multi-City Comparison Hub with Custom Search & Removal
 * - Multi-City Comparison Graph Modal (5-Day / 7-Day Week)
 * - Favourites & Unit (°C / °F) Management
 */

// City meteorological baseline profiles (realistic data generator)
const CITY_DATABASE = {
  "Bengaluru": { country: "IN", baseTemp: 25.0, icon: "⛅", cond: "Scattered Clouds", humidity: 65, pressure: 1013, wind: 3.5, rainChance: 20 },
  "Mumbai": { country: "IN", baseTemp: 31.0, icon: "☀️", cond: "Sunny & Humid", humidity: 78, pressure: 1010, wind: 4.8, rainChance: 10 },
  "Delhi": { country: "IN", baseTemp: 29.5, icon: "🌤️", cond: "Hazy Sunshine", humidity: 45, pressure: 1012, wind: 3.0, rainChance: 5 },
  "Hyderabad": { country: "IN", baseTemp: 28.0, icon: "⛅", cond: "Partly Cloudy", humidity: 55, pressure: 1014, wind: 3.8, rainChance: 15 },
  "Chennai": { country: "IN", baseTemp: 32.0, icon: "🌤️", cond: "Warm & Humid", humidity: 82, pressure: 1009, wind: 5.2, rainChance: 25 },
  "Kolkata": { country: "IN", baseTemp: 30.5, icon: "☀️", cond: "Clear Sky", humidity: 70, pressure: 1011, wind: 3.6, rainChance: 12 },
  "Pune": { country: "IN", baseTemp: 26.5, icon: "🌤️", cond: "Pleasant", humidity: 50, pressure: 1015, wind: 4.0, rainChance: 10 },
  "Jaipur": { country: "IN", baseTemp: 31.5, icon: "☀️", cond: "Sunny & Dry", humidity: 35, pressure: 1012, wind: 4.2, rainChance: 0 },
  "London": { country: "GB", baseTemp: 14.5, icon: "🌧️", cond: "Light Rain", humidity: 85, pressure: 1018, wind: 5.5, rainChance: 65 },
  "New York": { country: "US", baseTemp: 18.0, icon: "⛅", cond: "Partly Cloudy", humidity: 60, pressure: 1016, wind: 4.5, rainChance: 20 },
  "Tokyo": { country: "JP", baseTemp: 20.5, icon: "🌤️", cond: "Mild & Clear", humidity: 58, pressure: 1020, wind: 3.2, rainChance: 15 },
  "Paris": { country: "FR", baseTemp: 16.0, icon: "⛅", cond: "Overcast", humidity: 72, pressure: 1017, wind: 4.0, rainChance: 30 },
  "Dubai": { country: "AE", baseTemp: 36.0, icon: "☀️", cond: "Hot & Sunny", humidity: 40, pressure: 1008, wind: 5.0, rainChance: 0 },
  "Singapore": { country: "SG", baseTemp: 29.0, icon: "⛈️", cond: "Thundershowers", humidity: 88, pressure: 1009, wind: 3.0, rainChance: 70 },
  "Sydney": { country: "AU", baseTemp: 22.0, icon: "🌤️", cond: "Fresh Breeze", humidity: 62, pressure: 1022, wind: 6.0, rainChance: 20 },
  "Toronto": { country: "CA", baseTemp: 13.0, icon: "⛅", cond: "Cool & Breezy", humidity: 65, pressure: 1019, wind: 5.0, rainChance: 25 },
  "Berlin": { country: "DE", baseTemp: 15.0, icon: "🌧️", cond: "Drizzle", humidity: 78, pressure: 1015, wind: 4.5, rainChance: 45 },
};

// Vibrant color palette for multi-city graph visualization
const CITY_COLORS = [
  "#38bdf8", // Sky Blue
  "#f97316", // Amber / Orange
  "#10b981", // Emerald Green
  "#a855f7", // Purple
  "#f43f5e", // Rose
  "#eab308", // Yellow
  "#06b6d4", // Cyan
  "#ec4899", // Pink
];

// Application State
let currentCity = "Bengaluru";
let currentUnit = "C"; // "C" or "F"
let mainForecastDays = 5; // 5 or 7
let compGraphPeriod = 5; // 5 or 7
let currentWeatherData = null;
let currentForecast = [];
let comparedCities = JSON.parse(
  localStorage.getItem("skycast_compared_cities") ||
  '["Bengaluru", "Mumbai", "London", "Tokyo", "New York"]'
);
let favourites = JSON.parse(
  localStorage.getItem("skycast_favs") ||
  '["Bengaluru", "London", "Tokyo", "New York"]'
);

// DOM Elements: Header & Controls
const cityDropdown = document.getElementById("cityDropdown");
const cityInput = document.getElementById("cityInput");
const btnSearch = document.getElementById("btnSearch");
const chipsContainer = document.getElementById("chipsContainer");
const btnCelsius = document.getElementById("btnCelsius");
const btnFahrenheit = document.getElementById("btnFahrenheit");
const btnFavStar = document.getElementById("btnFavStar");
const liveClock = document.getElementById("liveClock");

// DOM Elements: Hero Weather Card
const heroCity = document.getElementById("heroCity");
const heroCountry = document.getElementById("heroCountry");
const heroTimestamp = document.getElementById("heroTimestamp");
const heroCondition = document.getElementById("heroCondition");
const heroIcon = document.getElementById("heroIcon");
const heroTemp = document.getElementById("heroTemp");
const heroUnit = document.getElementById("heroUnit");
const heroFeels = document.getElementById("heroFeels");
const heroMax = document.getElementById("heroMax");
const heroMin = document.getElementById("heroMin");
const heroSummary = document.getElementById("heroSummary");

// DOM Elements: Parameter Metrics
const valHumidity = document.getElementById("valHumidity");
const valWind = document.getElementById("valWind");
const valPressure = document.getElementById("valPressure");
const valPop = document.getElementById("valPop");

// DOM Elements: Forecast & Chart
const forecastSectionTitle = document.getElementById("forecastSectionTitle");
const forecastCardsRow = document.getElementById("forecastCardsRow");
const btnMain5Day = document.getElementById("btnMain5Day");
const btnMain7Day = document.getElementById("btnMain7Day");
const chartMainHeading = document.getElementById("chartMainHeading");
const chartLegendText = document.getElementById("chartLegendText");

// DOM Elements: Comparison Hub
const compCountBadge = document.getElementById("compCountBadge");
const compSearchInput = document.getElementById("compSearchInput");
const btnAddCompCity = document.getElementById("btnAddCompCity");
const compSuggestions = document.getElementById("compSuggestions");
const comparisonList = document.getElementById("comparisonList");
const btnOpenCompModal = document.getElementById("btnOpenCompModal");
const compPeriod5 = document.getElementById("compPeriod5");
const compPeriod7 = document.getElementById("compPeriod7");
const favList = document.getElementById("favList");

// DOM Elements: Comparison Modal
const compModal = document.getElementById("compModal");
const btnCloseModal = document.getElementById("btnCloseModal");
const modalToggle5 = document.getElementById("modalToggle5");
const modalToggle7 = document.getElementById("modalToggle7");
const multiCityCanvas = document.getElementById("multiCityCanvas");
const compLegendContainer = document.getElementById("compLegendContainer");
const compTableBody = document.getElementById("compTableBody");

// ==========================================================================
// Unit Conversion Helpers
// ==========================================================================
function cToF(celsius) {
  return (celsius * 9) / 5 + 32;
}

function formatTemp(celsius) {
  const val = currentUnit === "F" ? cToF(celsius) : celsius;
  return `${Math.round(val)}°${currentUnit}`;
}

function getUnitSymbol() {
  return `°${currentUnit}`;
}

// ==========================================================================
// Weather Simulator Engine (Supports 5 or 7 Days Extended Forecast)
// ==========================================================================
function generateWeatherForCity(cityName, numDays = 7) {
  const normalized = Object.keys(CITY_DATABASE).find(
    (k) => k.toLowerCase() === cityName.trim().toLowerCase()
  );

  const profile = normalized ? CITY_DATABASE[normalized] : {
    country: "GLOBAL",
    baseTemp: 22.0,
    icon: "🌤️",
    cond: "Clear Intervals",
    humidity: 55,
    pressure: 1013,
    wind: 3.5,
    rainChance: 15,
  };

  const actualCity = normalized || cityName.trim().charAt(0).toUpperCase() + cityName.trim().slice(1).toLowerCase();

  // Current Weather
  const temp = Math.round((profile.baseTemp + (Math.random() * 2 - 1)) * 10) / 10;
  const feelsLike = Math.round((temp + (profile.humidity > 70 ? 2 : -1)) * 10) / 10;
  const tempMax = Math.round((temp + 3.5) * 10) / 10;
  const tempMin = Math.round((temp - 4.2) * 10) / 10;

  const current = {
    city: actualCity,
    country: profile.country,
    temperature: temp,
    feelsLike: feelsLike,
    tempMax: tempMax,
    tempMin: tempMin,
    humidity: profile.humidity,
    pressure: profile.pressure,
    windSpeed: profile.wind,
    condition: profile.cond,
    icon: profile.icon,
    rainChance: profile.rainChance,
    timestamp: new Date(),
    summary: `Current weather in ${actualCity}, ${profile.country}: ${temp}°C (${Math.round(cToF(temp))}°F), ${profile.cond}. Humidity: ${profile.humidity}%, Wind: ${profile.wind} m/s.`,
  };

  // Forecast Days Generation
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const forecast = [];
  const now = new Date();

  for (let i = 1; i <= numDays; i++) {
    const fDate = new Date();
    fDate.setDate(now.getDate() + i);
    const dayName = days[fDate.getDay()];
    const dateStr = `${dayName}, ${fDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;

    const delta = (Math.sin(i * 1.3) * 3);
    const dayMax = Math.round((tempMax + delta) * 10) / 10;
    const dayMin = Math.round((tempMin + delta * 0.7) * 10) / 10;
    const dayAvg = Math.round(((dayMax + dayMin) / 2) * 10) / 10;
    const pop = Math.min(100, Math.max(0, Math.round(profile.rainChance + (Math.random() * 30 - 15))));

    let fIcon = profile.icon;
    let fCond = profile.cond;
    if (pop > 50) {
      fIcon = "🌧️";
      fCond = "Rain Likely";
    } else if (pop > 25) {
      fIcon = "⛅";
      fCond = "Scattered Clouds";
    }

    forecast.push({
      dateStr: dateStr,
      dayName: dayName,
      tempMax: dayMax,
      tempMin: dayMin,
      tempAvg: dayAvg,
      condition: fCond,
      icon: fIcon,
      pop: pop,
    });
  }

  return { current, forecast };
}

// ==========================================================================
// Primary Weather View Rendering
// ==========================================================================
function renderWeather(cityName) {
  currentCity = cityName;
  const { current, forecast } = generateWeatherForCity(cityName, mainForecastDays);
  currentWeatherData = current;
  currentForecast = forecast;

  // Synchronize Dropdown & Input
  if (cityDropdown) {
    for (let opt of cityDropdown.options) {
      if (opt.value.toLowerCase() === cityName.toLowerCase()) {
        cityDropdown.value = opt.value;
        break;
      }
    }
  }
  if (cityInput) {
    cityInput.value = cityName;
  }

  // Synchronize Quick City Chips
  document.querySelectorAll(".chip").forEach((chip) => {
    if (chip.getAttribute("data-city").toLowerCase() === cityName.toLowerCase()) {
      chip.classList.add("active");
    } else {
      chip.classList.remove("active");
    }
  });

  // Render Hero Information
  heroCity.textContent = current.city;
  heroCountry.textContent = current.country;
  heroCondition.textContent = current.condition;
  heroIcon.textContent = current.icon;

  const displayTemp = currentUnit === "F" ? Math.round(cToF(current.temperature)) : current.temperature;
  heroTemp.textContent = displayTemp;
  heroUnit.textContent = getUnitSymbol();

  heroFeels.textContent = formatTemp(current.feelsLike);
  heroMax.textContent = formatTemp(current.tempMax);
  heroMin.textContent = formatTemp(current.tempMin);
  heroSummary.textContent = current.summary;

  // Parameter metrics
  valHumidity.textContent = `${current.humidity}%`;
  valWind.textContent = `${current.windSpeed} m/s`;
  valPressure.textContent = `${current.pressure} hPa`;
  valPop.textContent = `${current.rainChance}%`;

  // Favourite Star
  btnFavStar.classList.toggle("active", favourites.includes(current.city));

  // Render Forecast Cards
  renderForecastCards(forecast);

  // Render Canvas Temperature Trend Chart
  drawTrendChart(forecast);

  // Render Comparison List
  renderComparisonList();

  // Render Favourites
  renderFavouritesList();
}

// Render Extended Forecast Cards
function renderForecastCards(forecast) {
  if (!forecastCardsRow) return;
  forecastCardsRow.innerHTML = "";
  
  if (forecastSectionTitle) {
    forecastSectionTitle.textContent = mainForecastDays === 7 
      ? "📅 Week's Forecast (7 Days)" 
      : "📅 5-Day Diurnal Forecast";
  }

  forecast.forEach((f) => {
    const card = document.createElement("div");
    card.className = "forecast-card";
    card.innerHTML = `
      <div class="fc-day">${f.dateStr}</div>
      <div class="fc-icon">${f.icon}</div>
      <div class="fc-desc">${f.condition}</div>
      <div class="fc-temps">
        <span class="fc-max">${formatTemp(f.tempMax)}</span>
        <span>/</span>
        <span class="fc-min">${formatTemp(f.tempMin)}</span>
      </div>
      <div class="fc-pop">💧 ${f.pop}%</div>
    `;
    forecastCardsRow.appendChild(card);
  });
}

// Draw HTML5 Canvas Curve Chart for Current City
function drawTrendChart(forecast) {
  const canvas = document.getElementById("trendChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);

  const w = rect.width;
  const h = rect.height;

  ctx.clearRect(0, 0, w, h);

  const paddingLeft = 45;
  const paddingRight = 35;
  const paddingTop = 25;
  const paddingBottom = 35;
  const plotW = w - paddingLeft - paddingRight;
  const plotH = h - paddingTop - paddingBottom;

  const maxTemps = forecast.map(f => currentUnit === "F" ? cToF(f.tempMax) : f.tempMax);
  const minTemps = forecast.map(f => currentUnit === "F" ? cToF(f.tempMin) : f.tempMin);

  const globalMax = Math.max(...maxTemps) + 2;
  const globalMin = Math.min(...minTemps) - 2;
  const range = globalMax - globalMin || 1;

  function getY(tempVal) {
    return paddingTop + plotH - ((tempVal - globalMin) / range) * plotH;
  }

  function getX(index) {
    return paddingLeft + (index / (forecast.length - 1)) * plotW;
  }

  // Grid Lines
  ctx.strokeStyle = "rgba(51, 65, 85, 0.4)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const yVal = paddingTop + (i / 4) * plotH;
    ctx.beginPath();
    ctx.moveTo(paddingLeft, yVal);
    ctx.lineTo(w - paddingRight, yVal);
    ctx.stroke();

    const tempLabel = Math.round(globalMax - (i / 4) * range);
    ctx.fillStyle = "#64748b";
    ctx.font = "10px JetBrains Mono, monospace";
    ctx.textAlign = "right";
    ctx.fillText(`${tempLabel}°`, paddingLeft - 8, yVal + 3);
  }

  // Shaded Region
  ctx.beginPath();
  ctx.moveTo(getX(0), getY(maxTemps[0]));
  for (let i = 1; i < forecast.length; i++) {
    ctx.lineTo(getX(i), getY(maxTemps[i]));
  }
  for (let i = forecast.length - 1; i >= 0; i--) {
    ctx.lineTo(getX(i), getY(minTemps[i]));
  }
  ctx.closePath();
  const fillGrad = ctx.createLinearGradient(0, paddingTop, 0, h - paddingBottom);
  fillGrad.addColorStop(0, "rgba(249, 115, 22, 0.2)");
  fillGrad.addColorStop(1, "rgba(56, 189, 248, 0.08)");
  ctx.fillStyle = fillGrad;
  ctx.fill();

  // High Temperature Curve
  ctx.beginPath();
  ctx.strokeStyle = "#f97316";
  ctx.lineWidth = 3;
  ctx.lineJoin = "round";
  for (let i = 0; i < forecast.length; i++) {
    const x = getX(i);
    const y = getY(maxTemps[i]);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Low Temperature Curve
  ctx.beginPath();
  ctx.strokeStyle = "#38bdf8";
  ctx.lineWidth = 3;
  ctx.lineJoin = "round";
  for (let i = 0; i < forecast.length; i++) {
    const x = getX(i);
    const y = getY(minTemps[i]);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Data Points & Labels
  forecast.forEach((f, i) => {
    const x = getX(i);
    const yMax = getY(maxTemps[i]);
    const yMin = getY(minTemps[i]);

    // High dot & label
    ctx.fillStyle = "#f97316";
    ctx.beginPath();
    ctx.arc(x, yMax, 4.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 11px Plus Jakarta Sans, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`${Math.round(maxTemps[i])}°`, x, yMax - 9);

    // Low dot & label
    ctx.fillStyle = "#38bdf8";
    ctx.beginPath();
    ctx.arc(x, yMin, 4.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#94a3b8";
    ctx.fillText(`${Math.round(minTemps[i])}°`, x, yMin + 16);

    // Day of week X axis label
    ctx.fillStyle = "#cbd5e1";
    ctx.font = "11px Plus Jakarta Sans, sans-serif";
    ctx.fillText(f.dayName, x, h - 8);
  });
}

// ==========================================================================
// City Comparison Hub Logic
// ==========================================================================
function renderComparisonList() {
  if (!comparisonList) return;
  comparisonList.innerHTML = "";

  if (compCountBadge) {
    compCountBadge.textContent = `${comparedCities.length} Cit${comparedCities.length === 1 ? 'y' : 'ies'}`;
  }

  if (comparedCities.length === 0) {
    comparisonList.innerHTML = `
      <div style="font-size: 12px; color: var(--text-muted); text-align: center; padding: 16px;">
        No cities in comparison list. Use the search bar above to add cities.
      </div>
    `;
    return;
  }

  comparedCities.forEach((city, index) => {
    const { current } = generateWeatherForCity(city);
    const item = document.createElement("div");
    item.className = `comparison-item ${city.toLowerCase() === currentCity.toLowerCase() ? 'active' : ''}`;
    
    // Choose color dot
    const cityColor = CITY_COLORS[index % CITY_COLORS.length];

    item.innerHTML = `
      <div class="comp-city-group">
        <span class="legend-color-dot" style="background-color: ${cityColor}; box-shadow: 0 0 6px ${cityColor};"></span>
        <span class="comp-icon">${current.icon}</span>
        <span class="comp-city">${city}</span>
      </div>
      <div class="comp-right-wrap">
        <div class="comp-temp-group">
          <div class="comp-temp">${formatTemp(current.temperature)}</div>
          <div class="comp-cond">${current.condition}</div>
        </div>
        <button class="btn-remove-city" title="Remove ${city} from comparison" data-city="${city}">✕</button>
      </div>
    `;

    // Click item to switch dashboard view
    item.addEventListener("click", (e) => {
      if (e.target.closest(".btn-remove-city")) return;
      renderWeather(city);
    });

    // Remove city handler
    const removeBtn = item.querySelector(".btn-remove-city");
    removeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      removeCityFromComparison(city);
    });

    comparisonList.appendChild(item);
  });
}

function addCityToComparison(cityName) {
  const trimmed = cityName.trim();
  if (!trimmed) return;

  const exists = comparedCities.some(
    (c) => c.toLowerCase() === trimmed.toLowerCase()
  );

  if (exists) {
    if (compSearchInput) {
      compSearchInput.style.borderColor = "#f59e0b";
      setTimeout(() => {
        compSearchInput.style.borderColor = "";
      }, 1000);
    }
    return;
  }

  const normalized = Object.keys(CITY_DATABASE).find(
    (k) => k.toLowerCase() === trimmed.toLowerCase()
  );
  const formattedCity = normalized || trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();

  comparedCities.push(formattedCity);
  localStorage.setItem("skycast_compared_cities", JSON.stringify(comparedCities));

  if (compSearchInput) {
    compSearchInput.value = "";
  }
  if (compSuggestions) {
    compSuggestions.style.display = "none";
  }

  renderComparisonList();

  // If modal is currently open, refresh chart & table
  if (compModal && compModal.style.display !== "none") {
    drawMultiCityChart(compGraphPeriod);
    renderComparisonLegend();
    renderComparisonTable(compGraphPeriod);
  }
}

function removeCityFromComparison(cityName) {
  if (comparedCities.length <= 1) {
    alert("Please keep at least 1 city in the comparison list.");
    return;
  }

  comparedCities = comparedCities.filter(
    (c) => c.toLowerCase() !== cityName.toLowerCase()
  );
  localStorage.setItem("skycast_compared_cities", JSON.stringify(comparedCities));

  renderComparisonList();

  // If modal is open, refresh
  if (compModal && compModal.style.display !== "none") {
    drawMultiCityChart(compGraphPeriod);
    renderComparisonLegend();
    renderComparisonTable(compGraphPeriod);
  }
}

// Comparison Suggestions Handler
function updateSuggestions(query) {
  if (!compSuggestions) return;
  const q = query.trim().toLowerCase();
  if (!q) {
    compSuggestions.style.display = "none";
    compSuggestions.innerHTML = "";
    return;
  }

  const matches = Object.keys(CITY_DATABASE).filter(
    (k) => k.toLowerCase().includes(q) && !comparedCities.some(c => c.toLowerCase() === k.toLowerCase())
  );

  if (matches.length === 0) {
    compSuggestions.style.display = "none";
    compSuggestions.innerHTML = "";
    return;
  }

  compSuggestions.innerHTML = "";
  matches.slice(0, 5).forEach((city) => {
    const chip = document.createElement("button");
    chip.className = "comp-suggestion-chip";
    chip.textContent = `+ ${city}`;
    chip.addEventListener("click", () => {
      addCityToComparison(city);
    });
    compSuggestions.appendChild(chip);
  });
  compSuggestions.style.display = "flex";
}

// ==========================================================================
// Multi-City Comparison Graph Modal Logic
// ==========================================================================
function openComparisonModal(period = compGraphPeriod) {
  compGraphPeriod = period;
  if (!compModal) return;

  // Update modal period buttons
  if (modalToggle5) modalToggle5.classList.toggle("active", compGraphPeriod === 5);
  if (modalToggle7) modalToggle7.classList.toggle("active", compGraphPeriod === 7);

  // Update sidebar period buttons
  if (compPeriod5) compPeriod5.classList.toggle("active", compGraphPeriod === 5);
  if (compPeriod7) compPeriod7.classList.toggle("active", compGraphPeriod === 7);

  compModal.style.display = "flex";

  // Render chart, legend, and comparative table
  requestAnimationFrame(() => {
    drawMultiCityChart(compGraphPeriod);
    renderComparisonLegend();
    renderComparisonTable(compGraphPeriod);
  });
}

function closeComparisonModal() {
  if (!compModal) return;
  compModal.style.display = "none";
}

// Render Legend in Comparison Modal
function renderComparisonLegend() {
  if (!compLegendContainer) return;
  compLegendContainer.innerHTML = "";

  comparedCities.forEach((city, index) => {
    const color = CITY_COLORS[index % CITY_COLORS.length];
    const { current } = generateWeatherForCity(city);
    const item = document.createElement("div");
    item.className = "comp-legend-item";
    item.innerHTML = `
      <span class="legend-color-dot" style="background-color: ${color}; box-shadow: 0 0 8px ${color};"></span>
      <span>${current.icon} ${city} (${formatTemp(current.temperature)})</span>
    `;
    compLegendContainer.appendChild(item);
  });
}

// Draw Multi-City Temperature Trend Lines on Canvas
function drawMultiCityChart(numDays = 5) {
  if (!multiCityCanvas) return;
  const ctx = multiCityCanvas.getContext("2d");

  const dpr = window.devicePixelRatio || 1;
  const rect = multiCityCanvas.getBoundingClientRect();
  multiCityCanvas.width = rect.width * dpr;
  multiCityCanvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);

  const w = rect.width;
  const h = rect.height;

  ctx.clearRect(0, 0, w, h);

  if (comparedCities.length === 0) return;

  const paddingLeft = 50;
  const paddingRight = 40;
  const paddingTop = 30;
  const paddingBottom = 40;
  const plotW = w - paddingLeft - paddingRight;
  const plotH = h - paddingTop - paddingBottom;

  // Gather forecast data for each city
  const cityDataList = comparedCities.map((city, idx) => {
    const { forecast } = generateWeatherForCity(city, numDays);
    const temps = forecast.map(f => currentUnit === "F" ? cToF(f.tempAvg) : f.tempAvg);
    return {
      city: city,
      color: CITY_COLORS[idx % CITY_COLORS.length],
      forecast: forecast,
      temps: temps,
    };
  });

  // Calculate overall Min & Max
  let allTemps = [];
  cityDataList.forEach(c => {
    allTemps.push(...c.temps);
  });
  const globalMax = Math.max(...allTemps) + 2.5;
  const globalMin = Math.min(...allTemps) - 2.5;
  const range = globalMax - globalMin || 1;

  function getY(tempVal) {
    return paddingTop + plotH - ((tempVal - globalMin) / range) * plotH;
  }

  function getX(index) {
    return paddingLeft + (index / (numDays - 1)) * plotW;
  }

  // Draw Grid Lines & Y-axis scale
  ctx.strokeStyle = "rgba(51, 65, 85, 0.4)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const yVal = paddingTop + (i / 4) * plotH;
    ctx.beginPath();
    ctx.moveTo(paddingLeft, yVal);
    ctx.lineTo(w - paddingRight, yVal);
    ctx.stroke();

    const tempLabel = Math.round(globalMax - (i / 4) * range);
    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px JetBrains Mono, monospace";
    ctx.textAlign = "right";
    ctx.fillText(`${tempLabel}°`, paddingLeft - 10, yVal + 4);
  }

  // Draw X-axis Day of Week Labels
  const sampleDays = cityDataList[0].forecast;
  sampleDays.forEach((f, i) => {
    const x = getX(i);
    ctx.fillStyle = "#cbd5e1";
    ctx.font = "12px Plus Jakarta Sans, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(f.dayName, x, h - 12);
  });

  // Draw Each City's Temperature Curve
  cityDataList.forEach((c) => {
    // Line Curve
    ctx.beginPath();
    ctx.strokeStyle = c.color;
    ctx.lineWidth = 3;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";

    for (let i = 0; i < c.temps.length; i++) {
      const x = getX(i);
      const y = getY(c.temps[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Data Dots & Value Labels
    for (let i = 0; i < c.temps.length; i++) {
      const x = getX(i);
      const y = getY(c.temps[i]);

      ctx.fillStyle = c.color;
      ctx.beginPath();
      ctx.arc(x, y, 4.5, 0, Math.PI * 2);
      ctx.fill();

      // Small label for each city data point
      ctx.fillStyle = "#f8fafc";
      ctx.font = "10px Plus Jakarta Sans, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(`${Math.round(c.temps[i])}°`, x, y - 8);
    }
  });
}

// Render Comparative Table in Modal
function renderComparisonTable(numDays = 5) {
  if (!compTableBody) return;
  compTableBody.innerHTML = "";

  comparedCities.forEach((city, idx) => {
    const { current, forecast } = generateWeatherForCity(city, numDays);
    const color = CITY_COLORS[idx % CITY_COLORS.length];

    const meanTemp = forecast.reduce((acc, f) => acc + f.tempAvg, 0) / forecast.length;
    const maxTemp = Math.max(...forecast.map(f => f.tempMax));
    const minTemp = Math.min(...forecast.map(f => f.tempMin));
    const rainDays = forecast.filter(f => f.pop >= 40).length;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${color};margin-right:8px;"></span>
        <strong>${city}</strong> <span style="font-size:11px;color:var(--text-muted);">${current.country}</span>
      </td>
      <td><strong>${formatTemp(current.temperature)}</strong></td>
      <td>${formatTemp(meanTemp)}</td>
      <td><span style="color:var(--accent-cyan)">${formatTemp(minTemp)}</span> – <span style="color:var(--accent-orange)">${formatTemp(maxTemp)}</span></td>
      <td>${current.icon} ${current.condition}</td>
      <td>${rainDays > 0 ? `🌧️ ${rainDays} of ${numDays} days` : '☀️ Low risk'}</td>
    `;
    compTableBody.appendChild(tr);
  });
}

// Render Favourites List
function renderFavouritesList() {
  if (!favList) return;
  favList.innerHTML = "";
  if (favourites.length === 0) {
    favList.innerHTML = "<span style='font-size:12px;color:#64748b;'>No saved cities yet. Click the ★ next to any city name.</span>";
    return;
  }

  favourites.forEach(city => {
    const chip = document.createElement("button");
    chip.className = "fav-chip";
    chip.textContent = `★ ${city}`;
    chip.addEventListener("click", () => renderWeather(city));
    favList.appendChild(chip);
  });
}

// ==========================================================================
// Event Listeners & Interactions
// ==========================================================================

// 1. Dropdown Selection
if (cityDropdown) {
  cityDropdown.addEventListener("change", (e) => {
    const selected = e.target.value;
    if (selected) renderWeather(selected);
  });
}

// 2. Quick City Pill Chips
if (chipsContainer) {
  chipsContainer.addEventListener("click", (e) => {
    const btn = e.target.closest(".chip");
    if (btn) {
      const city = btn.getAttribute("data-city");
      if (city) renderWeather(city);
    }
  });
}

// 3. Search Bar Submission
if (btnSearch && cityInput) {
  btnSearch.addEventListener("click", () => {
    const val = cityInput.value.trim();
    if (val) renderWeather(val);
  });

  cityInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const val = cityInput.value.trim();
      if (val) renderWeather(val);
    }
  });
}

// 4. Comparison Search & Add
if (btnAddCompCity && compSearchInput) {
  btnAddCompCity.addEventListener("click", () => {
    addCityToComparison(compSearchInput.value);
  });

  compSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      addCityToComparison(compSearchInput.value);
    }
  });

  compSearchInput.addEventListener("input", (e) => {
    updateSuggestions(e.target.value);
  });
}

// 5. Open Comparison Graph Modal
if (btnOpenCompModal) {
  btnOpenCompModal.addEventListener("click", () => {
    openComparisonModal(compGraphPeriod);
  });
}

// 6. Modal Close Buttons
if (btnCloseModal) {
  btnCloseModal.addEventListener("click", closeComparisonModal);
}

if (compModal) {
  compModal.addEventListener("click", (e) => {
    if (e.target === compModal) {
      closeComparisonModal();
    }
  });
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && compModal && compModal.style.display !== "none") {
    closeComparisonModal();
  }
});

// 7. Modal Period Toggles (5-Day vs Week)
if (modalToggle5) {
  modalToggle5.addEventListener("click", () => {
    openComparisonModal(5);
  });
}
if (modalToggle7) {
  modalToggle7.addEventListener("click", () => {
    openComparisonModal(7);
  });
}

// 8. Sidebar Period Switches
if (compPeriod5) {
  compPeriod5.addEventListener("click", () => {
    compGraphPeriod = 5;
    compPeriod5.classList.add("active");
    if (compPeriod7) compPeriod7.classList.remove("active");
    openComparisonModal(5);
  });
}
if (compPeriod7) {
  compPeriod7.addEventListener("click", () => {
    compGraphPeriod = 7;
    compPeriod7.classList.add("active");
    if (compPeriod5) compPeriod5.classList.remove("active");
    openComparisonModal(7);
  });
}

// 9. Main Forecast 5-Day vs 7-Day Week Toggles
if (btnMain5Day) {
  btnMain5Day.addEventListener("click", () => {
    if (mainForecastDays !== 5) {
      mainForecastDays = 5;
      btnMain5Day.classList.add("active");
      if (btnMain7Day) btnMain7Day.classList.remove("active");
      renderWeather(currentCity);
    }
  });
}
if (btnMain7Day) {
  btnMain7Day.addEventListener("click", () => {
    if (mainForecastDays !== 7) {
      mainForecastDays = 7;
      btnMain7Day.classList.add("active");
      if (btnMain5Day) btnMain5Day.classList.remove("active");
      renderWeather(currentCity);
    }
  });
}

// 10. Temperature Unit Toggle (°C / °F)
if (btnCelsius) {
  btnCelsius.addEventListener("click", () => {
    if (currentUnit !== "C") {
      currentUnit = "C";
      btnCelsius.classList.add("active");
      btnFahrenheit.classList.remove("active");
      renderWeather(currentCity);
      if (compModal && compModal.style.display !== "none") {
        drawMultiCityChart(compGraphPeriod);
        renderComparisonLegend();
        renderComparisonTable(compGraphPeriod);
      }
    }
  });
}

if (btnFahrenheit) {
  btnFahrenheit.addEventListener("click", () => {
    if (currentUnit !== "F") {
      currentUnit = "F";
      btnFahrenheit.classList.add("active");
      btnCelsius.classList.remove("active");
      renderWeather(currentCity);
      if (compModal && compModal.style.display !== "none") {
        drawMultiCityChart(compGraphPeriod);
        renderComparisonLegend();
        renderComparisonTable(compGraphPeriod);
      }
    }
  });
}

// 11. Favourite Toggle
if (btnFavStar) {
  btnFavStar.addEventListener("click", () => {
    const index = favourites.indexOf(currentCity);
    if (index > -1) {
      favourites.splice(index, 1);
    } else {
      favourites.push(currentCity);
    }
    localStorage.setItem("skycast_favs", JSON.stringify(favourites));
    btnFavStar.classList.toggle("active", favourites.includes(currentCity));
    renderFavouritesList();
  });
}

// 12. Live Clock
function updateClock() {
  if (!liveClock) return;
  const now = new Date();
  liveClock.textContent = now.toLocaleTimeString("en-US", { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

// 13. Window Resize Redraw
window.addEventListener("resize", () => {
  if (currentForecast.length > 0) {
    drawTrendChart(currentForecast);
  }
  if (compModal && compModal.style.display !== "none") {
    drawMultiCityChart(compGraphPeriod);
  }
});

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
  renderWeather("Bengaluru");
});
