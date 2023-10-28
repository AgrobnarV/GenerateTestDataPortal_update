function notifyMe() {
    if (Notification.permission !== 'granted') {
        Notification.requestPermission().then((result) => {
            if (result !== 'granted') {
                // The user denied permission
                alert('Desktop notifications were denied.');
                return;
            }
        });
    }

    var notification = new Notification('Generate Test Data Portal', {
        body: 'Tasks is created',
    });
}

function notifyMeN() {
    if (Notification.permission !== 'granted') {
        Notification.requestPermission().then((result) => {
            if (result !== 'granted') {
                // The user denied permission
                alert('Desktop notifications were denied.');
                return;
            }
        });
    }

    var notification = new Notification('Generate Test Data Portal', {
        body: 'Something went wrong',
    });
}
