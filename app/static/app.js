const state = {
  cursor: null,
  snapshot: null,
  pageHistory: [],
  currentPage: null,
  loading: false,
};

const elements = {
  category: document.getElementById("category"),
  limit: document.getElementById("limit"),
  refresh: document.getElementById("refresh"),
  next: document.getElementById("next"),
  prev: document.getElementById("prev"),
  rows: document.getElementById("rows"),
  snapshot: document.getElementById("snapshot"),
  visible: document.getElementById("visible"),
  hasMore: document.getElementById("hasMore"),
  cursor: document.getElementById("cursor"),
};

function setLoading(isLoading) {
  state.loading = isLoading;
  elements.refresh.disabled = isLoading;
  elements.next.disabled = isLoading || !state.currentPage?.next_cursor;
  elements.prev.disabled = isLoading || state.pageHistory.length === 0;
}

function renderRows(items) {
  elements.rows.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.name}</td>
          <td>${item.category}</td>
          <td class="right">$${Number(item.price).toFixed(2)}</td>
          <td>${new Date(item.updated_at).toLocaleString()}</td>
        </tr>`
    )
    .join("");
}

function renderEmpty() {
  elements.rows.innerHTML = `
    <tr>
      <td colspan="5" style="padding: 28px 18px; text-align: center; color: #6a5d55;">
        No products found for this filter.
      </td>
    </tr>`;
}

function renderState(page) {
  state.currentPage = page;
  state.snapshot = page.snapshot;
  elements.snapshot.textContent = new Date(page.snapshot).toLocaleString();
  elements.visible.textContent = String(page.items.length);
  elements.hasMore.textContent = page.has_more ? "yes" : "no";
  elements.cursor.textContent = page.next_cursor || "-";
  elements.next.disabled = !page.next_cursor || state.loading;
  elements.prev.disabled = state.pageHistory.length === 0 || state.loading;

  if (page.items.length === 0) {
    renderEmpty();
    return;
  }

  renderRows(page.items);
}

async function loadPage(cursor = null, pushHistory = false) {
  const params = new URLSearchParams();
  const category = elements.category.value;
  const limit = elements.limit.value || "20";

  params.set("limit", limit);
  if (category) {
    params.set("category", category);
  }
  if (cursor) {
    params.set("cursor", cursor);
  }

  setLoading(true);

  try {
    const response = await fetch(`/products?${params.toString()}`);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed with status ${response.status}`);
    }

    const page = await response.json();
    if (pushHistory && state.currentPage) {
      state.pageHistory.push(state.currentPage);
    }
    state.cursor = cursor;
    renderState(page);
  } catch (error) {
    elements.rows.innerHTML = `
      <tr>
        <td colspan="5" style="padding: 28px 18px; text-align: center; color: #8c2d1d;">
          ${error.message}
        </td>
      </tr>`;
    elements.cursor.textContent = "-";
    elements.snapshot.textContent = "-";
    elements.visible.textContent = "0";
    elements.hasMore.textContent = "error";
    elements.next.disabled = true;
    elements.prev.disabled = state.pageHistory.length === 0;
  } finally {
    setLoading(false);
  }
}

elements.refresh.addEventListener("click", () => {
  state.pageHistory = [];
  loadPage();
});

elements.next.addEventListener("click", () => {
  if (state.currentPage?.next_cursor) {
    loadPage(state.currentPage.next_cursor, true);
  }
});

elements.prev.addEventListener("click", () => {
  const previous = state.pageHistory.pop();
  if (!previous) {
    return;
  }
  renderState(previous);
});

elements.category.addEventListener("change", () => {
  state.pageHistory = [];
  loadPage();
});

elements.limit.addEventListener("change", () => {
  state.pageHistory = [];
  loadPage();
});

loadPage();