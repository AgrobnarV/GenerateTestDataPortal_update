$(function () {
    $("#btn").click(async function setPriority() {
        document.getElementById('log').innerHTML = `Generate is coming <div class="spinner-border spinner-border-sm text-danger" role="status"/>`;

        const priority = $("input[type='radio'][name='inlineRadioOptions']:checked").val();
            if (!priority) {
                return;
            }
        // Make a fetch request to the create_barcode endpoint
        const response = await fetch("set_priority", {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              box_id: $("#box_id").val(),
              priority,
            }),
        });

        // Check the response status code
        if (!response.ok) {
            const error = await response.text();
            document.getElementById('log').innerHTML = `<span>Error: ${error}</span><br>`;
            document.getElementById('btn').disabled = false;
            notifyMeN();
            return;
        }

        const data = await response.json();

        // Update the UI with the response data
        document.getElementById('log').innerHTML = `<span>${JSON.stringify(data)}</span><br>`;
        document.getElementById('btn').disabled = false;
        notifyMe();
    });
});
