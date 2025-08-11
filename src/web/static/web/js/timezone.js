(() => {
    'use strict'

    const TIMEZONE_STORAGE_KEY = 'timezone'

    const getTimezone = () => {
        try {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            return timezone;
        } catch (e) {
            console.warn('Could not detect timezone', e);
            return;
        }
    };

    const sendTimezone = () => {
        const timezone = getTimezone();
        if (!timezone || sessionStorage.getItem(TIMEZONE_STORAGE_KEY) === timezone) return;

        const request = new Request(
            '/settz/',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': Cookies.get('csrftoken')
                },
                credentials: 'include',
                mode: 'same-origin',
                body: `timezone=${encodeURIComponent(timezone)}`,
            }
        );
        fetch(request).then(() => {
            sessionStorage.setItem(TIMEZONE_STORAGE_KEY, timezone);
        }).catch((err) => {
            console.warn('Timezone sync failed', err);
        });
    };

    sendTimezone();
})();
