(function () {
  "use strict";

  const page = document.body.dataset.page || "overview";

  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[char];
    });
  }

  async function getJson(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error("HTTP " + response.status);
    return response.json();
  }

  function setHtml(id, html) {
    const node = document.getElementById(id);
    if (node) node.innerHTML = html;
  }

  function empty(message) {
    return '<div class="empty">' + esc(message) + "</div>";
  }

  function row(label, value) {
    return '<div class="row"><span>' + esc(label) + '</span><strong>' + esc(value) + "</strong></div>";
  }

  function card(title, lines) {
    return '<article class="item-card"><h3>' + esc(title) + "</h3>" + lines.map(function (line) {
      return '<div class="meta-line">' + esc(line) + "</div>";
    }).join("") + "</article>";
  }

  function table(headers, rows) {
    if (!rows.length) return empty("No hay datos persistidos todavia.");
    return "<table><thead><tr>" + headers.map(function (head) {
      return "<th>" + esc(head) + "</th>";
    }).join("") + "</tr></thead><tbody>" + rows.join("") + "</tbody></table>";
  }

  async function overview() {
    const sources = await getJson("/api/v1/esports/sources");
    const coverage = await getJson("/api/v1/esports/coverage");
    const stats = coverage.data || {};
    setHtml("stat-strip", [
      row("Tournaments", stats.tournaments || 0),
      row("Games", stats.games || 0),
      row("Patches", stats.patches || 0),
      row("Active sources", stats.active_sources || 0),
    ].join(""));
    const summary = sources.summary || {};
    setHtml("sources-pill", (summary.total || 0) + " total");
    setHtml("sources-list", (sources.sources || []).map(function (source) {
      return row(source.id, source.status + " / " + source.source_type);
    }).join("") || empty("No hay registry de fuentes."));
    setHtml("coverage-pill", "ok");
    setHtml("coverage-list", [
      row("Teams", stats.teams || 0),
      row("Players", stats.players || 0),
      row("Matches", stats.matches || 0),
      row("Storage", stats.storage_root || "data/esports_research"),
    ].join(""));
    const gaps = [].concat(sources.gaps || [], coverage.gaps || [], stats.gaps || []);
    setHtml("gaps-list", gaps.length ? gaps.map(function (gap) { return row("Gap", gap); }).join("") : row("Status", "Sin gaps criticos"));
  }

  async function drafts() {
    const draft = await getJson("/api/v1/esports/games/sample-game/draft");
    const rows = (draft.data || []).map(function (item) {
      return "<tr><td>" + esc(item.action_order) + "</td><td>" + esc(item.team_side) + "</td><td>" + esc(item.action_type) + "</td><td>" + esc(item.champion_id) + "</td><td>" + esc(item.phase) + "</td></tr>";
    });
    setHtml("drafts-count", String(draft.total_records || 0));
    setHtml("drafts-list", rows.length ? table(["Order", "Side", "Type", "Champion", "Phase"], rows) : empty((draft.gaps || ["No draft data"])[0]));
  }

  async function teams() {
    const payload = await getJson("/api/v1/esports/teams");
    const rows = payload.data || [];
    setHtml("teams-list", rows.length ? rows.map(function (team) {
      return card(team.name || team.team_id, ["Short: " + (team.short || "-"), "League: " + (team.league || "-"), "Region: " + (team.region || "-")]);
    }).join("") : empty((payload.gaps || ["No team data"])[0]));
  }

  async function players() {
    const playersPayload = await getJson("/api/v1/esports/teams");
    if (playersPayload.data && playersPayload.data.length) {
      setHtml("players-list", empty("Seleccion de jugadores disponible via /api/v1/esports/players/{player_id}."));
      return;
    }
    setHtml("players-list", empty("No hay players persistidos todavia."));
  }

  async function counterpicks() {
    const payload = await getJson("/api/v1/esports/counterpicks?limit=50");
    const rows = (payload.data || []).map(function (item) {
      return "<tr><td>" + esc(item.role) + "</td><td>" + esc(item.champion_id) + "</td><td>" + esc(item.against_champion_id) + "</td><td>" + esc(item.games) + "</td><td>" + esc((item.winrate_shrunken * 100).toFixed(1)) + "%</td></tr>";
    });
    setHtml("counterpicks-count", String(payload.total_records || 0));
    setHtml("counterpicks-list", rows.length ? table(["Role", "Champion", "Against", "Games", "Shrunken WR"], rows) : empty((payload.gaps || ["No counterpick data"])[0]));
  }

  async function tournaments() {
    const payload = await getJson("/api/v1/esports/tournaments");
    const rows = payload.data || [];
    setHtml("tournaments-list", rows.length ? rows.map(function (tournament) {
      return card(tournament.name || tournament.tournament_id, ["League: " + (tournament.league || "-"), "Region: " + (tournament.region || "-"), "Format: " + (tournament.format || "-")]);
    }).join("") : empty((payload.gaps || ["No tournament data"])[0]));
  }

  const runners = { overview, drafts, teams, players, counterpicks, tournaments };
  (runners[page] || overview)().catch(function (err) {
    const target = page === "overview" ? "gaps-list" : page + "-list";
    setHtml(target, empty("Error cargando datos: " + err.message));
  }).finally(function () {
    if (window.LOLCLI_ScrollToTop) window.LOLCLI_ScrollToTop.refresh();
  });
})();
