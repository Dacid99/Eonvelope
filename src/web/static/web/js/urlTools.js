function buildApiDetailUrl(baseUrl, id) {
	return new URL(id, baseUrl).href;
}

function buildApiDetailActionUrl(baseUrl, id, action) {
	return new URL(action, buildApiDetailUrl(id, baseUrl)).href;
}
