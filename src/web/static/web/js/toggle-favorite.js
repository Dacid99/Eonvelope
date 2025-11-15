// requires <script src="https://cdn.jsdelivr.net/npm/js-cookie@3.0.5/dist/js.cookie.min.js"></script> in the same template
const TOGGLE_CLASSES = {
    on: {
        class: 'bg-warning',
    },
    off: {
        class: 'bg-secondary',
    }
};
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.favorite-badge').forEach(function (badge) {
        badge.addEventListener('click', function () {
            const url = this.dataset.url;
            const badgeElement = this;
            const request = new Request(
                url,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    },
                    credentials: 'include',
                    mode: 'same-origin'
                }
            );
            fetch(request).then(response => {
                if (response.ok) {
                    const is_favorite = badgeElement.classList.contains(TOGGLE_CLASSES.on.class);
                    badgeElement.classList.remove(is_favorite ? TOGGLE_CLASSES.on.class : TOGGLE_CLASSES.off.class);
                    badgeElement.classList.add(is_favorite ? TOGGLE_CLASSES.off.class : TOGGLE_CLASSES.on.class);
                } else {
                    console.warn('Badge update failed with non-OK status.');
                }
            })
                .catch(() => {
                    console.error('Badge update failed!');
                });
        });
    });
});
