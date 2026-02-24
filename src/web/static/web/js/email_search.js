(() => {
	document.getElementById("emailSearch").addEventListener("submit", (e) => {
		e.preventDefault();

		const query = e.currentTarget.querySelector("input").value.trim();
		if (query) {
			const encodedQuery = encodeURIComponent(query);
			window.location.href = `/emails/?search=${encodedQuery}`;
		}
	});
})();
