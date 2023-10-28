$(function () {
    $("#btn").click(async function () {
        document.getElementById('log').innerHTML = `Generate is coming <div class="spinner-border spinner-border-sm text-danger" role="status"/>`;

        // Make a fetch request to the create_barcode endpoint
        const response = await fetch("create_barcode", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                count: $("#cartons_count").val(),
                boxes_count: $("#boxes").val(),
                route: $("#route_id").val(),
                start_place_id: $("#start_place_id").val(),
                delivery_variant_id: $("#type_id").val(),
            }),
        });

        // Check the response status code
        if (!response.ok) {
            console.error(response.statusText);
            document.getElementById('log').innerHTML = `<span>Error: ${response.statusText}</span><br>`;
            notifyMeN();
            return;
        }
        const data = await response.json();

        // Generate the barcode
        JsBarcode("#barcode", data);

        // Update the UI with the response data
        document.getElementById('log').innerHTML = `<span> Barcode created ${JSON.stringify(data)}</span><br>`;
        notifyMe();
    });
});