function buildApiDetailUrl(apiBaseUrl, id) {
	return new URL(id, `${apiBaseUrl}/`).href;
}

function buildApiDetailActionUrl(apiBaseUrl, id, action) {
	return new URL(action, buildApiDetailUrl(id, apiBaseUrl)).href;
}
