const state = {
  range: "all",
  year: "",
  month: "",
  genreChart: null,
  hourChart: null,
  weekdayChart: null,
};

const dom = {
  rangeSelect: document.getElementById("rangeSelect"),
  yearSelect: document.getElementById("yearSelect"),
  monthSelect: document.getElementById("monthSelect"),
  statusChip: document.getElementById("statusChip"),
  totalTime: document.getElementById("totalTime"),
  totalTracks: document.getElementById("totalTracks"),
  uniqueArtists: document.getElementById("uniqueArtists"),
  uniqueSongs: document.getElementById("uniqueSongs"),
  topArtists: document.getElementById("topArtists"),
  topTracks: document.getElementById("topTracks"),
  musicCount: document.getElementById("musicCount"),
  podcastCount: document.getElementById("podcastCount"),
  podcastHours: document.getElementById("podcastHours"),
  podcastEpisodes: document.getElementById("podcastEpisodes"),
  podcastShows: document.getElementById("podcastShows"),
  topShows: document.getElementById("topShows"),
  searchInput: document.getElementById("searchInput"),
  searchButton: document.getElementById("searchButton"),
  searchResults: document.getElementById("searchResults"),
};

function toHours(ms) {
  const hours = ms / 1000 / 60 / 60;
  return `${hours.toFixed(1)}h`;
}

function formatNumber(value) {
  return new Intl.NumberFormat().format(value);
}

function setStatus(text) {
  dom.statusChip.textContent = text;
}

async function api(path) {
  const query = new URLSearchParams();
  query.set("range", state.range);
  if (state.year) query.set("year", state.year);
  if (state.month) query.set("month", state.month);
  const response = await fetch(`${path}?${query.toString()}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

function renderList(container, items, mapper) {
  container.innerHTML = items.map(mapper).join("");
}

function updateNav() {
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.target === currentPage());
  });
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.toggle("active", page.id === currentPage());
  });
}

function currentPage() {
  const active = document.querySelector(".nav-button.active");
  return active ? active.dataset.target : "overview";
}

async function loadStats() {
  try {
    setStatus("Loading overview…");
    const data = await api("/api/stats");

    dom.totalTime.textContent = toHours(data.total_listening_time_ms);
    dom.totalTracks.textContent = formatNumber(data.total_tracks);
    dom.uniqueArtists.textContent = formatNumber(data.unique_artists);
    dom.uniqueSongs.textContent = formatNumber(data.unique_tracks);

    renderList(
      dom.topArtists,
      data.top_artists,
      (item) => `
    <div class="track-item">
      <strong>${item.artist}</strong>
      <span>${item.plays} plays</span>
    </div>
  `,
    );

    renderList(
      dom.topTracks,
      data.top_tracks,
      (item) => `
    <div class="track-item">
      <strong>${item.track}</strong>
      <span>${item.artist} • ${item.plays} plays</span>
    </div>
  `,
    );

    dom.musicCount.textContent = formatNumber(data.total_tracks);
    const podcastQuery = new URLSearchParams();
    podcastQuery.set("range", state.range);
    if (state.year) podcastQuery.set("year", state.year);
    if (state.month) podcastQuery.set("month", state.month);
    const podcastData = await fetch(
      `/api/podcasts?${podcastQuery.toString()}`,
    ).then((res) => {
      if (!res.ok) throw new Error(`Podcast API failed: ${res.status}`);
      return res.json();
    });
    dom.podcastCount.textContent = formatNumber(podcastData.episodes_listened);

    setStatus(
      `Active range: ${state.range.toUpperCase()}${state.year ? ` · ${state.year}${state.month ? " / " + state.month : ""}` : ""}`,
    );
    renderGenreChart(data.top_genres);
  } catch (error) {
    setStatus("Error loading dashboard");
    console.error(error);
  }
}

function renderGenreChart(genres) {
  const labels = genres.map((item) => item.genre);
  const values = genres.map((item) => item.plays);
  const ctx = document.getElementById("genreChart").getContext("2d");
  if (state.genreChart) state.genreChart.destroy();
  state.genreChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: [
            "#1db954",
            "#7b5cff",
            "#3e9cff",
            "#ffa86e",
            "#7bffb2",
          ],
        },
      ],
    },
    options: {
      plugins: { legend: { position: "right", labels: { color: "#fff" } } },
    },
  });
}

async function loadHabits() {
  setStatus("Loading habits…");
  const data = await api("/api/habits");
  renderHourChart(data.hours);
  renderWeekdayChart(data.weekday);
}

function renderHourChart(hours) {
  const labels = Object.keys(hours);
  const values = Object.values(hours);
  const ctx = document.getElementById("hourChart").getContext("2d");
  if (state.hourChart) state.hourChart.destroy();
  state.hourChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Plays", data: values, backgroundColor: "#7b5cff" }],
    },
    options: {
      scales: {
        x: { ticks: { color: "#bbb" } },
        y: { ticks: { color: "#bbb" } },
      },
    },
  });
}

function renderWeekdayChart(weekday) {
  const labels = Object.keys(weekday);
  const values = Object.values(weekday);
  const ctx = document.getElementById("weekdayChart").getContext("2d");
  if (state.weekdayChart) state.weekdayChart.destroy();
  state.weekdayChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Plays",
          data: values,
          borderColor: "#1db954",
          backgroundColor: "rgba(29, 185, 84, 0.18)",
        },
      ],
    },
    options: {
      scales: {
        x: { ticks: { color: "#bbb" } },
        y: { ticks: { color: "#bbb" } },
      },
    },
  });
}

async function loadPodcasts() {
  setStatus("Loading podcast summary…");
  const data = await api("/api/podcasts");
  dom.podcastHours.textContent = `${data.total_podcast_hours} hrs`;
  dom.podcastEpisodes.textContent = formatNumber(data.episodes_listened);
  dom.podcastShows.textContent = formatNumber(data.unique_shows);
  renderList(
    dom.topShows,
    data.top_shows,
    (item) => `
    <div class="show-item">
      <strong>${item.show}</strong>
      <span>${item.plays} listens</span>
    </div>
  `,
  );
}

async function searchContent() {
  const query = dom.searchInput.value.trim();
  if (!query) return;
  try {
    setStatus("Searching...");
    const data = await fetch(`/api/search?q=${encodeURIComponent(query)}`).then(
      (res) => {
        if (!res.ok) throw new Error(`Search failed: ${res.status}`);
        return res.json();
      },
    );
    let html = "";

    if (data.music.length) {
      html += "<h4>Music</h4>";
      html += data.music
        .map(
          (item) => `
      <div class="search-card">
        <strong>${item.track}</strong>
        <span>${item.artist} • ${item.album}</span>
        <small>${new Date(item.played_at).toLocaleString()}</small>
      </div>
    `,
        )
        .join("");
    }
    if (data.podcasts.length) {
      html += "<h4>Podcasts</h4>";
      html += data.podcasts
        .map(
          (item) => `
      <div class="search-card">
        <strong>${item.episode}</strong>
        <span>${item.show} • ${item.publisher}</span>
        <small>${new Date(item.played_at).toLocaleString()}</small>
      </div>
    `,
        )
        .join("");
    }
    if (!data.music.length && !data.podcasts.length) {
      html = "<p>No matches found.</p>";
    }
    dom.searchResults.innerHTML = html;
  } catch (error) {
    setStatus("Search failed");
    console.error(error);
  }
}

function attachEvents() {
  dom.rangeSelect.addEventListener("change", (event) => {
    state.range = event.target.value;
    refreshPage();
  });

  dom.yearSelect.addEventListener("change", (event) => {
    state.year = event.target.value;
    refreshPage();
  });

  dom.monthSelect.addEventListener("change", (event) => {
    state.month = event.target.value;
    refreshPage();
  });

  dom.searchButton.addEventListener("click", searchContent);
  dom.searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") searchContent();
  });

  document.querySelectorAll(".nav-button").forEach((button) => {
    button.addEventListener("click", () => {
      document
        .querySelectorAll(".nav-button")
        .forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      updateNav();
    });
  });
}

async function refreshPage() {
  await loadStats();
  if (currentPage() === "habits") await loadHabits();
  if (currentPage() === "podcasts") await loadPodcasts();
}

async function init() {
  attachEvents();
  updateNav();
  await loadStats();
}

init();
