(() => {
    'use strict';

    const TIMEZONE_STORAGE_KEY = 'timezone';

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
        if (!timezone) return;

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
                redirect: 'manual',
            }
        );
        fetch(request).then(() => { console.info(`Timezone set to ${timezone}`); }).catch((err) => {
            console.warn('Timezone sync failed', err);
        });
    };

    sendTimezone();
})();
