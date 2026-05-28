const state = {
  questions: [],
  query: "",
  category: "all",
  openId: 1,
};

const els = {
  input: document.querySelector("#searchInput"),
  form: document.querySelector(".search"),
  answers: document.querySelector("#answers"),
  resultTitle: document.querySelector("#resultTitle"),
  clearSearch: document.querySelector("#clearSearch"),
  categoryFilters: document.querySelector("#categoryFilters"),
  toTop: document.querySelector("#toTop"),
};

const normalize = (value) => String(value || "")
  .toLowerCase()
  .replaceAll("ё", "е")
  .normalize("NFKC");

const escapeHtml = (value) => String(value || "").replace(/[&<>'"]/g, (char) => ({
  "&": "\\u0026amp;",
  "<": "\\u0026lt;",
  ">": "\\u0026gt;",
  "'": "\\u0026#039;",
  '"': "\\u0026quot;",
}[char]));

const stripHtml = (value) => String(value || "")
  .replace(/<[^>]+>/g, " ")
  .replace(/&[^;]+;/g, " ")
  .replace(/\s+/g, " ")
  .trim();

const prepareQuestion = (question) => ({
  ...question,
  searchText: normalize(stripHtml(question.answerHtml)),
});

function scoreQuestion(question, query) {
  if (!query) return 1;
  const normalizedQuery = normalize(query).trim();
  const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
  const title = normalize(question.title);
  const answer = question.searchText;
  const id = String(question.id);
  const combined = `${id} ${title} ${answer} ${normalize((question.keywords || []).join(" "))}`;
  let score = 0;

  if (id === normalizedQuery) score += 120;
  if (title.includes(normalizedQuery)) score += 80;
  if (answer.includes(normalizedQuery)) score += 38;

  tokens.forEach((token) => {
    if (id === token) score += 80;
    if (title.includes(token)) score += 22;
    if (answer.includes(token)) score += 8;
    if (combined.includes(token)) score += 3;
  });

  return score;
}

function getContext(question, query) {
  const plain = question.answer ? stripHtml(question.answerHtml) : question.excerpt;
  if (!query) return question.excerpt || plain.slice(0, 220);
  const normalizedPlain = normalize(plain);
  const token = normalize(query).split(/\s+/).find((part) => part.length > 2) || normalize(query);
  const index = normalizedPlain.indexOf(token);
  if (index < 0) return question.excerpt || plain.slice(0, 220);
  const start = Math.max(0, index - 115);
  const end = Math.min(plain.length, index + token.length + 165);
  return `${start > 0 ? "..." : ""}${plain.slice(start, end)}${end < plain.length ? "..." : ""}`;
}

function highlight(text, query) {
  const safe = escapeHtml(text);
  const tokens = normalize(query).split(/\s+/).filter((part) => part.length > 1);
  if (!tokens.length) return safe;
  const unique = [...new Set(tokens)].sort((a, b) => b.length - a.length);
  const pattern = unique.map((token) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
  if (!pattern) return safe;
  return safe.replace(new RegExp(`(${pattern})`, "giu"), "<mark>$1</mark>");
}

function filteredQuestions() {
  const withScore = state.questions
    .filter((question) => state.category === "all" || question.category === state.category)
    .map((question) => ({ question, score: scoreQuestion(question, state.query) }))
    .filter((item) => !state.query || item.score > 0)
    .sort((a, b) => b.score - a.score || a.question.id - b.question.id);

  return withScore.map((item) => item.question);
}

function renderCategories() {
  const categories = ["all", ...new Set(state.questions.map((question) => question.category))];
  els.categoryFilters.innerHTML = categories.map((category) => {
    const label = category === "all" ? "Все" : category;
    const active = category === state.category ? " is-active" : "";
    return `<button class="chip${active}" type="button" data-category="${escapeHtml(category)}">${escapeHtml(label)}</button>`;
  }).join("");
}

function renderAnswers(questions) {
  if (!questions.length) {
    els.answers.innerHTML = `<div class="empty">Ничего не найдено. Попробуй другое слово, номер вопроса или часть формулировки.</div>`;
    return;
  }

  els.answers.innerHTML = questions.map((question) => {
    const isOpen = question.id === state.openId;
    const statusClass = question.status === "ready" ? "status-ready" : "status-missing";
    const statusLabel = question.status === "ready" ? "ответ загружен" : "ожидается ответ";
    const body = question.status === "ready" ? question.answerHtml : `<p class="muted">Ответ пока не добавлен.</p>`;
    const renderedBody = isOpen ? (state.query ? highlightAnswerHtml(body, state.query) : body) : "";
    return `
      <article class="answer-card${isOpen ? " is-open" : ""}" id="q-${question.id}" data-id="${question.id}">
        <header class="answer-card__header">
          <button class="answer-toggle" type="button" data-toggle="${question.id}" aria-expanded="${isOpen}">
            <div class="answer-card__top">
              <span class="badge">${question.id}</span>
              <span class="toggle-state">${isOpen ? "Свернуть" : "Открыть"}</span>
            </div>
            <h3>${highlight(question.title, state.query)}</h3>
            <div class="meta-list">
              <span class="meta-pill ${statusClass}">${statusLabel}</span>
              <span class="meta-pill">${escapeHtml(question.category)}</span>
              <span class="meta-pill">Источник: ${escapeHtml(question.source)}</span>
            </div>
          </button>
        </header>
        <div class="answer-card__body"${isOpen ? "" : " hidden"}>${renderedBody}</div>
      </article>`;
  }).join("");
}

function highlightAnswerHtml(html, query) {
  if (!query) return html;
  const wrapper = document.createElement("div");
  wrapper.innerHTML = html;
  const walker = document.createTreeWalker(wrapper, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  const tokens = normalize(query).split(/\s+/).filter((part) => part.length > 1);
  if (!tokens.length) return html;
  const pattern = tokens.map((token) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
  const regex = new RegExp(`(${pattern})`, "giu");
  nodes.forEach((node) => {
    const value = node.nodeValue;
    if (!regex.test(value)) return;
    const span = document.createElement("span");
    span.innerHTML = escapeHtml(value).replace(regex, "<mark>$1</mark>");
    node.replaceWith(...span.childNodes);
  });
  return wrapper.innerHTML;
}

function syncUrl() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category !== "all") params.set("category", state.category);
  const next = `${location.pathname}${params.toString() ? `?${params}` : ""}${location.hash}`;
  history.replaceState(null, "", next);
}

function render() {
  const questions = filteredQuestions();
  if (!questions.some((question) => question.id === state.openId)) {
    state.openId = questions[0]?.id || 0;
  }
  els.resultTitle.textContent = state.query
    ? `Найдено: ${questions.length}`
    : state.category === "all" ? "Все вопросы" : state.category;
  renderCategories();
  renderAnswers(questions);
  syncUrl();
}

function jumpToFirstResult() {
  const first = filteredQuestions()[0];
  if (!first) return;
  state.openId = first.id;
  render();
  requestAnimationFrame(() => {
    const card = document.querySelector(`#q-${first.id}`);
    if (!card) return;
    card.scrollIntoView({ behavior: "smooth", block: "start" });
    card.classList.add("is-highlighted");
    setTimeout(() => card.classList.remove("is-highlighted"), 1800);
  });
}

async function init() {
  const response = await fetch("data/questions.json");
  state.questions = (await response.json()).map(prepareQuestion);

  const params = new URLSearchParams(location.search);
  state.query = params.get("q") || "";
  state.category = params.get("category") || "all";
  els.input.value = state.query;

  render();

  if (location.hash) {
    requestAnimationFrame(() => document.querySelector(location.hash)?.scrollIntoView({ block: "start" }));
  }
}

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  state.query = els.input.value.trim();
  jumpToFirstResult();
});

els.input.addEventListener("input", () => {
  state.query = els.input.value.trim();
  render();
});

els.clearSearch.addEventListener("click", () => {
  state.query = "";
  state.category = "all";
  els.input.value = "";
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

els.categoryFilters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-category]");
  if (!button) return;
  state.category = button.dataset.category;
  render();
});

els.answers.addEventListener("click", (event) => {
  const button = event.target.closest("[data-toggle]");
  if (!button) return;
  state.openId = Number(button.dataset.toggle);
  render();
  requestAnimationFrame(() => document.querySelector(`#q-${state.openId}`)?.scrollIntoView({ block: "start" }));
});

window.addEventListener("scroll", () => {
  els.toTop.classList.toggle("is-visible", window.scrollY > 700);
});

els.toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

init().catch((error) => {
  console.error(error);
  els.answers.innerHTML = `<div class="empty">Не удалось загрузить базу вопросов. Проверь файл data/questions.json.</div>`;
});
